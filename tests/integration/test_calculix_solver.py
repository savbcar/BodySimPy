import shutil

import pytest

from bodysimpy.domain.materials import IsotropicMaterial
from bodysimpy.domain.sections import RectangularHollowSection
from bodysimpy.domain.structural_model import StructuralModel
from bodysimpy.solvers.calculix import CalculiXSolver


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_calculix_runs_static_beam_analysis() -> None:
    model = StructuralModel(
        name="integration_test_beam",
        section=RectangularHollowSection(
            width_m=0.080,
            height_m=0.040,
            thickness_m=0.0015,
        ),
        material=IsotropicMaterial(
            name="Generic structural steel",
            youngs_modulus_pa=210e9,
            poisson_ratio=0.30,
            density_kg_m3=7850.0,
            yield_strength_pa=350e6,
        ),
        length_m=1.0,
        tip_force_n=1000.0,
        mesh_elements=10,
    )

    result = CalculiXSolver().run(model)

    assert result.solver_name == "calculix"
    assert result.tip_deflection_m > 0.0
    assert result.max_axial_stress_pa is not None
    assert result.max_axial_stress_pa > 0.0
    assert result.work_directory is not None
