"""Skill Normalization Engine — resolves raw skill strings to canonical names."""

from hiremind.knowledge.ontology import SkillOntology


class SkillNormalizer:
    """Fuzzy and exact normalization of skills using the ontology and synonym engine."""

    def __init__(self, ontology: SkillOntology) -> None:
        self._ontology = ontology

    def normalize(self, raw_skill: str) -> str:
        """Resolve a raw skill string to its canonical name.

        Uses synonym resolution, exact mapping, then falls back to fuzzy matching (rapidfuzz).
        """
        if not raw_skill:
            return ""

        # 1. Try exact mapping (internally tries synonym resolution first)
        canonical = self._ontology.canonical_name(raw_skill)
        if canonical is not None:
            return canonical

        # 2. Try synonym resolution to see if it resolves to a known term
        resolved = raw_skill
        if self._ontology.synonym_engine:
            resolved = self._ontology.synonym_engine.resolve(raw_skill)
            canonical = self._ontology.canonical_name(resolved)
            if canonical is not None:
                return canonical

        # 3. Fuzzy matching fallback against alias map
        alias_map = self._ontology.all_alias_entries()
        try:
            from rapidfuzz import fuzz

            best_score = 0.0
            best_match = resolved
            lowered = resolved.lower()

            for alias, canonical_name in alias_map.items():
                score = fuzz.ratio(lowered, alias)
                if score > best_score:
                    best_score = score
                    best_match = canonical_name

            if best_score >= 80.0:
                return best_match
        except ImportError:
            pass

        return raw_skill
