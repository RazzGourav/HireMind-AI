"""Career Timeline Intelligence — extracts structured career metrics."""

from hiremind.domain.career import Career
from hiremind.domain.career_summary import CareerSummary
from hiremind.infrastructure.candidate.normalizer import normalize_title

# Company-size thresholds for startup vs enterprise classification.
_STARTUP_SIZES = frozenset({"1-10", "11-50", "1-50", "51-200"})
_ENTERPRISE_SIZES = frozenset({"501-1000", "1001-5000", "5001-10000", "10001+"})


def analyze_career(career_history: list[Career]) -> CareerSummary:
    """Analyse a candidate's career history and produce a CareerSummary.

    Calculates tenure metrics, promotion detection, industry diversity,
    and startup vs enterprise experience.
    """
    if not career_history:
        return CareerSummary()

    tenures: list[int] = []
    industries: list[str] = []
    titles: list[str] = []
    normalized_titles: list[str] = []
    startup_months = 0
    enterprise_months = 0
    current_tenure = 0
    has_current = False
    total_months = 0

    for job in career_history:
        months = job.duration_months or 0
        total_months += months
        tenures.append(months)

        if job.is_current:
            current_tenure = months
            has_current = True

        if job.title:
            titles.append(job.title)
            normalized_titles.append(normalize_title(job.title))

        if job.industry:
            industries.append(job.industry.lower().strip())

        size = (job.company_size or "").strip()
        if size in _STARTUP_SIZES:
            startup_months += months
        elif size in _ENTERPRISE_SIZES:
            enterprise_months += months

    # Dedup for counting changes.
    unique_industries = list(dict.fromkeys(industries))

    # Industry changes = transitions between distinct industries.
    industry_changes = _count_transitions(industries)

    # Role changes = transitions between distinct normalised titles.
    role_changes = _count_transitions(normalized_titles)

    # Promotion count: heuristic — role change where seniority increased.
    promotion_count = _detect_promotions(titles)

    # Career stability: weighted combination of tenure consistency.
    avg_tenure = sum(tenures) / len(tenures) if tenures else 0.0
    stability = _compute_stability(tenures, avg_tenure)

    return CareerSummary(
        total_experience_months=total_months,
        current_tenure_months=current_tenure,
        average_tenure_months=round(avg_tenure, 1),
        promotion_count=promotion_count,
        industry_changes=industry_changes,
        role_changes=role_changes,
        company_count=len(career_history),
        career_stability=round(stability, 3),
        startup_experience_months=startup_months,
        enterprise_experience_months=enterprise_months,
        has_current_role=has_current,
        industries=tuple(unique_industries),
        titles=tuple(titles),
    )


def _count_transitions(items: list[str]) -> int:
    """Count the number of transitions (changes) in a sequence."""
    if len(items) <= 1:
        return 0
    return sum(1 for a, b in zip(items, items[1:]) if a != b)


def _detect_promotions(titles: list[str]) -> int:
    """Heuristic promotion detection based on seniority keywords."""
    seniority_levels = {
        "intern": 0,
        "junior": 1,
        "associate": 1,
        "engineer": 2,
        "developer": 2,
        "analyst": 2,
        "senior": 3,
        "sr": 3,
        "sr.": 3,
        "staff": 4,
        "principal": 5,
        "lead": 4,
        "tech lead": 4,
        "team lead": 4,
        "manager": 5,
        "director": 6,
        "vp": 7,
        "head": 6,
    }
    promotions = 0
    prev_level = -1

    for title in reversed(titles):  # Oldest → newest.
        lowered = title.lower()
        level = 2  # Default mid-level.
        for keyword, lvl in seniority_levels.items():
            if keyword in lowered:
                level = max(level, lvl)
        if prev_level >= 0 and level > prev_level:
            promotions += 1
        prev_level = level

    return promotions


def _compute_stability(tenures: list[int], avg_tenure: float) -> float:
    """Compute career stability score (0.0–1.0).

    Higher stability = longer average tenure + lower variance.
    """
    if not tenures or avg_tenure == 0:
        return 0.0

    # Coefficient of variation (lower = more stable).
    variance = sum((t - avg_tenure) ** 2 for t in tenures) / len(tenures)
    std_dev = variance**0.5
    cv = std_dev / avg_tenure if avg_tenure > 0 else 1.0

    # Tenure bonus: longer avg tenure → higher stability.
    # 24 months = baseline, 48+ months = high stability.
    tenure_score = min(avg_tenure / 48.0, 1.0)

    # Stability = blend of low-CV and high-tenure.
    cv_score = max(0.0, 1.0 - cv)
    return 0.6 * tenure_score + 0.4 * cv_score
