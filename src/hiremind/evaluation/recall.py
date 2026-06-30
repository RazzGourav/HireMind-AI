"""Recall@K ranking evaluation metric calculation."""


def compute_recall(
    ranked_ids: list[str],
    ground_truth_relevance: dict[str, float],
    k: int,
) -> float:
    """Calculate Recall@K (proportion of total relevant candidates retrieved)."""
    k = min(k, len(ranked_ids))
    if k == 0:
        return 0.0

    top_k = ranked_ids[:k]
    # Candidates with relevance > 0.0 are considered target hits
    hits = sum(1 for cid in top_k if ground_truth_relevance.get(cid, 0.0) > 0.0)

    total_relevant = sum(1 for rel in ground_truth_relevance.values() if rel > 0.0)
    if total_relevant == 0:
        return 0.0

    return hits / total_relevant
