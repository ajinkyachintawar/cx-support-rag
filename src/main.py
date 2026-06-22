import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.models import QueryRequest, QueryResponse, SourceReference
from src.db import get_pool, close_pool
from src.agent.graph import build_graph
from src.middleware.logging import RequestLoggingMiddleware, append_audit_log
from src.middleware.errors import global_exception_handler

logger = structlog.get_logger()

_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph
    await get_pool()
    _graph = build_graph()
    logger.info("app_started", model=settings.synthesis_model)
    yield
    await close_pool()
    logger.info("app_stopped")


app = FastAPI(
    title="Otonomee Knowledge Base Agent",
    version="1.0.0",
    description="RAG agent for CX support knowledge base queries",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


@app.get("/health")
async def health():
    checks = {}
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks, "version": "1.0.0"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    start = time.perf_counter()

    result = await _graph.ainvoke({"query": request.question})

    latency_ms = int((time.perf_counter() - start) * 1000)

    sources = [
        SourceReference(filename=doc["source"], rrf_score=round(doc["rrf_score"], 4))
        for doc in result.get("retrieved_docs", [])
    ]

    response = QueryResponse(
        answer=result.get("answer", ""),
        confidence=round(result.get("confidence", 0.0), 2),
        sources=sources,
        should_escalate=result.get("should_escalate", False),
        latency_ms=latency_ms,
    )

    append_audit_log({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": request.question,
        "answer": response.answer,
        "sources": [s.filename for s in sources],
        "confidence": response.confidence,
        "should_escalate": response.should_escalate,
        "latency_ms": latency_ms,
    })

    return response
