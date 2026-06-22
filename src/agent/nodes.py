import asyncio
import json
import structlog
from groq import AsyncGroq

from src.agent.state import AgentState
from src.agent.prompts import SYNTHESIS_SYSTEM_PROMPT

logger = structlog.get_logger()

_groq_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _groq_client
    if _groq_client is None:
        from src.config import settings
        _groq_client = AsyncGroq(api_key=settings.groq_api_key)
    return _groq_client


async def query_node(state: AgentState) -> dict:
    from src.embeddings import embed_query
    query = state["query"].strip()[:500]
    embedding = await embed_query(query)
    return {"query": query, "query_embedding": embedding}


async def retrieval_node(state: AgentState) -> dict:
    from src.config import settings
    from src.db import get_pool
    from src.retrieval.vector import vector_search
    from src.retrieval.keyword import keyword_search
    from src.retrieval.fusion import reciprocal_rank_fusion

    pool = await get_pool()
    vector_results, kw_results = await asyncio.gather(
        vector_search(state["query_embedding"], pool, top_k=settings.vector_top_k),
        keyword_search(state["query"], pool, top_k=settings.keyword_top_k),
    )
    fused = reciprocal_rank_fusion(
        [vector_results, kw_results],
        k=settings.rrf_k,
        top_n=settings.fusion_top_n,
    )
    logger.info(
        "retrieval_complete",
        vector_count=len(vector_results),
        keyword_count=len(kw_results),
        fused_count=len(fused),
        top_sources=[d["source"] for d in fused[:3]],
    )
    return {"retrieved_docs": fused}


async def synthesis_node(state: AgentState) -> dict:
    from src.config import settings

    docs = state.get("retrieved_docs", [])
    if not docs:
        return {
            "answer": "I don't have enough information in the knowledge base to answer this question. Please escalate to a supervisor or subject matter expert.",
            "confidence": 0.0,
            "sources": [],
            "should_escalate": True,
        }

    # Pass only top-k docs to keep context tight (retrieve more, synthesize fewer)
    synthesis_docs = docs[:settings.synthesis_top_k]
    context = "\n\n---\n\n".join(
        f"[Source: {doc['source']}]\n{doc['content']}"
        for doc in synthesis_docs
    )
    user_prompt = f"Context documents:\n{context}\n\nSupport agent's question: {state['query']}"

    client = _get_client()
    try:
        response = await client.chat.completions.create(
            model=settings.synthesis_model,
            messages=[
                {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=settings.synthesis_max_tokens,
            temperature=0.1,
        )
    except Exception as e:
        logger.error("synthesis_api_error", error=str(e)[:200])
        raise

    raw = response.choices[0].message.content or ""
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("synthesis_json_parse_error", raw=raw[:300], error=str(e))
        return {
            "answer": "I encountered an error processing this query. Please try again or escalate.",
            "confidence": 0.0,
            "sources": [],
            "should_escalate": True,
        }

    return {
        "answer": result.get("answer", ""),
        "confidence": float(result.get("confidence", 0.0)),
        "sources": result.get("sources", []),
        "should_escalate": result.get("should_escalate", False),
    }


async def guard_node(state: AgentState) -> dict:
    from src.config import settings

    confidence = state.get("confidence", 0.0)
    docs = state.get("retrieved_docs", [])

    top_rrf = docs[0]["rrf_score"] if docs else 0.0
    if top_rrf < settings.rrf_score_floor:
        confidence = min(confidence, 0.3)

    if confidence < settings.confidence_threshold:
        return {
            "confidence": confidence,
            "should_escalate": True,
            "answer": (
                "I don't have enough information in the knowledge base to answer "
                "this confidently. Please escalate to a supervisor or subject matter expert."
            ),
        }

    return {"confidence": confidence}
