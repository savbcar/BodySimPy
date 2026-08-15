import csv
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

from bodysimpy.domain.structural_model import StructuralModel
from bodysimpy.ml.design_space import SurrogateDesignPoint
from bodysimpy.solvers.calculix import CalculiXSolver


@dataclass(frozen=True, slots=True)
class SurrogateFeaSample:
    sample_index: int

    thickness_m: float
    height_m: float
    width_m: float
    youngs_modulus_pa: float
    density_kg_m3: float
    tip_force_n: float

    max_stress_pa: float
    tip_deflection_m: float
    mode_1_frequency_hz: float


def evaluate_design_point(
    base_model: StructuralModel,
    design: SurrogateDesignPoint,
) -> SurrogateFeaSample:
    """Evaluate one surrogate-design point with CalculiX."""

    section = replace(
        base_model.section,
        thickness_m=design.thickness_m,
        height_m=design.height_m,
        width_m=design.width_m,
    )

    material = replace(
        base_model.material,
        youngs_modulus_pa=design.youngs_modulus_pa,
        density_kg_m3=design.density_kg_m3,
    )

    model = replace(
        base_model,
        name=(f"{base_model.name}_ml_{design.sample_index:04d}"),
        section=section,
        material=material,
        tip_force_n=design.tip_force_n,
    )

    solver = CalculiXSolver()

    static_result = solver.run(model)

    modal_result = solver.run_modal(
        model,
        modes=1,
    )

    if static_result.max_axial_stress_pa is None:
        raise ValueError("Static FEA returned no axial stress.")

    return SurrogateFeaSample(
        sample_index=design.sample_index,
        thickness_m=design.thickness_m,
        height_m=design.height_m,
        width_m=design.width_m,
        youngs_modulus_pa=design.youngs_modulus_pa,
        density_kg_m3=design.density_kg_m3,
        tip_force_n=design.tip_force_n,
        max_stress_pa=static_result.max_axial_stress_pa,
        tip_deflection_m=static_result.tip_deflection_m,
        mode_1_frequency_hz=(modal_result.natural_frequencies_hz[0]),
    )


def generate_fea_dataset(
    base_model: StructuralModel,
    designs: tuple[SurrogateDesignPoint, ...],
    *,
    max_workers: int = 4,
) -> tuple[SurrogateFeaSample, ...]:
    """Evaluate a complete surrogate training design."""

    if max_workers <= 0:
        raise ValueError("Maximum worker count must be positive.")

    def evaluate(
        design: SurrogateDesignPoint,
    ) -> SurrogateFeaSample:
        return evaluate_design_point(
            base_model,
            design,
        )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return tuple(
            executor.map(
                evaluate,
                designs,
            )
        )


def write_fea_dataset(
    samples: tuple[SurrogateFeaSample, ...],
    path: str | Path,
) -> None:
    """Write the generated surrogate dataset to CSV."""

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
                "sample",
                "thickness_m",
                "height_m",
                "width_m",
                "youngs_modulus_pa",
                "density_kg_m3",
                "tip_force_n",
                "max_stress_pa",
                "tip_deflection_m",
                "mode_1_frequency_hz",
            ]
        )

        for sample in samples:
            writer.writerow(
                [
                    sample.sample_index,
                    sample.thickness_m,
                    sample.height_m,
                    sample.width_m,
                    sample.youngs_modulus_pa,
                    sample.density_kg_m3,
                    sample.tip_force_n,
                    sample.max_stress_pa,
                    sample.tip_deflection_m,
                    sample.mode_1_frequency_hz,
                ]
            )
