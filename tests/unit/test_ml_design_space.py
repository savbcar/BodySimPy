import pytest

from bodysimpy.ml.design_space import generate_design_points


def test_generate_design_points() -> None:
    points = generate_design_points(
        sample_count=10,
        seed=42,
    )

    assert len(points) == 10

    for point in points:
        assert 0.0010 <= point.thickness_m <= 0.0020
        assert 0.032 <= point.height_m <= 0.050
        assert 0.060 <= point.width_m <= 0.100
        assert 190e9 <= point.youngs_modulus_pa <= 225e9
        assert 7600.0 <= point.density_kg_m3 <= 8100.0
        assert 700.0 <= point.tip_force_n <= 1300.0


def test_design_generation_is_reproducible() -> None:
    first = generate_design_points(
        sample_count=5,
        seed=42,
    )

    second = generate_design_points(
        sample_count=5,
        seed=42,
    )

    assert first == second


def test_design_generation_rejects_invalid_sample_count() -> None:
    with pytest.raises(ValueError):
        generate_design_points(
            sample_count=0,
            seed=42,
        )
