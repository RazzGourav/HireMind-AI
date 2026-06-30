"""Unit tests for the SkillSimilarityEngine."""

from pathlib import Path

import pytest

from hiremind.domain.ontology_models import SkillNode, TechRelation
from hiremind.knowledge.graph_builder import GraphBuilder
from hiremind.knowledge.ontology import SkillOntology
from hiremind.knowledge.similarity import SkillSimilarityEngine
from hiremind.knowledge.technology_graph import TechnologyGraph


@pytest.fixture()
def similarity_engine() -> SkillSimilarityEngine:
    skills = [
        SkillNode(
            canonical_name="FAISS",
            aliases=(),
            parents=("vector_databases",),
            category="vector_databases",
        ),
        SkillNode(
            canonical_name="Milvus",
            aliases=(),
            parents=("vector_databases",),
            category="vector_databases",
        ),
        SkillNode(
            canonical_name="Python",
            aliases=(),
            parents=("programming",),
            category="programming_languages",
        ),
    ]
    ontology = SkillOntology(skills)
    relations = [
        TechRelation(source="FAISS", target="Milvus", relation_type="ALTERNATIVE_TO"),
    ]
    g = GraphBuilder(ontology, relations).build()
    tech_graph = TechnologyGraph(g)
    return SkillSimilarityEngine(tech_graph, ontology)


def test_similarity_computation(similarity_engine: SkillSimilarityEngine) -> None:
    # Compute similarity matrix
    df = similarity_engine.compute_matrix()

    assert df.at["FAISS", "FAISS"] == 1.0
    # FAISS and Milvus are alternative_to each other, distance = 1.
    # similarity = 1.0 / (1.0 + 1) = 0.5
    assert df.at["FAISS", "Milvus"] == 0.5

    # FAISS and Python have no path between them, similarity = 0.0
    assert df.at["FAISS", "Python"] == 0.0


def test_similarity_saving_and_loading(
    similarity_engine: SkillSimilarityEngine, tmp_path: Path
) -> None:
    path = tmp_path / "skill_similarity_matrix.parquet"

    # Precompute and save
    similarity_engine.save_matrix(str(path))
    assert path.exists()

    # Load matrix back in a new engine
    new_engine = SkillSimilarityEngine(similarity_engine.tech_graph, similarity_engine.ontology)
    new_engine.load_matrix(str(path))

    assert new_engine.similarity("FAISS", "Milvus") == 0.5
    assert new_engine.similarity("FAISS", "Python") == 0.0
    assert new_engine.similarity("FAISS", "FAISS") == 1.0
