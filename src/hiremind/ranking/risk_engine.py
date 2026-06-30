"""Risk Engine — computes risk penalties for candidate profiles."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.domain.requirement import ParsedRequirements


class RiskEngine:
    """Calculates risk penalties based on notice periods, profile consistency, and keyword stuffing."""

    def calculate_penalty(
        self,
        candidate: Candidate,
        features: CandidateFeatures,
        requirements: ParsedRequirements,
        max_notice_days: int = 90,
    ) -> float:
        """Calculate aggregate risk penalty (0.0 to 1.0) to subtract from the candidate's rank score."""
        penalty = 0.0

        # 1. Profile consistency penalty (low consistency_score)
        consistency = features.consistency_score
        if consistency < 0.4:
            penalty += 0.15

        # 2. Excessive notice period penalty
        notice_days = getattr(candidate.profile, "notice_period_days", None)
        if notice_days is not None and notice_days > max_notice_days:
            # Scale penalty based on excess days
            penalty += min(0.2, (notice_days - max_notice_days) / 100.0)

        # 3. Missing required skills penalty
        if requirements.required:
            candidate_skills = {s.name.lower() for s in candidate.skills}
            reqs = [r.name.lower() for r in requirements.required]
            missing_count = sum(1 for r in reqs if r not in candidate_skills)
            if len(reqs) > 0:
                missing_ratio = missing_count / len(reqs)
                # Max 0.2 penalty if missing most mandatory skills
                penalty += missing_ratio * 0.2

        # 4. Job hopping penalty
        avg_tenure = features.career_summary.average_tenure_months
        if avg_tenure > 0 and avg_tenure < 12.0:
            penalty += 0.1

        # 5. Keyword stuffing penalty: >30 skills but very low average endorsements
        if len(candidate.skills) > 30:
            avg_endorsements = sum(s.endorsements for s in candidate.skills) / len(candidate.skills)
            if avg_endorsements < 2.0:
                penalty += 0.15

        # 6. Inactive user penalty (based on signup vs last active date if available)
        # Let's check candidate.signals.last_active_date or similar
        # If last active date is very old, we can add a small penalty (e.g. 0.05)

        return round(min(max(penalty, 0.0), 1.0), 3)
