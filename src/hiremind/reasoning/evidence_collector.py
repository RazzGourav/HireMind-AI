"""Evidence Collector — gathers factual evidence from candidate data for explanations."""

from __future__ import annotations

from dataclasses import dataclass, field

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures


@dataclass(slots=True)
class CollectedEvidence:
    """Container for all evidence collected from a candidate."""

    skill_names: list[str] = field(default_factory=list)
    normalized_skills: list[str] = field(default_factory=list)
    career_titles: list[str] = field(default_factory=list)
    career_companies: list[str] = field(default_factory=list)
    career_industries: list[str] = field(default_factory=list)
    total_experience_months: int = 0
    average_tenure_months: float = 0.0
    promotion_count: int = 0
    company_count: int = 0
    career_stability: float = 0.0
    github_activity_score: float = 0.0
    has_github: bool = False
    recruiter_response_score: float = 0.0
    open_to_work: bool = False
    notice_period_days: int | None = None
    education_degrees: list[str] = field(default_factory=list)
    education_institutions: list[str] = field(default_factory=list)
    production_score: float = 0.0
    consistency_score: float = 0.0
    leadership_score: float = 0.0
    growth_score: float = 0.0
    ai_depth: float = 0.0
    retrieval_depth: float = 0.0
    domain_breadth: float = 0.0
    programming_skill_count: int = 0


class EvidenceCollector:
    """Collects factual evidence from Candidate and CandidateFeatures for downstream reasoning."""

    def collect(self, candidate: Candidate, features: CandidateFeatures) -> CollectedEvidence:
        """Extract all relevant evidence from a candidate and their features."""
        evidence = CollectedEvidence()

        # --- Skills ---
        evidence.skill_names = [s.name for s in candidate.skills]
        evidence.normalized_skills = (
            list(features.normalized_skills) if features.normalized_skills else []
        )

        # --- Career ---
        summary = features.career_summary
        evidence.total_experience_months = summary.total_experience_months
        evidence.average_tenure_months = summary.average_tenure_months
        evidence.promotion_count = summary.promotion_count
        evidence.company_count = summary.company_count
        evidence.career_stability = summary.career_stability
        evidence.career_titles = list(summary.titles) if summary.titles else []
        evidence.career_companies = [job.company for job in candidate.career_history if job.company]
        evidence.career_industries = list(summary.industries) if summary.industries else []

        # --- Behavioral Signals ---
        signals = candidate.signals
        evidence.github_activity_score = signals.github_activity_score or 0.0
        evidence.has_github = signals.has_github or False
        evidence.recruiter_response_score = signals.recruiter_response_score or 0.0
        evidence.open_to_work = signals.open_to_work or False
        evidence.notice_period_days = getattr(signals, "notice_period_days", None) or getattr(
            candidate.profile, "notice_period_days", None
        )

        # --- Education ---
        for edu in candidate.education:
            degree_str = f"{edu.degree or 'Degree'} in {edu.field_of_study or 'Field'}"
            evidence.education_degrees.append(degree_str)
            if edu.institution:
                evidence.education_institutions.append(edu.institution)

        # --- Feature Scores ---
        evidence.production_score = features.production_score
        evidence.consistency_score = features.consistency_score
        evidence.leadership_score = features.leadership_score
        evidence.growth_score = features.growth_score

        # --- Knowledge Graph Features ---
        fv = features.feature_vector
        evidence.ai_depth = fv.get("ai_depth", 0.0)
        evidence.retrieval_depth = fv.get("retrieval_depth", 0.0)
        evidence.domain_breadth = fv.get("domain_breadth", 0.0)
        evidence.programming_skill_count = features.skill_summary.programming_skill_count

        return evidence
