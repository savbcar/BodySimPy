from pathlib import Path

from bodysimpy.ml.dataset import (
    load_surrogate_arrays,
)
from bodysimpy.ml.training import (
    save_training_checkpoint,
    train_surrogate,
)


def main() -> None:
    dataset_path = Path("data/surrogate/fea_surrogate_dataset.csv")

    features, targets = load_surrogate_arrays(dataset_path)

    result = train_surrogate(
        features,
        targets,
        seed=42,
        batch_size=32,
        learning_rate=1e-3,
        maximum_epochs=1000,
        patience=50,
    )

    save_training_checkpoint(
        result,
        "models/checkpoints/structural_surrogate.pt",
    )

    print()
    print("BodySimPy PyTorch Surrogate")
    print("=" * 55)
    print(f"Dataset samples: {features.shape[0]}")
    print(f"Training samples: {len(result.split.train_indices)}")
    print(f"Validation samples: {len(result.split.validation_indices)}")
    print(f"Test samples: {len(result.split.test_indices)}")
    print(f"Best epoch: {result.best_epoch}")
    print(f"Final stored validation loss: {min(result.validation_losses):.6f}")


if __name__ == "__main__":
    main()
