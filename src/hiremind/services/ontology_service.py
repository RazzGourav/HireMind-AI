"""Ontology Service — skill normalisation and semantic traversal wrapper.

Delegates internally to the new hiremind.knowledge package for backward compatibility.
"""


from hiremind.domain.ontology_models import SkillNode
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.knowledge.normalization import SkillNormalizer
from hiremind.knowledge.ontology import SkillOntology


class OntologyService:
    """Normalise skills and traverse the ontology graph.

    Wraps the new SkillOntology and SkillNormalizer for backward compatibility.
    """

    def __init__(self, loader: OntologyLoader | SkillOntology) -> None:
        if isinstance(loader, SkillOntology):
            self._ontology = loader
        else:
            # Build SkillOntology from the legacy OntologyLoader
            skills = []
            for skill_name in loader.all_canonical_names():
                data = loader.skill_data(skill_name) or {}
                skills.append(
                    SkillNode(
                        canonical_name=skill_name,
                        aliases=tuple(data.get("aliases", [])),
                        parents=tuple(data.get("parents", [])),
                        category=data.get("category", ""),
                    )
                )
            self._ontology = SkillOntology(
                skills=skills,
                protected_terms=loader.protected_terms,
            )

        self._normalizer = SkillNormalizer(self._ontology)
        self._all_canonical = self._ontology.all_canonical_names()

    def normalize_skill(self, raw_skill: str) -> str:
        """Resolve a raw skill string to its canonical name.

        Uses exact and fuzzy skill name resolution from the new normalizer.
        """
        return self._normalizer.normalize(raw_skill)

    def get_ancestors(self, skill: str) -> list[str]:
        """Return all ancestor categories for a skill (parents, grandparents, etc.)."""
        canonical = self._ontology.canonical_name(skill) or skill
        visited: set[str] = set()
        result: list[str] = []
        self._collect_ancestors(canonical, visited, result)
        return result

    def _collect_ancestors(self, skill: str, visited: set[str], result: list[str]) -> None:
        """Recursively collect ancestors."""
        parents = self._ontology.get_parents(skill)
        for parent in parents:
            if parent not in visited:
                visited.add(parent)
                result.append(parent)
                self._collect_ancestors(parent, visited, result)

    def get_related(self, skill: str) -> list[str]:
        """Return skills that share at least one parent with the given skill."""
        canonical = self._ontology.canonical_name(skill) or skill
        parents = set(self._ontology.get_parents(canonical))
        if not parents:
            return []

        related: set[str] = set()
        for other_skill in self._all_canonical:
            if other_skill == canonical:
                continue
            other_parents = set(self._ontology.get_parents(other_skill))
            if parents & other_parents:
                related.add(other_skill)

        return sorted(related)

    def get_aliases(self, skill: str) -> list[str]:
        """Return all known aliases for a skill."""
        return self._ontology.get_aliases(skill)
