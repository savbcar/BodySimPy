import math
from statistics import mean, stdev

from bodysimpy.agents.qa_models import (
    BaselineComparison,
    FrequencyShiftResult,
    OutlierResult,
    QACheckResult,
    StressLimitResult,
)

_FAILURE_MARKERS = (
    "no convergence",
    "failed",
    "fatal",
    "divergence",
    "too many cutbacks",
)


def check_solver_completion(
    *,
    return_code: int,
    expected_output_exists: bool,
) -> QACheckResult:
    """Check whether the external solver completed successfully."""

    if return_code != 0:
        return QACheckResult(
            name="solver_completion",
            passed=False,
            message=(f"Solver did not complete successfully: return code {return_code}."),
        )

    if not expected_output_exists:
        return QACheckResult(
            name="solver_completion",
            passed=False,
            message=("Solver returned successfully but the expected output file is missing."),
        )

    return QACheckResult(
        name="solver_completion",
        passed=True,
        message="Solver completed successfully.",
    )


def inspect_simulation_log(
    log_text: str,
) -> QACheckResult:
    """Search a solver log for known failure indicators."""

    normalized_log = log_text.lower()

    for marker in _FAILURE_MARKERS:
        if marker in normalized_log:
            return QACheckResult(
                name="simulation_log",
                passed=False,
                message=(f"Simulation log contains a potential failure marker: {marker}."),
            )

    return QACheckResult(
        name="simulation_log",
        passed=True,
        message=("No known solver failure marker was detected in the simulation log."),
    )


def compare_to_baseline(
    *,
    current_stress_pa: float,
    baseline_stress_pa: float,
    current_frequency_hz: float,
    baseline_frequency_hz: float,
) -> BaselineComparison:
    """Calculate structural-response changes relative to baseline."""

    if baseline_stress_pa <= 0.0:
        raise ValueError("Baseline stress must be positive.")

    if baseline_frequency_hz <= 0.0:
        raise ValueError("Baseline frequency must be positive.")

    stress_change_percent = (current_stress_pa - baseline_stress_pa) / baseline_stress_pa * 100.0

    frequency_change_percent = (
        (current_frequency_hz - baseline_frequency_hz) / baseline_frequency_hz * 100.0
    )

    return BaselineComparison(
        stress_change_percent=stress_change_percent,
        frequency_change_percent=(frequency_change_percent),
    )


def check_stress_limit(
    *,
    stress_pa: float,
    limit_pa: float,
) -> StressLimitResult:
    """Check a supplied engineering stress threshold."""

    if stress_pa < 0.0:
        raise ValueError("Stress magnitude cannot be negative.")

    if limit_pa <= 0.0:
        raise ValueError("Stress limit must be positive.")

    margin_percent = (limit_pa - stress_pa) / limit_pa * 100.0

    return StressLimitResult(
        passed=stress_pa <= limit_pa,
        stress_pa=stress_pa,
        limit_pa=limit_pa,
        margin_percent=margin_percent,
    )


def check_frequency_shift(
    *,
    current_frequency_hz: float,
    baseline_frequency_hz: float,
    maximum_absolute_shift_percent: float,
) -> FrequencyShiftResult:
    """Check frequency change against a supplied shift threshold."""

    if current_frequency_hz <= 0.0:
        raise ValueError("Current frequency must be positive.")

    if baseline_frequency_hz <= 0.0:
        raise ValueError("Baseline frequency must be positive.")

    if maximum_absolute_shift_percent < 0.0:
        raise ValueError("Maximum frequency shift cannot be negative.")

    shift_percent = (current_frequency_hz - baseline_frequency_hz) / baseline_frequency_hz * 100.0

    return FrequencyShiftResult(
        passed=(abs(shift_percent) <= maximum_absolute_shift_percent),
        shift_percent=shift_percent,
        maximum_absolute_shift_percent=(maximum_absolute_shift_percent),
    )


def detect_outlier(
    *,
    value: float,
    reference_values: tuple[float, ...],
    z_threshold: float = 3.0,
) -> OutlierResult:
    """Screen one result using a simple reference-set z-score."""

    if not reference_values:
        raise ValueError("At least one reference value is required.")

    if len(reference_values) < 2:
        raise ValueError("At least two reference values are required for outlier detection.")

    if z_threshold <= 0.0:
        raise ValueError("Z-score threshold must be positive.")

    if not math.isfinite(value):
        raise ValueError("Outlier candidate must be finite.")

    if not all(math.isfinite(reference) for reference in reference_values):
        raise ValueError("Outlier reference values must be finite.")

    reference_mean = mean(reference_values)

    reference_standard_deviation = stdev(reference_values)

    if reference_standard_deviation == 0.0:
        z_score = 0.0 if value == reference_mean else float("inf")
    else:
        z_score = (value - reference_mean) / reference_standard_deviation

    return OutlierResult(
        is_outlier=(abs(z_score) > z_threshold),
        value=value,
        z_score=z_score,
        z_threshold=z_threshold,
    )


def summarize_results(
    *,
    status: str,
    simulation_name: str,
    findings: tuple[str, ...],
    recommended_action: str,
) -> str:
    """Create a deterministic human-readable QA summary."""

    lines = [
        "BodySimPy Simulation QA",
        "=" * 60,
        f"Simulation: {simulation_name}",
        f"STATUS: {status}",
        "",
        "Findings:",
    ]

    for finding in findings:
        lines.append(f"- {finding}")

    lines.extend(
        [
            "",
            "Recommended next action:",
            recommended_action,
        ]
    )

    return "\n".join(lines)
