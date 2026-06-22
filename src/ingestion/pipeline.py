import asyncpg
import numpy as np
import structlog

from src.config import settings
from src.ingestion.loader import load_documents
from src.ingestion.chunker import chunk_document
from src.embeddings import embed_texts

logger = structlog.get_logger()


async def run_ingestion(pool: asyncpg.Pool):
    docs = load_documents(settings.knowledge_base_path)
    logger.info("loaded_documents", count=len(docs))

    all_chunks = []
    for doc in docs:
        chunks = chunk_document(
            doc["content"],
            doc["source"],
            max_tokens=settings.chunk_max_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
        for chunk in chunks:
            chunk["content_hash"] = doc["content_hash"]
        all_chunks.extend(chunks)

    logger.info("chunked_documents", chunk_count=len(all_chunks))

    async with pool.acquire() as conn:
        existing = await conn.fetch("SELECT source, chunk_index, content_hash FROM documents")
        existing_map = {(r["source"], r["chunk_index"]): r["content_hash"] for r in existing}

    new_chunks = [
        c for c in all_chunks
        if existing_map.get((c["source"], c["chunk_index"])) != c["content_hash"]
    ]

    if not new_chunks:
        logger.info("ingestion_skipped", reason="all documents unchanged")
        return len(all_chunks)

    logger.info("embedding_chunks", count=len(new_chunks))
    texts = [c["content"] for c in new_chunks]

    batch_size = 10
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = await embed_texts(batch)
        all_embeddings.extend(embeddings)

    async with pool.acquire() as conn:
        for chunk, embedding in zip(new_chunks, all_embeddings):
            embedding_array = np.array(embedding, dtype=np.float32)
            await conn.execute(
                """
                INSERT INTO documents (source, content, content_hash, chunk_index, token_count, embedding)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (source, chunk_index)
                DO UPDATE SET content = $2, content_hash = $3, token_count = $5,
                              embedding = $6, updated_at = now()
                """,
                chunk["source"],
                chunk["content"],
                chunk["content_hash"],
                chunk["chunk_index"],
                chunk["token_count"],
                embedding_array,
            )
            logger.info("upserted_chunk", source=chunk["source"], chunk_index=chunk["chunk_index"])

    logger.info("ingestion_complete", total_chunks=len(all_chunks), upserted=len(new_chunks))
    return len(all_chunks)
