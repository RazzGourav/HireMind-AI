"""JD Artifact Exporter — persists parsed requirements and graph to disk."""

import pickle
from pathlib import Path

import networkx as nx
import orjson

from hiremind.domain.requirement import ParsedRequirements


class JDExporter:
    """Save JD parsing artifacts to the artifacts directory.

    Produces:
        - ``jd_requirements.json`` — structured requirements (JSON)
        - ``jd_features.json``     — skill weights for the ranker (JSON)
        - ``jd_graph.pkl``         — networkx graph (pickle)
    """

    def __init__(self, artifacts_dir: str | Path = "artifacts") -> None:
        self._dir = Path(artifacts_dir)

    def export_all(
        self,
        requirements: ParsedRequirements,
        graph: nx.DiGraph,
    ) -> dict[str, Path]:
        """Export all artifacts and return a mapping of name→path."""
        self._dir.mkdir(parents=True, exist_ok=True)

        paths: dict[str, Path] = {}
        paths["requirements"] = self._export_requirements(requirements)
        paths["features"] = self._export_features(requirements)
        paths["graph"] = self._export_graph(graph)
        return paths

    def _export_requirements(self, requirements: ParsedRequirements) -> Path:
        """Write the full structured requirements JSON."""
        path = self._dir / "jd_requirements.json"
        path.write_bytes(orjson.dumps(requirements.to_dict(), option=orjson.OPT_INDENT_2))
        return path

    def _export_features(self, requirements: ParsedRequirements) -> Path:
        """Write a compact skill→weight mapping for the ranking pipeline."""
        features: dict[str, object] = {
            "required": {r.name: r.weight for r in requirements.required},
            "preferred": {r.name: r.weight for r in requirements.preferred},
            "negative": requirements.negative_names,
            "experience": {
                "min_years": requirements.experience.min_years,
                "max_years": requirements.experience.max_years,
                "preferred_years": requirements.experience.preferred_years,
            },
        }
        path = self._dir / "jd_features.json"
        path.write_bytes(orjson.dumps(features, option=orjson.OPT_INDENT_2))
        return path

    def _export_graph(self, graph: nx.DiGraph) -> Path:
        """Pickle the networkx graph for fast reload."""
        path = self._dir / "jd_graph.pkl"
        with path.open("wb") as f:
            pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
        return path
