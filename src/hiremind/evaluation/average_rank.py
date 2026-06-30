"""Average Rank evaluation metrics."""

from __future__ import annotations


def compute_mrr(
    ranked_ids: list[str],
    ground_truth_relevance: dict[str, float],
) -> float:
    """Calculate Mean Reciprocal Rank (MRR).

    MRR is the average of the reciprocal ranks of the first relevant candidate
    for a set of queries. Since we typically evaluate a single query at a time,
    this returns the reciprocal rank of the first relevant candidate.
    """
    for rank, cid in enumerate(ranked_ids, start=1):
        if ground_truth_relevance.get(cid, 0.0) > 0.0:
            return 1.0 / rank

    return 0.0


def compute_mean_average_rank(
    ranked_ids: list[str],
    ground_truth_relevance: dict[str, float],
) -> float:
    """Calculate the mean rank of all relevant candidates retrieved.

    Returns 0.0 if no relevant candidates are found.
    """
    ranks = []
    for rank, cid in enumerate(ranked_ids, start=1):
        if ground_truth_relevance.get(cid, 0.0) > 0.0:
            ranks.append(rank)

    if not ranks:
        return 0.0

    return sum(ranks) / len(ranks)
