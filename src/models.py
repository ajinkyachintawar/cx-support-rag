from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class SourceReference(BaseModel):
    filename: str
    rrf_score: float


class QueryResponse(BaseModel):
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: list[SourceReference]
    should_escalate: bool
    latency_ms: int
