from hiremind.infrastructure import load_config, logger


def main() -> None:
    config = load_config()
    logger.info("Evaluation complete for {}", config.project.name)
