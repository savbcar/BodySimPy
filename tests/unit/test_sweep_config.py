import pytest
from pydantic import ValidationError

from bodysimpy.config.loader import load_thickness_sweep_config
from bodysimpy.config.models import ThicknessSweepConfig


def test_valid_thickness_sweep_configuration() -> None:
    config = ThicknessSweepConfig.model_validate(
        {
            "base_config": "configs/baseline_crossmember.yaml",
            "thickness_values_m": [
                0.0010,
                0.0012,
                0.0014,
            ],
            "output_csv": "docs/validation/thickness_sweep.csv",
            "max_workers": 1,
        }
    )

    assert config.thickness_values_m == pytest.approx(
        (
            0.0010,
            0.0012,
            0.0014,
        )
    )

    assert config.max_workers == 1


def test_sweep_rejects_non_positive_thickness() -> None:
    with pytest.raises(ValidationError):
        ThicknessSweepConfig.model_validate(
            {
                "base_config": "configs/baseline_crossmember.yaml",
                "thickness_values_m": [
                    0.0010,
                    -0.0012,
                ],
                "output_csv": "docs/validation/thickness_sweep.csv",
                "max_workers": 1,
            }
        )


def test_sweep_rejects_duplicate_thickness_values() -> None:
    with pytest.raises(ValidationError):
        ThicknessSweepConfig.model_validate(
            {
                "base_config": "configs/baseline_crossmember.yaml",
                "thickness_values_m": [
                    0.0010,
                    0.0010,
                ],
                "output_csv": "docs/validation/thickness_sweep.csv",
                "max_workers": 1,
            }
        )


def test_load_thickness_sweep_yaml() -> None:
    config = load_thickness_sweep_config("configs/thickness_sweep.yaml")

    assert len(config.thickness_values_m) == 6
    assert config.thickness_values_m[0] == pytest.approx(0.0010)
    assert config.thickness_values_m[-1] == pytest.approx(0.0020)
    assert config.max_workers == 4


def test_sweep_rejects_empty_thickness_values() -> None:
    with pytest.raises(ValidationError):
        ThicknessSweepConfig.model_validate(
            {
                "base_config": "configs/baseline_crossmember.yaml",
                "thickness_values_m": [],
                "output_csv": "docs/validation/thickness_sweep.csv",
                "max_workers": 1,
            }
        )


def test_sweep_accepts_unsorted_thickness_values() -> None:
    config = ThicknessSweepConfig.model_validate(
        {
            "base_config": "configs/baseline_crossmember.yaml",
            "thickness_values_m": [
                0.0020,
                0.0010,
                0.0015,
            ],
            "output_csv": "docs/validation/thickness_sweep.csv",
            "max_workers": 1,
        }
    )

    # Values should be accepted as-is without being sorted
    assert config.thickness_values_m == pytest.approx((0.0020, 0.0010, 0.0015))


def test_sweep_rejects_zero_max_workers() -> None:
    with pytest.raises(ValidationError):
        ThicknessSweepConfig.model_validate(
            {
                "base_config": "configs/baseline_crossmember.yaml",
                "thickness_values_m": [0.0010],
                "output_csv": "docs/validation/thickness_sweep.csv",
                "max_workers": 0,
            }
        )


def test_sweep_rejects_infinite_thickness_value() -> None:
    with pytest.raises(ValidationError):
        ThicknessSweepConfig.model_validate(
            {
                "base_config": "configs/baseline_crossmember.yaml",
                "thickness_values_m": [0.0010, float("inf"), 0.0020],
                "output_csv": "docs/validation/thickness_sweep.csv",
                "max_workers": 1,
            }
        )
