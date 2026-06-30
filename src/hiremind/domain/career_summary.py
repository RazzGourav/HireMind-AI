"""Career summary — structured intelligence from career timeline analysis."""

from dataclasses import dataclass


@dataclass(slots=True)
class CareerSummary:
    """Structured career intelligence extracted from a candidate's career history."""

    total_experience_months: int = 0
    current_tenure_months: int = 0
    average_tenure_months: float = 0.0
    promotion_count: int = 0
    industry_changes: int = 0
    role_changes: int = 0
    company_count: int = 0
    career_stability: float = 0.0
    startup_experience_months: int = 0
    enterprise_experience_months: int = 0
    has_current_role: bool = False
    industries: tuple[str, ...] = ()
    titles: tuple[str, ...] = ()
