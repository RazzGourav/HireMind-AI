from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Education:
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    tier: str | None = None
    graduation_year: int | None = None
