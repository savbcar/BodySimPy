import pytest

from bodysimpy.ml.experiment import (
    build_nested_training_subsets,
    calculate_runtime_tradeoff,
    split_holdout_indices,
)


def test_training_subsets_are_nested() -> None:
    subsets = build_nested_training_subsets(
        pool_size=500,
        sample_counts=(50, 100, 250, 500),
        seed=42,
    )

    assert tuple(subset.sample_count for subset in subsets) == (
        50,
        100,
        250,
        500,
    )

    first = set(subsets[0].indices.tolist())
    second = set(subsets[1].indices.tolist())
    third = set(subsets[2].indices.tolist())
    fourth = set(subsets[3].indices.tolist())

    assert first < second
    assert second < third
    assert third < fourth


def test_holdout_validation_and_test_are_disjoint() -> None:
    split = split_holdout_indices(
        sample_count=200,
        validation_count=100,
        seed=42,
    )

    validation = set(split.validation_indices.tolist())

    test = set(split.test_indices.tolist())

    assert len(validation) == 100
    assert len(test) == 100
    assert validation.isdisjoint(test)


def test_runtime_tradeoff() -> None:
    result = calculate_runtime_tradeoff(
        fea_seconds_per_design=10.0,
        inference_seconds_per_design=0.01,
        training_samples=100,
        model_training_seconds=5.0,
    )

    assert result.speedup == pytest.approx(1000.0)

    assert result.break_even_queries > 100.0


def test_runtime_tradeoff_rejects_slower_surrogate() -> None:
    with pytest.raises(ValueError):
        calculate_runtime_tradeoff(
            fea_seconds_per_design=1.0,
            inference_seconds_per_design=2.0,
            training_samples=100,
            model_training_seconds=5.0,
        )
