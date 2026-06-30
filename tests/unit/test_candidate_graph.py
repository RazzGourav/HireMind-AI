"""Tests for candidate knowledge graph."""

from pathlib import Path

import pytest

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.career import Career
from hiremind.domain.profile import Profile
from hiremind.domain.skill import Skill
from hiremind.infrastructure.candidate.graph import build_candidate_graph
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.services.ontology_service import OntologyService

_MINIMAL_ONTOLOGY = """\
categories:
  programming_languages:
    Python:
      aliases: ["python3"]
      parents: ["programming"]
  vector_databases:
    FAISS:
      aliases: []
      parents: ["vector_database", "retrieval"]

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
        candidate_id="CAND_001",
        profile=Profile(current_title="Engineer"),
        career_history=[
            Career(company="Acme Corp", title="Engineer", industry="Tech"),
        ],
        education=[],
        skills=[Skill(name="Python"), Skill(name="FAISS")],
        signals=RedrobSignals(),
    )


def test_graph_has_candidate_node(ontology_service: OntologyService) -> None:
    """Graph contains the central candidate node."""
    cand = _make_candidate()
    g = build_candidate_graph(cand, ontology_service)
    assert g.has_node("CAND_001")
    assert g.nodes["CAND_001"]["node_type"] == "candidate"


def test_graph_has_skill_nodes(ontology_service: OntologyService) -> None:
    """Graph contains skill nodes with has_skill edges."""
    cand = _make_candidate()
    g = build_candidate_graph(cand, ontology_service)
    assert g.has_node("Python")
    assert g.has_node("FAISS")
    assert g.has_edge("CAND_001", "Python")
    assert g.has_edge("CAND_001", "FAISS")


def test_graph_has_company_nodes(ontology_service: OntologyService) -> None:
    """Graph contains company nodes with worked_at edges."""
    cand = _make_candidate()
    g = build_candidate_graph(cand, ontology_service)
    assert g.has_node("Acme Corp")
    assert g.has_edge("CAND_001", "Acme Corp")


def test_graph_has_industry_nodes(ontology_service: OntologyService) -> None:
    """Graph contains industry nodes linked from companies."""
    cand = _make_candidate()
    g = build_candidate_graph(cand, ontology_service)
    assert g.has_node("Tech")
    assert g.has_edge("Acme Corp", "Tech")


def test_graph_has_ontology_parents(ontology_service: OntologyService) -> None:
    """Graph contains ontology parent nodes via is_a edges."""
    cand = _make_candidate()
    g = build_candidate_graph(cand, ontology_service)
    assert g.has_node("programming")
    assert g.has_edge("Python", "programming")


def test_graph_serialization(ontology_service: OntologyService, tmp_path: Path) -> None:
    """Graph can be pickled and unpickled."""
    import pickle

    cand = _make_candidate()
    g = build_candidate_graph(cand, ontology_service)
    pkl_path = tmp_path / "graph.pkl"
    with pkl_path.open("wb") as f:
        pickle.dump(g, f)
    with pkl_path.open("rb") as f:
        loaded = pickle.load(f)  # noqa: S301
    assert loaded.number_of_nodes() == g.number_of_nodes()
