import shutil

import pytest

from bodysimpy.analysis.stochastic import (
    run_stochastic_study,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_stochastic_study_runs_real_solver() -> None:
    config = load_config("configs/stochastic_crossmember.yaml")

    assert config.stochastic is not None

    model = build_crossmember_model(config)

    result = run_stochastic_study(
        model,
        config.stochastic,
        sample_count=3,
    )

    assert len(result.samples) == 3

    for sample in result.samples:
        assert sample.max_stress_pa > 0.0
        assert sample.mode_1_frequency_hz > 0.0

    assert result.stress_summary.mean > 0.0
    assert result.frequency_summary.mean > 0.0
