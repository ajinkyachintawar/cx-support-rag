from dataclasses import dataclass


@dataclass
class EvalResult:
    test_id: str
    category: str
    question: str
    expected_source: str | None
    expected_answer_contains: list[str]
    expected_escalate: bool

    actual_answer: str
    actual_confidence: float
    actual_sources: list[str]
    actual_escalate: bool
    latency_ms: int

    retrieval_hit: bool = False
    answer_correct: bool = False
    escalation_correct: bool = False
    faithfulness_score: float = 0.0

    def __post_init__(self):
        if self.expected_source:
            self.retrieval_hit = self.expected_source in self.actual_sources[:3]
        else:
            self.retrieval_hit = True

        if self.expected_answer_contains:
            answer_lower = self.actual_answer.lower()
            # Normalize hyphens to spaces so "end-of-cycle" matches "end of"
            answer_normalized = answer_lower.replace("-", " ")
            self.answer_correct = all(
                kw.lower() in answer_lower or kw.lower() in answer_normalized
                for kw in self.expected_answer_contains
            )
        else:
            self.answer_correct = self.actual_escalate == self.expected_escalate

        self.escalation_correct = self.actual_escalate == self.expected_escalate

    @property
    def is_confident(self) -> bool:
        return self.actual_confidence >= 0.7

    @property
    def calibration_label(self) -> str:
        if self.is_confident and self.answer_correct and self.escalation_correct:
            return "confident_correct"
        if self.is_confident and (not self.answer_correct or not self.escalation_correct):
            return "confident_wrong"
        if self.actual_escalate and self.expected_escalate:
            return "escalated_correctly"
        if self.actual_escalate and not self.expected_escalate:
            return "escalated_unnecessarily"
        if not self.is_confident and self.answer_correct:
            return "cautious_correct"
        return "cautious_wrong"


def compute_metrics(results: list[EvalResult]) -> dict:
    n = len(results)

    retrieval_eligible = [r for r in results if r.expected_source is not None]
    hit_rate = (
        sum(r.retrieval_hit for r in retrieval_eligible) / len(retrieval_eligible)
        if retrieval_eligible else 0.0
    )

    correctness_eligible = [r for r in results if r.expected_answer_contains]
    correctness = (
        sum(r.answer_correct for r in correctness_eligible) / len(correctness_eligible)
        if correctness_eligible else 0.0
    )

    escalation_acc = sum(r.escalation_correct for r in results) / n if n else 0.0

    faithfulness_scores = [r.faithfulness_score for r in results if r.faithfulness_score > 0]
    avg_faithfulness = (
        sum(faithfulness_scores) / len(faithfulness_scores)
        if faithfulness_scores else 0.0
    )

    calibration = {
        "confident_correct": 0,
        "confident_wrong": 0,
        "escalated_correctly": 0,
        "escalated_unnecessarily": 0,
        "cautious_correct": 0,
        "cautious_wrong": 0,
    }
    for r in results:
        label = r.calibration_label
        calibration[label] = calibration.get(label, 0) + 1

    confident_wrong_rate = calibration["confident_wrong"] / n if n else 0.0

    latencies = sorted(r.latency_ms for r in results)
    p50 = latencies[int(0.50 * len(latencies))] if latencies else 0
    p95 = latencies[int(0.95 * len(latencies))] if latencies else 0
    p99 = latencies[min(int(0.99 * len(latencies)), len(latencies) - 1)] if latencies else 0

    passed = confident_wrong_rate < 0.05 and hit_rate >= 0.90

    return {
        "total_cases": n,
        "retrieval_hit_rate": round(hit_rate, 3),
        "answer_correctness": round(correctness, 3),
        "escalation_accuracy": round(escalation_acc, 3),
        "avg_faithfulness": round(avg_faithfulness, 3),
        "calibration": calibration,
        "confident_wrong_rate": round(confident_wrong_rate, 3),
        "latency_p50_ms": p50,
        "latency_p95_ms": p95,
        "latency_p99_ms": p99,
        "passed": passed,
    }
