from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from numpy.typing import NDArray
from torch import Tensor
from torch.utils.data import Dataset

FEATURE_COLUMNS = (
    "thickness_m",
    "height_m",
    "width_m",
    "youngs_modulus_pa",
    "density_kg_m3",
    "tip_force_n",
)

TARGET_COLUMNS = (
    "max_stress_pa",
    "tip_deflection_m",
    "mode_1_frequency_hz",
)


@dataclass(frozen=True, slots=True)
class Standardization:
    mean: NDArray[np.float64]
    standard_deviation: NDArray[np.float64]


class StructuralSurrogateDataset(Dataset[tuple[Tensor, Tensor]]):
    """PyTorch dataset for structural surrogate modelling."""

    def __init__(
        self,
        features: NDArray[np.float64],
        targets: NDArray[np.float64],
    ) -> None:
        if features.shape[0] != targets.shape[0]:
            raise ValueError("Feature and target row counts must match.")

        self._features = torch.tensor(
            features,
            dtype=torch.float32,
        )

        self._targets = torch.tensor(
            targets,
            dtype=torch.float32,
        )

    def __len__(self) -> int:
        return self._features.shape[0]

    def __getitem__(
        self,
        index: int,
    ) -> tuple[Tensor, Tensor]:
        return (
            self._features[index],
            self._targets[index],
        )


def load_surrogate_arrays(
    path: str | Path,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
]:
    dataframe = pd.read_csv(path)

    features = dataframe[list(FEATURE_COLUMNS)].to_numpy(dtype=np.float64)

    targets = dataframe[list(TARGET_COLUMNS)].to_numpy(dtype=np.float64)

    return features, targets


def fit_standardization(
    values: NDArray[np.float64],
) -> Standardization:
    mean = np.mean(
        values,
        axis=0,
    )

    standard_deviation = np.std(
        values,
        axis=0,
    )

    if np.any(standard_deviation == 0.0):
        raise ValueError("Cannot standardize a constant column.")

    return Standardization(
        mean=mean,
        standard_deviation=standard_deviation,
    )


def standardize(
    values: NDArray[np.float64],
    statistics: Standardization,
) -> NDArray[np.float64]:
    return (values - statistics.mean) / statistics.standard_deviation


def inverse_standardize(
    values: NDArray[np.float64],
    statistics: Standardization,
) -> NDArray[np.float64]:
    return values * statistics.standard_deviation + statistics.mean
