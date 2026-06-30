from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Skill:
    name: str
    proficiency: str | None = None
    endorsements: int = 0
    duration_months: int | None = None
