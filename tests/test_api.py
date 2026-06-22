from src.models import QueryRequest, QueryResponse, SourceReference
import pytest


def test_query_request_validation():
    req = QueryRequest(question="What is the refund policy?")
    assert req.question == "What is the refund policy?"


def test_query_request_empty_rejected():
    with pytest.raises(Exception):
        QueryRequest(question="")


def test_query_request_too_long_rejected():
    with pytest.raises(Exception):
        QueryRequest(question="x" * 501)


def test_query_response_model():
    resp = QueryResponse(
        answer="The standard refund window is 14 days.",
        confidence=0.95,
        sources=[SourceReference(filename="refund_policy_standard.md", rrf_score=0.033)],
        should_escalate=False,
        latency_ms=150,
    )
    assert resp.confidence == 0.95
    assert len(resp.sources) == 1
    assert resp.sources[0].filename == "refund_policy_standard.md"


def test_query_response_confidence_bounds():
    with pytest.raises(Exception):
        QueryResponse(
            answer="test",
            confidence=1.5,
            sources=[],
            should_escalate=False,
            latency_ms=100,
        )
