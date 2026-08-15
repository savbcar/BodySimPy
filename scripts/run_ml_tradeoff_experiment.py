import csv
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np

from bodysimpy.ml.dataset import (
    load_surrogate_arrays,
)
from bodysimpy.ml.evaluation import (
    calculate_metrics,
    predict,
)
from bodysimpy.ml.experiment import (
    build_nested_training_subsets,
    split_holdout_indices,
)
from bodysimpy.ml.training import (
    train_surrogate_fixed_validation,
)

TRAINING_SIZES = (
    50,
    100,
    250,
    500,
)

TRAINING_SEEDS = (
    11,
    22,
    33,
)


def main() -> None:
    training_features, training_targets = load_surrogate_arrays(
        "data/surrogate/fea_surrogate_dataset.csv"
    )

    holdout_features, holdout_targets = load_surrogate_arrays(
        "data/surrogate/fea_surrogate_holdout.csv"
    )

    subsets = build_nested_training_subsets(
        pool_size=training_features.shape[0],
        sample_counts=TRAINING_SIZES,
        seed=42,
    )

    holdout_split = split_holdout_indices(
        sample_count=holdout_features.shape[0],
        validation_count=100,
        seed=42,
    )

    validation_features = holdout_features[holdout_split.validation_indices]

    validation_targets = holdout_targets[holdout_split.validation_indices]

    test_features = holdout_features[holdout_split.test_indices]

    test_targets = holdout_targets[holdout_split.test_indices]

    rows: list[dict[str, float | int]] = []

    for subset in subsets:
        for training_seed in TRAINING_SEEDS:
            print(f"Training size={subset.sample_count}, seed={training_seed}")

            train_features = training_features[subset.indices]

            train_targets = training_targets[subset.indices]

            start = perf_counter()

            result = train_surrogate_fixed_validation(
                train_features,
                train_targets,
                validation_features,
                validation_targets,
                seed=training_seed,
            )

            training_seconds = perf_counter() - start

            predictions = predict(
                result.model,
                test_features,
                feature_standardization=(result.feature_standardization),
                target_standardization=(result.target_standardization),
            )

            stress_metrics = calculate_metrics(
                test_targets[:, 0],
                predictions[:, 0],
            )

            displacement_metrics = calculate_metrics(
                test_targets[:, 1],
                predictions[:, 1],
            )

            frequency_metrics = calculate_metrics(
                test_targets[:, 2],
                predictions[:, 2],
            )

            rows.append(
                {
                    "training_samples": (subset.sample_count),
                    "training_seed": (training_seed),
                    "best_epoch": (result.best_epoch),
                    "training_seconds": (training_seconds),
                    "stress_mae_mpa": (stress_metrics.mae / 1e6),
                    "stress_mape_percent": (stress_metrics.mean_absolute_percentage_error),
                    "deflection_mae_mm": (displacement_metrics.mae * 1000.0),
                    "deflection_mape_percent": (
                        displacement_metrics.mean_absolute_percentage_error
                    ),
                    "frequency_mae_hz": (frequency_metrics.mae),
                    "frequency_mape_percent": (frequency_metrics.mean_absolute_percentage_error),
                }
            )

    output_path = Path("docs/validation/ml_sample_efficiency.csv")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)

    plot_accuracy(rows)


def plot_accuracy(
    rows: list[dict[str, float | int]],
) -> None:
    figure_path = Path("docs/figures/ml_accuracy_vs_training_size.png")

    figure_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metric_fields = (
        (
            "Stress",
            "stress_mape_percent",
        ),
        (
            "Deflection",
            "deflection_mape_percent",
        ),
        (
            "Mode-1 frequency",
            "frequency_mape_percent",
        ),
    )

    plt.figure(figsize=(8, 5))

    for label, field in metric_fields:
        means: list[float] = []
        deviations: list[float] = []

        for sample_count in TRAINING_SIZES:
            values = np.array(
                [float(row[field]) for row in rows if int(row["training_samples"]) == sample_count],
                dtype=float,
            )

            means.append(float(np.mean(values)))

            deviations.append(
                float(
                    np.std(
                        values,
                        ddof=1,
                    )
                )
            )

        plt.errorbar(
            TRAINING_SIZES,
            means,
            yerr=deviations,
            marker="o",
            capsize=4,
            label=label,
        )

    plt.xlabel("Number of FEA training samples")

    plt.ylabel("Held-out test MAPE [%]")

    plt.title("Surrogate Accuracy vs Training-Data Size")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=200,
    )

    plt.close()


if __name__ == "__main__":
    main()
