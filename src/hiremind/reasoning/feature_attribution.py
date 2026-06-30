"""Feature Attribution Engine — decomposes final scores into weighted component contributions."""

from __future__ import annotations

from hiremind.domain.explanation import ScoreAttribution

# Human-readable labels for each scoring dimension.
_COMPONENT_LABELS: dict[str, str] = {
    "technical_score": "Technical Skill Alignment",
    "career_score": "Career Progression & Stability",
    "behavior_score": "Behavioral Signals & Engagement",
    "knowledge_score": "Knowledge Graph & Domain Depth",
    "growth_score": "Growth Trajectory",
    "leadership_score": "Leadership Indicators",
    "risk_penalty": "Risk Penalty",
}


class FeatureAttributionEngine:
    """Converts raw score components into structured ScoreAttribution objects."""

    def __init__(
        self,
        tech_weight: float = 0.40,
        career_weight: float = 0.20,
        behavior_weight: float = 0.15,
        knowledge_weight: float = 0.15,
        growth_weight: float = 0.05,
        leadership_weight: float = 0.05,
    ) -> None:
        self._weights: dict[str, float] = {
            "technical_score": tech_weight,
            "career_score": career_weight,
            "behavior_score": behavior_weight,
            "knowledge_score": knowledge_weight,
            "growth_score": growth_weight,
            "leadership_score": leadership_weight,
        }

    def attribute(self, components: dict[str, float], final_score: float) -> list[ScoreAttribution]:
        """Build a list of ScoreAttribution objects from raw score components.

        Args:
            components: Dict produced by ScoreFusionEngine.fuse() containing
                        raw (0-1) scores for each dimension plus risk_penalty.
            final_score: The calibrated final score (0-100).

        Returns:
            List of ScoreAttribution objects, one per component.
        """
        attributions: list[ScoreAttribution] = []
        total_positive = sum(
            self._weights.get(k, 0.0) * v for k, v in components.items() if k in self._weights
        )

        for component, weight in self._weights.items():
            raw = components.get(component, 0.0)
            weighted = weight * raw
            pct = (weighted / total_positive * 100.0) if total_positive > 0 else 0.0

            attributions.append(
                ScoreAttribution(
                    component=component,
                    label=_COMPONENT_LABELS.get(component, component),
                    raw_score=raw,
                    weight=weight,
                    weighted_contribution=weighted,
                    percentage_of_final=pct,
                )
            )

        # Risk penalty as a special negative attribution
        penalty = components.get("risk_penalty", 0.0)
        if penalty > 0:
            attributions.append(
                ScoreAttribution(
                    component="risk_penalty",
                    label=_COMPONENT_LABELS["risk_penalty"],
                    raw_score=penalty,
                    weight=-1.0,
                    weighted_contribution=-penalty,
                    percentage_of_final=0.0,
                )
            )

        return attributions
