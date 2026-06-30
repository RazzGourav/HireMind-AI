"""Candidate Diversity evaluation metric."""

from __future__ import annotations

from typing import Any


def compute_candidate_diversity(
    ranked_records: list[dict[str, Any]],
    k: int = 10,
) -> float:
    """Calculate the diversity of the top-K candidates.

    Measures variance in the technical and career scores among the top K candidates
    to ensure the model isn't just returning identical profiles.

    Returns a diversity score typically between 0.0 and 1.0, where higher is more diverse.
    """
    k = min(k, len(ranked_records))
    if k <= 1:
        return 0.0

    top_k = ranked_records[:k]

    tech_scores = [float(r.get("technical_score", 0.0)) for r in top_k]
    career_scores = [float(r.get("career_score", 0.0)) for r in top_k]

    # Calculate variance manually to avoid heavy dependencies if not needed
    def _variance(data: list[float]) -> float:
        n = len(data)
        mean = sum(data) / n
        return sum((x - mean) ** 2 for x in data) / (n - 1)

    tech_var = _variance(tech_scores)
    career_var = _variance(career_scores)

    # Normalize roughly (assuming scores are 0-100, variance can be up to ~2500)
    # We map it to a 0-1 scale relative to a "reasonable" expected variance of ~400
    norm_tech = min(tech_var / 400.0, 1.0)
    norm_career = min(career_var / 400.0, 1.0)

    return (norm_tech + norm_career) / 2.0
