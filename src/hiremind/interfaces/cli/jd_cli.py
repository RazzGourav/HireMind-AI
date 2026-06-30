"""CLI entrypoint for the JD Intelligence Engine pipeline."""

from pathlib import Path

from omegaconf import DictConfig

from hiremind.infrastructure import load_config, logger
from hiremind.services.jd_service import JDService


def main() -> None:
    """Run the full JD parsing pipeline from config."""
    config = load_config()
    jd_config = config.get("jd", {})
    service = _build_jd_service(jd_config)

    logger.info("Loading JD...")
    logger.info("Extracting requirements...")
    logger.info("Building ontology...")
    logger.info("Creating graph...")

    result = service.process()

    logger.info("{} required skills extracted", result.required_count)
    logger.info("{} preferred skills extracted", result.preferred_count)
    logger.info("{} negative signals detected", result.negative_count)
    logger.info("Graph: {} nodes, {} edges", result.node_count, result.edge_count)

    if result.requirements.experience.min_years is not None:
        logger.info(
            "Experience: {}-{} years (preferred: {})",
            result.requirements.experience.min_years,
            result.requirements.experience.max_years,
            result.requirements.experience.preferred_years,
        )

    for name, path in result.artifact_paths.items():
        logger.info("Exported {}: {}", name, path)

    logger.info("Export complete.")


def _build_jd_service(jd_config: DictConfig | dict[str, object]) -> JDService:
    """Construct JDService from configuration."""
    return JDService(
        jd_path=Path(str(jd_config.get("path", "Dataset/job_description.docx"))),
        ontology_path=Path(str(jd_config.get("ontology_path", "configs/ontology.yaml"))),
        artifacts_dir=Path(str(jd_config.get("artifacts_dir", "artifacts"))),
    )
