"""Evidence Service — coordinates production, leadership, and growth scoring."""

from hiremind.domain.candidate import Candidate
from hiremind.infrastructure.candidate.growth import score_growth
from hiremind.infrastructure.candidate.leadership import score_leadership
from hiremind.infrastructure.candidate.production import score_production


class EvidenceService:
    """Aggregate evidence scoring for a candidate."""

    @staticmethod
    def score(candidate: Candidate) -> dict[str, float]:
        """Run all evidence scorers and return a dict of scores."""
        return {
            "production_score": score_production(candidate),
            "leadership_score": score_leadership(candidate),
            "growth_score": score_growth(candidate),
        }
