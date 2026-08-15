import csv
from pathlib import Path

import matplotlib.pyplot as plt

from bodysimpy.analysis.modal_sensitivity import (
    ModalSensitivityPoint,
    density_sensitivity,
    section_height_sensitivity,
    thickness_sensitivity,
    youngs_modulus_sensitivity,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)

MULTIPLIERS = (
    0.8,
    0.9,
    1.0,
    1.1,
    1.2,
)


def write_study(
    *,
    name: str,
    x_label: str,
    points: tuple[ModalSensitivityPoint, ...],
    scale: float,
) -> None:
    csv_path = Path(f"docs/validation/{name}_sensitivity.csv")

    csv_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with csv_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.writer(stream)

        writer.writerow(
            [
                "parameter_value",
                "mode_1_frequency_hz",
            ]
        )

        for point in points:
            writer.writerow(
                [
                    point.parameter_value,
                    point.mode_1_frequency_hz,
                ]
            )

    x_values = [point.parameter_value * scale for point in points]

    frequencies = [point.mode_1_frequency_hz for point in points]

    figure_path = Path(f"docs/figures/{name}_sensitivity.png")

    figure_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(7, 5))

    plt.plot(
        x_values,
        frequencies,
        marker="o",
    )

    plt.xlabel(x_label)
    plt.ylabel("Mode-1 natural frequency [Hz]")

    plt.title(f"Mode-1 Sensitivity — {name.replace('_', ' ').title()}")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=200,
    )

    plt.close()


def main() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    write_study(
        name="thickness",
        x_label="Wall thickness [mm]",
        points=thickness_sensitivity(
            model,
            multipliers=MULTIPLIERS,
        ),
        scale=1000.0,
    )

    write_study(
        name="youngs_modulus",
        x_label="Young's modulus [GPa]",
        points=youngs_modulus_sensitivity(
            model,
            multipliers=MULTIPLIERS,
        ),
        scale=1e-9,
    )

    write_study(
        name="density",
        x_label="Density [kg/m³]",
        points=density_sensitivity(
            model,
            multipliers=MULTIPLIERS,
        ),
        scale=1.0,
    )

    write_study(
        name="section_height",
        x_label="Section height [mm]",
        points=section_height_sensitivity(
            model,
            multipliers=MULTIPLIERS,
        ),
        scale=1000.0,
    )


if __name__ == "__main__":
    main()
