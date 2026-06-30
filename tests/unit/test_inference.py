"""Unit tests for the InferenceEngine and GraphFeatureExtractor."""

import pytest

from hiremind.domain.ontology_models import DomainNode, SkillNode, TechRelation
from hiremind.knowledge.domain_graph import DomainGraph
from hiremind.knowledge.graph_builder import GraphBuilder
from hiremind.knowledge.graph_features import GraphFeatureExtractor
from hiremind.knowledge.inference_engine import InferenceEngine
from hiremind.knowledge.normalization import SkillNormalizer
from hiremind.knowledge.ontology import SkillOntology
from hiremind.knowledge.technology_graph import TechnologyGraph


@pytest.fixture()
def inference_setup() -> tuple[InferenceEngine, GraphFeatureExtractor, SkillOntology]:
    skills = [
        # AI/ML hierarchy
        SkillNode(canonical_name="ai", aliases=(), parents=(), category="concepts"),
        SkillNode(canonical_name="ml", aliases=(), parents=("ai",), category="concepts"),
        SkillNode(canonical_name="deep_learning", aliases=(), parents=("ml",), category="concepts"),
        SkillNode(
            canonical_name="PyTorch",
            aliases=(),
            parents=("deep_learning",),
            category="ml_frameworks",
        ),
        SkillNode(
            canonical_name="FAISS",
            aliases=(),
            parents=("vector_databases",),
            category="vector_databases",
        ),
        SkillNode(
            canonical_name="vector_databases",
            aliases=(),
            parents=("retrieval",),
            category="concepts",
        ),
        SkillNode(canonical_name="retrieval", aliases=(), parents=("ai",), category="concepts"),
        # Programming/Backend
        SkillNode(
            canonical_name="Python",
            aliases=(),
            parents=("programming",),
            category="programming_languages",
        ),
        SkillNode(canonical_name="programming", aliases=(), parents=(), category="concepts"),
        SkillNode(canonical_name="databases", aliases=(), parents=(), category="concepts"),
    ]
    ontology = SkillOntology(skills)
    relations = [
        TechRelation(source="PyTorch", target="Python", relation_type="USES"),
        TechRelation(source="FAISS", target="retrieval", relation_type="DEPENDS_ON"),
    ]
    g = GraphBuilder(ontology, relations).build()
    tech_graph = TechnologyGraph(g)

    domains = [
        DomainNode(name="finance", label="Finance", skills=("Python", "PyTorch"), subdomains=()),
    ]
    domain_graph = DomainGraph(domains, ontology)

    normalizer = SkillNormalizer(ontology)
    engine = InferenceEngine(normalizer, tech_graph, domain_graph)
    extractor = GraphFeatureExtractor(tech_graph, domain_graph, ontology)

    return engine, extractor, ontology


def test_inference_capabilities(
    inference_setup: tuple[InferenceEngine, GraphFeatureExtractor, SkillOntology],
) -> None:
    engine, _, _ = inference_setup

    # Inputting PyTorch
    inferred = engine.infer_capabilities(["PyTorch"])

    # Should infer canonical: PyTorch, deep_learning, ml, ai (ancestors)
    # Python (uses)
    # finance (domain)
    assert "PyTorch" in inferred
    assert "deep_learning" in inferred
    assert "ml" in inferred
    assert "ai" in inferred
    assert "Python" in inferred
    assert "finance" in inferred


def test_graph_feature_extraction(
    inference_setup: tuple[InferenceEngine, GraphFeatureExtractor, SkillOntology],
) -> None:
    _, extractor, _ = inference_setup

    # Candidate with PyTorch and Python
    features = extractor.extract(["PyTorch", "Python"])

    # 1. Tech diversity (programming_languages, ml_frameworks) -> 2
    assert features.technology_diversity == 2.0

    # 2. AI depth: PyTorch -> deep_learning -> ml -> ai (depth 3)
    assert features.ai_depth == 3.0

    # 3. Backend depth: PyTorch -> Python -> programming (depth 2)
    assert features.backend_depth == 2.0

    # 4. Domain breadth: PyTorch & Python are in "finance" domain -> 1
    assert features.domain_breadth == 1.0
