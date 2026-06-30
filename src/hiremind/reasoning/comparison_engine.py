"""Comparison Engine — generates structured head-to-head candidate comparisons."""

from __future__ import annotations

from hiremind.domain.explanation import (
    CandidateComparison,
    CandidateExplanation,
    DimensionComparison,
)

# Dimensions to compare, mapped to their record key.
_DIMENSIONS = [
    ("Final Score", "final_score"),
    ("Technical Alignment", "technical_score"),
    ("Career Progression", "career_score"),
    ("Behavioral Signals", "behavior_score"),
    ("Knowledge Graph Depth", "knowledge_score"),
]


class ComparisonEngine:
    """Compares two candidates and produces a structured CandidateComparison."""

    def compare(
        self,
        explanation_a: CandidateExplanation,
        explanation_b: CandidateExplanation,
        record_a: dict[str, object],
        record_b: dict[str, object],
    ) -> CandidateComparison:
        """Generate a head-to-head comparison between two candidates."""
        dims: list[DimensionComparison] = []
        a_wins = 0
        b_wins = 0

        for label, key in _DIMENSIONS:
            score_a = float(record_a.get(key, 0.0))
            score_b = float(record_b.get(key, 0.0))
            delta = abs(score_a - score_b)

            if score_a > score_b:
                winner = explanation_a.candidate_id
                a_wins += 1
            elif score_b > score_a:
                winner = explanation_b.candidate_id
                b_wins += 1
            else:
                winner = "Tie"

            dims.append(
                DimensionComparison(
                    dimension=label,
                    candidate_a_score=score_a,
                    candidate_b_score=score_b,
                    winner=winner,
                    delta=delta,
                )
            )

        # Unique strengths / concerns
        a_strength_labels = {s.label for s in explanation_a.strengths}
        b_strength_labels = {s.label for s in explanation_b.strengths}
        a_concern_labels = {c.label for c in explanation_a.concerns}
        b_concern_labels = {c.label for c in explanation_b.concerns}

        a_unique_str = tuple(sorted(a_strength_labels - b_strength_labels))
        b_unique_str = tuple(sorted(b_strength_labels - a_strength_labels))
        a_unique_con = tuple(sorted(a_concern_labels - b_concern_labels))
        b_unique_con = tuple(sorted(b_concern_labels - a_concern_labels))

        # Overall winner
        if a_wins > b_wins:
            overall = explanation_a.candidate_id
        elif b_wins > a_wins:
            overall = explanation_b.candidate_id
        else:
            # Tie-break on final score
            overall = (
                explanation_a.candidate_id
                if explanation_a.final_score >= explanation_b.final_score
                else explanation_b.candidate_id
            )

        summary = (
            f"{overall} is the stronger candidate, winning {max(a_wins, b_wins)} of "
            f"{len(_DIMENSIONS)} dimensions. "
            f"{explanation_a.candidate_id} has {len(a_unique_str)} unique strengths "
            f"and {len(a_unique_con)} unique concerns. "
            f"{explanation_b.candidate_id} has {len(b_unique_str)} unique strengths "
            f"and {len(b_unique_con)} unique concerns."
        )

        return CandidateComparison(
            candidate_a_id=explanation_a.candidate_id,
            candidate_b_id=explanation_b.candidate_id,
            overall_winner=overall,
            dimensions=tuple(dims),
            a_unique_strengths=a_unique_str,
            b_unique_strengths=b_unique_str,
            a_unique_concerns=a_unique_con,
            b_unique_concerns=b_unique_con,
            summary=summary,
        )
