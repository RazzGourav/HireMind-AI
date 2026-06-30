from pathlib import Path

from omegaconf import DictConfig, OmegaConf

DEFAULT_CONFIG_PATH = Path("configs/config.yaml")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> DictConfig:
    config = OmegaConf.load(config_path)
    if not isinstance(config, DictConfig):
        raise TypeError(f"Expected mapping config at {config_path}")
    return config
