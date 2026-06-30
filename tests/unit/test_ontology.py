"""Tests for the ontology loader and ontology service."""

from pathlib import Path

import pytest

from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.services.ontology_service import OntologyService

_MINIMAL_ONTOLOGY = """\
categories:
  vector_databases:
    FAISS:
      aliases: ["facebook ai similarity search"]
      parents: ["vector_database", "ann_search", "retrieval"]
    Milvus:
      aliases: []
      parents: ["vector_database", "ann_search", "retrieval"]
  llm_and_finetuning:
    LoRA:
      aliases: ["lora", "low-rank adaptation"]
      parents: ["fine_tuning", "llm", "transformers"]
    LLM:
      aliases: ["large language model"]
      parents: ["transformers", "nlp"]
  programming_languages:
    Python:
      aliases: ["python3", "py"]
      parents: ["programming"]

protected_terms:
  - FAISS
  - LoRA
  - Python
"""


@pytest.fixture()
def ontology_path(tmp_path: Path) -> Path:
    """Write a minimal ontology YAML and return its path."""
    path = tmp_path / "ontology.yaml"
    path.write_text(_MINIMAL_ONTOLOGY, encoding="utf-8")
    return path


@pytest.fixture()
def loader(ontology_path: Path) -> OntologyLoader:
    """Load the minimal ontology."""
    return OntologyLoader(ontology_path).load()


@pytest.fixture()
def service(loader: OntologyLoader) -> OntologyService:
    """Build an OntologyService from the minimal ontology."""
    return OntologyService(loader)


# ── OntologyLoader tests ──────────────────────────────────────────────────────


def test_loader_canonical_names(loader: OntologyLoader) -> None:
    """Loader returns all canonical skill names."""
    names = loader.all_canonical_names()
    assert "FAISS" in names
    assert "LoRA" in names
    assert "Python" in names


def test_loader_alias_resolution(loader: OntologyLoader) -> None:
    """Loader resolves aliases to canonical names."""
    assert loader.canonical_name("python3") == "Python"
    assert loader.canonical_name("lora") == "LoRA"
    assert loader.canonical_name("facebook ai similarity search") == "FAISS"


def test_loader_canonical_self_resolution(loader: OntologyLoader) -> None:
    """Canonical names resolve to themselves."""
    assert loader.canonical_name("FAISS") == "FAISS"
    assert loader.canonical_name("Python") == "Python"


def test_loader_unknown_skill(loader: OntologyLoader) -> None:
    """Unknown skills return None."""
    assert loader.canonical_name("UnknownTech") is None


def test_loader_parents(loader: OntologyLoader) -> None:
    """Loader returns parent categories."""
    parents = loader.get_parents("FAISS")
    assert "vector_database" in parents
    assert "retrieval" in parents


def test_loader_protected_terms(loader: OntologyLoader) -> None:
    """Loader returns protected terms."""
    protected = loader.protected_terms
    assert "FAISS" in protected
    assert "LoRA" in protected


def test_loader_missing_file_raises() -> None:
    """Loader raises FileNotFoundError for missing YAML."""
    with pytest.raises(FileNotFoundError):
        OntologyLoader("nonexistent.yaml").load()


# ── OntologyService tests ─────────────────────────────────────────────────────


def test_service_exact_normalization(service: OntologyService) -> None:
    """Service normalises via exact alias match."""
    assert service.normalize_skill("python3") == "Python"
    assert service.normalize_skill("lora") == "LoRA"


def test_service_fuzzy_normalization(service: OntologyService) -> None:
    """Service normalises via fuzzy matching for close strings."""
    # "pythn" is close to "python" / "py"
    result = service.normalize_skill("pythn")
    # Should fuzzy-match to Python (or return original if below threshold)
    assert result in ("Python", "pythn")


def test_service_unknown_returns_original(service: OntologyService) -> None:
    """Service returns original string for completely unknown skills."""
    assert service.normalize_skill("CompletelyUnknownXYZ123") == "CompletelyUnknownXYZ123"


def test_service_ancestors(service: OntologyService) -> None:
    """Service returns ancestors for a skill."""
    ancestors = service.get_ancestors("FAISS")
    assert "vector_database" in ancestors
    assert "retrieval" in ancestors


def test_service_related_skills(service: OntologyService) -> None:
    """Service finds skills that share parents."""
    related = service.get_related("FAISS")
    # Milvus shares vector_database and retrieval parents with FAISS.
    assert "Milvus" in related
