"""Retrieval Metrics — Evaluates candidate recall and similarity statistics."""

from typing import Any

from hiremind.domain.retrieval_result import RetrievalResult


class RetrievalEvaluator:
    """Computes retrieval metrics such as Recall@K and mean similarity score."""

    @staticmethod
    def calculate_recall(retrieved_ids: list[str], ground_truth_ids: list[str], k: int) -> float:
        """Calculate Recall@K against target ground truth candidate list."""
        if not ground_truth_ids:
            return 0.0

        top_k = retrieved_ids[:k]
        hits = len(set(top_k) & set(ground_truth_ids))
        return hits / len(ground_truth_ids)

    @classmethod
    def evaluate(
        self,
        retrieved: list[RetrievalResult],
        ground_truth_ids: list[str],
        latency_ms: float,
    ) -> dict[str, Any]:
        """Compute complete summary metrics dictionary."""
        retrieved_ids = [r.candidate_id for r in retrieved]

        recall_100 = self.calculate_recall(retrieved_ids, ground_truth_ids, 100)
        recall_500 = self.calculate_recall(retrieved_ids, ground_truth_ids, 500)

        # Average similarity of top matches
        scores = [r.score for r in retrieved]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        return {
            "recall_at_100": round(recall_100, 4),
            "recall_at_500": round(recall_500, 4),
            "average_similarity": round(avg_score, 4),
            "latency_ms": round(latency_ms, 2),
            "total_retrieved": len(retrieved),
        }
