import asyncpg
import numpy as np


async def vector_search(
    query_embedding: list[float],
    pool: asyncpg.Pool,
    top_k: int = 10,
) -> list[dict]:
    embedding_array = np.array(query_embedding, dtype=np.float32)
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Probe all lists for full recall on this small corpus
            await conn.execute("SET LOCAL ivfflat.probes = 10")
            rows = await conn.fetch(
                """
                SELECT id, source, content,
                       1 - (embedding <=> $1::vector) AS score
                FROM documents
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                embedding_array,
                top_k,
            )
    return [dict(r) for r in rows]
