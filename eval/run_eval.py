import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from groq import AsyncGroq

from src.config import settings
from src.db import get_pool, close_pool
from src.agent.graph import build_graph
from src.agent.prompts import FAITHFULNESS_JUDGE_PROMPT
from eval.metrics import EvalResult, compute_metrics

_judge_client: AsyncGroq | None = None


def _get_judge() -> AsyncGroq:
    global _judge_client
    if _judge_client is None:
        _judge_client = AsyncGroq(api_key=settings.groq_api_key)
    return _judge_client


async def evaluate_faithfulness(answer: str, retrieved_docs: list[dict]) -> float:
    if not retrieved_docs or not answer:
        return 0.0

    context = "\n\n---\n\n".join(
        f"[Source: {doc['source']}]\n{doc['content']}"
        for doc in retrieved_docs
    )
    prompt = FAITHFULNESS_JUDGE_PROMPT.format(context=context, answer=answer)

    try:
        client = _get_judge()
        response = await client.chat.completions.create(
            model=settings.synthesis_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=512,
            temperature=0.0,
        )
        result = json.loads(response.choices[0].message.content or "{}")
        return float(result.get("score", 0.0))
    except Exception as e:
        print(f"  Faithfulness eval error: {e}")
        return 0.0


async def run_single_case(graph, case: dict) -> EvalResult:
    # Retry on 429 with backoff
    for attempt in range(4):
        try:
            start = time.perf_counter()
            result = await graph.ainvoke({"query": case["question"]})
            latency_ms = int((time.perf_counter() - start) * 1000)
            break
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower() or "rate limit" in err.lower():
                wait = 30 * (attempt + 1)
                print(f"  [rate limit] waiting {wait}s (attempt {attempt+1}/4)...")
                await asyncio.sleep(wait)
            elif "503" in err or "502" in err or "unavailable" in err.lower():
                wait = 15 * (attempt + 1)
                print(f"  [server error] waiting {wait}s (attempt {attempt+1}/4)...")
                await asyncio.sleep(wait)
            else:
                raise
    else:
        return EvalResult(
            test_id=case["id"], category=case["category"], question=case["question"],
            expected_source=case.get("expected_source"), expected_answer_contains=case.get("expected_answer_contains", []),
            expected_escalate=case.get("should_escalate", False),
            actual_answer="Rate limit error", actual_confidence=0.0,
            actual_sources=[], actual_escalate=True, latency_ms=0,
        )

    retrieved_docs = result.get("retrieved_docs", [])
    actual_sources = [doc["source"] for doc in retrieved_docs]

    faithfulness = await evaluate_faithfulness(
        result.get("answer", ""),
        retrieved_docs,
    )

    eval_result = EvalResult(
        test_id=case["id"],
        category=case["category"],
        question=case["question"],
        expected_source=case.get("expected_source"),
        expected_answer_contains=case.get("expected_answer_contains", []),
        expected_escalate=case.get("should_escalate", False),
        actual_answer=result.get("answer", ""),
        actual_confidence=result.get("confidence", 0.0),
        actual_sources=actual_sources,
        actual_escalate=result.get("should_escalate", False),
        latency_ms=latency_ms,
        faithfulness_score=faithfulness,
    )

    status = "✓" if eval_result.answer_correct and eval_result.escalation_correct else "✗"
    print(f"  {status} {case['id']} ({case['category']}) — "
          f"conf={eval_result.actual_confidence:.2f}, "
          f"hit={eval_result.retrieval_hit}, "
          f"correct={eval_result.answer_correct}, "
          f"escalation={eval_result.escalation_correct}, "
          f"latency={latency_ms}ms")

    return eval_result


def generate_report(results: list[EvalResult], metrics: dict) -> str:
    lines = [
        "# Evaluation Report",
        "",
        f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Model:** {settings.synthesis_model}",
        f"**Embeddings:** {settings.embedding_model}",
        f"**Total cases:** {metrics['total_cases']}",
        "",
        "---",
        "",
        "## Overall Metrics",
        "",
        f"| Metric | Score | Target | Status |",
        f"|--------|-------|--------|--------|",
        f"| Retrieval Hit Rate @3 | {metrics['retrieval_hit_rate']:.1%} | >=90% | {'PASS' if metrics['retrieval_hit_rate'] >= 0.90 else 'FAIL'} |",
        f"| Answer Correctness | {metrics['answer_correctness']:.1%} | >=85% | {'PASS' if metrics['answer_correctness'] >= 0.85 else 'FAIL'} |",
        f"| Escalation Accuracy | {metrics['escalation_accuracy']:.1%} | >=90% | {'PASS' if metrics['escalation_accuracy'] >= 0.90 else 'FAIL'} |",
        f"| Avg Faithfulness | {metrics['avg_faithfulness']:.1%} | >=85% | {'PASS' if metrics['avg_faithfulness'] >= 0.85 else 'FAIL'} |",
        f"| **Confident + Wrong Rate** | **{metrics['confident_wrong_rate']:.1%}** | **<5%** | **{'PASS' if metrics['confident_wrong_rate'] < 0.05 else 'FAIL -- HARD GATE'}** |",
        "",
        "## Latency",
        "",
        f"| Percentile | Latency | Target |",
        f"|------------|---------|--------|",
        f"| p50 | {metrics['latency_p50_ms']}ms | |",
        f"| p95 | {metrics['latency_p95_ms']}ms | {'PASS' if metrics['latency_p95_ms'] < 3000 else 'FAIL'} (<3000ms) |",
        f"| p99 | {metrics['latency_p99_ms']}ms | |",
        "",
        "## Calibration Matrix",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
    ]

    for label, count in metrics["calibration"].items():
        marker = " [DANGER]" if label == "confident_wrong" and count > 0 else ""
        lines.append(f"| {label} | {count}{marker} |")

    lines.extend([
        "",
        "---",
        "",
        f"## EVAL {'PASSED' if metrics['passed'] else 'FAILED'}",
        "",
    ])

    if not metrics["passed"]:
        lines.append("**Failure reasons:**")
        if metrics["confident_wrong_rate"] >= 0.05:
            lines.append(f"- Confident+wrong rate ({metrics['confident_wrong_rate']:.1%}) exceeds 5% threshold")
        if metrics["retrieval_hit_rate"] < 0.90:
            lines.append(f"- Retrieval hit rate ({metrics['retrieval_hit_rate']:.1%}) below 90% target")

    lines.extend(["", "## Per-Case Results", ""])
    lines.append("| ID | Category | Confidence | Hit | Correct | Escalation | Latency | Calibration |")
    lines.append("|-----|----------|-----------|-----|---------|------------|---------|-------------|")

    for r in results:
        lines.append(
            f"| {r.test_id} | {r.category} | {r.actual_confidence:.2f} | "
            f"{'✓' if r.retrieval_hit else '✗'} | "
            f"{'✓' if r.answer_correct else '✗'} | "
            f"{'✓' if r.escalation_correct else '✗'} | "
            f"{r.latency_ms}ms | {r.calibration_label} |"
        )

    # Show details for failures
    failures = [r for r in results if not r.answer_correct or not r.escalation_correct]
    if failures:
        lines.extend(["", "## Failure Details", ""])
        for r in failures:
            lines.extend([
                f"### {r.test_id} — {r.category}",
                f"**Question:** {r.question}",
                f"**Expected source:** {r.expected_source}",
                f"**Expected keywords:** {r.expected_answer_contains}",
                f"**Expected escalation:** {r.expected_escalate}",
                f"**Actual answer:** {r.actual_answer[:200]}...",
                f"**Actual confidence:** {r.actual_confidence}",
                f"**Actual sources:** {r.actual_sources[:3]}",
                f"**Actual escalation:** {r.actual_escalate}",
                "",
            ])

    return "\n".join(lines)


async def main():
    gt_path = Path(__file__).parent / "ground_truth.json"
    test_cases = json.loads(gt_path.read_text())

    print(f"Running eval suite: {len(test_cases)} cases")
    print(f"Model: {settings.synthesis_model}")
    print(f"Embeddings: {settings.embedding_model}")
    print()

    await get_pool()
    graph = build_graph()

    results = []
    for i, case in enumerate(test_cases):
        result = await run_single_case(graph, case)
        results.append(result)
        # Groq: 30 RPM — small sleep to avoid bursting
        if i < len(test_cases) - 1:
            await asyncio.sleep(3)

    metrics = compute_metrics(results)

    print()
    print("=" * 60)
    print("EVAL RESULTS")
    print("=" * 60)
    print(f"Retrieval Hit Rate: {metrics['retrieval_hit_rate']:.1%}")
    print(f"Answer Correctness: {metrics['answer_correctness']:.1%}")
    print(f"Escalation Accuracy: {metrics['escalation_accuracy']:.1%}")
    print(f"Avg Faithfulness: {metrics['avg_faithfulness']:.1%}")
    print(f"Confident+Wrong Rate: {metrics['confident_wrong_rate']:.1%}")
    print(f"Latency p50={metrics['latency_p50_ms']}ms p95={metrics['latency_p95_ms']}ms p99={metrics['latency_p99_ms']}ms")
    print()

    cal = metrics["calibration"]
    print("Calibration Matrix:")
    for label, count in cal.items():
        print(f"  {label}: {count}")

    print()
    gate = "PASSED" if metrics["passed"] else "FAILED"
    print(f"EVAL GATE: {gate}")

    report = generate_report(results, metrics)
    report_path = Path(__file__).parent / "report.md"
    report_path.write_text(report)
    print(f"\nFull report written to {report_path}")

    await close_pool()
    return metrics["passed"]


if __name__ == "__main__":
    passed = asyncio.run(main())
    sys.exit(0 if passed else 1)
