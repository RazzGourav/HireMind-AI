"""Tests for skill ontology mapper."""

from pathlib import Path

import pytest

from hiremind.domain.skill import Skill
from hiremind.infrastructure.candidate.skill_mapper import map_skills
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.services.ontology_service import OntologyService

_MINIMAL_ONTOLOGY = """\
categories:
  vector_databases:
    FAISS:
      aliases: ["facebook ai similarity search"]
      parents: ["vector_database", "retrieval"]
    Milvus:
      aliases: []
      parents: ["vector_database", "retrieval"]
  programming_languages:
    Python:
      aliases: ["python3", "py"]
      parents: ["programming"]

protected_terms:
  - FAISS
  - Python
"""


@pytest.fixture()
def ontology_service(tmp_path: Path) -> OntologyService:
    path = tmp_path / "ontology.yaml"
    path.write_text(_MINIMAL_ONTOLOGY, encoding="utf-8")
    loader = OntologyLoader(path).load()
    return OntologyService(loader)


def test_normalises_skills(ontology_service: OntologyService) -> None:
    """Skills are normalised to canonical names."""
    skills = [Skill(name="python3"), Skill(name="FAISS")]
    result = map_skills(skills, ontology_service)
    assert "Python" in result
    assert "FAISS" in result


def test_deduplicates(ontology_service: OntologyService) -> None:
    """Duplicate skills (via aliases) are deduplicated."""
    skills = [
        Skill(name="FAISS"),
        Skill(name="facebook ai similarity search"),
    ]
    result = map_skills(skills, ontology_service)
    assert result.count("FAISS") == 1


def test_unknown_skill_passthrough(ontology_service: OntologyService) -> None:
    """Unknown skills pass through as-is."""
    skills = [Skill(name="SomeUnknownTech")]
    result = map_skills(skills, ontology_service)
    assert "SomeUnknownTech" in result


def test_empty_skills(ontology_service: OntologyService) -> None:
    """Empty skill list returns empty result."""
    result = map_skills([], ontology_service)
    assert result == []


def test_result_is_sorted(ontology_service: OntologyService) -> None:
    """Result is sorted alphabetically."""
    skills = [Skill(name="Python"), Skill(name="FAISS"), Skill(name="Milvus")]
    result = map_skills(skills, ontology_service)
    assert result == sorted(result)
