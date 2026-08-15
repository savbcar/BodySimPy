import shutil

import pytest

from bodysimpy.analysis.fea_validation import (
    run_static_validation_study,
)
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import build_crossmember_model


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_static_validation_study_runs_multiple_meshes() -> None:
    config = load_config("configs/baseline_crossmember.yaml")
    model = build_crossmember_model(config)

    points = run_static_validation_study(
        model,
        element_counts=(5, 10),
    )

    assert len(points) == 2
    assert points[0].mesh_elements == 5
    assert points[1].mesh_elements == 10

    for point in points:
        assert point.fea_tip_deflection_m > 0.0
        assert point.fea_max_axial_stress_pa > 0.0
