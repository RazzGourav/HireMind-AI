"""Skill Intelligence — per-skill analysis with category, evidence, and confidence."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.skill import Skill
from hiremind.domain.skill_summary import SkillIntelligence, SkillSummary
from hiremind.services.ontology_service import OntologyService

_AI_ML_CATEGORIES = frozenset(
    {
        "ml",
        "ai",
        "deep_learning",
        "nlp",
        "transformers",
        "embeddings",
        "retrieval",
        "fine_tuning",
        "llm",
        "ranking",
        "vector_database",
        "ann_search",
        "evaluation",
        "recommendation_systems",
        "computer_vision",
    }
)

_PROGRAMMING_CATEGORIES = frozenset(
    {
        "programming",
        "programming_languages",
    }
)


def analyze_skills(
    candidate: Candidate,
    ontology_service: OntologyService,
) -> SkillSummary:
    """Produce a SkillSummary with per-skill intelligence breakdown."""
    skill_intels: list[SkillIntelligence] = []
    normalized_names: list[str] = []
    seen: set[str] = set()
    ai_ml_count = 0
    programming_count = 0
    categories: set[str] = set()

    # Collect all career description text for evidence counting.
    career_text = " ".join((job.description or "") for job in candidate.career_history).lower()

    for skill in candidate.skills:
        canonical = ontology_service.normalize_skill(skill.name)
        if canonical in seen:
            continue
        seen.add(canonical)

        parents = tuple(ontology_service.get_ancestors(canonical))
        parent_set = set(parents)

        # Classify.
        if parent_set & _AI_ML_CATEGORIES:
            ai_ml_count += 1
        if parent_set & _PROGRAMMING_CATEGORIES:
            programming_count += 1
        categories.update(parents)

        # Evidence: count career description mentions.
        evidence_count = _count_evidence(canonical, skill, career_text)

        # Confidence heuristic.
        confidence = _compute_confidence(skill, evidence_count)

        # Determine primary category.
        primary_category = parents[0] if parents else ""

        skill_intels.append(
            SkillIntelligence(
                canonical_name=canonical,
                raw_name=skill.name,
                category=primary_category,
                proficiency=skill.proficiency,
                duration_months=skill.duration_months or 0,
                endorsements=skill.endorsements,
                evidence_sources=evidence_count,
                confidence=round(confidence, 3),
                parents=parents,
            )
        )
        normalized_names.append(canonical)

    return SkillSummary(
        skills=skill_intels,
        normalized_names=normalized_names,
        total_skills=len(skill_intels),
        ai_ml_skill_count=ai_ml_count,
        programming_skill_count=programming_count,
        unique_categories=len(categories),
    )


def _count_evidence(canonical: str, skill: Skill, career_text: str) -> int:
    """Count how many evidence sources mention this skill."""
    count = 0
    # Listed as a skill = 1 source.
    count += 1
    # Mentioned in career descriptions.
    if canonical.lower() in career_text or skill.name.lower() in career_text:
        count += 1
    # Has endorsements.
    if skill.endorsements > 0:
        count += 1
    # Has duration.
    if skill.duration_months and skill.duration_months > 0:
        count += 1
    return count


def _compute_confidence(skill: Skill, evidence_count: int) -> float:
    """Compute confidence score (0.0–1.0) based on available evidence."""
    score = 0.0
    # Base: skill is listed.
    score += 0.2
    # Duration contributes up to 0.3.
    if skill.duration_months and skill.duration_months > 0:
        score += min(skill.duration_months / 60.0, 1.0) * 0.3
    # Endorsements contribute up to 0.2.
    if skill.endorsements > 0:
        score += min(skill.endorsements / 10.0, 1.0) * 0.2
    # Evidence count contributes up to 0.2.
    score += min(evidence_count / 4.0, 1.0) * 0.2
    # Proficiency label.
    if skill.proficiency:
        prof_lower = skill.proficiency.lower()
        if prof_lower in ("advanced", "expert"):
            score += 0.1
        elif prof_lower == "intermediate":
            score += 0.05
    return min(score, 1.0)
