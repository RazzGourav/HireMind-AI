"""Feature Vector Builder — flattens all scores into a single dict for Parquet."""

from hiremind.domain.career_summary import CareerSummary
from hiremind.domain.ontology_models import GraphFeatures
from hiremind.domain.skill_summary import SkillSummary


def build_feature_vector(
    candidate_id: str,
    technical_score: float,
    career_score: float,
    leadership_score: float,
    production_score: float,
    growth_score: float,
    consistency_score: float,
    education_score: float,
    career_summary: CareerSummary,
    skill_summary: SkillSummary,
    graph_features: GraphFeatures | None = None,
) -> dict[str, float]:
    """Build a flat feature vector dict suitable for Parquet storage.

    All values are numeric (float or int cast to float).
    """
    g_feat = graph_features or GraphFeatures()
    return {
        # Scores.
        "technical_score": technical_score,
        "career_score": career_score,
        "leadership_score": leadership_score,
        "production_score": production_score,
        "growth_score": growth_score,
        "consistency_score": consistency_score,
        "education_score": education_score,
        # Career summary.
        "total_experience_months": float(career_summary.total_experience_months),
        "current_tenure_months": float(career_summary.current_tenure_months),
        "average_tenure_months": career_summary.average_tenure_months,
        "promotion_count": float(career_summary.promotion_count),
        "industry_changes": float(career_summary.industry_changes),
        "role_changes": float(career_summary.role_changes),
        "company_count": float(career_summary.company_count),
        "career_stability": career_summary.career_stability,
        "startup_experience_months": float(career_summary.startup_experience_months),
        "enterprise_experience_months": float(career_summary.enterprise_experience_months),
        "has_current_role": 1.0 if career_summary.has_current_role else 0.0,
        # Skill summary.
        "total_skills": float(skill_summary.total_skills),
        "ai_ml_skill_count": float(skill_summary.ai_ml_skill_count),
        "programming_skill_count": float(skill_summary.programming_skill_count),
        "unique_categories": float(skill_summary.unique_categories),
        # Graph features.
        "technology_diversity": g_feat.technology_diversity,
        "ai_depth": g_feat.ai_depth,
        "backend_depth": g_feat.backend_depth,
        "cloud_depth": g_feat.cloud_depth,
        "retrieval_depth": g_feat.retrieval_depth,
        "domain_breadth": g_feat.domain_breadth,
        "graph_connectivity": g_feat.graph_connectivity,
    }
