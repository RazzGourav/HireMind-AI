"""Precision@K evaluation metric calculation."""


def compute_precision(
    ranked_ids: list[str],
    ground_truth_relevance: dict[str, float],
    k: int,
) -> float:
    """Calculate Precision@K (proportion of retrieved candidates that are relevant)."""
    k = min(k, len(ranked_ids))
    if k == 0:
        return 0.0

    top_k = ranked_ids[:k]
    # Treat relevance > 0.0 as relevant
    hits = sum(1 for cid in top_k if ground_truth_relevance.get(cid, 0.0) > 0.0)

    return hits / k
