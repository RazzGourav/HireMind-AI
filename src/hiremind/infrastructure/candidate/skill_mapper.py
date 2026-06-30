"""Skill Ontology Mapper — normalises candidate skills via the ontology."""

from hiremind.domain.skill import Skill
from hiremind.services.ontology_service import OntologyService


def map_skills(
    skills: list[Skill],
    ontology_service: OntologyService,
) -> list[str]:
    """Normalise a list of candidate skills to canonical ontology names.

    Deduplicates results (e.g. FAISS + Facebook AI Similarity Search → one entry).

    Returns:
        Sorted list of unique canonical skill names.
    """
    seen: set[str] = set()
    result: list[str] = []

    for skill in skills:
        canonical = ontology_service.normalize_skill(skill.name)
        if canonical not in seen:
            seen.add(canonical)
            result.append(canonical)

    return sorted(result)
