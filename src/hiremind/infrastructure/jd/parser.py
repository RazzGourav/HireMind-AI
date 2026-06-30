"""Rule-based JD Requirement Parser.

Extracts structured requirements from cleaned JD text using pattern matching
and keyword detection. Deterministic — no LLM dependency.
"""

import re
import uuid
from collections.abc import Sequence

from hiremind.domain.requirement import (
    ExperienceRequirement,
    NegativeRequirement,
    ParsedRequirements,
    Requirement,
)
from hiremind.domain.requirement_type import RequirementType


def _uid() -> str:
    """Generate a short unique ID for a requirement."""
    return f"REQ_{uuid.uuid4().hex[:8].upper()}"


# ──────────────────────────────────────────────────────────────────────────────
# Section header patterns (case-insensitive).
# ──────────────────────────────────────────────────────────────────────────────
_REQUIRED_HEADERS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"must[\s-]*have",
        r"required\s+skills?",
        r"key\s+requirements?",
        r"what\s+you(?:'ll)?\s+(?:need|bring)",
        r"mandatory",
        r"essential\s+(?:skills?|qualifications?|requirements?)",
        r"responsibilities\s+and\s+requirements",
        r"core\s+(?:skills?|competenc)",
        r"minimum\s+qualifications?",
        r"what\s+we(?:'re)?\s+looking\s+for",
    )
)

_PREFERRED_HEADERS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"nice[\s-]*to[\s-]*have",
        r"good[\s-]*to[\s-]*have",
        r"preferred\s+(?:skills?|qualifications?)",
        r"bonus\s+(?:skills?|points?)",
        r"additional\s+(?:skills?|qualifications?)",
        r"desirable",
        r"plus\s+(?:if|points?)",
    )
)

_NEGATIVE_HEADERS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"not\s+(?:looking|interested)\s+(?:for|in)",
        r"we\s+don(?:'t|t)\s+(?:need|want)",
        r"avoid",
        r"reject",
        r"disqualif",
        r"red\s+flags?",
        r"deal\s+breakers?",
    )
)

# ──────────────────────────────────────────────────────────────────────────────
# Experience patterns.
# ──────────────────────────────────────────────────────────────────────────────
_EXPERIENCE_RANGE = re.compile(
    r"(\d+)\s*[-–—to]+\s*(\d+)\s*(?:\+)?\s*years?",
    re.IGNORECASE,
)
_EXPERIENCE_MIN = re.compile(
    r"(?:minimum|min|at\s+least)\s*(?:of\s+)?(\d+)\s*(?:\+)?\s*years?",
    re.IGNORECASE,
)
_EXPERIENCE_MAX = re.compile(
    r"(?:maximum|max|up\s+to)\s*(\d+)\s*(?:\+)?\s*years?",
    re.IGNORECASE,
)
_EXPERIENCE_BARE = re.compile(
    r"(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:experience|exp)",
    re.IGNORECASE,
)

# ──────────────────────────────────────────────────────────────────────────────
# Inline negative signal patterns.
# ──────────────────────────────────────────────────────────────────────────────
_INLINE_NEGATIVE = re.compile(
    r"(?:not|no|don'?t|avoid|reject)\s+(?:just|only|purely?)?\s*" r"([A-Za-z][A-Za-z /\-]+)",
    re.IGNORECASE,
)


class JDParser:
    """Parse cleaned JD text into structured ``ParsedRequirements``.

    The parser is deterministic, uses no external models, and works by:
        1. Splitting text into sections via header detection.
        2. Extracting bullet-point items from each section.
        3. Classifying items by section type.
        4. Extracting experience requirements via regex.
        5. Detecting inline negative signals.
    """

    def __init__(
        self,
        known_skills: Sequence[str] = (),
        skill_aliases: dict[str, list[str]] | None = None,
    ) -> None:
        self._known_skills = set(known_skills)
        self._skill_aliases = skill_aliases or {}

    def parse(self, cleaned_text: str) -> ParsedRequirements:
        """Extract all requirements from the cleaned JD text."""
        sections = self._split_sections(cleaned_text)
        required = self._extract_from_sections(sections.get("required", []), is_required=True)
        preferred = self._extract_from_sections(sections.get("preferred", []), is_required=False)
        negative = self._extract_negatives(sections.get("negative", []), cleaned_text)
        experience = self._extract_experience(cleaned_text)

        return ParsedRequirements(
            required=tuple(required),
            preferred=tuple(preferred),
            negative=tuple(negative),
            experience=experience,
        )

    def _split_sections(self, text: str) -> dict[str, list[str]]:
        """Split text into classified sections based on header patterns."""
        lines = text.split("\n")
        sections: dict[str, list[str]] = {"required": [], "preferred": [], "negative": []}
        current_section = "required"  # Default to required if no header found.

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check if this line is a section header.
            new_section = self._classify_header(stripped)
            if new_section is not None:
                current_section = new_section
                continue

            # Strip leading bullet/dash/number markers.
            item = re.sub(r"^(?:\d+[.)]\s*|[-*]\s*)", "", stripped).strip()
            if item:
                sections[current_section].append(item)

        return sections

    @staticmethod
    def _classify_header(line: str) -> str | None:
        """Classify a line as a section header, or None if it isn't."""
        for pattern in _NEGATIVE_HEADERS:
            if pattern.search(line):
                return "negative"
        for pattern in _PREFERRED_HEADERS:
            if pattern.search(line):
                return "preferred"
        for pattern in _REQUIRED_HEADERS:
            if pattern.search(line):
                return "required"
        return None

    def _extract_from_sections(self, items: list[str], *, is_required: bool) -> list[Requirement]:
        """Convert raw text items into Requirement objects."""
        requirements: list[Requirement] = []
        seen_names: set[str] = set()

        for item in items:
            name = self._normalise_item(item)
            if not name or name in seen_names:
                continue
            seen_names.add(name)

            aliases = tuple(self._skill_aliases.get(name, []))
            category = RequirementType.REQUIRED if is_required else RequirementType.PREFERRED

            requirements.append(
                Requirement(
                    id=_uid(),
                    name=name,
                    category=category,
                    weight=1.0 if is_required else 0.5,
                    required=is_required,
                    aliases=aliases,
                    evidence=item,
                )
            )

        return requirements

    def _extract_negatives(
        self, section_items: list[str], full_text: str
    ) -> list[NegativeRequirement]:
        """Extract negative requirements from both section items and inline patterns."""
        negatives: list[NegativeRequirement] = []
        seen: set[str] = set()

        # From explicit negative section.
        for item in section_items:
            name = self._normalise_item(item)
            if name and name not in seen:
                seen.add(name)
                negatives.append(
                    NegativeRequirement(
                        id=_uid(),
                        name=name,
                        reason="Explicitly listed in negative section",
                        evidence=item,
                    )
                )

        # From inline negative patterns in the full text.
        for match in _INLINE_NEGATIVE.finditer(full_text):
            name = self._normalise_item(match.group(1))
            if name and name not in seen:
                seen.add(name)
                negatives.append(
                    NegativeRequirement(
                        id=_uid(),
                        name=name,
                        reason="Inline negative signal",
                        evidence=match.group(0).strip(),
                    )
                )

        return negatives

    @staticmethod
    def _extract_experience(text: str) -> ExperienceRequirement:
        """Extract experience requirements from the full text."""
        min_years: int | None = None
        max_years: int | None = None
        preferred_years: int | None = None

        # Try range pattern first (e.g. "5-9 years").
        range_match = _EXPERIENCE_RANGE.search(text)
        if range_match:
            min_years = int(range_match.group(1))
            max_years = int(range_match.group(2))
            preferred_years = min_years

        # Explicit minimum.
        min_match = _EXPERIENCE_MIN.search(text)
        if min_match:
            min_years = int(min_match.group(1))

        # Explicit maximum.
        max_match = _EXPERIENCE_MAX.search(text)
        if max_match:
            max_years = int(max_match.group(1))

        # Bare "X+ years of experience".
        if min_years is None:
            bare_match = _EXPERIENCE_BARE.search(text)
            if bare_match:
                min_years = int(bare_match.group(1))

        return ExperienceRequirement(
            min_years=min_years,
            max_years=max_years,
            preferred_years=preferred_years,
        )

    @staticmethod
    def _normalise_item(item: str) -> str:
        """Normalise a raw extracted item into a clean skill/requirement name."""
        # Remove trailing punctuation and extra whitespace.
        item = re.sub(r"[.,:;!?]+$", "", item).strip()
        # Collapse whitespace.
        item = re.sub(r"\s+", " ", item)
        # Skip items that are too long to be a single skill (likely a sentence).
        if len(item) > 80:
            return ""
        return item
