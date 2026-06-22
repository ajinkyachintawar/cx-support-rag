import tiktoken


_enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def chunk_document(
    content: str,
    source: str,
    max_tokens: int = 400,
    overlap_tokens: int = 50,
) -> list[dict]:
    token_count = count_tokens(content)

    if token_count <= max_tokens:
        return [{
            "content": content,
            "source": source,
            "chunk_index": 0,
            "token_count": token_count,
        }]

    paragraphs = content.split("\n\n")
    chunks = []
    current_paragraphs: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if current_tokens + para_tokens > max_tokens and current_paragraphs:
            chunk_text = "\n\n".join(current_paragraphs)
            chunks.append({
                "content": chunk_text,
                "source": source,
                "chunk_index": len(chunks),
                "token_count": count_tokens(chunk_text),
            })
            overlap_paras = []
            overlap_count = 0
            for p in reversed(current_paragraphs):
                p_tokens = count_tokens(p)
                if overlap_count + p_tokens > overlap_tokens:
                    break
                overlap_paras.insert(0, p)
                overlap_count += p_tokens
            current_paragraphs = overlap_paras
            current_tokens = overlap_count

        current_paragraphs.append(para)
        current_tokens += para_tokens

    if current_paragraphs:
        chunk_text = "\n\n".join(current_paragraphs)
        chunks.append({
            "content": chunk_text,
            "source": source,
            "chunk_index": len(chunks),
            "token_count": count_tokens(chunk_text),
        })

    return chunks
