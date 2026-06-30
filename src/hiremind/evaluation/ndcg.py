"""NDCG evaluation metric calculation."""

import numpy as np


def compute_dcg(relevances: list[float], k: int) -> float:
    """Calculate Discounted Cumulative Gain at K."""
    k = min(k, len(relevances))
    if k == 0:
        return 0.0

    rels = np.ascontiguousarray(relevances[:k], dtype=np.float32)
    discounts = np.log2(np.arange(2, k + 2, dtype=np.float32))

    return float(np.sum((2**rels - 1) / discounts))


def compute_ndcg(
    ranked_ids: list[str],
    ground_truth_relevance: dict[str, float],
    k: int,
) -> float:
    """Calculate Normalized Discounted Cumulative Gain at K."""
    if not ground_truth_relevance:
        return 0.0

    # Get relevance scores in ranked order
    relevances = [ground_truth_relevance.get(cid, 0.0) for cid in ranked_ids]

    dcg = compute_dcg(relevances, k)

    # Ideal DCG is sorted relevances in descending order
    ideal_relevances = sorted(ground_truth_relevance.values(), reverse=True)
    idcg = compute_dcg(ideal_relevances, k)

    if idcg == 0.0:
        return 0.0

    return dcg / idcg
