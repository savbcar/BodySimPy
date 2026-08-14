import shutil

import pytest

from bodysimpy.workflows.crossmember_validation import validate_crossmember


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_crossmember_validation() -> None:
    result = validate_crossmember("configs/baseline_crossmember.yaml")

    assert result.analytical_tip_deflection_m > 0.0
    assert result.fea_tip_deflection_m > 0.0

    assert result.tip_deflection_error_percent < 5.0
