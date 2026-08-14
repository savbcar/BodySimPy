from dataclasses import dataclass
from math import pi, sqrt

from bodysimpy.domain.materials import IsotropicMaterial
from bodysimpy.domain.sections import RectangularHollowSection


@dataclass(frozen=True, slots=True)
class CantileverResult:
    tip_deflection_m: float
    root_bending_stress_pa: float
    first_natural_frequency_hz: float


def solve_cantilever(
    *,
    section: RectangularHollowSection,
    material: IsotropicMaterial,
    length_m: float,
    tip_force_n: float,
) -> CantileverResult:
    """Analytical Euler-Bernoulli cantilever reference solution."""

    if length_m <= 0.0:
        raise ValueError("Beam length must be positive.")

    moment_of_inertia = section.second_moment_y_m4

    tip_deflection = (
        tip_force_n * length_m**3 / (3.0 * material.youngs_modulus_pa * moment_of_inertia)
    )

    root_moment = tip_force_n * length_m

    root_bending_stress = root_moment * (section.height_m / 2.0) / moment_of_inertia

    beta_1 = 1.875104068711

    first_natural_frequency = (
        beta_1**2
        / (2.0 * pi)
        * sqrt(
            material.youngs_modulus_pa
            * moment_of_inertia
            / (material.density_kg_m3 * section.area_m2 * length_m**4)
        )
    )

    return CantileverResult(
        tip_deflection_m=tip_deflection,
        root_bending_stress_pa=root_bending_stress,
        first_natural_frequency_hz=first_natural_frequency,
    )
