"""Immutable domain models for parsed Job Description requirements."""

from dataclasses import dataclass, field

from hiremind.domain.requirement_type import RequirementType


@dataclass(frozen=True, slots=True)
class Requirement:
    """A single extracted requirement from a Job Description.

    Every skill, tool, or competency mentioned in the JD becomes a Requirement
    with a weight, category, and optional aliases for fuzzy matching.
    """

    id: str
    name: str
    category: RequirementType
    weight: float = 1.0
    required: bool = True
    aliases: tuple[str, ...] = ()
    evidence: str = ""


@dataclass(frozen=True, slots=True)
class ExperienceRequirement:
    """Experience range extracted from a Job Description."""

    min_years: int | None = None
    max_years: int | None = None
    preferred_years: int | None = None


@dataclass(frozen=True, slots=True)
class NegativeRequirement:
    """A negative signal — candidates matching this should be penalised."""

    id: str
    name: str
    reason: str = ""
    evidence: str = ""


@dataclass(frozen=True, slots=True)
class ParsedRequirements:
    """Aggregate container for all requirements extracted from a JD."""

    required: tuple[Requirement, ...] = ()
    preferred: tuple[Requirement, ...] = ()
    negative: tuple[NegativeRequirement, ...] = ()
    experience: ExperienceRequirement = field(default_factory=ExperienceRequirement)

    @property
    def all_positive(self) -> tuple[Requirement, ...]:
        """All non-negative requirements (required + preferred)."""
        return self.required + self.preferred

    @property
    def required_names(self) -> list[str]:
        return [r.name for r in self.required]

    @property
    def preferred_names(self) -> list[str]:
        return [r.name for r in self.preferred]

    @property
    def negative_names(self) -> list[str]:
        return [n.name for n in self.negative]

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON export."""
        return {
            "required": [
                {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category.value,
                    "weight": r.weight,
                    "required": r.required,
                    "aliases": list(r.aliases),
                    "evidence": r.evidence,
                }
                for r in self.required
            ],
            "preferred": [
                {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category.value,
                    "weight": r.weight,
                    "required": r.required,
                    "aliases": list(r.aliases),
                    "evidence": r.evidence,
                }
                for r in self.preferred
            ],
            "negative": [
                {
                    "id": n.id,
                    "name": n.name,
                    "reason": n.reason,
                    "evidence": n.evidence,
                }
                for n in self.negative
            ],
            "experience": {
                "min_years": self.experience.min_years,
                "max_years": self.experience.max_years,
                "preferred_years": self.experience.preferred_years,
            },
        }
