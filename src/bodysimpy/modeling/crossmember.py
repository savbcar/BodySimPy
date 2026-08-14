from bodysimpy.config.models import SimulationConfig
from bodysimpy.domain.materials import IsotropicMaterial
from bodysimpy.domain.sections import RectangularHollowSection
from bodysimpy.domain.structural_model import StructuralModel


def build_crossmember_model(
    config: SimulationConfig,
) -> StructuralModel:
    """Build the simplified automotive crossmember surrogate."""

    section = RectangularHollowSection(
        width_m=config.geometry.width_m,
        height_m=config.geometry.height_m,
        thickness_m=config.geometry.thickness_m,
    )

    material = IsotropicMaterial(
        name="Configured structural material",
        youngs_modulus_pa=config.material.youngs_modulus_pa,
        poisson_ratio=config.material.poisson_ratio,
        density_kg_m3=config.material.density_kg_m3,
        yield_strength_pa=None,
    )

    return StructuralModel(
        name=config.project.name,
        section=section,
        material=material,
        length_m=config.geometry.length_m,
        tip_force_n=config.loading.tip_force_n,
        mesh_elements=config.mesh.elements,
    )
