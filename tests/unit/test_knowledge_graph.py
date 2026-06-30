"""Unit tests for GraphBuilder, TechnologyGraph, and DomainGraph."""

import pytest

from hiremind.domain.ontology_models import DomainNode, SkillNode, TechRelation
from hiremind.knowledge.domain_graph import DomainGraph
from hiremind.knowledge.graph_builder import GraphBuilder
from hiremind.knowledge.ontology import SkillOntology
from hiremind.knowledge.technology_graph import TechnologyGraph


@pytest.fixture()
def sample_ontology() -> SkillOntology:
    skills = [
        SkillNode(
            canonical_name="Python",
            aliases=(),
            parents=("programming",),
            category="programming_languages",
        ),
        SkillNode(
            canonical_name="FastAPI", aliases=(), parents=("frameworks",), category="web_frameworks"
        ),
        SkillNode(
            canonical_name="Flask", aliases=(), parents=("frameworks",), category="web_frameworks"
        ),
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
    ]
    return SkillOntology(skills)


def test_technology_graph_builder_and_queries(sample_ontology: SkillOntology) -> None:
    relations = [
        TechRelation(source="FastAPI", target="Python", relation_type="USES"),
        TechRelation(source="FastAPI", target="Flask", relation_type="ALTERNATIVE_TO"),
    ]
    builder = GraphBuilder(sample_ontology, relations)
    g = builder.build()

    tech_graph = TechnologyGraph(g)

    # Test nodes and types
    assert g.has_node("Python")
    assert g.nodes["Python"].get("node_type") == "skill"
    assert g.has_node("programming")
    assert g.nodes["programming"].get("node_type") == "category"

    # Test USES query
    assert "Python" in tech_graph.uses("FastAPI")

    # Test ALTERNATIVE_TO query (bidirectional fallback in query layer)
    assert "Flask" in tech_graph.alternatives("FastAPI")
    assert "FastAPI" in tech_graph.alternatives("Flask")

    # Test ancestors (IS_A edges)
    # FastAPI -> frameworks -> web_frameworks...
    assert "frameworks" in tech_graph.ancestors("FastAPI")

    # Test shortest path
    path = tech_graph.shortest_path("FastAPI", "Python")
    assert path is not None
    assert path[0] == "FastAPI"
    assert path[-1] == "Python"


def test_domain_graph_queries(sample_ontology: SkillOntology) -> None:
    domains = [
        DomainNode(
            name="finance", label="Finance", skills=("Python", "PyTorch"), subdomains=("fintech",)
        ),
        DomainNode(name="fintech", label="FinTech", skills=("FastAPI",), subdomains=()),
    ]
    dg = DomainGraph(domains, sample_ontology)

    # Test skills_in_domain (with subdomains)
    finance_skills = dg.skills_in_domain("finance", include_subdomains=True)
    assert "Python" in finance_skills
    assert "PyTorch" in finance_skills
    assert "FastAPI" in finance_skills  # From subdomain fintech

    # Test skills_in_domain (without subdomains)
    finance_only_skills = dg.skills_in_domain("finance", include_subdomains=False)
    assert "FastAPI" not in finance_only_skills

    # Test domains_for_skill
    domains_for_fastapi = dg.domains_for_skill("FastAPI")
    assert "fintech" in domains_for_fastapi
    assert "finance" in domains_for_fastapi  # finance is parent of fintech

    # Test domain overlap (Jaccard similarity)
    overlap = dg.domain_overlap("finance", "fintech")
    # finance skills = {Python, PyTorch, FastAPI}
    # fintech skills = {FastAPI}
    # intersection = {FastAPI} (size 1), union = {Python, PyTorch, FastAPI} (size 3)
    # overlap = 1/3 = 0.3333
    assert abs(overlap - 0.3333) < 0.01
