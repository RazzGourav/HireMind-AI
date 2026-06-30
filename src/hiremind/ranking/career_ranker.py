"""Career Ranker — evaluates candidate career timeline, progression, and stability."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures


class CareerRanker:
    """Computes career score based on stability, promotions, tenure, and startup/enterprise exposure."""

    def score(self, candidate: Candidate, features: CandidateFeatures) -> float:
        """Score candidate's career progression and stability (0.0 to 1.0)."""
        summary = features.career_summary

        # Experience depth: target 120 months (10 years) for full score
        exp_months = summary.total_experience_months or 0
        exp_score = min(exp_months / 120.0, 1.0)

        # Stability score directly from summary
        stability = summary.career_stability or 0.0

        # Promotion score: 1 point per promotion, max 3
        promo_count = summary.promotion_count or 0
        promo_score = min(promo_count / 3.0, 1.0)

        # Company count: too many companies (job hopping) gets slight penalty, ideal is ~2-4
        company_count = summary.company_count or 1
        # Penalty if company count is high compared to total months (e.g. less than 18 months average tenure)
        hop_penalty = 0.0
        avg_tenure = summary.average_tenure_months or 0.0
        if avg_tenure > 0 and avg_tenure < 18.0:
            hop_penalty = min(0.3, (18.0 - avg_tenure) / 18.0)

        # Blend: 40% stability + 30% experience depth + 30% promotions - hop_penalty
        raw = 0.4 * stability + 0.3 * exp_score + 0.3 * promo_score - hop_penalty
        return round(min(max(raw, 0.0), 1.0), 3)
