"""Tests for CandidateFeatures and the full intelligence pipeline."""

from pathlib import Path

import pytest

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.career import Career
from hiremind.domain.education import Education
from hiremind.domain.profile import Profile
from hiremind.domain.skill import Skill
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.services.candidate_intelligence_service import (
    CandidateIntelligenceService,
)
from hiremind.services.ontology_service import OntologyService

_MINIMAL_ONTOLOGY = """\
categories:
  programming_languages:
    Python:
      aliases: ["python3"]
      parents: ["programming"]
  embeddings_and_retrieval:
    Embeddings:
      aliases: ["text embeddings"]
      parents: ["nlp"]

protected_terms: []
"""


@pytest.fixture()
def ontology_service(tmp_path: Path) -> OntologyService:
    path = tmp_path / "ontology.yaml"
    path.write_text(_MINIMAL_ONTOLOGY, encoding="utf-8")
    loader = OntologyLoader(path).load()
    return OntologyService(loader)


def _make_candidate() -> Candidate:
    return Candidate(
        candidate_id="CAND_TEST",
        profile=Profile(
            current_title="ML Engineer",
            headline="ML Engineer | Python, Embeddings",
            summary="Machine learning engineer with 5 years experience.",
            total_experience_months=60,
        ),
        career_history=[
            Career(
                company="TechCo",
                title="ML Engineer",
                duration_months=30,
                is_current=True,
                industry="Technology",
                company_size="1001-5000",
                description="Built and deployed production ML pipelines. Led a team of 3.",
            ),
            Career(
                company="StartupInc",
                title="Software Engineer",
                duration_months=24,
                is_current=False,
                industry="Technology",
                company_size="11-50",
                description="Implemented backend services and data processing pipelines.",
            ),
        ],
        education=[
            Education(
                institution="IIT Delhi",
                degree="B.Tech",
                field_of_study="Computer Science",
                tier="tier_1",
                graduation_year=2020,
            ),
        ],
        skills=[
            Skill(name="Python", proficiency="advanced", endorsements=5, duration_months=48),
            Skill(name="Embeddings", proficiency="intermediate", duration_months=12),
        ],
        signals=RedrobSignals(github_activity_score=0.7, has_github=True),
    )


def test_pipeline_produces_features(ontology_service: OntologyService, tmp_path: Path) -> None:
    """Full pipeline produces CandidateFeatures with all scores."""
    service = CandidateIntelligenceService(
        ontology_service=ontology_service,
        artifacts_dir=tmp_path,
    )
    result = service.process([_make_candidate()], show_progress=False)

    assert result.total_processed == 1
    assert result.features_path.exists()
    assert result.summary_path.exists()


def test_feature_vector_has_expected_keys(
    ontology_service: OntologyService, tmp_path: Path
) -> None:
    """Feature vector contains all expected keys."""
    service = CandidateIntelligenceService(
        ontology_service=ontology_service,
        artifacts_dir=tmp_path,
    )
    result = service.process([_make_candidate()], show_progress=False)

    import pickle

    with result.summary_path.open("rb") as f:
        features = pickle.load(f)  # noqa: S301

    assert len(features) == 1
    feat = features[0]

    expected_keys = {
        "technical_score",
        "career_score",
        "leadership_score",
        "production_score",
        "growth_score",
        "consistency_score",
        "education_score",
        "total_experience_months",
        "career_stability",
        "total_skills",
        "ai_ml_skill_count",
    }
    assert expected_keys.issubset(feat.feature_vector.keys())


def test_scores_are_bounded(ontology_service: OntologyService, tmp_path: Path) -> None:
    """All scores are between 0.0 and 1.0."""
    service = CandidateIntelligenceService(
        ontology_service=ontology_service,
        artifacts_dir=tmp_path,
    )
    service.process([_make_candidate()], show_progress=False)

    import pickle

    summary_path = tmp_path / "candidate_summary.pkl"
    with summary_path.open("rb") as f:
        features = pickle.load(f)  # noqa: S301

    feat = features[0]
    for score_name in [
        "technical_score",
        "career_score",
        "leadership_score",
        "production_score",
        "growth_score",
        "consistency_score",
        "education_score",
    ]:
        value = getattr(feat, score_name)
        assert 0.0 <= value <= 1.0, f"{score_name}={value} out of bounds"


def test_normalized_skills_populated(ontology_service: OntologyService, tmp_path: Path) -> None:
    """Normalized skills list is populated."""
    service = CandidateIntelligenceService(
        ontology_service=ontology_service,
        artifacts_dir=tmp_path,
    )
    service.process([_make_candidate()], show_progress=False)

    import pickle

    summary_path = tmp_path / "candidate_summary.pkl"
    with summary_path.open("rb") as f:
        features = pickle.load(f)  # noqa: S301

    feat = features[0]
    assert len(feat.normalized_skills) > 0
    assert "Python" in feat.normalized_skills


def test_parquet_roundtrip(ontology_service: OntologyService, tmp_path: Path) -> None:
    """Parquet feature store can be loaded back."""
    import pandas as pd

    service = CandidateIntelligenceService(
        ontology_service=ontology_service,
        artifacts_dir=tmp_path,
    )
    result = service.process([_make_candidate()], show_progress=False)

    df = pd.read_parquet(result.features_path)
    assert len(df) == 1
    assert "candidate_id" in df.columns
    assert "technical_score" in df.columns
