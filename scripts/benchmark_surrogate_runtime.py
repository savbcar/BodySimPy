import csv
from dataclasses import replace
from pathlib import Path
from statistics import median
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from bodysimpy.config.loader import load_config
from bodysimpy.ml.dataset import Standardization
from bodysimpy.ml.dataset_generation import evaluate_design_point
from bodysimpy.ml.design_space import (
    SurrogateDesignPoint,
    generate_design_points,
)
from bodysimpy.ml.experiment import calculate_runtime_tradeoff
from bodysimpy.ml.model import StructuralSurrogate
from bodysimpy.modeling.crossmember import build_crossmember_model

BENCHMARK_DESIGNS = 10
BENCHMARK_SEED = 20260816

WARMUP_CALLS = 100
INFERENCE_REPETITIONS_PER_DESIGN = 2_000

CHECKPOINT_PATH = Path("models/checkpoints/structural_surrogate.pt")

SAMPLE_EFFICIENCY_PATH = Path("docs/validation/ml_sample_efficiency.csv")

RUNTIME_CSV_PATH = Path("docs/validation/ml_runtime_benchmark.csv")

BREAK_EVEN_CSV_PATH = Path("docs/validation/ml_break_even.csv")

RUNTIME_FIGURE_PATH = Path("docs/figures/ml_runtime_comparison.png")

BREAK_EVEN_FIGURE_PATH = Path("docs/figures/ml_break_even_vs_training_size.png")


def _as_float64_array(
    value: object,
    *,
    name: str,
) -> np.ndarray:
    """Convert checkpoint preprocessing data to a 1D float array."""

    array = np.asarray(
        value,
        dtype=np.float64,
    )

    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array.")

    return array


def load_surrogate_checkpoint() -> tuple[
    StructuralSurrogate,
    Standardization,
    Standardization,
]:
    """Load the trained surrogate and preprocessing statistics."""

    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(
            "Surrogate checkpoint was not found at "
            f"{CHECKPOINT_PATH}. "
            "Run scripts/train_surrogate.py first."
        )

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location="cpu",
        weights_only=False,
    )

    if not isinstance(checkpoint, dict):
        raise TypeError("Surrogate checkpoint must contain a dictionary.")

    required_keys = {
        "model_state_dict",
        "feature_mean",
        "feature_standard_deviation",
        "target_mean",
        "target_standard_deviation",
    }

    missing_keys = required_keys - checkpoint.keys()

    if missing_keys:
        missing = ", ".join(sorted(missing_keys))

        raise KeyError(f"Surrogate checkpoint is missing: {missing}")

    model = StructuralSurrogate()

    model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()

    feature_standardization = Standardization(
        mean=_as_float64_array(
            checkpoint["feature_mean"],
            name="feature_mean",
        ),
        standard_deviation=_as_float64_array(
            checkpoint["feature_standard_deviation"],
            name="feature_standard_deviation",
        ),
    )

    target_standardization = Standardization(
        mean=_as_float64_array(
            checkpoint["target_mean"],
            name="target_mean",
        ),
        standard_deviation=_as_float64_array(
            checkpoint["target_standard_deviation"],
            name="target_standard_deviation",
        ),
    )

    return (
        model,
        feature_standardization,
        target_standardization,
    )


def design_to_feature_array(
    design: SurrogateDesignPoint,
) -> np.ndarray:
    """Convert one structural design into the six ML inputs."""

    return np.array(
        [
            [
                design.thickness_m,
                design.height_m,
                design.width_m,
                design.youngs_modulus_pa,
                design.density_kg_m3,
                design.tip_force_n,
            ]
        ],
        dtype=np.float64,
    )


def predict_single_design(
    model: StructuralSurrogate,
    design: SurrogateDesignPoint,
    *,
    feature_standardization: Standardization,
    target_standardization: Standardization,
) -> np.ndarray:
    """Run complete end-to-end inference for one structural design."""

    features = design_to_feature_array(design)

    normalized_features = (
        features - feature_standardization.mean
    ) / feature_standardization.standard_deviation

    feature_tensor = torch.tensor(
        normalized_features,
        dtype=torch.float32,
    )

    with torch.inference_mode():
        normalized_prediction = model(feature_tensor).cpu().numpy().astype(np.float64)

    prediction = (
        normalized_prediction * target_standardization.standard_deviation
        + target_standardization.mean
    )

    return prediction[0]


def warm_up_surrogate(
    model: StructuralSurrogate,
    designs: tuple[SurrogateDesignPoint, ...],
    *,
    feature_standardization: Standardization,
    target_standardization: Standardization,
) -> None:
    """Warm up PyTorch before latency measurements."""

    for call_index in range(WARMUP_CALLS):
        design = designs[call_index % len(designs)]

        predict_single_design(
            model,
            design,
            feature_standardization=(feature_standardization),
            target_standardization=(target_standardization),
        )


def benchmark_fea(
    designs: tuple[SurrogateDesignPoint, ...],
) -> tuple[float, ...]:
    """Measure sequential static-plus-modal FEA runtime."""

    config = load_config("configs/baseline_crossmember.yaml")

    base_model = build_crossmember_model(config)

    benchmark_model = replace(
        base_model,
        name=(f"{base_model.name}_runtime_benchmark"),
    )

    durations: list[float] = []

    print()
    print("Benchmarking CalculiX FEA")
    print("-" * 70)

    for design in designs:
        start = perf_counter()

        sample = evaluate_design_point(
            benchmark_model,
            design,
        )

        elapsed = perf_counter() - start

        durations.append(elapsed)

        print(
            f"Design {design.sample_index:>2}: "
            f"{elapsed:.6f} s | "
            f"stress="
            f"{sample.max_stress_pa / 1e6:.3f} MPa | "
            f"deflection="
            f"{sample.tip_deflection_m * 1000.0:.4f} mm | "
            f"mode1="
            f"{sample.mode_1_frequency_hz:.4f} Hz"
        )

    return tuple(durations)


def benchmark_surrogate(
    model: StructuralSurrogate,
    designs: tuple[SurrogateDesignPoint, ...],
    *,
    feature_standardization: Standardization,
    target_standardization: Standardization,
) -> tuple[float, ...]:
    """Measure end-to-end single-design surrogate inference."""

    print()
    print("Warming up PyTorch surrogate")
    print("-" * 70)

    warm_up_surrogate(
        model,
        designs,
        feature_standardization=(feature_standardization),
        target_standardization=(target_standardization),
    )

    print(f"Completed {WARMUP_CALLS} warm-up calls.")

    durations: list[float] = []

    print()
    print("Benchmarking PyTorch inference")
    print("-" * 70)

    for design in designs:
        start = perf_counter()

        for _ in range(INFERENCE_REPETITIONS_PER_DESIGN):
            predict_single_design(
                model,
                design,
                feature_standardization=(feature_standardization),
                target_standardization=(target_standardization),
            )

        elapsed = perf_counter() - start

        seconds_per_design = elapsed / INFERENCE_REPETITIONS_PER_DESIGN

        durations.append(seconds_per_design)

        print(f"Design {design.sample_index:>2}: {seconds_per_design * 1e6:.3f} microseconds/query")

    return tuple(durations)


def write_runtime_csv(
    fea_durations: tuple[float, ...],
    inference_durations: tuple[float, ...],
) -> None:
    """Write individual runtime measurements to CSV."""

    RUNTIME_CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with RUNTIME_CSV_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.writer(stream)

        writer.writerow(
            [
                "design",
                "fea_seconds",
                "surrogate_seconds",
                "surrogate_microseconds",
                "speedup",
            ]
        )

        for index, (
            fea_seconds,
            inference_seconds,
        ) in enumerate(
            zip(
                fea_durations,
                inference_durations,
                strict=True,
            ),
            start=1,
        ):
            writer.writerow(
                [
                    index,
                    fea_seconds,
                    inference_seconds,
                    inference_seconds * 1e6,
                    fea_seconds / inference_seconds,
                ]
            )


def write_runtime_plot(
    *,
    median_fea_seconds: float,
    median_inference_seconds: float,
) -> None:
    """Plot median FEA and surrogate runtimes."""

    RUNTIME_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    labels = [
        "CalculiX\nstatic + modal",
        "PyTorch\nsurrogate",
    ]

    values = [
        median_fea_seconds,
        median_inference_seconds,
    ]

    plt.figure(figsize=(7, 5))

    plt.bar(
        labels,
        values,
    )

    plt.yscale("log")

    plt.ylabel("Median runtime per design [s, log scale]")

    plt.title("FEA vs Surrogate Runtime")

    plt.tight_layout()

    plt.savefig(
        RUNTIME_FIGURE_PATH,
        dpi=200,
    )

    plt.close()


def load_training_runtime_summary() -> dict[int, float]:
    """Read median ML training time for each dataset size."""

    if not SAMPLE_EFFICIENCY_PATH.exists():
        raise FileNotFoundError(
            "Sample-efficiency results were not found at "
            f"{SAMPLE_EFFICIENCY_PATH}. "
            "Run scripts/run_ml_tradeoff_experiment.py first."
        )

    dataframe = pd.read_csv(SAMPLE_EFFICIENCY_PATH)

    required_columns = {
        "training_samples",
        "training_seconds",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise ValueError(f"Sample-efficiency CSV is missing: {missing}")

    grouped = dataframe.groupby(
        "training_samples",
        sort=True,
    )["training_seconds"].median()

    return {
        int(sample_count): float(training_seconds)
        for (
            sample_count,
            training_seconds,
        ) in grouped.items()
    }


def write_break_even_outputs(
    *,
    median_fea_seconds: float,
    median_inference_seconds: float,
) -> None:
    """Calculate full-cost and sunk-data break-even estimates."""

    training_runtime_by_size = load_training_runtime_summary()

    rows: list[
        tuple[
            int,
            float,
            float,
            float,
            float,
            float,
            float,
        ]
    ] = []

    runtime_saving_per_query = median_fea_seconds - median_inference_seconds

    if runtime_saving_per_query <= 0.0:
        raise ValueError("Measured surrogate inference is not faster than FEA.")

    for (
        training_samples,
        training_seconds,
    ) in sorted(training_runtime_by_size.items()):
        tradeoff = calculate_runtime_tradeoff(
            fea_seconds_per_design=(median_fea_seconds),
            inference_seconds_per_design=(median_inference_seconds),
            training_samples=(training_samples),
            model_training_seconds=(training_seconds),
        )

        incremental_break_even_queries = training_seconds / runtime_saving_per_query

        rows.append(
            (
                training_samples,
                training_seconds,
                tradeoff.fea_seconds_per_design,
                tradeoff.inference_seconds_per_design,
                tradeoff.speedup,
                tradeoff.break_even_queries,
                incremental_break_even_queries,
            )
        )

    BREAK_EVEN_CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with BREAK_EVEN_CSV_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as stream:
        writer = csv.writer(stream)

        writer.writerow(
            [
                "training_samples",
                "median_model_training_seconds",
                "median_fea_seconds_per_design",
                "median_surrogate_seconds_per_design",
                "speedup",
                ("sequential_equivalent_break_even_queries"),
                ("incremental_break_even_queries_if_fea_data_is_sunk"),
            ]
        )

        writer.writerows(rows)

    write_break_even_plot(rows)


def write_break_even_plot(
    rows: list[
        tuple[
            int,
            float,
            float,
            float,
            float,
            float,
            float,
        ]
    ],
) -> None:
    """Plot break-even query count versus training-set size."""

    BREAK_EVEN_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    training_sizes = [row[0] for row in rows]

    full_break_even = [row[5] for row in rows]

    incremental_break_even = [row[6] for row in rows]

    plt.figure(figsize=(8, 5))

    plt.plot(
        training_sizes,
        full_break_even,
        marker="o",
        label=("Full FEA-data + training cost"),
    )

    plt.plot(
        training_sizes,
        incremental_break_even,
        marker="o",
        label=("Training-only cost (FEA data already available)"),
    )

    plt.xlabel("Training samples")

    plt.ylabel("Break-even future queries")

    plt.title("Surrogate Computational Break-Even")

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        BREAK_EVEN_FIGURE_PATH,
        dpi=200,
    )

    plt.close()


def main() -> None:
    print()
    print("BodySimPy Surrogate Runtime Benchmark")
    print("=" * 70)

    (
        model,
        feature_standardization,
        target_standardization,
    ) = load_surrogate_checkpoint()

    designs = generate_design_points(
        sample_count=BENCHMARK_DESIGNS,
        seed=BENCHMARK_SEED,
    )

    print()
    print(f"Generated {len(designs)} fresh benchmark designs.")

    fea_durations = benchmark_fea(designs)

    inference_durations = benchmark_surrogate(
        model,
        designs,
        feature_standardization=(feature_standardization),
        target_standardization=(target_standardization),
    )

    write_runtime_csv(
        fea_durations,
        inference_durations,
    )

    median_fea_seconds = float(median(fea_durations))

    median_inference_seconds = float(median(inference_durations))

    speedup = median_fea_seconds / median_inference_seconds

    write_runtime_plot(
        median_fea_seconds=(median_fea_seconds),
        median_inference_seconds=(median_inference_seconds),
    )

    write_break_even_outputs(
        median_fea_seconds=(median_fea_seconds),
        median_inference_seconds=(median_inference_seconds),
    )

    print()
    print("Runtime summary")
    print("-" * 70)

    print(f"Median FEA/design:        {median_fea_seconds:.6f} s")

    print(
        f"Median surrogate/design:  "
        f"{median_inference_seconds:.9f} s "
        f"("
        f"{median_inference_seconds * 1e6:.3f} "
        f"microseconds)"
    )

    print(f"Measured speedup:          {speedup:,.1f}x")

    print()
    print("Generated artifacts")
    print("-" * 70)

    print(RUNTIME_CSV_PATH)

    print(BREAK_EVEN_CSV_PATH)

    print(RUNTIME_FIGURE_PATH)

    print(BREAK_EVEN_FIGURE_PATH)

    print()
    print("Break-even values are sequential-equivalent estimates.")

    print("Full-cost break-even includes FEA training-data generation.")

    print("Incremental break-even treats the FEA dataset as already available.")


if __name__ == "__main__":
    main()
