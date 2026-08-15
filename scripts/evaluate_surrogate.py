from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray

from bodysimpy.ml.dataset import (
    load_surrogate_arrays,
)
from bodysimpy.ml.evaluation import (
    TargetMetrics,
    calculate_metrics,
    calculate_percentage_errors,
    predict,
)
from bodysimpy.ml.training import (
    TrainingResult,
    train_surrogate,
)

DATASET_PATH = Path("data/surrogate/fea_surrogate_dataset.csv")

FIGURE_DIRECTORY = Path("docs/figures")

VALIDATION_DIRECTORY = Path("docs/validation")


def save_loss_plot(
    result: TrainingResult,
) -> None:
    """Plot training and validation loss versus epoch."""

    epochs = np.arange(
        1,
        len(result.train_losses) + 1,
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        epochs,
        result.train_losses,
        label="Training loss",
    )

    plt.plot(
        epochs,
        result.validation_losses,
        label="Validation loss",
    )

    plt.axvline(
        result.best_epoch,
        linestyle="--",
        label=f"Best epoch: {result.best_epoch}",
    )

    plt.xlabel("Epoch")
    plt.ylabel("Normalized MSE")
    plt.title("BodySimPy Surrogate Training History")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        FIGURE_DIRECTORY / "ml_training_validation_loss.png",
        dpi=200,
    )

    plt.close()


def save_prediction_scatter(
    reference: NDArray[np.float64],
    prediction: NDArray[np.float64],
    *,
    x_label: str,
    y_label: str,
    title: str,
    output_path: Path,
) -> None:
    """Create an FEA-versus-surrogate prediction plot."""

    lower_bound = float(
        min(
            np.min(reference),
            np.min(prediction),
        )
    )

    upper_bound = float(
        max(
            np.max(reference),
            np.max(prediction),
        )
    )

    plt.figure(figsize=(6, 6))

    plt.scatter(
        reference,
        prediction,
        alpha=0.75,
    )

    plt.plot(
        [
            lower_bound,
            upper_bound,
        ],
        [
            lower_bound,
            upper_bound,
        ],
        linestyle="--",
        label="Ideal prediction",
    )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=200,
    )

    plt.close()


def save_error_distribution(
    stress_errors_percent: NDArray[np.float64],
    deflection_errors_percent: NDArray[np.float64],
    frequency_errors_percent: NDArray[np.float64],
) -> None:
    """Plot percentage-error distributions for all predicted responses."""

    plt.figure(figsize=(9, 5))

    plt.hist(
        stress_errors_percent,
        bins=20,
        alpha=0.5,
        label="Stress",
    )

    plt.hist(
        deflection_errors_percent,
        bins=20,
        alpha=0.5,
        label="Tip deflection",
    )

    plt.hist(
        frequency_errors_percent,
        bins=20,
        alpha=0.5,
        label="Mode-1 frequency",
    )

    plt.xlabel("Absolute percentage error [%]")
    plt.ylabel("Test samples")

    plt.title("BodySimPy Surrogate Prediction Error Distribution")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        FIGURE_DIRECTORY / "prediction_error_distribution.png",
        dpi=200,
    )

    plt.close()


def save_metrics_csv(
    *,
    stress_metrics: TargetMetrics,
    deflection_metrics: TargetMetrics,
    frequency_metrics: TargetMetrics,
) -> None:
    """Store held-out test metrics in engineering units."""

    dataframe = pd.DataFrame(
        [
            {
                "response": "max_stress",
                "mae": stress_metrics.mae / 1e6,
                "rmse": stress_metrics.rmse / 1e6,
                "unit": "MPa",
                "mape_percent": (stress_metrics.mean_absolute_percentage_error),
            },
            {
                "response": "tip_deflection",
                "mae": deflection_metrics.mae * 1000.0,
                "rmse": deflection_metrics.rmse * 1000.0,
                "unit": "mm",
                "mape_percent": (deflection_metrics.mean_absolute_percentage_error),
            },
            {
                "response": "mode_1_frequency",
                "mae": frequency_metrics.mae,
                "rmse": frequency_metrics.rmse,
                "unit": "Hz",
                "mape_percent": (frequency_metrics.mean_absolute_percentage_error),
            },
        ]
    )

    dataframe.to_csv(
        VALIDATION_DIRECTORY / "ml_test_metrics.csv",
        index=False,
    )


def save_test_predictions(
    *,
    reference: NDArray[np.float64],
    prediction: NDArray[np.float64],
    test_indices: NDArray[np.int64],
) -> None:
    """Store every held-out FEA and PyTorch prediction."""

    stress_error = calculate_percentage_errors(
        reference[:, 0],
        prediction[:, 0],
    )

    deflection_error = calculate_percentage_errors(
        reference[:, 1],
        prediction[:, 1],
    )

    frequency_error = calculate_percentage_errors(
        reference[:, 2],
        prediction[:, 2],
    )

    dataframe = pd.DataFrame(
        {
            "dataset_index": test_indices,
            "fea_stress_mpa": (reference[:, 0] / 1e6),
            "predicted_stress_mpa": (prediction[:, 0] / 1e6),
            "stress_error_percent": (stress_error),
            "fea_deflection_mm": (reference[:, 1] * 1000.0),
            "predicted_deflection_mm": (prediction[:, 1] * 1000.0),
            "deflection_error_percent": (deflection_error),
            "fea_mode_1_hz": (reference[:, 2]),
            "predicted_mode_1_hz": (prediction[:, 2]),
            "frequency_error_percent": (frequency_error),
        }
    )

    dataframe.to_csv(
        VALIDATION_DIRECTORY / "ml_test_predictions.csv",
        index=False,
    )


def print_metrics(
    *,
    stress_metrics: TargetMetrics,
    deflection_metrics: TargetMetrics,
    frequency_metrics: TargetMetrics,
) -> None:
    """Print held-out test-set metrics."""

    print()
    print("BodySimPy PyTorch Surrogate Evaluation")
    print("=" * 78)

    print()
    print(f"{'Response':<20}{'MAE':>16}{'RMSE':>16}{'MAPE':>16}")

    print("-" * 78)

    print(
        f"{'Stress':<20}"
        f"{stress_metrics.mae / 1e6:>12.4f} MPa"
        f"{stress_metrics.rmse / 1e6:>12.4f} MPa"
        f"{stress_metrics.mean_absolute_percentage_error:>14.3f} %"
    )

    print(
        f"{'Tip deflection':<20}"
        f"{deflection_metrics.mae * 1000.0:>12.5f} mm"
        f"{deflection_metrics.rmse * 1000.0:>12.5f} mm"
        f"{deflection_metrics.mean_absolute_percentage_error:>14.3f} %"
    )

    print(
        f"{'Mode-1 frequency':<20}"
        f"{frequency_metrics.mae:>12.4f} Hz"
        f"{frequency_metrics.rmse:>12.4f} Hz"
        f"{frequency_metrics.mean_absolute_percentage_error:>14.3f} %"
    )


def main() -> None:
    FIGURE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    VALIDATION_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Loading FEA dataset from {DATASET_PATH}...")

    features, targets = load_surrogate_arrays(DATASET_PATH)

    print(f"Loaded {features.shape[0]} FEA samples.")

    print()
    print("Training surrogate using deterministic train/validation/test split...")

    training_result = train_surrogate(
        features,
        targets,
        seed=42,
        batch_size=32,
        learning_rate=1e-3,
        maximum_epochs=1000,
        patience=50,
    )

    test_indices = training_result.split.test_indices

    test_features = features[test_indices]

    test_targets = targets[test_indices]

    print()
    print(f"Evaluating {len(test_indices)} held-out test samples...")

    predictions = predict(
        training_result.model,
        test_features,
        feature_standardization=(training_result.feature_standardization),
        target_standardization=(training_result.target_standardization),
    )

    stress_reference = test_targets[:, 0]

    stress_prediction = predictions[:, 0]

    deflection_reference = test_targets[:, 1]

    deflection_prediction = predictions[:, 1]

    frequency_reference = test_targets[:, 2]

    frequency_prediction = predictions[:, 2]

    stress_metrics = calculate_metrics(
        stress_reference,
        stress_prediction,
    )

    deflection_metrics = calculate_metrics(
        deflection_reference,
        deflection_prediction,
    )

    frequency_metrics = calculate_metrics(
        frequency_reference,
        frequency_prediction,
    )

    stress_errors_percent = calculate_percentage_errors(
        stress_reference,
        stress_prediction,
    )

    deflection_errors_percent = calculate_percentage_errors(
        deflection_reference,
        deflection_prediction,
    )

    frequency_errors_percent = calculate_percentage_errors(
        frequency_reference,
        frequency_prediction,
    )

    save_loss_plot(training_result)

    save_prediction_scatter(
        stress_reference / 1e6,
        stress_prediction / 1e6,
        x_label="CalculiX FEA stress [MPa]",
        y_label="PyTorch predicted stress [MPa]",
        title=("FEA vs PyTorch — Maximum Stress"),
        output_path=(FIGURE_DIRECTORY / "fea_vs_predicted_stress.png"),
    )

    save_prediction_scatter(
        deflection_reference * 1000.0,
        deflection_prediction * 1000.0,
        x_label="CalculiX FEA tip deflection [mm]",
        y_label="PyTorch predicted tip deflection [mm]",
        title=("FEA vs PyTorch — Tip Deflection"),
        output_path=(FIGURE_DIRECTORY / "fea_vs_predicted_deflection.png"),
    )

    save_prediction_scatter(
        frequency_reference,
        frequency_prediction,
        x_label="CalculiX FEA mode-1 frequency [Hz]",
        y_label="PyTorch predicted mode-1 frequency [Hz]",
        title=("FEA vs PyTorch — Mode-1 Frequency"),
        output_path=(FIGURE_DIRECTORY / "fea_vs_predicted_frequency.png"),
    )

    save_error_distribution(
        stress_errors_percent,
        deflection_errors_percent,
        frequency_errors_percent,
    )

    save_metrics_csv(
        stress_metrics=stress_metrics,
        deflection_metrics=deflection_metrics,
        frequency_metrics=frequency_metrics,
    )

    save_test_predictions(
        reference=test_targets,
        prediction=predictions,
        test_indices=test_indices,
    )

    print_metrics(
        stress_metrics=stress_metrics,
        deflection_metrics=deflection_metrics,
        frequency_metrics=frequency_metrics,
    )

    print()
    print(f"Best validation epoch: {training_result.best_epoch}")

    print(f"Best normalized validation MSE: {min(training_result.validation_losses):.6f}")

    print()
    print("Generated figures:")

    for path in (
        FIGURE_DIRECTORY / "ml_training_validation_loss.png",
        FIGURE_DIRECTORY / "fea_vs_predicted_stress.png",
        FIGURE_DIRECTORY / "fea_vs_predicted_deflection.png",
        FIGURE_DIRECTORY / "fea_vs_predicted_frequency.png",
        FIGURE_DIRECTORY / "prediction_error_distribution.png",
    ):
        print(f"  {path}")

    print()
    print("Generated validation data:")

    print("  " + str(VALIDATION_DIRECTORY / "ml_test_metrics.csv"))

    print("  " + str(VALIDATION_DIRECTORY / "ml_test_predictions.csv"))


if __name__ == "__main__":
    main()
