from pathlib import Path
from src.ingestion.chunker import chunk_document, count_tokens
from src.ingestion.loader import load_documents


def test_short_document_single_chunk():
    content = "This is a short document about refund policies. The standard refund window is 14 days."
    chunks = chunk_document(content, "test.md", max_tokens=400)
    assert len(chunks) == 1
    assert chunks[0]["source"] == "test.md"
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["token_count"] == count_tokens(content)


def test_long_document_splits():
    paragraphs = [f"Paragraph {i}. " * 30 for i in range(10)]
    content = "\n\n".join(paragraphs)
    chunks = chunk_document(content, "long.md", max_tokens=100, overlap_tokens=20)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk["source"] == "long.md"
        assert chunk["token_count"] <= 150  # allow overshoot from paragraph boundaries


def test_all_kb_documents_fit_single_chunk():
    kb_path = Path(__file__).parent.parent / "data" / "knowledge_base"
    if not kb_path.exists():
        return
    docs = load_documents(str(kb_path))
    assert len(docs) == 20
    for doc in docs:
        chunks = chunk_document(doc["content"], doc["source"], max_tokens=400)
        assert len(chunks) == 1, f"{doc['source']} was split into {len(chunks)} chunks"
        assert chunks[0]["token_count"] <= 400, f"{doc['source']} has {chunks[0]['token_count']} tokens"


def test_chunk_metadata():
    content = "Test content for metadata verification."
    chunks = chunk_document(content, "metadata_test.md")
    chunk = chunks[0]
    assert "source" in chunk
    assert "chunk_index" in chunk
    assert "token_count" in chunk
    assert "content" in chunk
    assert chunk["source"] == "metadata_test.md"
