import shutil

import pytest

from bodysimpy.analysis.parameter_sweep import (
    run_thickness_sweep,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_thickness_sweep_runs_real_solver() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    points = run_thickness_sweep(
        model,
        thickness_values_m=(
            0.0010,
            0.0020,
        ),
        max_workers=1,
    )

    assert len(points) == 2

    assert points[0].thickness_m == pytest.approx(0.0010)

    assert points[1].thickness_m == pytest.approx(0.0020)

    for point in points:
        assert point.max_stress_pa > 0.0
        assert point.tip_deflection_m > 0.0
        assert point.mode_1_frequency_hz > 0.0
        assert point.mass_kg > 0.0

    assert points[1].mass_kg > points[0].mass_kg


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_parallel_thickness_sweep() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    points = run_thickness_sweep(
        model,
        thickness_values_m=(
            0.0010,
            0.0015,
        ),
        max_workers=2,
    )

    assert len(points) == 2

    assert points[0].thickness_m == pytest.approx(0.0010)

    assert points[1].thickness_m == pytest.approx(0.0015)
