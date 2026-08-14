from pathlib import Path

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
