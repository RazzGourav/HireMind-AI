"""Error analysis to investigate highly relevant but dropped candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hiremind.domain.explanation import CandidateExplanation


class ErrorAnalysis:
    """Analyzes edge cases and misses in the ranking pipeline."""

    def __init__(self) -> None:
        self.misses: list[dict[str, Any]] = []

    def analyze_misses(
        self,
        retrieved_ids: set[str],
        ranked_records: list[dict[str, Any]],
        ground_truth_relevance: dict[str, float],
        explanations: list[CandidateExplanation],
        relevance_threshold: float = 2.0,
    ) -> list[dict[str, Any]]:
        """Identify relevant candidates that were either not retrieved or ranked low."""
        self.misses = []

        # Build quick lookups
        ranked_dict = {r["candidate_id"]: r for r in ranked_records}
        rank_positions = {r["candidate_id"]: i + 1 for i, r in enumerate(ranked_records)}
        exp_dict = {e.candidate_id: e for e in explanations}

        for cid, relevance in ground_truth_relevance.items():
            if relevance >= relevance_threshold:
                # Highly relevant candidate

                # Case 1: Not retrieved at all
                if cid not in retrieved_ids:
                    self.misses.append(
                        {
                            "candidate_id": cid,
                            "type": "retrieval_miss",
                            "relevance": relevance,
                            "reason": "Filtered out by structured filters or dense search failed to retrieve.",
                        }
                    )
                    continue

                # Case 2: Retrieved but ranked poorly (e.g. outside top 50)
                rank = rank_positions.get(cid, 9999)
                if rank > 50:
                    exp = exp_dict.get(cid)
                    concerns = [c.label for c in exp.concerns] if exp else []
                    penalty = ranked_dict.get(cid, {}).get("risk_penalty", 0.0)

                    self.misses.append(
                        {
                            "candidate_id": cid,
                            "type": "ranking_miss",
                            "rank": rank,
                            "relevance": relevance,
                            "risk_penalty": penalty,
                            "concerns_flagged": concerns,
                            "reason": "Candidate was retrieved but received a low ranking score.",
                        }
                    )

        return self.misses

    def generate_report(self, output_path: str = "outputs/error_analysis.json") -> dict[str, Any]:
        """Save error analysis report to JSON."""
        report = {
            "total_misses": len(self.misses),
            "retrieval_misses": sum(1 for m in self.misses if m["type"] == "retrieval_miss"),
            "ranking_misses": sum(1 for m in self.misses if m["type"] == "ranking_miss"),
            "miss_details": self.misses,
        }

        if output_path:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        return report
