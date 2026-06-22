import hashlib
from pathlib import Path


def load_documents(kb_path: str) -> list[dict]:
    docs = []
    for md_file in sorted(Path(kb_path).glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        docs.append({
            "source": md_file.name,
            "content": content,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        })
    return docs
