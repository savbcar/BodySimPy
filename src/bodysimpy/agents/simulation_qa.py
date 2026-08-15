from dataclasses import dataclass

from bodysimpy.agents.qa_models import (
    BaselineComparison,
    FrequencyShiftResult,
    OutlierResult,
    QACheckResult,
    QAStatus,
    StressLimitResult,
)
from bodysimpy.agents.qa_tools import (
    check_frequency_shift,
    check_solver_completion,
    check_stress_limit,
    compare_to_baseline,
    detect_outlier,
    inspect_simulation_log,
)


@dataclass(frozen=True, slots=True)
class SimulationQAInput:
    """Metadata and engineering results available to the QA agent."""

    simulation_name: str

    solver_return_code: int
    expected_output_exists: bool
    solver_log: str

    max_stress_pa: float | None
    mode_1_frequency_hz: float | None

    baseline_stress_pa: float | None = None
    baseline_frequency_hz: float | None = None

    stress_limit_pa: float | None = None
    maximum_frequency_shift_percent: float | None = None

    historical_stress_values_pa: tuple[float, ...] = ()
    historical_frequency_values_hz: tuple[float, ...] = ()

    outlier_z_threshold: float = 3.0


@dataclass(frozen=True, slots=True)
class SimulationQAResult:
    """Complete result produced by the simulation QA agent."""

    simulation_name: str
    status: QAStatus

    completion_check: QACheckResult
    log_check: QACheckResult

    baseline_comparison: BaselineComparison | None

    stress_check: StressLimitResult | None
    frequency_check: FrequencyShiftResult | None

    stress_outlier: OutlierResult | None
    frequency_outlier: OutlierResult | None

    findings: tuple[str, ...]
    recommended_action: str


class SimulationQAAgent:
    """Tool-orchestrating simulation quality-assurance agent."""

    def run(
        self,
        input_data: SimulationQAInput,
    ) -> SimulationQAResult:
        completion_check = check_solver_completion(
            return_code=input_data.solver_return_code,
            expected_output_exists=input_data.expected_output_exists,
        )

        log_check = inspect_simulation_log(input_data.solver_log)

        if not completion_check.passed or not log_check.passed:
            failure_findings = (
                completion_check.message,
                log_check.message,
            )

            return SimulationQAResult(
                simulation_name=input_data.simulation_name,
                status=QAStatus.FAILED,
                completion_check=completion_check,
                log_check=log_check,
                baseline_comparison=None,
                stress_check=None,
                frequency_check=None,
                stress_outlier=None,
                frequency_outlier=None,
                findings=failure_findings,
                recommended_action=(
                    "Inspect solver execution and output files "
                    "before interpreting engineering results."
                ),
            )

        baseline_comparison: BaselineComparison | None = None
        stress_check: StressLimitResult | None = None
        frequency_check: FrequencyShiftResult | None = None
        stress_outlier: OutlierResult | None = None
        frequency_outlier: OutlierResult | None = None

        findings: list[str] = []

        should_investigate = False

        if (
            input_data.max_stress_pa is not None
            and input_data.mode_1_frequency_hz is not None
            and input_data.baseline_stress_pa is not None
            and input_data.baseline_frequency_hz is not None
        ):
            baseline_comparison = compare_to_baseline(
                current_stress_pa=input_data.max_stress_pa,
                baseline_stress_pa=input_data.baseline_stress_pa,
                current_frequency_hz=input_data.mode_1_frequency_hz,
                baseline_frequency_hz=input_data.baseline_frequency_hz,
            )

            findings.append(
                "Peak stress changed by "
                f"{baseline_comparison.stress_change_percent:+.1f}% "
                "relative to baseline."
            )

            findings.append(
                "Mode-1 frequency changed by "
                f"{baseline_comparison.frequency_change_percent:+.1f}% "
                "relative to baseline."
            )

        if input_data.max_stress_pa is not None and input_data.stress_limit_pa is not None:
            stress_check = check_stress_limit(
                stress_pa=input_data.max_stress_pa,
                limit_pa=input_data.stress_limit_pa,
            )

            if not stress_check.passed:
                should_investigate = True

                findings.append(
                    "Supplied stress threshold was exceeded "
                    f"by {-stress_check.margin_percent:.1f}%."
                )

        if (
            input_data.mode_1_frequency_hz is not None
            and input_data.baseline_frequency_hz is not None
            and input_data.maximum_frequency_shift_percent is not None
        ):
            frequency_check = check_frequency_shift(
                current_frequency_hz=input_data.mode_1_frequency_hz,
                baseline_frequency_hz=input_data.baseline_frequency_hz,
                maximum_absolute_shift_percent=(input_data.maximum_frequency_shift_percent),
            )

            if not frequency_check.passed:
                should_investigate = True

                findings.append(
                    "Mode-1 frequency shift exceeds the configured screening threshold."
                )

        if (
            input_data.max_stress_pa is not None
            and len(input_data.historical_stress_values_pa) >= 2
        ):
            stress_outlier = detect_outlier(
                value=input_data.max_stress_pa,
                reference_values=(input_data.historical_stress_values_pa),
                z_threshold=input_data.outlier_z_threshold,
            )

            if stress_outlier.is_outlier:
                should_investigate = True

                findings.append(
                    "Peak stress is statistically unusual "
                    "relative to the supplied reference set "
                    f"(z={stress_outlier.z_score:.2f})."
                )

        if (
            input_data.mode_1_frequency_hz is not None
            and len(input_data.historical_frequency_values_hz) >= 2
        ):
            frequency_outlier = detect_outlier(
                value=input_data.mode_1_frequency_hz,
                reference_values=(input_data.historical_frequency_values_hz),
                z_threshold=input_data.outlier_z_threshold,
            )

            if frequency_outlier.is_outlier:
                should_investigate = True

                findings.append(
                    "Mode-1 frequency is statistically unusual "
                    "relative to the supplied reference set "
                    f"(z={frequency_outlier.z_score:.2f})."
                )

        if not findings:
            findings.append("No applicable engineering comparison tools were requested.")

        if should_investigate:
            status = QAStatus.INVESTIGATE

            recommended_action = (
                "Inspect the flagged configuration and compare "
                "its geometry, material, loading and solver "
                "results with neighboring design points."
            )

        else:
            status = QAStatus.PASS

            recommended_action = (
                "No QA screening issue was detected. Continue with normal engineering review."
            )

        return SimulationQAResult(
            simulation_name=input_data.simulation_name,
            status=status,
            completion_check=completion_check,
            log_check=log_check,
            baseline_comparison=baseline_comparison,
            stress_check=stress_check,
            frequency_check=frequency_check,
            stress_outlier=stress_outlier,
            frequency_outlier=frequency_outlier,
            findings=tuple(findings),
            recommended_action=recommended_action,
        )
