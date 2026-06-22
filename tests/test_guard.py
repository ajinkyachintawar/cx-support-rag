import os
import asyncio
import pytest

os.environ.setdefault("KB_JINA_API_KEY", "test")
os.environ.setdefault("KB_GEMINI_API_KEY", "test")
os.environ.setdefault("KB_SUPABASE_URL", "postgresql://localhost/test")

from src.agent.nodes import guard_node


def test_guard_passes_high_confidence():
    state = {
        "confidence": 0.85,
        "retrieved_docs": [{"rrf_score": 0.03, "source": "test.md"}],
        "answer": "The refund window is 14 days.",
        "should_escalate": False,
    }
    result = asyncio.run(guard_node(state))
    assert result["confidence"] == 0.85
    assert result.get("should_escalate") is not True


def test_guard_escalates_low_confidence():
    state = {
        "confidence": 0.2,
        "retrieved_docs": [{"rrf_score": 0.03, "source": "test.md"}],
        "answer": "Some answer",
        "should_escalate": False,
    }
    result = asyncio.run(guard_node(state))
    assert result["should_escalate"] is True
    assert "escalate" in result["answer"].lower()


def test_guard_clamps_on_low_rrf():
    state = {
        "confidence": 0.8,
        "retrieved_docs": [{"rrf_score": 0.005, "source": "test.md"}],
        "answer": "Some answer",
        "should_escalate": False,
    }
    result = asyncio.run(guard_node(state))
    assert result["confidence"] <= 0.3
    assert result["should_escalate"] is True


def test_guard_handles_empty_docs():
    state = {
        "confidence": 0.0,
        "retrieved_docs": [],
        "answer": "No info",
        "should_escalate": True,
    }
    result = asyncio.run(guard_node(state))
    assert result["should_escalate"] is True
