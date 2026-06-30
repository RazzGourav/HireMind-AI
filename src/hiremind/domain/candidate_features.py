"""CandidateFeatures — the single intelligence profile object for ranking."""

from dataclasses import dataclass, field

from hiremind.domain.career_summary import CareerSummary
from hiremind.domain.skill_summary import SkillSummary


@dataclass(slots=True)
class CandidateFeatures:
    """Complete intelligence profile for a single candidate.

    This is the object that the ranking pipeline consumes.
    Every score is 0.0–1.0. The feature_vector is a flat dict
    suitable for direct conversion to a Parquet row.
    """

    candidate_id: str
    technical_score: float = 0.0
    career_score: float = 0.0
    leadership_score: float = 0.0
    production_score: float = 0.0
    growth_score: float = 0.0
    consistency_score: float = 0.0
    education_score: float = 0.0
    career_summary: CareerSummary = field(default_factory=CareerSummary)
    skill_summary: SkillSummary = field(default_factory=SkillSummary)
    normalized_skills: list[str] = field(default_factory=list)
    feature_vector: dict[str, float] = field(default_factory=dict)
