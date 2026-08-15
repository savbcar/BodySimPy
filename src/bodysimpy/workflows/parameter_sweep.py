from pathlib import Path

from bodysimpy.analysis.parameter_sweep import (
    SweepPoint,
    run_thickness_sweep,
    write_sweep_csv,
)
from bodysimpy.config.loader import (
    load_config,
    load_thickness_sweep_config,
)
from bodysimpy.modeling.crossmember import (
    build_crossmember_model,
)


def run_thickness_sweep_from_config(
    path: str | Path,
) -> tuple[SweepPoint, ...]:
    """Run a configured wall-thickness parameter sweep."""

    sweep_config = load_thickness_sweep_config(path)

    base_config = load_config(sweep_config.base_config)

    model = build_crossmember_model(base_config)

    points = run_thickness_sweep(
        model,
        thickness_values_m=(sweep_config.thickness_values_m),
        max_workers=sweep_config.max_workers,
    )

    write_sweep_csv(
        points,
        sweep_config.output_csv,
    )

    return points
