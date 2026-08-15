import csv
from pathlib import Path

import matplotlib.pyplot as plt

from bodysimpy.analysis.modal_validation import (
    validate_modal_response,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)


def main() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    result = validate_modal_response(
        model,
        modes=10,
    )

    table_path = Path("docs/validation/modal_frequencies.csv")

    table_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with table_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.writer(stream)

        writer.writerow(
            [
                "mode",
                "frequency_hz",
            ]
        )

        for mode, frequency in enumerate(
            result.fea_frequencies_hz,
            start=1,
        ):
            writer.writerow(
                [
                    mode,
                    frequency,
                ]
            )

    modes = list(
        range(
            1,
            len(result.fea_frequencies_hz) + 1,
        )
    )

    figure_path = Path("docs/figures/modal_frequencies.png")

    figure_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        modes,
        result.fea_frequencies_hz,
        marker="o",
    )

    plt.xlabel("Mode number")
    plt.ylabel("Natural frequency [Hz]")
    plt.title("BodySimPy Baseline Natural Frequencies")

    plt.xticks(modes)
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=200,
    )

    plt.close()

    print()
    print("BodySimPy Modal Analysis")
    print("-" * 55)

    for mode, frequency in enumerate(
        result.fea_frequencies_hz,
        start=1,
    ):
        print(f"Mode {mode:>2}: {frequency:>12.4f} Hz")

    print()
    print(f"Analytical mode 1: {result.analytical_mode_1_hz:.4f} Hz")

    print(f"FEA mode 1:        {result.fea_mode_1_hz:.4f} Hz")

    print(f"Mode-1 error:      {result.mode_1_error_percent:.4f} %")


if __name__ == "__main__":
    main()
