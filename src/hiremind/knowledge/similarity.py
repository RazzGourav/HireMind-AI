"""Skill Similarity Engine — computes pairwise skill similarity from the graph."""

import networkx as nx
import pandas as pd

from hiremind.knowledge.ontology import SkillOntology
from hiremind.knowledge.technology_graph import TechnologyGraph


class SkillSimilarityEngine:
    """Computes and queries semantic similarity between skills based on graph distance."""

    def __init__(self, tech_graph: TechnologyGraph, ontology: SkillOntology) -> None:
        self.tech_graph = tech_graph
        self.ontology = ontology
        self._matrix: pd.DataFrame | None = None
        self._similarity_cache: dict[tuple[str, str], float] = {}

    def compute_matrix(self) -> pd.DataFrame:
        """Precompute the pairwise similarity matrix for all canonical skills in ontology."""
        skills = sorted(self.ontology.all_canonical_names())
        matrix_data = {s: [0.0] * len(skills) for s in skills}
        df = pd.DataFrame(matrix_data, index=skills)

        # Build undirected graph once for speed
        undirected_g = self.tech_graph.graph.to_undirected()

        for i, skill_a in enumerate(skills):
            df.at[skill_a, skill_a] = 1.0
            self._similarity_cache[(skill_a, skill_a)] = 1.0

            # Compute shortest paths from skill_a to all other reachable nodes
            try:
                paths = nx.single_source_shortest_path_length(undirected_g, skill_a)
                for skill_b in skills[i + 1 :]:
                    if skill_b in paths:
                        dist = paths[skill_b]
                        sim = round(1.0 / (1.0 + dist), 4)
                    else:
                        sim = 0.0

                    df.at[skill_a, skill_b] = sim
                    df.at[skill_b, skill_a] = sim
                    self._similarity_cache[(skill_a, skill_b)] = sim
                    self._similarity_cache[(skill_b, skill_a)] = sim
            except nx.NodeNotFound:
                # Node not in graph, keep similarity at 0.0
                for skill_b in skills[i + 1 :]:
                    self._similarity_cache[(skill_a, skill_b)] = 0.0
                    self._similarity_cache[(skill_b, skill_a)] = 0.0

        self._matrix = df
        return df

    def save_matrix(self, path: str = "artifacts/skill_similarity_matrix.parquet") -> None:
        """Save the precomputed matrix to a Parquet file."""
        if self._matrix is None:
            self.compute_matrix()
        assert self._matrix is not None
        self._matrix.to_parquet(path)

    def load_matrix(self, path: str = "artifacts/skill_similarity_matrix.parquet") -> None:
        """Load precomputed similarity matrix from Parquet file."""
        self._matrix = pd.read_parquet(path)
        # Populate cache from matrix
        skills = self._matrix.columns
        for skill_a in skills:
            for skill_b in skills:
                self._similarity_cache[(skill_a, skill_b)] = float(
                    self._matrix.at[skill_a, skill_b]
                )

    def similarity(self, skill_a: str, skill_b: str) -> float:
        """Query similarity between two skills. Falls back to dynamic graph lookup."""
        canonical_a = self.ontology.canonical_name(skill_a) or skill_a
        canonical_b = self.ontology.canonical_name(skill_b) or skill_b

        if canonical_a == canonical_b:
            return 1.0

        # Try cache
        key = (canonical_a, canonical_b)
        if key in self._similarity_cache:
            return self._similarity_cache[key]

        # Dynamic graph distance fallback (e.g. for skills not precomputed or newly added)
        path = self.tech_graph.shortest_path(canonical_a, canonical_b)
        if path:
            dist = len(path) - 1
            sim = round(1.0 / (1.0 + dist), 4)
        else:
            sim = 0.0

        self._similarity_cache[key] = sim
        self._similarity_cache[(canonical_b, canonical_a)] = sim
        return sim
