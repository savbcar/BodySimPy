import shutil

import pytest

from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)
from bodysimpy.solvers.calculix import (
    CalculiXSolver,
)


@pytest.mark.skipif(
    shutil.which("ccx") is None,
    reason="CalculiX is not installed.",
)
def test_calculix_modal_analysis() -> None:
    config = load_config("configs/baseline_crossmember.yaml")

    model = build_crossmember_model(config)

    result = CalculiXSolver().run_modal(
        model,
        modes=3,
    )

    assert result.solver_name == "calculix"

    assert len(result.natural_frequencies_hz) == 3

    assert all(frequency > 0.0 for frequency in result.natural_frequencies_hz)

    assert (
        result.natural_frequencies_hz[0]
        < result.natural_frequencies_hz[1]
        < result.natural_frequencies_hz[2]
    )
