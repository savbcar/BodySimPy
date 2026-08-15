import csv
from pathlib import Path

import matplotlib.pyplot as plt

from bodysimpy.analysis.fea_validation import (
    FeaValidationPoint,
    run_static_validation_study,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import build_crossmember_model


def write_csv(
    points: tuple[FeaValidationPoint, ...],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)

        writer.writerow(
            [
                "mesh_elements",
                "analytical_deflection_mm",
                "fea_deflection_mm",
                "deflection_error_percent",
                "analytical_stress_mpa",
                "fea_stress_mpa",
                "stress_error_percent",
            ]
        )

        for point in points:
            writer.writerow(
                [
                    point.mesh_elements,
                    point.analytical_tip_deflection_m * 1000.0,
                    point.fea_tip_deflection_m * 1000.0,
                    point.tip_deflection_error_percent,
                    point.analytical_max_axial_stress_pa / 1e6,
                    point.fea_max_axial_stress_pa / 1e6,
                    point.stress_error_percent,
                ]
            )


def write_plot(
    points: tuple[FeaValidationPoint, ...],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    element_counts = [point.mesh_elements for point in points]

    displacement_errors = [point.tip_deflection_error_percent for point in points]

    stress_errors = [point.stress_error_percent for point in points]

    plt.figure(figsize=(8, 5))

    plt.plot(
        element_counts,
        displacement_errors,
        marker="o",
        label="Tip displacement",
    )

    plt.plot(
        element_counts,
        stress_errors,
        marker="o",
        label="Maximum axial stress",
    )

    plt.xlabel("Longitudinal B32R elements")
    plt.ylabel("Relative error [%]")
    plt.title("BodySimPy Static FEA Mesh Convergence")
    plt.xticks(element_counts)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path, dpi=200)
    plt.close()


def main() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    points = run_static_validation_study(model)

    print()
    print("BodySimPy Static FEA Validation")
    print("-" * 79)

    for point in points:
        print(
            f"{point.mesh_elements:>3} elements | "
            f"deflection: "
            f"{point.fea_tip_deflection_m * 1000:>9.5f} mm | "
            f"error: "
            f"{point.tip_deflection_error_percent:>8.4f}% | "
            f"stress: "
            f"{point.fea_max_axial_stress_pa / 1e6:>10.4f} MPa | "
            f"error: "
            f"{point.stress_error_percent:>8.4f}%"
        )

    write_csv(
        points,
        Path("docs/validation/static_mesh_convergence.csv"),
    )

    write_plot(
        points,
        Path("docs/figures/static_mesh_convergence.png"),
    )


if __name__ == "__main__":
    main()
