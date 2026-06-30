"""Explanation Validator — validates consistency of generated explanations."""

from __future__ import annotations

from dataclasses import dataclass, field

from hiremind.domain.explanation import AlignmentStatus, CandidateExplanation


@dataclass(slots=True)
class ValidationResult:
    """Result of validating a CandidateExplanation."""

    valid: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "warnings": self.warnings,
            "errors": self.errors,
        }


class ExplanationValidator:
    """Validates that a CandidateExplanation is internally consistent."""

    def validate(self, explanation: CandidateExplanation) -> ValidationResult:
        """Run all validation checks on an explanation.

        Returns:
            ValidationResult with status, warnings, and errors.
        """
        result = ValidationResult()

        self._validate_attribution_sum(explanation, result)
        self._validate_matched_evidence(explanation, result)
        self._validate_no_duplicates(explanation, result)
        self._validate_recommendation_consistency(explanation, result)

        if result.errors:
            result.valid = False

        return result

    @staticmethod
    def _validate_attribution_sum(
        explanation: CandidateExplanation, result: ValidationResult
    ) -> None:
        """Check that positive attributions sum approximately to final score before calibration."""
        if not explanation.attributions:
            result.warnings.append("No score attributions found.")
            return

        positive_sum = sum(
            a.weighted_contribution for a in explanation.attributions if a.weight > 0
        )
        penalty = sum(
            abs(a.weighted_contribution) for a in explanation.attributions if a.weight < 0
        )
        reconstructed = max(0.0, positive_sum - penalty) * 100.0

        # Allow ±2.0 tolerance (due to calibration rounding)
        if abs(reconstructed - explanation.final_score) > 2.0:
            result.warnings.append(
                f"Attribution sum ({reconstructed:.2f}) differs from final score "
                f"({explanation.final_score:.2f}) by more than 2.0 points."
            )

    @staticmethod
    def _validate_matched_evidence(
        explanation: CandidateExplanation, result: ValidationResult
    ) -> None:
        """Check that every MATCHED requirement has a matched_skill and evidence."""
        for alignment in explanation.requirement_alignments:
            if alignment.status == AlignmentStatus.MATCHED:
                if not alignment.matched_skill:
                    result.errors.append(
                        f"Requirement '{alignment.requirement_name}' is MATCHED but has no matched_skill."
                    )
                if not alignment.evidence:
                    result.warnings.append(
                        f"Requirement '{alignment.requirement_name}' is MATCHED but has no evidence string."
                    )

    @staticmethod
    def _validate_no_duplicates(
        explanation: CandidateExplanation, result: ValidationResult
    ) -> None:
        """Check for duplicate strength or concern labels."""
        strength_labels = [s.label for s in explanation.strengths]
        if len(strength_labels) != len(set(strength_labels)):
            result.warnings.append("Duplicate strength labels detected.")

        concern_labels = [c.label for c in explanation.concerns]
        if len(concern_labels) != len(set(concern_labels)):
            result.warnings.append("Duplicate concern labels detected.")

    @staticmethod
    def _validate_recommendation_consistency(
        explanation: CandidateExplanation, result: ValidationResult
    ) -> None:
        """Check that recommendation is broadly consistent with the score."""
        score = explanation.final_score
        rec = explanation.recommendation

        # Flag obviously inconsistent combinations
        if score >= 85 and rec == "Reject":
            result.errors.append(
                f"Score is {score:.1f} but recommendation is 'Reject'. This is inconsistent."
            )
        if score < 30 and rec == "Strong Hire":
            result.errors.append(
                f"Score is {score:.1f} but recommendation is 'Strong Hire'. This is inconsistent."
            )
