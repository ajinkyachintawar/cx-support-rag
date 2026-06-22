from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    query: str
    query_embedding: list[float]
    retrieved_docs: list[dict[str, Any]]
    answer: str
    confidence: float
    sources: list[str]
    should_escalate: bool
    latency_ms: int
