"""Interview recommendation domain models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InterviewRecommendation(Enum):
    """Interview recommendation classification."""

    STRONG_HIRE = "Strong Hire"
    HIRE = "Hire"
    INTERVIEW = "Interview"
    HOLD = "Hold"
    REJECT = "Reject"


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Structured interview recommendation for a single candidate."""

    candidate_id: str
    recommendation: InterviewRecommendation
    confidence: float
    rationale: str

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "recommendation": self.recommendation.value,
            "confidence": round(self.confidence, 2),
            "rationale": self.rationale,
        }
