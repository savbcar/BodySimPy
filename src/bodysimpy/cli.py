from pathlib import Path

import typer

from bodysimpy.workflows.parameter_sweep import (
    run_thickness_sweep_from_config,
)

app = typer.Typer(
    name="bodysim",
    help="Structural CAE workflow automation for automotive body structures.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Show the installed BodySimPy version."""

    typer.echo("BodySimPy 0.1.0")


@app.command()
def sweep(
    config_path: Path,
) -> None:
    """Run a configured parameter sweep."""

    points = run_thickness_sweep_from_config(config_path)

    typer.echo(f"Completed {len(points)} sweep points.")

    for point in points:
        typer.echo(
            f"{point.thickness_m * 1000:.1f} mm | "
            f"{point.max_stress_pa / 1e6:.3f} MPa | "
            f"{point.tip_deflection_m * 1000:.4f} mm | "
            f"{point.mode_1_frequency_hz:.4f} Hz | "
            f"{point.mass_kg:.4f} kg"
        )


if __name__ == "__main__":
    app()
