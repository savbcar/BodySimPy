import shutil

import pytest

from bodysimpy.config.loader import load_config
from bodysimpy.ml.dataset_generation import generate_fea_dataset
from bodysimpy.ml.design_space import generate_design_points
from bodysimpy.modeling.crossmember import build_crossmember_model


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_generate_small_fea_surrogate_dataset() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    designs = generate_design_points(
        sample_count=2,
        seed=42,
    )

    samples = generate_fea_dataset(
        model,
        designs,
        max_workers=2,
    )

    assert len(samples) == 2

    for sample in samples:
        assert sample.max_stress_pa > 0.0
        assert sample.tip_deflection_m > 0.0
        assert sample.mode_1_frequency_hz > 0.0
