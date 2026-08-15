from dataclasses import replace
from pathlib import Path

from bodysimpy.config.loader import load_config
from bodysimpy.ml.dataset_generation import (
    generate_fea_dataset,
    write_fea_dataset,
)
from bodysimpy.ml.design_space import (
    generate_design_points,
)
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)

SAMPLE_COUNT = 200
RANDOM_SEED = 20260815
MAX_WORKERS = 4


def main() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    base_model = build_crossmember_model(config)

    holdout_model = replace(
        base_model,
        name=(f"{base_model.name}_ml_holdout"),
    )

    designs = generate_design_points(
        sample_count=SAMPLE_COUNT,
        seed=RANDOM_SEED,
    )

    samples = generate_fea_dataset(
        holdout_model,
        designs,
        max_workers=MAX_WORKERS,
    )

    output_path = Path("data/surrogate/fea_surrogate_holdout.csv")

    write_fea_dataset(
        samples,
        output_path,
    )

    print()
    print(f"Generated {len(samples)} independent holdout samples.")

    print(output_path)


if __name__ == "__main__":
    main()
