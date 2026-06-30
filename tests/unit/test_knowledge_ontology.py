"""Unit tests for SkillOntology and OntologyConfigLoader."""

from pathlib import Path

import pytest

from hiremind.domain.ontology_models import SkillNode
from hiremind.knowledge.ontology import SkillOntology
from hiremind.knowledge.ontology_loader import OntologyConfigLoader


@pytest.fixture()
def sample_ontology_yaml(tmp_path: Path) -> Path:
    yaml_content = """
categories:
  programming_languages:
    Python:
      aliases: ["python3", "py"]
      parents: ["programming"]
    Go:
      aliases: ["golang"]
      parents: ["programming"]
  databases:
    SQL:
      aliases: []
      parents: ["databases"]

protected_terms:
  - Python
  - Go
"""
    path = tmp_path / "ontology.yaml"
    path.write_text(yaml_content, encoding="utf-8")
    return path


def test_ontology_config_loader(sample_ontology_yaml: Path) -> None:
    loader = OntologyConfigLoader(ontology_path=sample_ontology_yaml)
    skills = loader.load_skills()
    protected = loader.load_protected_terms()

    assert len(skills) == 3
    assert any(s.canonical_name == "Python" for s in skills)
    assert any(s.canonical_name == "Go" for s in skills)
    assert any(s.canonical_name == "SQL" for s in skills)
    assert "Python" in protected
    assert "Go" in protected
    assert "SQL" not in protected


def test_skill_ontology_resolution() -> None:
    skills = [
        SkillNode(
            canonical_name="Python",
            aliases=("python3", "py"),
            parents=("programming",),
            category="programming_languages",
        ),
        SkillNode(
            canonical_name="Go",
            aliases=("golang",),
            parents=("programming",),
            category="programming_languages",
        ),
    ]
    ontology = SkillOntology(skills, protected_terms=frozenset(["Python"]))

    # Test exact resolution
    assert ontology.canonical_name("Python") == "Python"
    assert ontology.canonical_name("py") == "Python"
    assert ontology.canonical_name("python3") == "Python"

    # Test case insensitivity
    assert ontology.canonical_name("go") == "Go"
    assert ontology.canonical_name("GOLANG") == "Go"

    # Test missing/unknown
    assert ontology.canonical_name("UnknownTech") is None

    # Test properties
    assert ontology.protected_terms == frozenset(["Python"])
    assert "Python" in ontology.all_canonical_names()
    assert "Go" in ontology.all_canonical_names()
    assert ontology.get_parents("Python") == ["programming"]
    assert ontology.get_aliases("Python") == ["python3", "py"]
    assert ontology.skill_data("Python") == {
        "aliases": ["python3", "py"],
        "parents": ["programming"],
        "category": "programming_languages",
    }
