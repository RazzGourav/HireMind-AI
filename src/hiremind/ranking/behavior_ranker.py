"""Behavioral Ranker — evaluates Redrob behavioral signals and profile completeness."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures


class BehaviorRanker:
    """Computes behavioral score based on response scores, open to work flags, and github scores."""

    def score(self, candidate: Candidate, features: CandidateFeatures) -> float:
        """Score candidate's behavioral activity and signals (0.0 to 1.0)."""
        signals = candidate.signals

        # 1. Github activity score (normalize 0-10+ range to 0.0-1.0)
        git_score = min((signals.github_activity_score or 0.0) / 10.0, 1.0)
        # If they don't have github score but have a github profile, give small baseline
        if git_score <= 0.0 and getattr(signals, "has_github", False):
            git_score = 0.3

        # 2. Recruiter response score
        resp_score = signals.recruiter_response_score or 0.0

        # 3. Open to work flag boost
        open_boost = 0.0
        if getattr(signals, "open_to_work", False) or getattr(
            candidate.profile, "open_to_work", False
        ):
            open_boost = 0.2

        # 4. Profile completeness score (estimate based on summary and skills populated)
        completeness = 0.5
        if candidate.profile.summary:
            completeness += 0.25
        if len(candidate.skills) > 5:
            completeness += 0.25

        # Blend: 40% recruiter response + 30% github + 30% profile completeness + open_boost
        raw = 0.4 * resp_score + 0.3 * git_score + 0.3 * completeness + open_boost
        return round(min(max(raw, 0.0), 1.0), 3)
