import pytest

from bodysimpy.agents.qa_tools import (
    check_frequency_shift,
    check_solver_completion,
    check_stress_limit,
    compare_to_baseline,
    detect_outlier,
    inspect_simulation_log,
    summarize_results,
)


def test_summary_contains_status_and_recommendation() -> None:
    summary = summarize_results(
        status="INVESTIGATE",
        simulation_name="thin_variant",
        findings=(
            "Mode-1 frequency changed by -18.3% relative to baseline.",
            "Peak stress changed by +11.7% relative to baseline.",
        ),
        recommended_action=("Inspect low-thickness configurations."),
    )

    assert "STATUS: INVESTIGATE" in summary

    assert "Mode-1 frequency changed by -18.3%" in summary

    assert "Inspect low-thickness configurations." in summary


def test_solver_completion_passes_for_successful_run() -> None:
    result = check_solver_completion(
        return_code=0,
        expected_output_exists=True,
    )

    assert result.passed is True
    assert result.message == "Solver completed successfully."


def test_solver_completion_fails_for_nonzero_return_code() -> None:
    result = check_solver_completion(
        return_code=1,
        expected_output_exists=True,
    )

    assert result.passed is False
    assert "return code 1" in result.message


def test_solver_completion_fails_when_output_is_missing() -> None:
    result = check_solver_completion(
        return_code=0,
        expected_output_exists=False,
    )

    assert result.passed is False
    assert "output" in result.message.lower()


def test_log_inspection_detects_solver_failure_marker() -> None:
    result = inspect_simulation_log("Increment failed: no convergence after repeated cutbacks.")

    assert result.passed is False
    assert "no convergence" in result.message.lower()


def test_clean_log_passes_inspection() -> None:
    result = inspect_simulation_log("CalculiX analysis completed successfully.")

    assert result.passed is True


def test_compare_to_baseline_calculates_percentage_changes() -> None:
    comparison = compare_to_baseline(
        current_stress_pa=220e6,
        baseline_stress_pa=200e6,
        current_frequency_hz=45.0,
        baseline_frequency_hz=50.0,
    )

    assert comparison.stress_change_percent == pytest.approx(10.0)

    assert comparison.frequency_change_percent == pytest.approx(-10.0)


def test_stress_limit_flags_exceedance() -> None:
    result = check_stress_limit(
        stress_pa=360e6,
        limit_pa=350e6,
    )

    assert result.passed is False
    assert result.margin_percent < 0.0


def test_stress_limit_passes_below_limit() -> None:
    result = check_stress_limit(
        stress_pa=300e6,
        limit_pa=350e6,
    )

    assert result.passed is True
    assert result.margin_percent > 0.0


def test_frequency_shift_flags_large_change() -> None:
    result = check_frequency_shift(
        current_frequency_hz=40.0,
        baseline_frequency_hz=50.0,
        maximum_absolute_shift_percent=10.0,
    )

    assert result.passed is False
    assert result.shift_percent == pytest.approx(-20.0)


def test_frequency_shift_accepts_small_change() -> None:
    result = check_frequency_shift(
        current_frequency_hz=48.0,
        baseline_frequency_hz=50.0,
        maximum_absolute_shift_percent=10.0,
    )

    assert result.passed is True


def test_outlier_detection_flags_large_z_score() -> None:
    result = detect_outlier(
        value=140.0,
        reference_values=(
            98.0,
            100.0,
            101.0,
            99.0,
            102.0,
        ),
        z_threshold=3.0,
    )

    assert result.is_outlier is True


def test_outlier_detection_accepts_typical_value() -> None:
    result = detect_outlier(
        value=101.0,
        reference_values=(
            98.0,
            100.0,
            101.0,
            99.0,
            102.0,
        ),
        z_threshold=3.0,
    )

    assert result.is_outlier is False


def test_outlier_detection_requires_reference_data() -> None:
    with pytest.raises(ValueError):
        detect_outlier(
            value=100.0,
            reference_values=(),
            z_threshold=3.0,
        )
