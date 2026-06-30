from pathlib import Path

from omegaconf import DictConfig

from hiremind.infrastructure import load_config, logger
from hiremind.services.dataset_service import DatasetService


def main() -> None:
    config = load_config()
    dataset_config = config.get("dataset", {})
    service = _build_dataset_service(dataset_config)

    logger.info("Loading Dataset...")
    logger.info("Validating...")
    result = service.preprocess()
    logger.info("{} candidates loaded", result.valid_records)
    logger.info("{} duplicate IDs", result.duplicate_ids)
    logger.info("{} invalid record{}", result.invalid_records, _plural(result.invalid_records))
    logger.info("Saving cache...")
    logger.info("Done.")


def _build_dataset_service(dataset_config: DictConfig | dict[str, object]) -> DatasetService:
    return DatasetService(
        raw_path=Path(str(dataset_config.get("raw_path", "data/raw/candidates.jsonl"))),
        schema_path=Path(str(dataset_config.get("schema_path", "configs/candidate_schema.json"))),
        output_dir=Path(str(dataset_config.get("output_dir", "outputs"))),
        cache_dir=Path(str(dataset_config.get("cache_dir", "feature_cache"))),
        dataset_version=str(dataset_config.get("version", "1.0")),
    )


def _plural(count: int) -> str:
    return "" if count == 1 else "s"
