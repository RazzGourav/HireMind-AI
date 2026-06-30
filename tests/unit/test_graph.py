"""Tests for the graph service."""

from pathlib import Path

import pytest

from hiremind.domain.requirement import (
    ExperienceRequirement,
    NegativeRequirement,
    ParsedRequirements,
    Requirement,
)
from hiremind.domain.requirement_type import RequirementType
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.services.graph_service import GraphService

_MINIMAL_ONTOLOGY = """\
categories:
  vector_databases:
    FAISS:
      aliases: []
      parents: ["vector_database", "retrieval"]
    Milvus:
      aliases: []
      parents: ["vector_database", "retrieval"]
  embeddings_and_retrieval:
    Retrieval:
      aliases: []
      parents: ["nlp"]
    Embeddings:
      aliases: []
      parents: ["nlp"]

protected_terms: []
"""


@pytest.fixture()
def ontology_loader(tmp_path: Path) -> OntologyLoader:
    path = tmp_path / "ontology.yaml"
    path.write_text(_MINIMAL_ONTOLOGY, encoding="utf-8")
    return OntologyLoader(path).load()


@pytest.fixture()
def graph_service(ontology_loader: OntologyLoader) -> GraphService:
    return GraphService(ontology_loader)


def test_graph_has_skill_nodes(graph_service: GraphService) -> None:
    """Graph contains all skills from the ontology."""
    graph = graph_service.build()
    assert graph.has_node("FAISS")
    assert graph.has_node("Milvus")
    assert graph.has_node("Retrieval")
    assert graph.has_node("Embeddings")


def test_graph_has_category_nodes(graph_service: GraphService) -> None:
    """Graph creates category nodes from parent references."""
    graph = graph_service.build()
    assert graph.has_node("vector_database")
    assert graph.has_node("retrieval")
    assert graph.has_node("nlp")


def test_graph_has_is_a_edges(graph_service: GraphService) -> None:
    """Graph contains is_a edges from skills to parents."""
    graph = graph_service.build()
    assert graph.has_edge("FAISS", "vector_database")
    assert graph.has_edge("FAISS", "retrieval")
    assert graph.has_edge("Milvus", "vector_database")


def test_graph_node_edge_counts(graph_service: GraphService) -> None:
    """Graph has expected node and edge counts."""
    graph_service.build()
    assert graph_service.node_count() > 0
    assert graph_service.edge_count() > 0


def test_graph_ancestors(graph_service: GraphService) -> None:
    """Ancestors traversal returns parent nodes."""
    graph_service.build()
    ancestors = graph_service.ancestors("FAISS")
    assert "vector_database" in ancestors
    assert "retrieval" in ancestors


def test_graph_descendants(graph_service: GraphService) -> None:
    """Descendants traversal returns child skill nodes."""
    graph_service.build()
    descendants = graph_service.descendants("vector_database")
    assert "FAISS" in descendants
    assert "Milvus" in descendants


def test_graph_shortest_path(graph_service: GraphService) -> None:
    """Shortest path finds a route between connected nodes."""
    graph_service.build()
    path = graph_service.shortest_path("FAISS", "Milvus")
    assert path is not None
    assert len(path) >= 2


def test_graph_shortest_path_no_route(graph_service: GraphService) -> None:
    """Shortest path returns None for disconnected nodes."""
    graph_service.build()
    path = graph_service.shortest_path("FAISS", "nonexistent_node")
    assert path is None


def test_graph_marks_requirements(graph_service: GraphService) -> None:
    """Graph marks requirement nodes with type and weight."""
    requirements = ParsedRequirements(
        required=(
            Requirement(
                id="REQ_001",
                name="FAISS",
                category=RequirementType.REQUIRED,
                weight=0.9,
            ),
        ),
        preferred=(
            Requirement(
                id="REQ_002",
                name="Embeddings",
                category=RequirementType.PREFERRED,
                weight=0.5,
                required=False,
            ),
        ),
        negative=(NegativeRequirement(id="NEG_001", name="nonexistent"),),
        experience=ExperienceRequirement(),
    )

    graph = graph_service.build(requirements)

    assert graph.nodes["FAISS"].get("requirement") == "required"
    assert graph.nodes["FAISS"].get("weight") == 0.9
    assert graph.nodes["Embeddings"].get("requirement") == "preferred"


def test_requirement_nodes_listing(graph_service: GraphService) -> None:
    """requirement_nodes() returns only marked nodes."""
    requirements = ParsedRequirements(
        required=(Requirement(id="REQ_001", name="FAISS", category=RequirementType.REQUIRED),),
    )
    graph_service.build(requirements)
    req_nodes = graph_service.requirement_nodes()
    assert "FAISS" in req_nodes
    assert req_nodes["FAISS"] == "required"


def test_graph_serialization(graph_service: GraphService, tmp_path: Path) -> None:
    """Graph can be serialised and deserialised via pickle."""
    import pickle

    graph = graph_service.build()
    pkl_path = tmp_path / "graph.pkl"
    with pkl_path.open("wb") as f:
        pickle.dump(graph, f)

    with pkl_path.open("rb") as f:
        loaded = pickle.load(f)  # noqa: S301

    assert loaded.number_of_nodes() == graph.number_of_nodes()
    assert loaded.number_of_edges() == graph.number_of_edges()
