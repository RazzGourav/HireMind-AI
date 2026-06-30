"""Retrieval result domain model holding candidate similarity matches."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RetrievalResult:
    """Structure representing a single candidate match returned by the retrieval stage."""

    candidate_id: str
    score: float
    features: dict[str, float] = field(default_factory=dict)
