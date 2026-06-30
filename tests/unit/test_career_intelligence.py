"""Tests for career timeline intelligence."""

from hiremind.domain.career import Career
from hiremind.infrastructure.candidate.timeline import analyze_career


def test_empty_career() -> None:
    """Empty career history returns default CareerSummary."""
    result = analyze_career([])
    assert result.total_experience_months == 0
    assert result.career_stability == 0.0
    assert result.company_count == 0


def test_single_job() -> None:
    """Single job produces expected metrics."""
    career = [
        Career(
            company="Acme",
            title="Software Engineer",
            duration_months=36,
            is_current=True,
            industry="IT Services",
            company_size="10001+",
        )
    ]
    result = analyze_career(career)
    assert result.total_experience_months == 36
    assert result.current_tenure_months == 36
    assert result.has_current_role is True
    assert result.company_count == 1
    assert result.enterprise_experience_months == 36
    assert result.industry_changes == 0


def test_multiple_jobs_industry_changes() -> None:
    """Multiple jobs with different industries count transitions."""
    career = [
        Career(company="A", title="Eng", duration_months=24, industry="Finance"),
        Career(company="B", title="Eng", duration_months=24, industry="Healthcare"),
        Career(company="C", title="Eng", duration_months=24, industry="Finance"),
    ]
    result = analyze_career(career)
    assert result.industry_changes == 2
    assert result.company_count == 3
    assert result.total_experience_months == 72


def test_promotion_detection() -> None:
    """Promotions are detected when seniority increases."""
    career = [
        Career(company="A", title="Senior Engineer", duration_months=24),
        Career(company="A", title="Junior Developer", duration_months=12),
    ]
    result = analyze_career(career)
    assert result.promotion_count >= 1


def test_startup_vs_enterprise() -> None:
    """Startup and enterprise months are classified by company size."""
    career = [
        Career(company="Startup", duration_months=18, company_size="1-50"),
        Career(company="BigCo", duration_months=30, company_size="10001+"),
    ]
    result = analyze_career(career)
    assert result.startup_experience_months == 18
    assert result.enterprise_experience_months == 30


def test_stability_high_for_consistent_tenure() -> None:
    """Career stability is higher for consistent tenures."""
    career = [
        Career(company="A", title="Eng", duration_months=36),
        Career(company="B", title="Eng", duration_months=36),
        Career(company="C", title="Eng", duration_months=36),
    ]
    result = analyze_career(career)
    assert result.career_stability > 0.3


def test_stability_lower_for_varied_tenure() -> None:
    """Career stability is lower for highly varied tenures."""
    career = [
        Career(company="A", title="Eng", duration_months=3),
        Career(company="B", title="Eng", duration_months=60),
        Career(company="C", title="Eng", duration_months=6),
    ]
    result = analyze_career(career)
    assert result.career_stability < 0.6
