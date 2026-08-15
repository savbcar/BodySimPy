from dataclasses import dataclass

import numpy as np
import torch
from numpy.typing import NDArray

from bodysimpy.ml.dataset import (
    Standardization,
    inverse_standardize,
    standardize,
)
from bodysimpy.ml.model import StructuralSurrogate


@dataclass(frozen=True, slots=True)
class TargetMetrics:
    """Regression metrics for one structural response."""

    mae: float
    rmse: float
    mean_absolute_percentage_error: float


def predict(
    model: StructuralSurrogate,
    features: NDArray[np.float64],
    *,
    feature_standardization: Standardization,
    target_standardization: Standardization,
) -> NDArray[np.float64]:
    """Predict structural responses in physical units."""

    normalized_features = standardize(
        features,
        feature_standardization,
    )

    feature_tensor = torch.tensor(
        normalized_features,
        dtype=torch.float32,
    )

    model.eval()

    with torch.no_grad():
        normalized_predictions = model(feature_tensor).cpu().numpy().astype(np.float64)

    return inverse_standardize(
        normalized_predictions,
        target_standardization,
    )


def calculate_metrics(
    reference: NDArray[np.float64],
    prediction: NDArray[np.float64],
) -> TargetMetrics:
    """Calculate MAE, RMSE and MAPE."""

    if reference.shape != prediction.shape:
        raise ValueError("Reference and prediction arrays must have matching shapes.")

    if reference.size == 0:
        raise ValueError("At least one prediction is required.")

    if np.any(reference == 0.0):
        raise ValueError("MAPE cannot be calculated with zero reference values.")

    errors = prediction - reference

    mae = float(np.mean(np.abs(errors)))

    rmse = float(np.sqrt(np.mean(errors**2)))

    percentage_errors = np.abs(errors) / np.abs(reference) * 100.0

    return TargetMetrics(
        mae=mae,
        rmse=rmse,
        mean_absolute_percentage_error=float(np.mean(percentage_errors)),
    )


def calculate_percentage_errors(
    reference: NDArray[np.float64],
    prediction: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Return absolute percentage error for each prediction."""

    if reference.shape != prediction.shape:
        raise ValueError("Reference and prediction arrays must have matching shapes.")

    if np.any(reference == 0.0):
        raise ValueError("Percentage error cannot use zero reference values.")

    return np.abs(prediction - reference) / np.abs(reference) * 100.0
