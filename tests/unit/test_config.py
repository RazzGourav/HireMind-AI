from hiremind.infrastructure import load_config


def test_load_config() -> None:
    config = load_config()

    assert config.project.name == "HireMind AI"
    assert config.ranking.top_k == 100
