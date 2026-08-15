from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Solver-independent structural simulation result."""

    solver_name: str
    tip_deflection_m: float
    max_axial_stress_pa: float | None = None
    natural_frequencies_hz: tuple[float, ...] = ()
    work_directory: Path | None = None
