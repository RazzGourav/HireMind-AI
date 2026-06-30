"""Graph Service — builds and queries a NetworkX requirement graph.

The graph encodes skill→category→concept relationships from the ontology,
enabling semantic reasoning beyond exact keyword matches.
"""

import networkx as nx

from hiremind.domain.requirement import ParsedRequirements
from hiremind.infrastructure.jd.ontology import OntologyLoader


class GraphService:
    """Build and query a directed skill knowledge graph.

    Nodes represent skills, categories, and abstract concepts.
    Edges encode ``is_a`` and ``part_of`` relationships.

    The graph is used by the ranking pipeline to compute semantic
    similarity between candidate skills and JD requirements.
    """

    def __init__(self, ontology_loader: OntologyLoader) -> None:
        self._loader = ontology_loader
        self._graph = nx.DiGraph()

    def build(self, requirements: ParsedRequirements | None = None) -> nx.DiGraph:
        """Build the full knowledge graph from the ontology and parsed requirements.

        Args:
            requirements: If provided, highlights requirement nodes in the graph.

        Returns:
            A ``networkx.DiGraph`` with skill→parent edges.
        """
        self._graph = nx.DiGraph()

        # Add all skills from the ontology.
        self._add_ontology_nodes()

        # Highlight requirement nodes if provided.
        if requirements is not None:
            self._mark_requirements(requirements)

        return self._graph

    def _add_ontology_nodes(self) -> None:
        """Add all skills and their parent edges from the ontology."""
        for skill_name in self._loader.all_canonical_names():
            self._graph.add_node(skill_name, node_type="skill")

            parents = self._loader.get_parents(skill_name)
            for parent in parents:
                # Ensure parent node exists (may be an abstract category).
                if not self._graph.has_node(parent):
                    self._graph.add_node(parent, node_type="category")

                self._graph.add_edge(skill_name, parent, relation="is_a")

    def _mark_requirements(self, requirements: ParsedRequirements) -> None:
        """Mark nodes that correspond to extracted requirements."""
        for req in requirements.required:
            if self._graph.has_node(req.name):
                self._graph.nodes[req.name]["requirement"] = "required"
                self._graph.nodes[req.name]["weight"] = req.weight

        for req in requirements.preferred:
            if self._graph.has_node(req.name):
                self._graph.nodes[req.name]["requirement"] = "preferred"
                self._graph.nodes[req.name]["weight"] = req.weight

        for neg in requirements.negative:
            if self._graph.has_node(neg.name):
                self._graph.nodes[neg.name]["requirement"] = "negative"

    @property
    def graph(self) -> nx.DiGraph:
        """Return the current graph instance."""
        return self._graph

    def ancestors(self, skill: str) -> list[str]:
        """Return all ancestors of a skill node (transitive parents).

        Since edges are directed skill→parent, ancestors follow outgoing edges.
        """
        if not self._graph.has_node(skill):
            return []
        # Edges go skill→parent, so following outgoing edges = going UP.
        return list(nx.descendants(self._graph, skill))

    def descendants(self, category: str) -> list[str]:
        """Return all descendants of a category node (skills below it).

        Since edges are directed skill→parent, descendants follow incoming edges.
        """
        if not self._graph.has_node(category):
            return []
        # Edges go skill→parent, so following incoming edges = going DOWN.
        return list(nx.ancestors(self._graph, category))

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        """Find the shortest path between two nodes, if one exists."""
        try:
            # Try in both directions since the graph is directed.
            return list(nx.shortest_path(self._graph.to_undirected(), source, target))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def node_count(self) -> int:
        """Total number of nodes in the graph."""
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        """Total number of edges in the graph."""
        return self._graph.number_of_edges()

    def requirement_nodes(self) -> dict[str, str]:
        """Return nodes marked as requirements with their type."""
        return {
            node: data.get("requirement", "")
            for node, data in self._graph.nodes(data=True)
            if "requirement" in data
        }
