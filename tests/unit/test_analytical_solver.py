import pytest

from bodysimpy.domain.materials import IsotropicMaterial
from bodysimpy.domain.sections import RectangularHollowSection
from bodysimpy.solvers.analytical import solve_cantilever


def test_cantilever_reference_solution() -> None:
    section = RectangularHollowSection(
        width_m=0.080,
        height_m=0.040,
        thickness_m=0.0015,
    )

    steel = IsotropicMaterial(
        name="Generic structural steel",
        youngs_modulus_pa=210e9,
        poisson_ratio=0.30,
        density_kg_m3=7850.0,
        yield_strength_pa=350e6,
    )

    result = solve_cantilever(
        section=section,
        material=steel,
        length_m=1.0,
        tip_force_n=1000.0,
    )

    assert result.tip_deflection_m == pytest.approx(
        0.0156164,
        rel=1e-5,
    )

    assert result.root_bending_stress_pa == pytest.approx(
        196.7666e6,
        rel=1e-5,
    )

    assert result.first_natural_frequency_hz == pytest.approx(
        49.2529,
        rel=1e-5,
    )
