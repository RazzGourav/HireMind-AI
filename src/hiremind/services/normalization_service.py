"""Normalisation Service — wraps title and skill normalisation."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.skill import Skill
from hiremind.infrastructure.candidate.normalizer import normalize_title
from hiremind.infrastructure.candidate.skill_mapper import map_skills
from hiremind.services.ontology_service import OntologyService


class NormalizationService:
    """Normalise candidate titles and skills using ontology + static lookups."""

    def __init__(self, ontology_service: OntologyService) -> None:
        self._ontology = ontology_service

    def normalize_candidate_title(self, candidate: Candidate) -> str:
        """Normalise the candidate's current title."""
        return normalize_title(candidate.profile.current_title)

    def normalize_candidate_skills(self, candidate: Candidate) -> list[str]:
        """Normalise all candidate skills via the ontology."""
        return map_skills(candidate.skills, self._ontology)

    def normalize_skill(self, skill: Skill) -> str:
        """Normalise a single skill name."""
        return self._ontology.normalize_skill(skill.name)
