"""Synonym Engine — Resolves equivalent terms to a canonical representation."""

from collections.abc import Iterable

from hiremind.domain.ontology_models import SynonymGroup


class SynonymEngine:
    """Engine to resolve and check synonyms based on synonym groups."""

    def __init__(self, synonym_groups: Iterable[SynonymGroup]) -> None:
        self._term_to_canonical: dict[str, str] = {}
        self._canonical_to_group: dict[str, set[str]] = {}

        for group in synonym_groups:
            canonical = group.canonical
            group_terms = set(group.terms)
            # Register in lowercase for case-insensitive matching
            canonical_lower = canonical.lower()
            self._canonical_to_group[canonical_lower] = {t.lower() for t in group_terms}

            for term in group.terms:
                term_lower = term.lower()
                self._term_to_canonical[term_lower] = canonical

    def resolve(self, term: str) -> str:
        """Resolve a term to its canonical synonym representation, or return original term."""
        if not term:
            return ""
        term_lower = term.strip().lower()
        return self._term_to_canonical.get(term_lower, term)

    def are_synonyms(self, a: str, b: str) -> bool:
        """Check if two terms are synonyms of each other."""
        if not a or not b:
            return False
        a_lower = a.strip().lower()
        b_lower = b.strip().lower()
        if a_lower == b_lower:
            return True
        canonical_a = self._term_to_canonical.get(a_lower)
        canonical_b = self._term_to_canonical.get(b_lower)
        if canonical_a and canonical_b:
            return canonical_a.lower() == canonical_b.lower()
        return False

    def all_synonyms(self, term: str) -> set[str]:
        """Return all known synonyms of a term, including the term itself."""
        if not term:
            return set()
        term_lower = term.strip().lower()
        canonical = self._term_to_canonical.get(term_lower)
        if canonical:
            canonical_lower = canonical.lower()
            # Try to find original cased terms or canonical
            # Let's return the lowercased terms in the group
            return self._canonical_to_group.get(canonical_lower, {term_lower})
        return {term_lower}
