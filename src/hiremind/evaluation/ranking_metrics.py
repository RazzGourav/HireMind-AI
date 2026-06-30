"""Ranking Evaluator — Computes ranking quality reports including NDCG, Precision, and MAP."""

import json
from pathlib import Path
from typing import Any

from hiremind.evaluation.ndcg import compute_ndcg
from hiremind.evaluation.precision import compute_precision
from hiremind.evaluation.recall import compute_recall


class RankingEvaluator:
    """Computes ranking quality statistics and exports JSON evaluation reports."""

    @staticmethod
    def compute_average_precision(
        ranked_ids: list[str],
        ground_truth_relevance: dict[str, float],
    ) -> float:
        """Calculate Average Precision (AP) for a ranked list."""
        relevances = [ground_truth_relevance.get(cid, 0.0) for cid in ranked_ids]
        total_relevant = sum(1 for rel in ground_truth_relevance.values() if rel > 0.0)

        if total_relevant == 0:
            return 0.0

        ap = 0.0
        hits = 0.0
        for i, val in enumerate(relevances):
            if val > 0.0:
                hits += 1.0
                precision_at_i = hits / (i + 1)
                ap += precision_at_i

        return ap / total_relevant

    @classmethod
    def evaluate_ranking(
        cls,
        ranked_records: list[dict[str, Any]],
        ground_truth_relevance: dict[str, float],
        latency_ms: float,
        output_path: str = "outputs/ranking_report.json",
    ) -> dict[str, Any]:
        """Compute comprehensive metrics including NDCG, Precision, Recall, MRR, and Diversity."""
        from hiremind.evaluation.average_rank import (
            compute_mean_average_rank,
            compute_mrr,
        )
        from hiremind.evaluation.diversity import compute_candidate_diversity

        ranked_ids = [r["candidate_id"] for r in ranked_records]

        ndcg_10 = compute_ndcg(ranked_ids, ground_truth_relevance, 10)
        ndcg_50 = compute_ndcg(ranked_ids, ground_truth_relevance, 50)
        precision_10 = compute_precision(ranked_ids, ground_truth_relevance, 10)

        recall_10 = compute_recall(ranked_ids, ground_truth_relevance, 10)
        recall_50 = compute_recall(ranked_ids, ground_truth_relevance, 50)
        recall_100 = compute_recall(ranked_ids, ground_truth_relevance, 100)
        recall_500 = compute_recall(ranked_ids, ground_truth_relevance, 500)

        ap = cls.compute_average_precision(ranked_ids, ground_truth_relevance)
        mrr = compute_mrr(ranked_ids, ground_truth_relevance)
        mean_rank = compute_mean_average_rank(ranked_ids, ground_truth_relevance)
        diversity_10 = compute_candidate_diversity(ranked_records, 10)

        report = {
            "ndcg_at_10": round(ndcg_10, 4),
            "ndcg_at_50": round(ndcg_50, 4),
            "precision_at_10": round(precision_10, 4),
            "recall_at_10": round(recall_10, 4),
            "recall_at_50": round(recall_50, 4),
            "recall_at_100": round(recall_100, 4),
            "recall_at_500": round(recall_500, 4),
            "mean_average_precision": round(ap, 4),
            "mrr": round(mrr, 4),
            "mean_relevant_rank": round(mean_rank, 2),
            "diversity_at_10": round(diversity_10, 4),
            "latency_ms": round(latency_ms, 2),
            "total_candidates_ranked": len(ranked_ids),
        }

        # Write to JSON
        if output_path:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        return report
