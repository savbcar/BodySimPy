from typing import Protocol

from bodysimpy.domain.results import ModalResult, SimulationResult
from bodysimpy.domain.structural_model import StructuralModel


class StructuralSolver(Protocol):
    """Common interface implemented by structural solvers."""

    def run(self, model: StructuralModel) -> SimulationResult:
        """Run a structural simulation."""
        ...


class ModalSolver(Protocol):
    """Interface implemented by modal-analysis solvers."""

    def run_modal(
        self,
        model: StructuralModel,
        *,
        modes: int,
    ) -> ModalResult:
        """Run a modal analysis."""
        ...
