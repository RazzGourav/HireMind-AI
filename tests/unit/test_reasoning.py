"""Tests for Milestone 8 — Explainability & Recruiter Reasoning Engine."""

from __future__ import annotations

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.domain.career_summary import CareerSummary
from hiremind.domain.education import Education
from hiremind.domain.explanation import (
    AlignmentStatus,
    CandidateExplanation,
    ConcernSeverity,
)
from hiremind.domain.profile import Profile
from hiremind.domain.recommendation import InterviewRecommendation
from hiremind.domain.requirement import (
    ExperienceRequirement,
    ParsedRequirements,
    Requirement,
)
from hiremind.domain.requirement_type import RequirementType
from hiremind.domain.skill import Skill
from hiremind.domain.skill_summary import SkillSummary
from hiremind.reasoning.comparison_engine import ComparisonEngine
from hiremind.reasoning.concern_detector import ConcernDetector
from hiremind.reasoning.evidence_collector import EvidenceCollector
from hiremind.reasoning.explanation_builder import ReasoningExplanationBuilder
from hiremind.reasoning.feature_attribution import FeatureAttributionEngine
from hiremind.reasoning.recommendation_engine import RecommendationEngine
from hiremind.reasoning.requirement_alignment import RequirementAlignmentEngine
from hiremind.reasoning.strength_detector import StrengthDetector
from hiremind.reasoning.validator import ExplanationValidator

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_candidate(
    cid: str = "C001",
    skills: list[str] | None = None,
    github_score: float = 0.5,
    recruiter_score: float = 0.5,
    notice_days: int | None = 30,
    avg_tenure: float = 36.0,
    experience_months: int = 60,
) -> Candidate:
    skill_list = skills or ["Python", "PyTorch", "Docker", "Kubernetes", "FastAPI"]
    return Candidate(
        candidate_id=cid,
        profile=Profile(
            current_title="Senior ML Engineer",
            headline="AI/ML Engineer",
            summary="Experienced engineer with production ML systems.",
            country="India",
            total_experience_months=experience_months,
            notice_period_days=notice_days,
        ),
        career_history=[],
        education=[
            Education(degree="B.Tech", field_of_study="Computer Science", institution="IIT Delhi"),
        ],
        skills=[Skill(name=s, endorsements=5) for s in skill_list],
        signals=RedrobSignals(
            github_activity_score=github_score,
            recruiter_response_score=recruiter_score,
            has_github=github_score > 0,
            open_to_work=True,
            notice_period_days=notice_days,
        ),
    )


def _make_features(
    cid: str = "C001",
    production: float = 0.7,
    consistency: float = 0.8,
    leadership: float = 0.6,
    growth: float = 0.65,
    avg_tenure: float = 36.0,
    stability: float = 0.8,
    experience_months: int = 60,
    normalized_skills: list[str] | None = None,
) -> CandidateFeatures:
    return CandidateFeatures(
        candidate_id=cid,
        technical_score=0.7,
        career_score=0.6,
        leadership_score=leadership,
        production_score=production,
        growth_score=growth,
        consistency_score=consistency,
        education_score=0.5,
        career_summary=CareerSummary(
            total_experience_months=experience_months,
            average_tenure_months=avg_tenure,
            promotion_count=2,
            company_count=3,
            career_stability=stability,
            titles=("ML Engineer", "Senior ML Engineer"),
            industries=("Technology",),
        ),
        skill_summary=SkillSummary(
            normalized_names=normalized_skills
            or ["python", "pytorch", "docker", "kubernetes", "fastapi"],
            total_skills=5,
            ai_ml_skill_count=2,
            programming_skill_count=3,
            unique_categories=3,
        ),
        normalized_skills=normalized_skills
        or ["python", "pytorch", "docker", "kubernetes", "fastapi"],
        feature_vector={
            "technology_diversity": 4.0,
            "ai_depth": 3.0,
            "backend_depth": 2.0,
            "cloud_depth": 1.0,
            "retrieval_depth": 2.5,
            "domain_breadth": 2.0,
            "graph_connectivity": 0.6,
        },
    )


def _make_requirements() -> ParsedRequirements:
    return ParsedRequirements(
        required=(
            Requirement(id="R1", name="Python", category=RequirementType.TECHNOLOGY, weight=1.0),
            Requirement(id="R2", name="PyTorch", category=RequirementType.TECHNOLOGY, weight=1.0),
            Requirement(
                id="R3", name="TensorFlow", category=RequirementType.TECHNOLOGY, weight=0.8
            ),
            Requirement(id="R4", name="Docker", category=RequirementType.TECHNOLOGY, weight=0.7),
        ),
        preferred=(
            Requirement(
                id="P1",
                name="Kubernetes",
                category=RequirementType.TECHNOLOGY,
                weight=0.5,
                required=False,
            ),
            Requirement(
                id="P2",
                name="GraphQL",
                category=RequirementType.TECHNOLOGY,
                weight=0.3,
                required=False,
            ),
        ),
        experience=ExperienceRequirement(min_years=3, preferred_years=5),
    )


def _make_components() -> dict[str, float]:
    return {
        "technical_score": 0.75,
        "career_score": 0.60,
        "behavior_score": 0.70,
        "knowledge_score": 0.55,
        "growth_score": 0.65,
        "leadership_score": 0.50,
        "risk_penalty": 0.05,
    }


# ---------------------------------------------------------------------------
# Feature Attribution Tests
# ---------------------------------------------------------------------------


class TestFeatureAttribution:
    def test_attribution_components_count(self):
        engine = FeatureAttributionEngine()
        components = _make_components()
        attrs = engine.attribute(components, final_score=65.0)

        # 6 positive components + 1 risk penalty = 7
        assert len(attrs) == 7

    def test_attribution_sums_correctly(self):
        engine = FeatureAttributionEngine()
        components = _make_components()
        attrs = engine.attribute(components, final_score=65.0)

        positive_sum = sum(a.weighted_contribution for a in attrs if a.weight > 0)
        penalty = sum(abs(a.weighted_contribution) for a in attrs if a.weight < 0)

        # Reconstructed should match the fusion formula
        expected = 0.40 * 0.75 + 0.20 * 0.60 + 0.15 * 0.70 + 0.15 * 0.55 + 0.05 * 0.65 + 0.05 * 0.50
        assert abs(positive_sum - expected) < 0.01

    def test_attribution_labels(self):
        engine = FeatureAttributionEngine()
        components = _make_components()
        attrs = engine.attribute(components, final_score=65.0)

        labels = {a.component: a.label for a in attrs}
        assert labels["technical_score"] == "Technical Skill Alignment"
        assert labels["risk_penalty"] == "Risk Penalty"


# ---------------------------------------------------------------------------
# Evidence Collector Tests
# ---------------------------------------------------------------------------


class TestEvidenceCollector:
    def test_collects_skills(self):
        collector = EvidenceCollector()
        candidate = _make_candidate()
        features = _make_features()
        evidence = collector.collect(candidate, features)

        assert "Python" in evidence.skill_names
        assert "python" in evidence.normalized_skills

    def test_collects_signals(self):
        collector = EvidenceCollector()
        candidate = _make_candidate(github_score=0.8, notice_days=45)
        features = _make_features()
        evidence = collector.collect(candidate, features)

        assert evidence.github_activity_score == 0.8
        assert evidence.notice_period_days == 45
        assert evidence.has_github is True


# ---------------------------------------------------------------------------
# Requirement Alignment Tests
# ---------------------------------------------------------------------------


class TestRequirementAlignment:
    def test_all_matched(self):
        """Candidate has all required skills → all MATCHED."""
        engine = RequirementAlignmentEngine()
        reqs = ParsedRequirements(
            required=(
                Requirement(id="R1", name="Python", category=RequirementType.TECHNOLOGY),
                Requirement(id="R2", name="Docker", category=RequirementType.TECHNOLOGY),
            ),
        )
        evidence = EvidenceCollector().collect(
            _make_candidate(skills=["Python", "Docker"]),
            _make_features(normalized_skills=["python", "docker"]),
        )
        alignments = engine.align(reqs, evidence)
        assert all(a.status == AlignmentStatus.MATCHED for a in alignments)
        assert engine.compute_required_alignment_ratio(alignments) == 1.0

    def test_partial_match(self):
        """Candidate has some required skills → mix of MATCHED and MISSING."""
        engine = RequirementAlignmentEngine()
        reqs = _make_requirements()
        evidence = EvidenceCollector().collect(
            _make_candidate(skills=["Python", "Docker"]),
            _make_features(normalized_skills=["python", "docker"]),
        )
        alignments = engine.align(reqs, evidence)

        statuses = {a.requirement_name: a.status for a in alignments}
        assert statuses["Python"] == AlignmentStatus.MATCHED
        assert statuses["Docker"] == AlignmentStatus.MATCHED
        # TensorFlow should be MISSING since candidate doesn't have it
        assert statuses["TensorFlow"] == AlignmentStatus.MISSING

    def test_alignment_ratio(self):
        engine = RequirementAlignmentEngine()
        reqs = _make_requirements()
        evidence = EvidenceCollector().collect(_make_candidate(), _make_features())
        alignments = engine.align(reqs, evidence)

        ratio = engine.compute_alignment_ratio(alignments)
        assert 0.0 <= ratio <= 1.0


# ---------------------------------------------------------------------------
# Strength Detection Tests
# ---------------------------------------------------------------------------


class TestStrengthDetector:
    def test_detects_production_ai(self):
        detector = StrengthDetector()
        evidence = EvidenceCollector().collect(
            _make_candidate(),
            _make_features(production=0.8),
        )
        strengths = detector.detect(evidence)

        labels = [s.label for s in strengths]
        assert "Production AI Experience" in labels

    def test_detects_stable_career(self):
        detector = StrengthDetector()
        evidence = EvidenceCollector().collect(
            _make_candidate(),
            _make_features(stability=0.85, avg_tenure=30.0),
        )
        strengths = detector.detect(evidence)

        labels = [s.label for s in strengths]
        assert "Stable Career Trajectory" in labels

    def test_no_false_strengths(self):
        """Candidate with low scores should not trigger strengths."""
        detector = StrengthDetector()
        evidence = EvidenceCollector().collect(
            _make_candidate(github_score=0.1, recruiter_score=0.1),
            _make_features(
                production=0.2, leadership=0.1, growth=0.1, stability=0.3, avg_tenure=10.0
            ),
        )
        strengths = detector.detect(evidence)

        labels = {s.label for s in strengths}
        assert "Production AI Experience" not in labels
        assert "Stable Career Trajectory" not in labels
        assert "High Recruiter Engagement" not in labels


# ---------------------------------------------------------------------------
# Concern Detection Tests
# ---------------------------------------------------------------------------


class TestConcernDetector:
    def test_detects_missing_skills(self):
        detector = ConcernDetector()
        engine = RequirementAlignmentEngine()
        reqs = _make_requirements()
        evidence = EvidenceCollector().collect(
            _make_candidate(skills=["Python"]),
            _make_features(normalized_skills=["python"]),
        )
        alignments = engine.align(reqs, evidence)
        concerns = detector.detect(evidence, alignments)

        labels = [c.label for c in concerns]
        assert "Missing Mandatory Skills" in labels

    def test_detects_job_hopping(self):
        detector = ConcernDetector()
        evidence = EvidenceCollector().collect(
            _make_candidate(),
            _make_features(avg_tenure=8.0),
        )
        concerns = detector.detect(evidence, [])

        labels = [c.label for c in concerns]
        assert "Frequent Job Changes" in labels

    def test_detects_long_notice(self):
        detector = ConcernDetector()
        evidence = EvidenceCollector().collect(
            _make_candidate(notice_days=120),
            _make_features(),
        )
        concerns = detector.detect(evidence, [], max_notice_days=90)

        labels = [c.label for c in concerns]
        assert "Extended Notice Period" in labels

    def test_no_github_concern(self):
        detector = ConcernDetector()
        evidence = EvidenceCollector().collect(
            _make_candidate(github_score=0.0),
            _make_features(),
        )
        # Set has_github to False explicitly
        evidence.has_github = False
        evidence.github_activity_score = 0.0
        concerns = detector.detect(evidence, [])

        labels = [c.label for c in concerns]
        assert "No GitHub Presence" in labels


# ---------------------------------------------------------------------------
# Recommendation Engine Tests
# ---------------------------------------------------------------------------


class TestRecommendationEngine:
    def test_strong_hire(self):
        engine = RecommendationEngine()
        result = engine.recommend("C001", final_score=90.0, alignment_ratio=0.9)
        assert result.recommendation == InterviewRecommendation.STRONG_HIRE

    def test_hire(self):
        engine = RecommendationEngine()
        result = engine.recommend("C001", final_score=75.0, alignment_ratio=0.85)
        assert result.recommendation == InterviewRecommendation.HIRE

    def test_interview(self):
        engine = RecommendationEngine()
        result = engine.recommend("C001", final_score=55.0, alignment_ratio=0.85)
        assert result.recommendation == InterviewRecommendation.INTERVIEW

    def test_reject(self):
        engine = RecommendationEngine()
        result = engine.recommend("C001", final_score=30.0, alignment_ratio=0.3)
        assert result.recommendation == InterviewRecommendation.REJECT

    def test_critical_concern_override(self):
        """Multiple HIGH severity concerns should cap at HOLD."""
        from hiremind.domain.explanation import Concern, ConcernSeverity

        engine = RecommendationEngine()
        high_concerns = [
            Concern(label="C1", severity=ConcernSeverity.HIGH, description="Issue 1"),
            Concern(label="C2", severity=ConcernSeverity.HIGH, description="Issue 2"),
        ]
        result = engine.recommend(
            "C001", final_score=90.0, alignment_ratio=0.95, concerns=high_concerns
        )
        assert result.recommendation == InterviewRecommendation.HOLD


# ---------------------------------------------------------------------------
# Comparison Engine Tests
# ---------------------------------------------------------------------------


class TestComparisonEngine:
    def test_comparison_structure(self):
        engine = ComparisonEngine()

        exp_a = CandidateExplanation(
            candidate_id="A",
            final_score=85.0,
            strengths=(
                __import__("hiremind.domain.explanation", fromlist=["Strength"]).Strength(
                    label="Production AI", description="Has production AI exp."
                ),
            ),
            concerns=(),
        )
        exp_b = CandidateExplanation(
            candidate_id="B",
            final_score=70.0,
            strengths=(),
            concerns=(
                __import__("hiremind.domain.explanation", fromlist=["Concern"]).Concern(
                    label="Job Hopping", severity=ConcernSeverity.MEDIUM, description="Hops."
                ),
            ),
        )
        rec_a = {
            "final_score": 85.0,
            "technical_score": 80.0,
            "career_score": 70.0,
            "behavior_score": 60.0,
            "knowledge_score": 55.0,
        }
        rec_b = {
            "final_score": 70.0,
            "technical_score": 60.0,
            "career_score": 75.0,
            "behavior_score": 50.0,
            "knowledge_score": 40.0,
        }

        comparison = engine.compare(exp_a, exp_b, rec_a, rec_b)

        assert comparison.overall_winner == "A"
        assert len(comparison.dimensions) == 5
        assert "Production AI" in comparison.a_unique_strengths
        assert "Job Hopping" in comparison.b_unique_concerns

        # Verify serialization
        d = comparison.to_dict()
        assert d["overall_winner"] == "A"


# ---------------------------------------------------------------------------
# Validator Tests
# ---------------------------------------------------------------------------


class TestExplanationValidator:
    def test_valid_explanation(self):
        validator = ExplanationValidator()
        builder = ReasoningExplanationBuilder()
        candidate = _make_candidate()
        features = _make_features()
        reqs = _make_requirements()
        components = _make_components()

        explanation = builder.build(candidate, features, reqs, components, final_score=65.0)
        result = validator.validate(explanation)

        # Should pass (may have warnings but no errors)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_catches_inconsistent_recommendation(self):
        """A score of 90 with recommendation 'Reject' should be flagged."""
        validator = ExplanationValidator()

        bad_explanation = CandidateExplanation(
            candidate_id="BAD",
            final_score=90.0,
            recommendation="Reject",
        )
        result = validator.validate(bad_explanation)

        assert result.valid is False
        assert any("inconsistent" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Full Pipeline Test
# ---------------------------------------------------------------------------


class TestFullExplanationPipeline:
    def test_end_to_end(self):
        """Full pipeline: build → validate → serialize."""
        builder = ReasoningExplanationBuilder()
        validator = ExplanationValidator()

        candidate = _make_candidate()
        features = _make_features()
        reqs = _make_requirements()
        components = _make_components()

        explanation = builder.build(candidate, features, reqs, components, final_score=65.0)

        # Verify structure
        assert explanation.candidate_id == "C001"
        assert explanation.final_score == 65.0
        assert len(explanation.attributions) > 0
        assert len(explanation.requirement_alignments) > 0
        assert explanation.recommendation in ("Strong Hire", "Hire", "Interview", "Hold", "Reject")
        assert explanation.recruiter_summary != ""

        # Validate
        validation = validator.validate(explanation)
        assert validation.valid is True

        # Serialize
        d = explanation.to_dict()
        assert d["candidate_id"] == "C001"
        assert "score_attributions" in d
        assert "requirement_alignments" in d
        assert "strengths" in d
        assert "concerns" in d
        assert "interview_recommendation" in d
