from typing import Protocol

from bodysimpy.domain.results import SimulationResult
from bodysimpy.domain.structural_model import StructuralModel


class StructuralSolver(Protocol):
    """Common interface implemented by structural solvers."""

    def run(self, model: StructuralModel) -> SimulationResult:
        """Run a structural simulation."""
        ...
