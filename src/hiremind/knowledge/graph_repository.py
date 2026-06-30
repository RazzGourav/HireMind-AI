"""Graph Repository — caches all constructed graphs as pickle files."""

import pickle
from pathlib import Path
from typing import Any


class GraphRepository:
    """Save and load cached ontology and graph structures to/from artifacts."""

    def __init__(self, artifacts_dir: str | Path = "artifacts") -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    @property
    def ontology_cache_path(self) -> Path:
        return self.artifacts_dir / "ontology.pkl"

    @property
    def tech_graph_cache_path(self) -> Path:
        return self.artifacts_dir / "knowledge_graph.pkl"

    @property
    def domain_graph_cache_path(self) -> Path:
        return self.artifacts_dir / "domain_graph.pkl"

    def save_ontology(self, ontology: Any) -> None:
        """Cache the SkillOntology instance."""
        with self.ontology_cache_path.open("wb") as f:
            pickle.dump(ontology, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_ontology(self) -> Any:
        """Load the cached SkillOntology instance."""
        with self.ontology_cache_path.open("rb") as f:
            return pickle.load(f)  # noqa: S301

    def save_tech_graph(self, tech_graph: Any) -> None:
        """Cache the TechnologyGraph or NetworkX graph instance."""
        with self.tech_graph_cache_path.open("wb") as f:
            pickle.dump(tech_graph, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_tech_graph(self) -> Any:
        """Load the cached TechnologyGraph or NetworkX graph instance."""
        with self.tech_graph_cache_path.open("rb") as f:
            return pickle.load(f)  # noqa: S301

    def save_domain_graph(self, domain_graph: Any) -> None:
        """Cache the DomainGraph instance."""
        with self.domain_graph_cache_path.open("wb") as f:
            pickle.dump(domain_graph, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_domain_graph(self) -> Any:
        """Load the cached DomainGraph instance."""
        with self.domain_graph_cache_path.open("rb") as f:
            return pickle.load(f)  # noqa: S301

    def clear_cache(self) -> None:
        """Remove all cached files."""
        for path in (
            self.ontology_cache_path,
            self.tech_graph_cache_path,
            self.domain_graph_cache_path,
        ):
            if path.exists():
                path.unlink()
