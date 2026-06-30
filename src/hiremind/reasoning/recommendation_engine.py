"""Recommendation Engine — maps scores and alignment to interview recommendations."""

from __future__ import annotations

from hiremind.domain.explanation import ConcernSeverity
from hiremind.domain.recommendation import InterviewRecommendation, RecommendationResult


class RecommendationEngine:
    """Generates interview recommendations based on score thresholds and requirement alignment."""

    def __init__(
        self,
        strong_hire_threshold: float = 85.0,
        hire_threshold: float = 70.0,
        interview_threshold: float = 50.0,
        alignment_cutoff: float = 0.8,
    ) -> None:
        self.strong_hire_threshold = strong_hire_threshold
        self.hire_threshold = hire_threshold
        self.interview_threshold = interview_threshold
        self.alignment_cutoff = alignment_cutoff

    def recommend(
        self,
        candidate_id: str,
        final_score: float,
        alignment_ratio: float,
        concerns: list | None = None,
    ) -> RecommendationResult:
        """Generate an interview recommendation for a candidate.

        Args:
            candidate_id: Candidate identifier.
            final_score: Calibrated final score (0-100).
            alignment_ratio: Fraction of requirements matched (0-1).
            concerns: List of Concern objects (for override logic).

        Returns:
            RecommendationResult with recommendation, confidence, and rationale.
        """
        concerns = concerns or []

        # Check for critical concern overrides
        high_concerns = [c for c in concerns if c.severity == ConcernSeverity.HIGH]
        has_critical_concerns = len(high_concerns) >= 2

        # Base recommendation from score + alignment matrix
        high_align = alignment_ratio >= self.alignment_cutoff

        if final_score >= self.strong_hire_threshold:
            rec = (
                InterviewRecommendation.STRONG_HIRE if high_align else InterviewRecommendation.HIRE
            )
        elif final_score >= self.hire_threshold:
            rec = InterviewRecommendation.HIRE if high_align else InterviewRecommendation.INTERVIEW
        elif final_score >= self.interview_threshold:
            rec = InterviewRecommendation.INTERVIEW if high_align else InterviewRecommendation.HOLD
        else:
            rec = InterviewRecommendation.HOLD if high_align else InterviewRecommendation.REJECT

        # Critical concern override: cap at HOLD
        if has_critical_concerns and rec in (
            InterviewRecommendation.STRONG_HIRE,
            InterviewRecommendation.HIRE,
            InterviewRecommendation.INTERVIEW,
        ):
            rec = InterviewRecommendation.HOLD

        # Confidence calculation
        confidence = self._compute_confidence(final_score, alignment_ratio, len(concerns))

        # Rationale
        rationale = self._build_rationale(rec, final_score, alignment_ratio, high_concerns)

        return RecommendationResult(
            candidate_id=candidate_id,
            recommendation=rec,
            confidence=confidence,
            rationale=rationale,
        )

    @staticmethod
    def _compute_confidence(score: float, alignment: float, concern_count: int) -> float:
        """Compute confidence in the recommendation (0-1).

        High score + high alignment + few concerns = high confidence.
        """
        score_conf = min(score / 100.0, 1.0)
        align_conf = alignment
        concern_penalty = min(concern_count * 0.1, 0.4)
        raw = 0.5 * score_conf + 0.35 * align_conf - concern_penalty + 0.15
        return round(min(max(raw, 0.0), 1.0), 2)

    @staticmethod
    def _build_rationale(
        rec: InterviewRecommendation,
        score: float,
        alignment: float,
        high_concerns: list,
    ) -> str:
        """Generate human-readable rationale for the recommendation."""
        parts: list[str] = []
        parts.append(f"Final score: {score:.1f}/100.")
        parts.append(f"Requirement alignment: {alignment:.0%}.")

        if rec == InterviewRecommendation.STRONG_HIRE:
            parts.append(
                "Exceptional match across all dimensions with strong requirement coverage."
            )
        elif rec == InterviewRecommendation.HIRE:
            parts.append("Strong candidate with good alignment to core requirements.")
        elif rec == InterviewRecommendation.INTERVIEW:
            parts.append("Promising profile warranting further evaluation through interview.")
        elif rec == InterviewRecommendation.HOLD:
            parts.append(
                "Profile shows potential but has gaps or concerns that need clarification."
            )
        else:
            parts.append("Significant misalignment with role requirements.")

        if high_concerns:
            concern_labels = ", ".join(c.label for c in high_concerns)
            parts.append(f"Critical concerns: {concern_labels}.")

        return " ".join(parts)
