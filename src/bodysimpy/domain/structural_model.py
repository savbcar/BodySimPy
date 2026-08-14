from dataclasses import dataclass

from bodysimpy.domain.materials import IsotropicMaterial
from bodysimpy.domain.sections import RectangularHollowSection


@dataclass(frozen=True, slots=True)
class StructuralModel:
    """Solver-independent structural model definition."""

    name: str
    section: RectangularHollowSection
    material: IsotropicMaterial
    length_m: float
    tip_force_n: float
    mesh_elements: int = 10

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Model name must not be empty.")

        if self.length_m <= 0.0:
            raise ValueError("Beam length must be positive.")

        if self.mesh_elements <= 0:
            raise ValueError("Mesh element count must be positive.")
