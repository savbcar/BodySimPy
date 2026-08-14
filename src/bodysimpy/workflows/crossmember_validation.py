from dataclasses import dataclass
from pathlib import Path

from bodysimpy.analysis.validation import relative_error_percent
from bodysimpy.config.loader import load_config
from bodysimpy.modeling.crossmember import build_crossmember_model
from bodysimpy.solvers.analytical import AnalyticalSolver
from bodysimpy.solvers.calculix import CalculiXSolver


@dataclass(frozen=True, slots=True)
class CrossmemberValidationResult:
    analytical_tip_deflection_m: float
    fea_tip_deflection_m: float
    tip_deflection_error_percent: float


def validate_crossmember(
    config_path: str | Path,
) -> CrossmemberValidationResult:
    """Validate the crossmember FEA model against the analytical reference."""

    config = load_config(config_path)
    model = build_crossmember_model(config)

    analytical_result = AnalyticalSolver().run(model)
    fea_result = CalculiXSolver().run(model)

    error_percent = relative_error_percent(
        reference=analytical_result.tip_deflection_m,
        value=fea_result.tip_deflection_m,
    )

    return CrossmemberValidationResult(
        analytical_tip_deflection_m=analytical_result.tip_deflection_m,
        fea_tip_deflection_m=fea_result.tip_deflection_m,
        tip_deflection_error_percent=error_percent,
    )
