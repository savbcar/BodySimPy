import pytest
from pydantic import ValidationError

from bodysimpy.config.models import SimulationConfig


def valid_configuration() -> dict[str, object]:
    return {
        "project": {
            "name": "baseline_crossmember",
        },
        "geometry": {
            "type": "rectangular_hollow_section",
            "length_m": 1.0,
            "width_m": 0.080,
            "height_m": 0.040,
            "thickness_m": 0.0015,
        },
        "mesh": {
            "elements": 20,
        },
        "material": {
            "youngs_modulus_pa": 210e9,
            "poisson_ratio": 0.30,
            "density_kg_m3": 7850.0,
        },
        "loading": {
            "tip_force_n": 1000.0,
        },
        "analysis": {
            "static": True,
            "modal": {
                "modes": 10,
            },
        },
    }


def test_valid_simulation_configuration() -> None:
    config = SimulationConfig.model_validate(valid_configuration())

    assert config.project.name == "baseline_crossmember"
    assert config.geometry.thickness_m == pytest.approx(0.0015)
    assert config.material.youngs_modulus_pa == pytest.approx(210e9)
    assert config.analysis.modal.modes == 10
    assert config.mesh.elements == 20


def test_configuration_rejects_impossible_section() -> None:
    data = valid_configuration()

    geometry = data["geometry"]
    assert isinstance(geometry, dict)

    geometry["thickness_m"] = 0.025
    geometry["height_m"] = 0.040

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_configuration_rejects_unknown_fields() -> None:
    data = valid_configuration()
    data["mystery_setting"] = 42

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)
