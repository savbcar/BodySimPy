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


def test_geometry_rejects_thickness_equal_to_min_half_dimension() -> None:
    data = valid_configuration()
    geometry = data["geometry"]
    assert isinstance(geometry, dict)

    # 2 * thickness == min(width, height) should be rejected (strict inequality required)
    geometry["width_m"] = 0.080
    geometry["height_m"] = 0.040
    geometry["thickness_m"] = 0.020  # 2 * 0.020 == 0.040 (min of dimensions)

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_geometry_accepts_thickness_just_below_min_half_dimension() -> None:
    data = valid_configuration()
    geometry = data["geometry"]
    assert isinstance(geometry, dict)

    # 2 * thickness < min(width, height) should be accepted
    geometry["width_m"] = 0.080
    geometry["height_m"] = 0.040
    geometry["thickness_m"] = 0.01999  # just below 0.020

    config = SimulationConfig.model_validate(data)
    assert config.geometry.thickness_m == pytest.approx(0.01999)


def test_material_rejects_poisson_ratio_equal_to_minus_one() -> None:
    data = valid_configuration()
    material = data["material"]
    assert isinstance(material, dict)

    # Poisson's ratio at lower boundary should be rejected (strict > -1.0)
    material["poisson_ratio"] = -1.0

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_material_rejects_poisson_ratio_equal_to_half() -> None:
    data = valid_configuration()
    material = data["material"]
    assert isinstance(material, dict)

    # Poisson's ratio at upper boundary should be rejected (strict < 0.5)
    material["poisson_ratio"] = 0.5

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_loading_accepts_negative_tip_force() -> None:
    data = valid_configuration()
    loading = data["loading"]
    assert isinstance(loading, dict)

    # Negative tip force should be accepted (signed quantity, valid opposite direction)
    loading["tip_force_n"] = -1000.0

    config = SimulationConfig.model_validate(data)
    assert config.loading.tip_force_n == pytest.approx(-1000.0)


def test_simulation_rejects_extra_field_in_geometry() -> None:
    data = valid_configuration()
    geometry = data["geometry"]
    assert isinstance(geometry, dict)

    # Extra field in nested model should be rejected
    geometry["material_id"] = "steel_a"

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_geometry_rejects_infinite_thickness() -> None:
    data = valid_configuration()
    geometry = data["geometry"]
    assert isinstance(geometry, dict)

    # Infinite thickness is not a valid physical value
    geometry["thickness_m"] = float("inf")

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_geometry_rejects_nan_thickness() -> None:
    data = valid_configuration()
    geometry = data["geometry"]
    assert isinstance(geometry, dict)

    # NaN thickness is not a valid physical value
    geometry["thickness_m"] = float("nan")

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_material_rejects_infinite_youngs_modulus() -> None:
    data = valid_configuration()
    material = data["material"]
    assert isinstance(material, dict)

    # Infinite stiffness is not a valid physical value
    material["youngs_modulus_pa"] = float("inf")

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_loading_rejects_infinite_tip_force() -> None:
    data = valid_configuration()
    loading = data["loading"]
    assert isinstance(loading, dict)

    # Infinite force is not a valid physical value (even though signed)
    loading["tip_force_n"] = float("inf")

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)


def test_normal_distribution_rejects_infinite_std_dev() -> None:
    data = valid_configuration()
    stochastic = {
        "samples": 1000,
        "seed": 42,
        "stress_threshold_pa": 100e6,
        "thickness_m": {
            "mean": 0.0015,
            "standard_deviation": float("inf"),
        },
        "youngs_modulus_pa": {
            "mean": 210e9,
            "standard_deviation": 1e9,
        },
        "tip_force_n": {
            "mean": 1000.0,
            "standard_deviation": 100.0,
        },
    }
    data["stochastic"] = stochastic

    with pytest.raises(ValidationError):
        SimulationConfig.model_validate(data)
