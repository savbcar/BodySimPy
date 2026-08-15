from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class TrainingSubset:
    sample_count: int
    indices: NDArray[np.int64]


@dataclass(frozen=True, slots=True)
class HoldoutSplit:
    validation_indices: NDArray[np.int64]
    test_indices: NDArray[np.int64]


@dataclass(frozen=True, slots=True)
class RuntimeTradeoff:
    fea_seconds_per_design: float
    inference_seconds_per_design: float
    speedup: float
    break_even_queries: float


def build_nested_training_subsets(
    *,
    pool_size: int,
    sample_counts: tuple[int, ...],
    seed: int,
) -> tuple[TrainingSubset, ...]:
    """Create deterministic nested subsets from one training pool."""

    if pool_size <= 0:
        raise ValueError("Training pool size must be positive.")

    if not sample_counts:
        raise ValueError("At least one training sample count is required.")

    if any(count <= 0 for count in sample_counts):
        raise ValueError("Training sample counts must be positive.")

    if any(count > pool_size for count in sample_counts):
        raise ValueError("Training sample count exceeds the available pool.")

    if tuple(sorted(sample_counts)) != sample_counts:
        raise ValueError("Training sample counts must be increasing.")

    rng = np.random.default_rng(seed)

    order = rng.permutation(pool_size).astype(np.int64)

    return tuple(
        TrainingSubset(
            sample_count=count,
            indices=order[:count].copy(),
        )
        for count in sample_counts
    )


def split_holdout_indices(
    *,
    sample_count: int,
    validation_count: int,
    seed: int,
) -> HoldoutSplit:
    """Split an independent holdout dataset into validation and test sets."""

    if sample_count <= 1:
        raise ValueError("Holdout dataset must contain at least two samples.")

    if validation_count <= 0 or validation_count >= sample_count:
        raise ValueError("Validation count must lie inside the holdout sample range.")

    rng = np.random.default_rng(seed)

    order = rng.permutation(sample_count).astype(np.int64)

    return HoldoutSplit(
        validation_indices=(order[:validation_count].copy()),
        test_indices=(order[validation_count:].copy()),
    )


def calculate_runtime_tradeoff(
    *,
    fea_seconds_per_design: float,
    inference_seconds_per_design: float,
    training_samples: int,
    model_training_seconds: float,
) -> RuntimeTradeoff:
    """Calculate surrogate speedup and sequential break-even point."""

    if fea_seconds_per_design <= 0.0:
        raise ValueError("FEA runtime must be positive.")

    if inference_seconds_per_design <= 0.0:
        raise ValueError("Inference runtime must be positive.")

    if training_samples <= 0:
        raise ValueError("Training sample count must be positive.")

    if model_training_seconds < 0.0:
        raise ValueError("Model training runtime cannot be negative.")

    runtime_saving = fea_seconds_per_design - inference_seconds_per_design

    if runtime_saving <= 0.0:
        raise ValueError(
            "Surrogate inference must be faster than FEA "
            "for a positive computational break-even point."
        )

    speedup = fea_seconds_per_design / inference_seconds_per_design

    estimated_upfront_seconds = training_samples * fea_seconds_per_design + model_training_seconds

    break_even_queries = estimated_upfront_seconds / runtime_saving

    return RuntimeTradeoff(
        fea_seconds_per_design=(fea_seconds_per_design),
        inference_seconds_per_design=(inference_seconds_per_design),
        speedup=speedup,
        break_even_queries=break_even_queries,
    )
