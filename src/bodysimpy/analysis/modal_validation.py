from dataclasses import dataclass

from bodysimpy.analysis.validation import (
    relative_error_percent,
)
from bodysimpy.domain.structural_model import (
    StructuralModel,
)
from bodysimpy.solvers.analytical import (
    AnalyticalSolver,
)
from bodysimpy.solvers.calculix import (
    CalculiXSolver,
)


@dataclass(frozen=True, slots=True)
class ModalValidationResult:
    analytical_mode_1_hz: float
    fea_mode_1_hz: float
    mode_1_error_percent: float
    fea_frequencies_hz: tuple[float, ...]


def validate_modal_response(
    model: StructuralModel,
    *,
    modes: int = 10,
) -> ModalValidationResult:
    """Validate first FE natural frequency against beam theory."""

    analytical = AnalyticalSolver().run(model)

    if not analytical.natural_frequencies_hz:
        raise ValueError("Analytical solver returned no natural frequency.")

    modal = CalculiXSolver().run_modal(
        model,
        modes=modes,
    )

    analytical_mode_1 = analytical.natural_frequencies_hz[0]

    fea_mode_1 = modal.natural_frequencies_hz[0]

    error = relative_error_percent(
        reference=analytical_mode_1,
        value=fea_mode_1,
    )

    return ModalValidationResult(
        analytical_mode_1_hz=analytical_mode_1,
        fea_mode_1_hz=fea_mode_1,
        mode_1_error_percent=error,
        fea_frequencies_hz=(modal.natural_frequencies_hz),
    )
