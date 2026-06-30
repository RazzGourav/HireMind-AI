"""JD Service — orchestrates the full Job Intelligence Engine pipeline.

Pipeline:  Load → Clean → Parse → Enrich → Build Graph → Export
"""

from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from hiremind.domain.jd import JobDescription
from hiremind.domain.requirement import ParsedRequirements
from hiremind.infrastructure.jd.exporter import JDExporter
from hiremind.infrastructure.jd.loader import JDLoader
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.infrastructure.jd.parser import JDParser
from hiremind.services.graph_service import GraphService
from hiremind.services.ontology_service import OntologyService
from hiremind.services.parser_service import ParserService


@dataclass(frozen=True, slots=True)
class JDProcessResult:
    """Summary of the JD processing pipeline output."""

    jd: JobDescription
    requirements: ParsedRequirements
    graph: nx.DiGraph
    artifact_paths: dict[str, Path]
    required_count: int
    preferred_count: int
    negative_count: int
    node_count: int
    edge_count: int


class JDService:
    """Orchestrate the full JD Intelligence Engine pipeline.

    Usage::

        service = JDService(
            jd_path="Dataset/job_description.docx",
            ontology_path="configs/ontology.yaml",
            artifacts_dir="artifacts",
        )
        result = service.process()
    """

    def __init__(
        self,
        jd_path: str | Path = "Dataset/job_description.docx",
        ontology_path: str | Path = "configs/ontology.yaml",
        artifacts_dir: str | Path = "artifacts",
        weight_overrides: dict[str, float] | None = None,
    ) -> None:
        self._jd_path = Path(jd_path)
        self._ontology_path = Path(ontology_path)
        self._artifacts_dir = Path(artifacts_dir)
        self._weight_overrides = weight_overrides

    def process(self) -> JDProcessResult:
        """Run the full pipeline: load → parse → graph → export.

        Returns:
            A ``JDProcessResult`` with all outputs and summary stats.
        """
        # 1. Load & clean the JD document.
        loader = JDLoader()
        jd = loader.load(self._jd_path)

        # 2. Load the skill ontology.
        ontology_loader = OntologyLoader(self._ontology_path).load()
        ontology_service = OntologyService(ontology_loader)

        # 3. Build the parser with ontology knowledge.
        known_skills = ontology_loader.all_canonical_names()
        alias_map: dict[str, list[str]] = {
            skill: ontology_loader.get_aliases(skill) for skill in known_skills
        }
        jd_parser = JDParser(known_skills=known_skills, skill_aliases=alias_map)

        # 4. Parse & enrich requirements.
        parser_service = ParserService(
            parser=jd_parser,
            ontology_service=ontology_service,
            weight_overrides=self._weight_overrides,
        )
        requirements = parser_service.parse_and_enrich(jd.cleaned_text)

        # 5. Build the requirement graph.
        graph_service = GraphService(ontology_loader)
        graph = graph_service.build(requirements)

        # 6. Export artifacts.
        exporter = JDExporter(self._artifacts_dir)
        artifact_paths = exporter.export_all(requirements, graph)

        return JDProcessResult(
            jd=jd,
            requirements=requirements,
            graph=graph,
            artifact_paths=artifact_paths,
            required_count=len(requirements.required),
            preferred_count=len(requirements.preferred),
            negative_count=len(requirements.negative),
            node_count=graph_service.node_count(),
            edge_count=graph_service.edge_count(),
        )
