from hiremind.infrastructure import load_config, logger


def main() -> None:
    config = load_config()
    logger.info("Ranking complete")
    logger.info("Top K candidates configured: {}", config.ranking.top_k)
