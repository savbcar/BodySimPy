from pathlib import Path

import yaml

from bodysimpy.config.models import SimulationConfig


def load_config(path: str | Path) -> SimulationConfig:
    """Load and validate a BodySimPy YAML configuration file."""

    config_path = Path(path)

    with config_path.open("r", encoding="utf-8") as stream:
        raw_config = yaml.safe_load(stream)

    if not isinstance(raw_config, dict):
        raise TypeError("Configuration root must be a YAML mapping.")

    return SimulationConfig.model_validate(raw_config)
