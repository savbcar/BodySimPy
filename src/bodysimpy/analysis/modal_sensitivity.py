from dataclasses import dataclass, replace

from bodysimpy.domain.structural_model import (
    StructuralModel,
)
from bodysimpy.solvers.calculix import (
    CalculiXSolver,
)


@dataclass(frozen=True, slots=True)
class ModalSensitivityPoint:
    parameter_value: float
    mode_1_frequency_hz: float


def _solve_mode_1(
    model: StructuralModel,
) -> float:
    result = CalculiXSolver().run_modal(
        model,
        modes=1,
    )

    return result.natural_frequencies_hz[0]


def thickness_sensitivity(
    model: StructuralModel,
    *,
    multipliers: tuple[float, ...],
) -> tuple[ModalSensitivityPoint, ...]:
    points: list[ModalSensitivityPoint] = []

    for multiplier in multipliers:
        thickness = model.section.thickness_m * multiplier

        section = replace(
            model.section,
            thickness_m=thickness,
        )

        variant = replace(
            model,
            name=(f"{model.name}_thickness_{multiplier:.2f}"),
            section=section,
        )

        points.append(
            ModalSensitivityPoint(
                parameter_value=thickness,
                mode_1_frequency_hz=(_solve_mode_1(variant)),
            )
        )

    return tuple(points)


def youngs_modulus_sensitivity(
    model: StructuralModel,
    *,
    multipliers: tuple[float, ...],
) -> tuple[ModalSensitivityPoint, ...]:
    points: list[ModalSensitivityPoint] = []

    for multiplier in multipliers:
        youngs_modulus = model.material.youngs_modulus_pa * multiplier

        material = replace(
            model.material,
            youngs_modulus_pa=youngs_modulus,
        )

        variant = replace(
            model,
            name=(f"{model.name}_youngs_{multiplier:.2f}"),
            material=material,
        )

        points.append(
            ModalSensitivityPoint(
                parameter_value=youngs_modulus,
                mode_1_frequency_hz=(_solve_mode_1(variant)),
            )
        )

    return tuple(points)


def density_sensitivity(
    model: StructuralModel,
    *,
    multipliers: tuple[float, ...],
) -> tuple[ModalSensitivityPoint, ...]:
    points: list[ModalSensitivityPoint] = []

    for multiplier in multipliers:
        density = model.material.density_kg_m3 * multiplier

        material = replace(
            model.material,
            density_kg_m3=density,
        )

        variant = replace(
            model,
            name=(f"{model.name}_density_{multiplier:.2f}"),
            material=material,
        )

        points.append(
            ModalSensitivityPoint(
                parameter_value=density,
                mode_1_frequency_hz=(_solve_mode_1(variant)),
            )
        )

    return tuple(points)


def section_height_sensitivity(
    model: StructuralModel,
    *,
    multipliers: tuple[float, ...],
) -> tuple[ModalSensitivityPoint, ...]:
    points: list[ModalSensitivityPoint] = []

    for multiplier in multipliers:
        height = model.section.height_m * multiplier

        section = replace(
            model.section,
            height_m=height,
        )

        variant = replace(
            model,
            name=(f"{model.name}_height_{multiplier:.2f}"),
            section=section,
        )

        points.append(
            ModalSensitivityPoint(
                parameter_value=height,
                mode_1_frequency_hz=(_solve_mode_1(variant)),
            )
        )

    return tuple(points)
