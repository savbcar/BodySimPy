from pathlib import Path

import pytest

from bodysimpy.config.loader import load_config


def test_load_baseline_configuration() -> None:
    config_path = Path("configs/baseline_crossmember.yaml")

    config = load_config(config_path)

    assert config.project.name == "baseline_crossmember"
    assert config.geometry.length_m == 1.0
    assert config.geometry.width_m == 0.080
    assert config.geometry.height_m == 0.040
    assert config.geometry.thickness_m == 0.0015
    assert config.material.youngs_modulus_pa == 210e9
    assert config.loading.tip_force_n == 1000.0
    assert config.analysis.static is True
    assert config.analysis.modal.modes == 10
    assert config.mesh.elements == 20


def test_load_stochastic_configuration() -> None:
    config = load_config("configs/stochastic_crossmember.yaml")

    assert config.stochastic is not None
    assert config.stochastic.samples == 500
    assert config.stochastic.seed == 42
    assert config.stochastic.thickness_m.mean == pytest.approx(0.0015)
    assert config.stochastic.thickness_m.standard_deviation == pytest.approx(0.00005)
    assert config.stochastic.youngs_modulus_pa.mean == pytest.approx(210e9)
