from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IsotropicMaterial:
    """Linear isotropic material definition in SI units."""

    name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    density_kg_m3: float
    yield_strength_pa: float | None = None

    def __post_init__(self) -> None:
        if self.youngs_modulus_pa <= 0.0:
            raise ValueError("Young's modulus must be positive.")

        if not -1.0 < self.poisson_ratio < 0.5:
            raise ValueError("Poisson ratio must be between -1.0 and 0.5.")

        if self.density_kg_m3 <= 0.0:
            raise ValueError("Density must be positive.")

        if self.yield_strength_pa is not None and self.yield_strength_pa <= 0.0:
            raise ValueError("Yield strength must be positive when provided.")
