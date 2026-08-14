import pytest

from bodysimpy.config.models import SimulationConfig
from bodysimpy.modeling.crossmember import build_crossmember_model


def test_build_crossmember_model() -> None:
    config = SimulationConfig.model_validate(
        {
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
            "material": {
                "youngs_modulus_pa": 210e9,
                "poisson_ratio": 0.30,
                "density_kg_m3": 7850.0,
            },
            "loading": {
                "tip_force_n": 1000.0,
            },
            "mesh": {
                "elements": 20,
            },
            "analysis": {
                "static": True,
                "modal": {
                    "modes": 10,
                },
            },
        }
    )

    model = build_crossmember_model(config)

    assert model.name == "baseline_crossmember"
    assert model.length_m == pytest.approx(1.0)
    assert model.section.width_m == pytest.approx(0.080)
    assert model.section.height_m == pytest.approx(0.040)
    assert model.section.thickness_m == pytest.approx(0.0015)
    assert model.material.youngs_modulus_pa == pytest.approx(210e9)
    assert model.tip_force_n == pytest.approx(1000.0)
    assert model.mesh_elements == 20
