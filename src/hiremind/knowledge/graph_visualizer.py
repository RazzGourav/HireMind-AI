"""Graph Visualizer — Generates visual representations of the knowledge graph."""

from pathlib import Path

import networkx as nx


class GraphVisualizer:
    """Generates and saves visual PNG representations of the technology knowledge graph."""

    def __init__(self, graph: nx.DiGraph) -> None:
        self.graph = graph

    def visualize(self, output_path: str = "docs/images/knowledge_graph.png") -> Path:
        """Draw and save the graph as a PNG image, color-coding nodes by node_type."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            import matplotlib

            matplotlib.use("Agg")  # Non-interactive headless backend
            import matplotlib.pyplot as plt

            plt.figure(figsize=(16, 12))

            # Color coding nodes based on node_type
            color_map = []
            for node, data in self.graph.nodes(data=True):
                node_type = data.get("node_type", "concept")
                if node_type == "skill":
                    color_map.append("#3498db")  # Blue
                elif node_type == "category":
                    color_map.append("#2ecc71")  # Green
                elif node_type == "domain":
                    color_map.append("#e67e22")  # Orange
                elif node_type == "subdomain":
                    color_map.append("#f1c40f")  # Yellow
                else:
                    color_map.append("#95a5a6")  # Grey

            # Limit the number of nodes drawn if the graph is too dense
            # Draw up to 100 nodes for a clean visualization
            g_to_draw = self.graph
            if self.graph.number_of_nodes() > 100:
                # Get high centrality nodes or sample them
                degrees = dict(self.graph.degree())
                top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:100]
                g_to_draw = self.graph.subgraph(top_nodes)

                # Recompute color map for subgraph
                color_map = []
                for node, data in g_to_draw.nodes(data=True):
                    node_type = data.get("node_type", "concept")
                    if node_type == "skill":
                        color_map.append("#3498db")
                    elif node_type == "category":
                        color_map.append("#2ecc71")
                    elif node_type == "domain":
                        color_map.append("#e67e22")
                    elif node_type == "subdomain":
                        color_map.append("#f1c40f")
                    else:
                        color_map.append("#95a5a6")

            # Compute layout
            pos = nx.spring_layout(g_to_draw, k=0.15, iterations=20)

            # Draw nodes, edges, labels
            nx.draw_networkx_nodes(g_to_draw, pos, node_size=600, node_color=color_map, alpha=0.85)
            nx.draw_networkx_labels(
                g_to_draw, pos, font_size=8, font_family="sans-serif", font_weight="bold"
            )

            # Draw edges with different styles/colors based on relation types
            edge_colors = []
            for u, v in g_to_draw.edges():
                rel = g_to_draw[u][v].get("relation", "RELATED_TO")
                if rel == "IS_A":
                    edge_colors.append("#2c3e50")
                elif rel in ("USES", "DEPENDS_ON"):
                    edge_colors.append("#e74c3c")
                else:
                    edge_colors.append("#bdc3c7")

            nx.draw_networkx_edges(
                g_to_draw,
                pos,
                arrowstyle="-|>",
                arrowsize=10,
                edge_color=edge_colors,
                width=1.0,
                alpha=0.6,
            )

            plt.title(
                "HireMind technology Knowledge Graph (Sub-Sample)", fontsize=14, fontweight="bold"
            )
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(out_file, dpi=150, bbox_inches="tight")
            plt.close()
        except ImportError:
            # If matplotlib or networkx drawing modules fail, write a placeholder/warning text file or pass
            placeholder_path = out_file.with_suffix(".txt")
            placeholder_path.write_text(
                "Graph visualization is unavailable because matplotlib is not installed.",
                encoding="utf-8",
            )

        return out_file
