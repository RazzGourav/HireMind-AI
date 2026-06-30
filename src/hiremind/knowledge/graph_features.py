"""Graph Feature Extractor — extracts candidate graph features."""

import networkx as nx

from hiremind.domain.ontology_models import GraphFeatures
from hiremind.knowledge.domain_graph import DomainGraph
from hiremind.knowledge.ontology import SkillOntology
from hiremind.knowledge.technology_graph import TechnologyGraph


class GraphFeatureExtractor:
    """Computes graph-based features for a candidate's skill profile."""

    def __init__(
        self,
        tech_graph: TechnologyGraph,
        domain_graph: DomainGraph,
        ontology: SkillOntology,
    ) -> None:
        self.tech_graph = tech_graph
        self.domain_graph = domain_graph
        self.ontology = ontology

    def extract(self, normalized_skills: list[str]) -> GraphFeatures:
        """Extract GraphFeatures for a candidate's normalised skills list."""
        if not normalized_skills:
            return GraphFeatures()

        skills = [s for s in normalized_skills if self.tech_graph.graph.has_node(s)]

        # 1. Technology Diversity: number of unique categories of candidate skills
        categories = set()
        for s in skills:
            skill_node = self.ontology.get_skill(s)
            if skill_node and skill_node.category:
                categories.add(skill_node.category)
        tech_div = float(len(categories))

        # 2. Subtree Depths (max path length to root nodes in tech graph)
        # We traverse the directed graph skill -> parent
        ai_depth = self._max_depth(skills, "ai")
        # For backend, we check "programming" or "databases" or "backend_engineer"
        backend_depth = max(
            self._max_depth(skills, "programming"), self._max_depth(skills, "databases")
        )
        cloud_depth = self._max_depth(skills, "cloud")
        retrieval_depth = max(
            self._max_depth(skills, "retrieval"), self._max_depth(skills, "embeddings")
        )

        # 3. Domain Breadth: number of unique business domains candidate has skills in
        candidate_domains = set()
        for s in skills:
            candidate_domains.update(self.domain_graph.domains_for_skill(s))
        domain_breadth = float(len(candidate_domains))

        # 4. Graph Connectivity: density of candidate's induced skill subgraph
        connectivity = 0.0
        if len(skills) > 1:
            try:
                # Get induced subgraph in undirected technology graph to capture connectivity
                subg = self.tech_graph.graph.to_undirected().subgraph(skills)
                connectivity = nx.density(subg)
            except Exception:
                pass

        return GraphFeatures(
            technology_diversity=tech_div,
            ai_depth=float(ai_depth),
            backend_depth=float(backend_depth),
            cloud_depth=float(cloud_depth),
            retrieval_depth=float(retrieval_depth),
            domain_breadth=domain_breadth,
            graph_connectivity=round(connectivity, 4),
        )

    def _max_depth(self, skills: list[str], root_node: str) -> int:
        """Find max path length from any skill to root_node in tech graph."""
        if not self.tech_graph.graph.has_node(root_node):
            return 0

        max_d = 0
        g = self.tech_graph.graph
        for s in skills:
            # We want to find the shortest path from skill s to root_node
            # in directed graph where edges go skill -> parent
            try:
                if nx.has_path(g, s, root_node):
                    path = nx.shortest_path(g, s, root_node)
                    # Length of path (number of hops)
                    depth = len(path) - 1
                    max_d = max(max_d, depth)
            except nx.NodeNotFound:
                continue
        return max_d
