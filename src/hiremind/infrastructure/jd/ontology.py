"""Ontology Loader — reads the skill taxonomy from YAML config."""

from pathlib import Path
from typing import Any

from omegaconf import OmegaConf


class OntologyLoader:
    """Load and query the skill ontology from a YAML configuration file.

    The ontology defines:
        - Canonical skill names
        - Aliases for fuzzy matching
        - Parent categories for graph construction
        - Protected terms for the text cleaner
    """

    def __init__(self, ontology_path: str | Path = "configs/ontology.yaml") -> None:
        self._path = Path(ontology_path)
        self._raw: dict[str, Any] = {}
        self._skills: dict[str, dict[str, Any]] = {}
        self._alias_map: dict[str, str] = {}
        self._protected_terms: frozenset[str] = frozenset()
        self._loaded = False

    def load(self) -> "OntologyLoader":
        """Load the ontology YAML file and build internal indices."""
        if not self._path.exists():
            raise FileNotFoundError(f"Ontology file not found: {self._path}")

        cfg = OmegaConf.load(self._path)
        self._raw = OmegaConf.to_container(cfg, resolve=True)  # type: ignore[assignment]

        self._build_indices()
        self._loaded = True
        return self

    def _build_indices(self) -> None:
        """Build the skill lookup and alias map from raw config."""
        categories = self._raw.get("categories", {})

        for _category_name, skills in categories.items():
            if not isinstance(skills, dict):
                continue
            for skill_name, skill_data in skills.items():
                if not isinstance(skill_data, dict):
                    continue

                canonical = skill_name
                self._skills[canonical] = skill_data

                # Map canonical name (lowercased) to itself.
                self._alias_map[canonical.lower()] = canonical

                # Map each alias to the canonical name.
                for alias in skill_data.get("aliases", []):
                    if alias:
                        self._alias_map[alias.lower()] = canonical

        # Protected terms.
        protected = self._raw.get("protected_terms", [])
        self._protected_terms = frozenset(protected) if protected else frozenset()

    @property
    def protected_terms(self) -> frozenset[str]:
        """Terms whose casing must be preserved during text cleaning."""
        return self._protected_terms

    def canonical_name(self, raw_skill: str) -> str | None:
        """Resolve a raw skill string to its canonical name.

        Returns None if no match is found.
        """
        return self._alias_map.get(raw_skill.lower())

    def get_parents(self, skill_name: str) -> list[str]:
        """Return the parent categories for a canonical skill name."""
        canonical = self.canonical_name(skill_name) or skill_name
        skill_data = self._skills.get(canonical, {})
        return list(skill_data.get("parents", []))

    def get_aliases(self, skill_name: str) -> list[str]:
        """Return aliases for a canonical skill name."""
        canonical = self.canonical_name(skill_name) or skill_name
        skill_data = self._skills.get(canonical, {})
        return list(skill_data.get("aliases", []))

    def all_canonical_names(self) -> list[str]:
        """Return all canonical skill names in the ontology."""
        return list(self._skills.keys())

    def all_alias_entries(self) -> dict[str, str]:
        """Return the full alias→canonical mapping."""
        return dict(self._alias_map)

    def skill_data(self, skill_name: str) -> dict[str, Any] | None:
        """Return raw skill data dict for a canonical skill name."""
        canonical = self.canonical_name(skill_name) or skill_name
        return self._skills.get(canonical)
