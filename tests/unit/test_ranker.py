"""Unit tests for the Ranker scoring engines (Technical, Career, Behavior, Graph, and Risk)."""

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.domain.career_summary import CareerSummary
from hiremind.domain.profile import Profile
from hiremind.domain.requirement import ParsedRequirements, Requirement
from hiremind.domain.requirement_type import RequirementType
from hiremind.domain.skill import Skill
from hiremind.ranking.behavior_ranker import BehaviorRanker
from hiremind.ranking.career_ranker import CareerRanker
from hiremind.ranking.graph_ranker import GraphRanker
from hiremind.ranking.risk_engine import RiskEngine
from hiremind.ranking.technical_ranker import TechnicalRanker


def test_technical_ranker() -> None:
    ranker = TechnicalRanker()
    cand = Candidate(
        candidate_id="CAND_01",
        profile=Profile(),
        career_history=[],
        education=[],
        skills=[Skill(name="Python"), Skill(name="FAISS")],
        signals=RedrobSignals(),
    )
    features = CandidateFeatures(candidate_id="CAND_01", production_score=0.8)
    reqs = ParsedRequirements(
        required=(Requirement(id="1", name="Python", category=RequirementType.REQUIRED),),
        preferred=(Requirement(id="2", name="FAISS", category=RequirementType.PREFERRED),),
    )

    score = ranker.score(cand, features, reqs)
    assert score > 0.5
    assert score <= 1.0


def test_career_ranker() -> None:
    ranker = CareerRanker()
    cand = Candidate(
        candidate_id="CAND_01",
        profile=Profile(),
        career_history=[],
        education=[],
        skills=[],
        signals=RedrobSignals(),
    )
    # total exp: 60 months, average tenure: 24, stable career
    summary = CareerSummary(
        total_experience_months=60,
        average_tenure_months=24.0,
        promotion_count=1,
        career_stability=0.8,
    )
    features = CandidateFeatures(candidate_id="CAND_01", career_summary=summary)

    score = ranker.score(cand, features)
    assert score > 0.4
    assert score <= 1.0


def test_behavior_ranker() -> None:
    ranker = BehaviorRanker()
    cand = Candidate(
        candidate_id="CAND_01",
        profile=Profile(summary="Experience resume summary content..."),
        career_history=[],
        education=[],
        skills=[Skill(name=f"Skill_{i}") for i in range(8)],
        signals=RedrobSignals(github_activity_score=0.9, open_to_work=True),
    )
    features = CandidateFeatures(candidate_id="CAND_01")

    score = ranker.score(cand, features)
    # High signals + summary + skills = high score
    assert score > 0.5
    assert score <= 1.0


def test_graph_ranker() -> None:
    ranker = GraphRanker()
    cand = Candidate(
        candidate_id="CAND_01",
        profile=Profile(),
        career_history=[],
        education=[],
        skills=[],
        signals=RedrobSignals(),
    )
    features = CandidateFeatures(candidate_id="CAND_01")
    features.feature_vector = {
        "technology_diversity": 4.0,
        "ai_depth": 3.0,
        "backend_depth": 2.0,
        "retrieval_depth": 3.0,
        "domain_breadth": 2.0,
        "graph_connectivity": 0.5,
    }
    reqs = ParsedRequirements()

    score = ranker.score(cand, features, reqs)
    assert score > 0.5
    assert score <= 1.0


def test_risk_engine() -> None:
    engine = RiskEngine()
    cand = Candidate(
        candidate_id="CAND_01",
        profile=Profile(notice_period_days=120),
        career_history=[],
        education=[],
        skills=[],
        signals=RedrobSignals(),
    )
    features = CandidateFeatures(candidate_id="CAND_01", consistency_score=0.2)
    reqs = ParsedRequirements()

    penalty = engine.calculate_penalty(cand, features, reqs, max_notice_days=90)
    # Consistency penalty (0.15) + notice period (0.2) = ~0.35
    assert penalty > 0.2
    assert penalty <= 1.0
