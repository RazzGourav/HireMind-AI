"""Skill summary — structured intelligence from skill analysis."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class SkillIntelligence:
    """Per-skill intelligence breakdown."""

    canonical_name: str
    raw_name: str = ""
    category: str = ""
    proficiency: str | None = None
    duration_months: int = 0
    endorsements: int = 0
    evidence_sources: int = 0
    confidence: float = 0.0
    parents: tuple[str, ...] = ()


@dataclass(slots=True)
class SkillSummary:
    """Aggregated skill intelligence for a candidate."""

    skills: list[SkillIntelligence] = field(default_factory=list)
    normalized_names: list[str] = field(default_factory=list)
    total_skills: int = 0
    ai_ml_skill_count: int = 0
    programming_skill_count: int = 0
    unique_categories: int = 0

    @property
    def skill_names_set(self) -> frozenset[str]:
        return frozenset(self.normalized_names)
