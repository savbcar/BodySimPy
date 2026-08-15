from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True, slots=True)
class ReportingSummary:
    project_name: str
    baseline_deflection_error_percent: float | None
    baseline_stress_error_percent: float | None
    mode_1_frequency_hz: float | None
    stress_exceedance_percent: float | None
    best_ml_frequency_mape_percent: float | None


def _read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def load_reporting_summary() -> ReportingSummary:
    validation_dir = Path("docs/validation")

    static_mesh = _read_csv_if_exists(validation_dir / "static_mesh_convergence.csv")
    modal = _read_csv_if_exists(validation_dir / "modal_frequencies.csv")
    stochastic = _read_csv_if_exists(validation_dir / "stochastic_samples.csv")
    ml = _read_csv_if_exists(validation_dir / "ml_sample_efficiency.csv")

    baseline_deflection_error = None
    baseline_stress_error = None

    if static_mesh is not None and not static_mesh.empty:
        final_row = static_mesh.iloc[-1]
        baseline_deflection_error = float(final_row["deflection_error_percent"])
        baseline_stress_error = float(final_row["stress_error_percent"])

    mode_1_frequency = None
    if modal is not None and not modal.empty:
        mode_1_frequency = float(modal.iloc[0]["frequency_hz"])

    stress_exceedance = None
    if stochastic is not None and not stochastic.empty:
        stress_exceedance = float((stochastic["max_stress_mpa"] > 350.0).mean() * 100.0)

    best_ml_frequency_mape = None
    if ml is not None and not ml.empty:
        best_ml_frequency_mape = float(ml["frequency_mape_percent"].min())

    return ReportingSummary(
        project_name="BodySimPy",
        baseline_deflection_error_percent=baseline_deflection_error,
        baseline_stress_error_percent=baseline_stress_error,
        mode_1_frequency_hz=mode_1_frequency,
        stress_exceedance_percent=stress_exceedance,
        best_ml_frequency_mape_percent=best_ml_frequency_mape,
    )
