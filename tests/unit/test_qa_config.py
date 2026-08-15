import pytest
from pydantic import ValidationError

from bodysimpy.config.models import (
    SimulationQAConfig,
)


def test_valid_simulation_qa_config() -> None:
    config = SimulationQAConfig.model_validate(
        {
            "stress_limit_pa": 350e6,
            "maximum_frequency_shift_percent": 10.0,
            "outlier_z_threshold": 3.0,
        }
    )

    assert config.stress_limit_pa == pytest.approx(350e6)

    assert config.maximum_frequency_shift_percent == pytest.approx(10.0)


def test_qa_config_rejects_invalid_stress_limit() -> None:
    with pytest.raises(ValidationError):
        SimulationQAConfig.model_validate(
            {
                "stress_limit_pa": 0.0,
                "maximum_frequency_shift_percent": 10.0,
            }
        )


def test_qa_config_rejects_negative_frequency_threshold() -> None:
    with pytest.raises(ValidationError):
        SimulationQAConfig.model_validate(
            {
                "stress_limit_pa": 350e6,
                "maximum_frequency_shift_percent": -1.0,
            }
        )
