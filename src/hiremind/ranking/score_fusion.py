"""Score Fusion — weights and fuses subscores into a single ranking score."""



class ScoreFusionEngine:
    """Fuses subscores into a single combined score and subtracts risk penalties."""

    def __init__(
        self,
        tech_weight: float = 0.40,
        career_weight: float = 0.20,
        behavior_weight: float = 0.15,
        knowledge_weight: float = 0.15,
        growth_weight: float = 0.05,
        leadership_weight: float = 0.05,
    ) -> None:
        self.tech_weight = tech_weight
        self.career_weight = career_weight
        self.behavior_weight = behavior_weight
        self.knowledge_weight = knowledge_weight
        self.growth_weight = growth_weight
        self.leadership_weight = leadership_weight

    def fuse(
        self,
        technical: float,
        career: float,
        behavior: float,
        knowledge: float,
        growth: float,
        leadership: float,
        risk_penalty: float,
    ) -> tuple[float, dict[str, float]]:
        """Combine all subscores and subtract the risk penalty."""
        fused = (
            self.tech_weight * technical
            + self.career_weight * career
            + self.behavior_weight * behavior
            + self.knowledge_weight * knowledge
            + self.growth_weight * growth
            + self.leadership_weight * leadership
        )

        final_score = max(0.0, fused - risk_penalty)

        components = {
            "technical_score": technical,
            "career_score": career,
            "behavior_score": behavior,
            "knowledge_score": knowledge,
            "growth_score": growth,
            "leadership_score": leadership,
            "risk_penalty": risk_penalty,
            "raw_fused_score": round(fused, 4),
        }

        return round(final_score, 4), components
