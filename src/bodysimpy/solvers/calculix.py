from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from bodysimpy.domain.results import SimulationResult
from bodysimpy.domain.structural_model import StructuralModel
from bodysimpy.solvers.parsers.dat_parser import parse_tip_displacement
from bodysimpy.solvers.parsers.frd_parser import parse_max_abs_stress_component


class CalculiXError(RuntimeError):
    """Raised when a CalculiX analysis cannot be completed."""


def build_input_deck(model: StructuralModel) -> str:
    """Generate a CalculiX input deck for a cantilever box beam."""

    element_count = model.mesh_elements
    node_count = 2 * element_count + 1

    lines: list[str] = [
        "*HEADING",
        f"BodySimPy model: {model.name}",
        "*NODE,NSET=NALL",
    ]

    for node_index in range(node_count):
        node_id = node_index + 1
        x_coordinate = model.length_m * node_index / (2 * element_count)

        lines.append(f"{node_id},{x_coordinate:.12e},0.0,0.0")

    lines.append("*ELEMENT,TYPE=B32R,ELSET=EALL")

    for element_index in range(element_count):
        element_id = element_index + 1
        first_node = 2 * element_index + 1
        middle_node = first_node + 1
        last_node = first_node + 2

        lines.append(f"{element_id},{first_node},{middle_node},{last_node}")

    tip_node_id = node_count

    lines.extend(
        [
            "*NSET,NSET=FIX",
            "1",
            "*NSET,NSET=TIP",
            str(tip_node_id),
            "*BOUNDARY",
            "FIX,1,6",
            "*MATERIAL,NAME=STEEL",
            "*ELASTIC",
            (f"{model.material.youngs_modulus_pa:.12e},{model.material.poisson_ratio:.12e}"),
            "*DENSITY",
            f"{model.material.density_kg_m3:.12e}",
            "*BEAM SECTION,ELSET=EALL,MATERIAL=STEEL,SECTION=BOX",
            (
                f"{model.section.height_m:.12e},"
                f"{model.section.width_m:.12e},"
                f"{model.section.thickness_m:.12e},"
                f"{model.section.thickness_m:.12e},"
                f"{model.section.thickness_m:.12e},"
                f"{model.section.thickness_m:.12e}"
            ),
            "0.0,0.0,1.0",
            "*STEP",
            "*STATIC",
            "*CLOAD",
            f"TIP,3,{model.tip_force_n:.12e}",
            "*NODE PRINT,NSET=TIP",
            "U",
            "*EL FILE,OUTPUT=3D",
            "S,NOE",
            "*END STEP",
        ]
    )

    return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class CalculiXSolver:
    """CalculiX CrunchiX structural solver adapter."""

    executable: str = "ccx"
    work_root: Path = Path("results/raw")
    timeout_seconds: float = 60.0

    def run(self, model: StructuralModel) -> SimulationResult:
        executable_path = shutil.which(self.executable)

        if executable_path is None:
            raise CalculiXError(f"CalculiX executable '{self.executable}' was not found.")

        work_directory = self.work_root / model.name
        work_directory.mkdir(parents=True, exist_ok=True)

        job_name = "static"

        generated_suffixes = (
            ".dat",
            ".frd",
            ".sta",
            ".cvg",
        )

        for suffix in generated_suffixes:
            output_path = work_directory / f"{job_name}{suffix}"
            output_path.unlink(missing_ok=True)

        input_path = work_directory / f"{job_name}.inp"
        input_path.write_text(
            build_input_deck(model),
            encoding="utf-8",
        )

        try:
            completed = subprocess.run(
                [executable_path, job_name],
                cwd=work_directory,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise CalculiXError("CalculiX execution exceeded the configured timeout.") from error

        if completed.returncode != 0:
            raise CalculiXError(
                "CalculiX execution failed.\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )

        dat_path = work_directory / f"{job_name}.dat"
        frd_path = work_directory / f"{job_name}.frd"

        if not dat_path.exists():
            raise CalculiXError("CalculiX completed without producing the expected .dat file.")

        if not frd_path.exists():
            raise CalculiXError("CalculiX completed without producing the expected .frd file.")

        tip_node_id = 2 * model.mesh_elements + 1

        tip_deflection = parse_tip_displacement(
            dat_path,
            tip_node_id=tip_node_id,
            component=3,
        )

        max_axial_stress = parse_max_abs_stress_component(
            frd_path,
            component=1,
        )

        return SimulationResult(
            solver_name="calculix",
            tip_deflection_m=tip_deflection,
            max_axial_stress_pa=max_axial_stress,
            work_directory=work_directory,
        )
