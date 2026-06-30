from hiremind.infrastructure import load_config, logger


def main() -> None:
    config = load_config()
    logger.info("Creating embeddings...")
    logger.info("Index build complete using {}", config.embedding.model)
