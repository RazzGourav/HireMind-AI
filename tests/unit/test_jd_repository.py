"""Tests for the JD artifact exporter (repository layer)."""

import json
import pickle
from pathlib import Path

import networkx as nx

from hiremind.domain.requirement import (
    ExperienceRequirement,
    NegativeRequirement,
    ParsedRequirements,
    Requirement,
)
from hiremind.domain.requirement_type import RequirementType
from hiremind.infrastructure.jd.exporter import JDExporter


def _sample_requirements() -> ParsedRequirements:
    """Build a sample ParsedRequirements for testing."""
    return ParsedRequirements(
        required=(
            Requirement(
                id="REQ_001",
                name="Python",
                category=RequirementType.REQUIRED,
                weight=1.0,
                aliases=("python3",),
                evidence="Must have Python",
            ),
            Requirement(
                id="REQ_002",
                name="Retrieval",
                category=RequirementType.REQUIRED,
                weight=1.0,
            ),
        ),
        preferred=(
            Requirement(
                id="REQ_003",
                name="LoRA",
                category=RequirementType.PREFERRED,
                weight=0.5,
                required=False,
            ),
        ),
        negative=(
            NegativeRequirement(
                id="NEG_001",
                name="Research Only",
                reason="Not looking for pure research",
            ),
        ),
        experience=ExperienceRequirement(min_years=5, max_years=9, preferred_years=5),
    )


def _sample_graph() -> nx.DiGraph:
    """Build a sample graph for testing."""
    g = nx.DiGraph()
    g.add_node("Python", node_type="skill")
    g.add_node("programming", node_type="category")
    g.add_edge("Python", "programming", relation="is_a")
    return g


def test_export_creates_requirements_json(tmp_path: Path) -> None:
    """Exporter writes jd_requirements.json with correct structure."""
    exporter = JDExporter(tmp_path)
    paths = exporter.export_all(_sample_requirements(), _sample_graph())

    req_path = paths["requirements"]
    assert req_path.exists()

    data = json.loads(req_path.read_text(encoding="utf-8"))
    assert "required" in data
    assert "preferred" in data
    assert "negative" in data
    assert "experience" in data

    required_names = [r["name"] for r in data["required"]]
    assert "Python" in required_names
    assert "Retrieval" in required_names


def test_export_creates_features_json(tmp_path: Path) -> None:
    """Exporter writes jd_features.json with skill→weight mapping."""
    exporter = JDExporter(tmp_path)
    paths = exporter.export_all(_sample_requirements(), _sample_graph())

    feat_path = paths["features"]
    assert feat_path.exists()

    data = json.loads(feat_path.read_text(encoding="utf-8"))
    assert data["required"]["Python"] == 1.0
    assert data["preferred"]["LoRA"] == 0.5
    assert "Research Only" in data["negative"]
    assert data["experience"]["min_years"] == 5


def test_export_creates_graph_pkl(tmp_path: Path) -> None:
    """Exporter writes jd_graph.pkl that can be loaded back."""
    exporter = JDExporter(tmp_path)
    paths = exporter.export_all(_sample_requirements(), _sample_graph())

    pkl_path = paths["graph"]
    assert pkl_path.exists()

    with pkl_path.open("rb") as f:
        loaded = pickle.load(f)  # noqa: S301

    assert isinstance(loaded, nx.DiGraph)
    assert loaded.has_node("Python")


def test_export_is_idempotent(tmp_path: Path) -> None:
    """Running export twice produces identical output."""
    exporter = JDExporter(tmp_path)
    reqs = _sample_requirements()
    graph = _sample_graph()

    paths_1 = exporter.export_all(reqs, graph)
    content_1 = paths_1["requirements"].read_bytes()

    paths_2 = exporter.export_all(reqs, graph)
    content_2 = paths_2["requirements"].read_bytes()

    assert content_1 == content_2


def test_export_creates_directory(tmp_path: Path) -> None:
    """Exporter creates the artifacts directory if it doesn't exist."""
    nested = tmp_path / "nested" / "artifacts"
    exporter = JDExporter(nested)
    paths = exporter.export_all(_sample_requirements(), _sample_graph())

    assert nested.exists()
    assert paths["requirements"].exists()
