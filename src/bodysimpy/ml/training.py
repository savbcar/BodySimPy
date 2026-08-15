from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from numpy.typing import NDArray
from torch import Tensor, nn
from torch.optim import Adam
from torch.utils.data import DataLoader

from bodysimpy.ml.dataset import (
    Standardization,
    StructuralSurrogateDataset,
    fit_standardization,
    standardize,
)
from bodysimpy.ml.model import StructuralSurrogate


@dataclass(frozen=True, slots=True)
class DataSplit:
    train_indices: NDArray[np.int64]
    validation_indices: NDArray[np.int64]
    test_indices: NDArray[np.int64]


@dataclass(frozen=True, slots=True)
class TrainingResult:
    model: StructuralSurrogate
    feature_standardization: Standardization
    target_standardization: Standardization
    train_losses: tuple[float, ...]
    validation_losses: tuple[float, ...]
    best_epoch: int
    split: DataSplit


def create_data_split(
    sample_count: int,
    *,
    seed: int,
) -> DataSplit:
    if sample_count < 10:
        raise ValueError("At least ten samples are required.")

    rng = np.random.default_rng(seed)

    indices = rng.permutation(sample_count)

    train_end = int(0.70 * sample_count)

    validation_end = int(0.85 * sample_count)

    return DataSplit(
        train_indices=indices[:train_end],
        validation_indices=indices[train_end:validation_end],
        test_indices=indices[validation_end:],
    )


def _mean_loss(
    model: StructuralSurrogate,
    loader: DataLoader[tuple[Tensor, Tensor]],
    loss_function: nn.Module,
    device: torch.device,
) -> float:
    model.eval()

    losses: list[float] = []

    with torch.no_grad():
        for features, targets in loader:
            features = features.to(device)
            targets = targets.to(device)

            predictions = model(features)

            loss = loss_function(
                predictions,
                targets,
            )

            losses.append(float(loss.item()))

    return float(np.mean(losses))


def train_surrogate(
    features: NDArray[np.float64],
    targets: NDArray[np.float64],
    *,
    seed: int = 42,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    maximum_epochs: int = 1000,
    patience: int = 50,
) -> TrainingResult:
    """Train the BodySimPy structural surrogate."""

    torch.manual_seed(seed)

    split = create_data_split(
        features.shape[0],
        seed=seed,
    )

    train_features = features[split.train_indices]

    train_targets = targets[split.train_indices]

    feature_statistics = fit_standardization(train_features)

    target_statistics = fit_standardization(train_targets)

    normalized_features = standardize(
        features,
        feature_statistics,
    )

    normalized_targets = standardize(
        targets,
        target_statistics,
    )

    train_dataset = StructuralSurrogateDataset(
        normalized_features[split.train_indices],
        normalized_targets[split.train_indices],
    )

    validation_dataset = StructuralSurrogateDataset(
        normalized_features[split.validation_indices],
        normalized_targets[split.validation_indices],
    )

    training_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = StructuralSurrogate().to(device)

    optimizer = Adam(
        model.parameters(),
        lr=learning_rate,
    )

    loss_function = nn.MSELoss()

    train_losses: list[float] = []
    validation_losses: list[float] = []

    best_validation_loss = float("inf")
    best_model_state = deepcopy(model.state_dict())

    best_epoch = 0
    epochs_without_improvement = 0

    for epoch in range(
        1,
        maximum_epochs + 1,
    ):
        model.train()

        batch_losses: list[float] = []

        for features_batch, targets_batch in training_loader:
            features_batch = features_batch.to(device)

            targets_batch = targets_batch.to(device)

            optimizer.zero_grad()

            predictions = model(features_batch)

            loss = loss_function(
                predictions,
                targets_batch,
            )

            loss.backward()

            optimizer.step()

            batch_losses.append(float(loss.item()))

        training_loss = float(np.mean(batch_losses))

        validation_loss = _mean_loss(
            model,
            validation_loader,
            loss_function,
            device,
        )

        train_losses.append(training_loss)

        validation_losses.append(validation_loss)

        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss

            best_model_state = deepcopy(model.state_dict())

            best_epoch = epoch
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            break

    model.load_state_dict(best_model_state)

    model.to("cpu")
    model.eval()

    return TrainingResult(
        model=model,
        feature_standardization=(feature_statistics),
        target_standardization=(target_statistics),
        train_losses=tuple(train_losses),
        validation_losses=tuple(validation_losses),
        best_epoch=best_epoch,
        split=split,
    )


def save_training_checkpoint(
    result: TrainingResult,
    path: str | Path,
) -> None:
    """Save trained model and preprocessing metadata."""

    checkpoint_path = Path(path)

    checkpoint_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(
        {
            "model_state_dict": (result.model.state_dict()),
            "feature_mean": (result.feature_standardization.mean),
            "feature_standard_deviation": (result.feature_standardization.standard_deviation),
            "target_mean": (result.target_standardization.mean),
            "target_standard_deviation": (result.target_standardization.standard_deviation),
            "best_epoch": (result.best_epoch),
        },
        checkpoint_path,
    )
