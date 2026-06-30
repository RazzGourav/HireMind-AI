"""Tests for the weight engine in the parser service."""

from pathlib import Path

import pytest

from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.infrastructure.jd.parser import JDParser
from hiremind.services.ontology_service import OntologyService
from hiremind.services.parser_service import ParserService

_MINIMAL_ONTOLOGY = """\
categories:
  programming_languages:
    Python:
      aliases: ["python3"]
      parents: ["programming"]
  embeddings_and_retrieval:
    Retrieval:
      aliases: ["information retrieval"]
      parents: ["nlp"]
    Embeddings:
      aliases: ["text embeddings"]
      parents: ["nlp"]
  llm_and_finetuning:
    LoRA:
      aliases: ["lora"]
      parents: ["fine_tuning", "llm"]

protected_terms:
  - Python
  - LoRA
"""


@pytest.fixture()
def ontology_path(tmp_path: Path) -> Path:
    path = tmp_path / "ontology.yaml"
    path.write_text(_MINIMAL_ONTOLOGY, encoding="utf-8")
    return path


@pytest.fixture()
def parser_service(ontology_path: Path) -> ParserService:
    loader = OntologyLoader(ontology_path).load()
    ontology_service = OntologyService(loader)
    jd_parser = JDParser(
        known_skills=loader.all_canonical_names(),
        skill_aliases={s: loader.get_aliases(s) for s in loader.all_canonical_names()},
    )
    return ParserService(parser=jd_parser, ontology_service=ontology_service)


def test_required_skills_get_high_weight(parser_service: ParserService) -> None:
    """Required skills receive weight >= 0.8 from the default weight table."""
    text = "Must Have:\n- Python\n- Retrieval\n- Embeddings\n"
    result = parser_service.parse_and_enrich(text)

    for req in result.required:
        if req.name in ("Python", "Retrieval", "Embeddings"):
            assert req.weight >= 0.8, f"{req.name} weight={req.weight} should be >= 0.8"


def test_preferred_skills_get_lower_weight(parser_service: ParserService) -> None:
    """Preferred skills receive weight <= 0.6 from the default weight table."""
    text = "Must Have:\n- Python\n\nNice to Have:\n- LoRA\n"
    result = parser_service.parse_and_enrich(text)

    for req in result.preferred:
        if req.name == "LoRA":
            assert req.weight <= 0.6, f"LoRA weight={req.weight} should be <= 0.6"


def test_custom_weight_overrides() -> None:
    """Custom weight overrides are applied during enrichment."""
    ontology_yaml = (
        "categories:\n"
        "  programming_languages:\n"
        "    Python:\n"
        "      aliases: []\n"
        "      parents: []\n"
        "protected_terms: []\n"
    )
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(ontology_yaml)
        f.flush()
        loader = OntologyLoader(f.name).load()

    ontology_service = OntologyService(loader)
    jd_parser = JDParser()
    service = ParserService(
        parser=jd_parser,
        ontology_service=ontology_service,
        weight_overrides={"Python": 0.42},
    )

    text = "Must Have:\n- Python\n"
    result = service.parse_and_enrich(text)

    python_reqs = [r for r in result.required if r.name == "Python"]
    assert len(python_reqs) == 1
    assert python_reqs[0].weight == 0.42


def test_enrichment_adds_aliases(parser_service: ParserService) -> None:
    """Enrichment populates aliases from the ontology."""
    text = "Must Have:\n- Python\n"
    result = parser_service.parse_and_enrich(text)

    python_reqs = [r for r in result.required if r.name == "Python"]
    assert len(python_reqs) == 1
    assert "python3" in python_reqs[0].aliases
