"""Unit tests for the SynonymEngine."""

from hiremind.domain.ontology_models import SynonymGroup
from hiremind.knowledge.synonym_engine import SynonymEngine


def test_synonym_engine_resolution() -> None:
    groups = [
        SynonymGroup(
            canonical="Sentence Transformers",
            terms=("Sentence Transformers", "SBERT", "sentence-transformers"),
        ),
        SynonymGroup(
            canonical="Vector Search",
            terms=("Vector Search", "ANN Search", "Approximate Nearest Neighbor"),
        ),
    ]
    engine = SynonymEngine(groups)

    # Test resolving canonical
    assert engine.resolve("SBERT") == "Sentence Transformers"
    assert engine.resolve("sentence-transformers") == "Sentence Transformers"
    assert engine.resolve("Sentence Transformers") == "Sentence Transformers"

    # Test resolving case-insensitivity
    assert engine.resolve("sbert") == "Sentence Transformers"

    # Test resolving unmapped term (should return the term itself)
    assert engine.resolve("PyTorch") == "PyTorch"


def test_synonym_engine_are_synonyms() -> None:
    groups = [
        SynonymGroup(
            canonical="Sentence Transformers",
            terms=("Sentence Transformers", "SBERT", "sentence-transformers"),
        ),
    ]
    engine = SynonymEngine(groups)

    assert engine.are_synonyms("SBERT", "sentence-transformers") is True
    assert engine.are_synonyms("sbert", "Sentence Transformers") is True
    assert engine.are_synonyms("PyTorch", "torch") is False
    assert engine.are_synonyms("PyTorch", "PyTorch") is True


def test_synonym_engine_all_synonyms() -> None:
    groups = [
        SynonymGroup(
            canonical="Sentence Transformers",
            terms=("Sentence Transformers", "SBERT", "sentence-transformers"),
        ),
    ]
    engine = SynonymEngine(groups)

    syns = engine.all_synonyms("SBERT")
    assert "sbert" in syns
    assert "sentence transformers" in syns

    # Unmapped term returns set containing itself
    assert engine.all_synonyms("PyTorch") == {"pytorch"}
