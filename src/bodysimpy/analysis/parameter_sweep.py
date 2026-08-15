import csv
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

from bodysimpy.domain.structural_model import (
    StructuralModel,
)
from bodysimpy.solvers.calculix import (
    CalculiXSolver,
)


@dataclass(frozen=True, slots=True)
class SweepPoint:
    """Results from one wall-thickness design point."""

    thickness_m: float
    max_stress_pa: float
    tip_deflection_m: float
    mode_1_frequency_hz: float
    mass_kg: float


def _evaluate_thickness(
    model: StructuralModel,
    thickness_m: float,
) -> SweepPoint:
    if thickness_m <= 0.0:
        raise ValueError("Sweep thickness must be positive.")

    section = replace(
        model.section,
        thickness_m=thickness_m,
    )

    thickness_mm = thickness_m * 1000.0

    thickness_tag = f"{thickness_mm:.3f}".replace(".", "p")

    variant = replace(
        model,
        name=(f"{model.name}_thickness_{thickness_tag}mm"),
        section=section,
    )

    solver = CalculiXSolver()

    static_result = solver.run(variant)

    modal_result = solver.run_modal(
        variant,
        modes=1,
    )

    if static_result.max_axial_stress_pa is None:
        raise ValueError("Static solver returned no axial stress.")

    mass_kg = variant.material.density_kg_m3 * variant.section.area_m2 * variant.length_m

    return SweepPoint(
        thickness_m=thickness_m,
        max_stress_pa=(static_result.max_axial_stress_pa),
        tip_deflection_m=(static_result.tip_deflection_m),
        mode_1_frequency_hz=(modal_result.natural_frequencies_hz[0]),
        mass_kg=mass_kg,
    )


def run_thickness_sweep(
    model: StructuralModel,
    *,
    thickness_values_m: tuple[float, ...],
    max_workers: int = 1,
) -> tuple[SweepPoint, ...]:
    """Evaluate a wall-thickness parameter sweep."""

    if not thickness_values_m:
        raise ValueError("Thickness sweep must contain at least one value.")

    if max_workers <= 0:
        raise ValueError("Maximum worker count must be positive.")

    if max_workers == 1:
        return tuple(
            _evaluate_thickness(
                model,
                thickness,
            )
            for thickness in thickness_values_m
        )

    def evaluate(
        thickness_m: float,
    ) -> SweepPoint:
        return _evaluate_thickness(
            model,
            thickness_m,
        )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return tuple(
            executor.map(
                evaluate,
                thickness_values_m,
            )
        )


def write_sweep_csv(
    points: tuple[SweepPoint, ...],
    path: str | Path,
) -> None:
    """Write parameter-sweep results to CSV."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.writer(stream)

        writer.writerow(
            [
                "thickness_mm",
                "max_stress_mpa",
                "deflection_mm",
                "mode1_hz",
                "mass_kg",
            ]
        )

        for point in points:
            writer.writerow(
                [
                    point.thickness_m * 1000.0,
                    point.max_stress_pa / 1e6,
                    point.tip_deflection_m * 1000.0,
                    point.mode_1_frequency_hz,
                    point.mass_kg,
                ]
            )
