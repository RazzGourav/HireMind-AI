"""Skill Ontology — unified skill taxonomy and metadata representation."""

from collections.abc import Iterable
from typing import Any

from hiremind.domain.ontology_models import SkillNode
from hiremind.knowledge.synonym_engine import SynonymEngine


class SkillOntology:
    """Represents the global ontology of skills, categories, and categories relationships.

    Backward compatible with the original OntologyLoader, but enhanced.
    """

    def __init__(
        self,
        skills: Iterable[SkillNode],
        protected_terms: frozenset[str] = frozenset(),
        synonym_engine: SynonymEngine | None = None,
    ) -> None:
        self._skills: dict[str, SkillNode] = {}
        self._alias_map: dict[str, str] = {}
        self._protected_terms = protected_terms
        self.synonym_engine = synonym_engine

        for skill in skills:
            canonical = skill.canonical_name
            self._skills[canonical] = skill

            # Register canonical name (lowercased) to itself
            self._alias_map[canonical.lower()] = canonical

            # Register each alias
            for alias in skill.aliases:
                if alias:
                    self._alias_map[alias.lower()] = canonical

    @property
    def protected_terms(self) -> frozenset[str]:
        """Terms whose casing must be preserved during text cleaning."""
        return self._protected_terms

    def canonical_name(self, raw_skill: str) -> str | None:
        """Resolve a raw skill string to its canonical name.

        Returns None if no match is found. Synonym resolution is attempted first.
        """
        if not raw_skill:
            return None

        # Try synonym resolution first
        resolved = raw_skill
        if self.synonym_engine:
            resolved = self.synonym_engine.resolve(raw_skill)

        # Lookup alias map
        canonical = self._alias_map.get(resolved.lower())
        if canonical:
            return canonical

        # Fallback to direct alias map lookup of raw skill if synonym resolution didn't map
        return self._alias_map.get(raw_skill.lower())

    def get_parents(self, skill_name: str) -> list[str]:
        """Return the parent categories for a canonical skill name."""
        canonical = self.canonical_name(skill_name) or skill_name
        skill = self._skills.get(canonical)
        if skill:
            return list(skill.parents)
        return []

    def get_aliases(self, skill_name: str) -> list[str]:
        """Return aliases for a canonical skill name."""
        canonical = self.canonical_name(skill_name) or skill_name
        skill = self._skills.get(canonical)
        if skill:
            return list(skill.aliases)
        return []

    def all_canonical_names(self) -> list[str]:
        """Return all canonical skill names in the ontology."""
        return list(self._skills.keys())

    def all_alias_entries(self) -> dict[str, str]:
        """Return the full alias -> canonical mapping."""
        return dict(self._alias_map)

    def skill_data(self, skill_name: str) -> dict[str, Any] | None:
        """Return backward-compatible skill data dict for a canonical skill name."""
        canonical = self.canonical_name(skill_name) or skill_name
        skill = self._skills.get(canonical)
        if skill:
            return {
                "aliases": list(skill.aliases),
                "parents": list(skill.parents),
                "category": skill.category,
            }
        return None

    def get_skill(self, skill_name: str) -> SkillNode | None:
        """Get the original SkillNode object."""
        canonical = self.canonical_name(skill_name) or skill_name
        return self._skills.get(canonical)
