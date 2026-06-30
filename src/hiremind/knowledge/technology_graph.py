"""Technology Graph — Query interface for technology knowledge graph."""

import networkx as nx


class TechnologyGraph:
    """Wraps a NetworkX DiGraph representing technology relationships and ontology hierarchy."""

    def __init__(self, graph: nx.DiGraph) -> None:
        self._graph = graph

    @property
    def graph(self) -> nx.DiGraph:
        """Return the raw DiGraph."""
        return self._graph

    def uses(self, skill: str) -> list[str]:
        """Find technologies that this skill uses."""
        return self._find_targets_by_relation(skill, "USES")

    def depends_on(self, skill: str) -> list[str]:
        """Find technologies that this skill depends on."""
        return self._find_targets_by_relation(skill, "DEPENDS_ON")

    def alternatives(self, skill: str) -> list[str]:
        """Find alternative technologies to this skill."""
        return self._find_targets_by_relation(skill, "ALTERNATIVE_TO")

    def related(self, skill: str) -> list[str]:
        """Find related technologies/concepts."""
        return self._find_targets_by_relation(skill, "RELATED_TO")

    def ancestors(self, node: str) -> list[str]:
        """Find all ancestors (transitive parents) via IS_A relations."""
        if not self._graph.has_node(node):
            return []
        # Filter graph to only contain IS_A or PARENT_OF edges for hierarchy ancestors
        # Or traverse using nx.descendants on DiGraph since IS_A goes skill -> parent
        # Let's write a simple BFS/DFS or use a subgraph containing hierarchy edges
        hierarchy_sub = nx.subgraph_view(
            self._graph,
            filter_edge=lambda u, v: self._graph[u][v].get("relation") in ("IS_A", "PARENT_OF"),
        )
        return list(nx.descendants(hierarchy_sub, node))

    def descendants(self, node: str) -> list[str]:
        """Find all descendants (transitive children) via CHILD_OF / reverse IS_A relations."""
        if not self._graph.has_node(node):
            return []
        # Following CHILD_OF edges
        hierarchy_sub = nx.subgraph_view(
            self._graph,
            filter_edge=lambda u, v: self._graph[u][v].get("relation") in ("CHILD_OF", "CHILD_OF"),
        )
        # Note: If IS_A goes from child -> parent, then descendants follow reverse edges,
        # which in hierarchy_sub with CHILD_OF goes parent -> child.
        return list(nx.descendants(hierarchy_sub, node))

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        """Find the shortest path between two nodes, ignoring edge direction."""
        if not self._graph.has_node(source) or not self._graph.has_node(target):
            return None
        try:
            return list(nx.shortest_path(self._graph.to_undirected(), source, target))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def _find_targets_by_relation(self, source: str, relation_type: str) -> list[str]:
        """Helper to find target nodes starting from source with a given relation type."""
        if not self._graph.has_node(source):
            return []
        targets = []
        # Look at outgoing edges
        for target, edge_data in self._graph[source].items():
            if edge_data.get("relation") == relation_type:
                targets.append(target)
        # For symmetric relations (like ALTERNATIVE_TO or RELATED_TO), also look at incoming edges
        if relation_type in ("ALTERNATIVE_TO", "RELATED_TO"):
            for predecessor in self._graph.predecessors(source):
                edge_data = self._graph[predecessor][source]
                if edge_data.get("relation") == relation_type:
                    if predecessor not in targets:
                        targets.append(predecessor)
        return targets
