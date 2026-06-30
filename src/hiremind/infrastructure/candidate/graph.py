"""Candidate Knowledge Graph — builds per-candidate graph with NetworkX."""

import networkx as nx

from hiremind.domain.candidate import Candidate
from hiremind.services.ontology_service import OntologyService


def build_candidate_graph(
    candidate: Candidate,
    ontology_service: OntologyService,
) -> nx.DiGraph:
    """Build a knowledge graph for a single candidate.

    Nodes: candidate, skills, companies, industries, technologies.
    Edges: has_skill, worked_at, in_industry, is_a (from ontology).
    """
    g = nx.DiGraph()
    cid = candidate.candidate_id

    # Central candidate node.
    g.add_node(cid, node_type="candidate")

    # Skills.
    for skill in candidate.skills:
        canonical = ontology_service.normalize_skill(skill.name)
        if not g.has_node(canonical):
            g.add_node(canonical, node_type="skill")
        g.add_edge(cid, canonical, relation="has_skill")

        # Add ontology parents.
        for parent in ontology_service.get_ancestors(canonical):
            if not g.has_node(parent):
                g.add_node(parent, node_type="category")
            g.add_edge(canonical, parent, relation="is_a")

    # Companies.
    for job in candidate.career_history:
        if job.company:
            company = job.company
            if not g.has_node(company):
                g.add_node(company, node_type="company")
            g.add_edge(cid, company, relation="worked_at")

            # Industry.
            if job.industry:
                industry = job.industry
                if not g.has_node(industry):
                    g.add_node(industry, node_type="industry")
                g.add_edge(company, industry, relation="in_industry")

    return g
