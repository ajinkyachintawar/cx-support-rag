import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from src.config import settings


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503)
    return isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout))


_client = httpx.AsyncClient(timeout=30.0)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(_is_retryable),
)
async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await _client.post(
        settings.embedding_api_url,
        headers={"Authorization": f"Bearer {settings.jina_api_key}"},
        json={
            "model": settings.embedding_model,
            "input": texts,
            "dimensions": settings.embedding_dimension,
        },
    )
    response.raise_for_status()
    data = response.json()
    return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]


async def embed_query(text: str) -> list[float]:
    results = await embed_texts([text])
    return results[0]
