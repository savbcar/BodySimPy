import numpy as np
import pytest

from bodysimpy.ml.dataset import (
    StructuralSurrogateDataset,
    fit_standardization,
    inverse_standardize,
    standardize,
)


def test_surrogate_dataset_shapes() -> None:
    features = np.ones(
        (10, 6),
        dtype=np.float64,
    )

    targets = np.ones(
        (10, 3),
        dtype=np.float64,
    )

    dataset = StructuralSurrogateDataset(
        features,
        targets,
    )

    features_row, targets_row = dataset[0]

    assert len(dataset) == 10
    assert tuple(features_row.shape) == (6,)
    assert tuple(targets_row.shape) == (3,)


def test_standardization_round_trip() -> None:
    values = np.array(
        [
            [1.0, 10.0],
            [2.0, 20.0],
            [3.0, 30.0],
        ],
        dtype=np.float64,
    )

    statistics = fit_standardization(values)

    normalized = standardize(
        values,
        statistics,
    )

    recovered = inverse_standardize(
        normalized,
        statistics,
    )

    assert recovered == pytest.approx(values)
