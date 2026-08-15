from dataclasses import dataclass, replace

from bodysimpy.analysis.validation import relative_error_percent
from bodysimpy.domain.structural_model import StructuralModel
from bodysimpy.solvers.analytical import AnalyticalSolver
from bodysimpy.solvers.calculix import CalculiXSolver


@dataclass(frozen=True, slots=True)
class FeaValidationPoint:
    mesh_elements: int
    analytical_tip_deflection_m: float
    fea_tip_deflection_m: float
    tip_deflection_error_percent: float
    analytical_max_axial_stress_pa: float
    fea_max_axial_stress_pa: float
    stress_error_percent: float


def run_static_validation_study(
    model: StructuralModel,
    *,
    element_counts: tuple[int, ...] = (20, 40, 80, 160),
) -> tuple[FeaValidationPoint, ...]:
    """Run static analytical-vs-FEA validation across several meshes."""

    analytical = AnalyticalSolver().run(model)

    if analytical.max_axial_stress_pa is None:
        raise ValueError("Analytical solver did not return an axial stress.")

    solver = CalculiXSolver()
    points: list[FeaValidationPoint] = []

    for element_count in element_counts:
        mesh_model = replace(
            model,
            name=f"{model.name}_mesh_{element_count}",
            mesh_elements=element_count,
        )

        fea = solver.run(mesh_model)

        if fea.max_axial_stress_pa is None:
            raise ValueError("CalculiX did not return an axial stress.")

        points.append(
            FeaValidationPoint(
                mesh_elements=element_count,
                analytical_tip_deflection_m=(analytical.tip_deflection_m),
                fea_tip_deflection_m=fea.tip_deflection_m,
                tip_deflection_error_percent=relative_error_percent(
                    reference=analytical.tip_deflection_m,
                    value=fea.tip_deflection_m,
                ),
                analytical_max_axial_stress_pa=(analytical.max_axial_stress_pa),
                fea_max_axial_stress_pa=fea.max_axial_stress_pa,
                stress_error_percent=relative_error_percent(
                    reference=analytical.max_axial_stress_pa,
                    value=fea.max_axial_stress_pa,
                ),
            )
        )

    return tuple(points)
