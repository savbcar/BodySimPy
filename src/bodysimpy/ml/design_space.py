from dataclasses import dataclass

import numpy as np
from scipy.stats import qmc


@dataclass(frozen=True, slots=True)
class SurrogateDesignPoint:
    sample_index: int
    thickness_m: float
    height_m: float
    width_m: float
    youngs_modulus_pa: float
    density_kg_m3: float
    tip_force_n: float


def generate_design_points(
    *,
    sample_count: int,
    seed: int,
) -> tuple[SurrogateDesignPoint, ...]:
    """Generate a six-dimensional Latin Hypercube design."""

    if sample_count <= 0:
        raise ValueError("Surrogate sample count must be positive.")

    lower_bounds = np.array(
        [
            0.0010,
            0.032,
            0.060,
            190e9,
            7600.0,
            700.0,
        ],
        dtype=float,
    )

    upper_bounds = np.array(
        [
            0.0020,
            0.050,
            0.100,
            225e9,
            8100.0,
            1300.0,
        ],
        dtype=float,
    )

    sampler = qmc.LatinHypercube(
        d=6,
        seed=seed,
    )

    unit_sample = sampler.random(n=sample_count)

    scaled_sample = qmc.scale(
        unit_sample,
        lower_bounds,
        upper_bounds,
    )

    return tuple(
        SurrogateDesignPoint(
            sample_index=index + 1,
            thickness_m=float(row[0]),
            height_m=float(row[1]),
            width_m=float(row[2]),
            youngs_modulus_pa=float(row[3]),
            density_kg_m3=float(row[4]),
            tip_force_n=float(row[5]),
        )
        for index, row in enumerate(scaled_sample)
    )
