from pathlib import Path

from bodysimpy.config.loader import load_config
from bodysimpy.ml.dataset_generation import (
    generate_fea_dataset,
    write_fea_dataset,
)
from bodysimpy.ml.design_space import generate_design_points
from bodysimpy.modeling.crossmember import build_crossmember_model

SAMPLE_COUNT = 500
RANDOM_SEED = 42
MAX_WORKERS = 4


def main() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    designs = generate_design_points(
        sample_count=SAMPLE_COUNT,
        seed=RANDOM_SEED,
    )

    print(f"Generated {len(designs)} Latin Hypercube design points.")

    samples = generate_fea_dataset(
        model,
        designs,
        max_workers=MAX_WORKERS,
    )

    output_path = Path("data/surrogate/fea_surrogate_dataset.csv")

    write_fea_dataset(
        samples,
        output_path,
    )

    print()
    print(f"Saved {len(samples)} FEA samples to:")
    print(output_path)


if __name__ == "__main__":
    main()
