from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bodysimpy.analysis.stochastic import (
    StochasticStudyResult,
    run_stochastic_study,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)


def build_dataframe(
    result: StochasticStudyResult,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sample": [sample.sample_index for sample in result.samples],
            "thickness_mm": [sample.thickness_m * 1000.0 for sample in result.samples],
            "youngs_modulus_gpa": [sample.youngs_modulus_pa / 1e9 for sample in result.samples],
            "tip_force_n": [sample.tip_force_n for sample in result.samples],
            "max_stress_mpa": [sample.max_stress_pa / 1e6 for sample in result.samples],
            "mode_1_frequency_hz": [sample.mode_1_frequency_hz for sample in result.samples],
        }
    )


def save_histogram(
    values: pd.Series,
    *,
    x_label: str,
    title: str,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=30)
    plt.xlabel(x_label)
    plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def save_correlation_matrix(
    dataframe: pd.DataFrame,
    path: Path,
) -> None:
    columns = [
        "thickness_mm",
        "youngs_modulus_gpa",
        "tip_force_n",
        "max_stress_mpa",
        "mode_1_frequency_hz",
    ]

    values = dataframe[columns].to_numpy(dtype=float)

    correlation = np.corrcoef(
        values,
        rowvar=False,
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(9, 7))

    image = plt.imshow(
        correlation,
        vmin=-1.0,
        vmax=1.0,
    )

    plt.colorbar(
        image,
        label="Pearson correlation",
    )

    labels = [
        "Thickness",
        "E",
        "Load",
        "Stress",
        "Mode 1",
    ]

    plt.xticks(
        range(len(labels)),
        labels,
        rotation=45,
        ha="right",
    )

    plt.yticks(
        range(len(labels)),
        labels,
    )

    for row in range(len(labels)):
        for column in range(len(labels)):
            plt.text(
                column,
                row,
                f"{correlation[row, column]:.2f}",
                ha="center",
                va="center",
            )

    plt.title("BodySimPy Monte Carlo Correlation Matrix")

    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def save_sensitivity_plot(
    sensitivities,
    *,
    title: str,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    names = [point.parameter for point in sensitivities]

    values = [point.coefficient for point in sensitivities]

    plt.figure(figsize=(8, 5))
    plt.bar(names, values)

    plt.axhline(
        0.0,
        linewidth=1.0,
    )

    plt.ylabel("Standardized regression coefficient")

    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def main() -> None:
    config = load_config("configs/stochastic_crossmember.yaml")

    if config.stochastic is None:
        raise ValueError("Stochastic configuration is required.")

    model = build_crossmember_model(config)

    result = run_stochastic_study(
        model,
        config.stochastic,
    )

    dataframe = build_dataframe(result)

    validation_directory = Path("docs/validation")

    figure_directory = Path("docs/figures")

    validation_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        validation_directory / "stochastic_samples.csv",
        index=False,
    )

    correlation_columns = [
        "thickness_mm",
        "youngs_modulus_gpa",
        "tip_force_n",
        "max_stress_mpa",
        "mode_1_frequency_hz",
    ]

    dataframe[correlation_columns].corr().to_csv(
        validation_directory / "stochastic_correlation.csv"
    )

    save_histogram(
        dataframe["max_stress_mpa"],
        x_label="Maximum axial stress [MPa]",
        title="Monte Carlo Stress Distribution",
        path=(figure_directory / "stress_histogram.png"),
    )

    save_histogram(
        dataframe["mode_1_frequency_hz"],
        x_label="Mode-1 natural frequency [Hz]",
        title="Monte Carlo Frequency Distribution",
        path=(figure_directory / "frequency_histogram.png"),
    )

    save_correlation_matrix(
        dataframe,
        figure_directory / "stochastic_correlation_matrix.png",
    )

    save_sensitivity_plot(
        result.stress_sensitivity,
        title="Stress Sensitivity Ranking",
        path=(figure_directory / "stress_sensitivity_ranking.png"),
    )

    save_sensitivity_plot(
        result.frequency_sensitivity,
        title="Mode-1 Frequency Sensitivity Ranking",
        path=(figure_directory / "frequency_sensitivity_ranking.png"),
    )

    print()
    print("BodySimPy Stochastic Engineering Study")
    print("=" * 60)

    print()
    print(f"Monte Carlo samples: {len(result.samples)}")

    print()
    print("Maximum stress")
    print("-" * 40)
    print(f"Mean:        {result.stress_summary.mean / 1e6:.4f} MPa")
    print(f"Std. dev.:   {result.stress_summary.standard_deviation / 1e6:.4f} MPa")
    print(f"5th pct.:    {result.stress_summary.percentile_5 / 1e6:.4f} MPa")
    print(f"95th pct.:   {result.stress_summary.percentile_95 / 1e6:.4f} MPa")
    print(f"CoV:         {result.stress_summary.coefficient_of_variation_percent:.3f} %")
    print(f"P(stress > threshold): {result.stress_exceedance_probability_percent:.3f} %")

    print()
    print("Mode-1 frequency")
    print("-" * 40)
    print(f"Mean:        {result.frequency_summary.mean:.4f} Hz")
    print(f"Std. dev.:   {result.frequency_summary.standard_deviation:.4f} Hz")
    print(f"5th pct.:    {result.frequency_summary.percentile_5:.4f} Hz")
    print(f"95th pct.:   {result.frequency_summary.percentile_95:.4f} Hz")
    print(f"CoV:         {result.frequency_summary.coefficient_of_variation_percent:.3f} %")

    print()
    print("Stress sensitivity")
    print("-" * 40)

    for rank, item in enumerate(
        result.stress_sensitivity,
        start=1,
    ):
        print(f"{rank}. {item.parameter:<18} {item.coefficient:+.4f}")

    print()
    print("Frequency sensitivity")
    print("-" * 40)

    for rank, item in enumerate(
        result.frequency_sensitivity,
        start=1,
    ):
        print(f"{rank}. {item.parameter:<18} {item.coefficient:+.4f}")


if __name__ == "__main__":
    main()
