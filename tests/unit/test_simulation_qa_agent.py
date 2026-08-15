import pytest

from bodysimpy.agents.qa_models import QAStatus
from bodysimpy.agents.simulation_qa import (
    SimulationQAAgent,
    SimulationQAInput,
)


def test_agent_passes_healthy_simulation() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name="baseline_variant",
        solver_return_code=0,
        expected_output_exists=True,
        solver_log=("CalculiX analysis completed successfully."),
        max_stress_pa=210e6,
        mode_1_frequency_hz=48.5,
        baseline_stress_pa=200e6,
        baseline_frequency_hz=50.0,
        stress_limit_pa=350e6,
        maximum_frequency_shift_percent=10.0,
    )

    result = agent.run(input_data)

    assert result.status == QAStatus.PASS

    assert result.baseline_comparison is not None

    assert result.baseline_comparison.stress_change_percent == pytest.approx(5.0)


def test_agent_investigates_large_frequency_shift() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name="thin_variant",
        solver_return_code=0,
        expected_output_exists=True,
        solver_log=("CalculiX analysis completed successfully."),
        max_stress_pa=223.4e6,
        mode_1_frequency_hz=40.85,
        baseline_stress_pa=200e6,
        baseline_frequency_hz=50.0,
        stress_limit_pa=350e6,
        maximum_frequency_shift_percent=10.0,
    )

    result = agent.run(input_data)

    assert result.status == QAStatus.INVESTIGATE

    assert result.frequency_check is not None

    assert result.frequency_check.shift_percent == pytest.approx(-18.3)


def test_agent_investigates_stress_limit_exceedance() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name="high_load_variant",
        solver_return_code=0,
        expected_output_exists=True,
        solver_log=("CalculiX analysis completed successfully."),
        max_stress_pa=370e6,
        mode_1_frequency_hz=49.0,
        baseline_stress_pa=200e6,
        baseline_frequency_hz=50.0,
        stress_limit_pa=350e6,
        maximum_frequency_shift_percent=10.0,
    )

    result = agent.run(input_data)

    assert result.status == QAStatus.INVESTIGATE

    assert result.stress_check is not None
    assert result.stress_check.passed is False


def test_agent_fails_solver_failure() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name="failed_variant",
        solver_return_code=1,
        expected_output_exists=False,
        solver_log="Fatal solver error.",
        max_stress_pa=None,
        mode_1_frequency_hz=None,
        baseline_stress_pa=200e6,
        baseline_frequency_hz=50.0,
        stress_limit_pa=350e6,
        maximum_frequency_shift_percent=10.0,
    )

    result = agent.run(input_data)

    assert result.status == QAStatus.FAILED


def test_agent_uses_outlier_tools_when_history_is_available() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name="possible_outlier",
        solver_return_code=0,
        expected_output_exists=True,
        solver_log=("CalculiX analysis completed successfully."),
        max_stress_pa=300e6,
        mode_1_frequency_hz=49.0,
        baseline_stress_pa=200e6,
        baseline_frequency_hz=50.0,
        stress_limit_pa=350e6,
        maximum_frequency_shift_percent=10.0,
        historical_stress_values_pa=(
            198e6,
            200e6,
            201e6,
            199e6,
            202e6,
        ),
        outlier_z_threshold=3.0,
    )

    result = agent.run(input_data)

    assert result.status == QAStatus.INVESTIGATE

    assert result.stress_outlier is not None
    assert result.stress_outlier.is_outlier is True


def test_agent_does_not_require_optional_baseline() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name="standalone_run",
        solver_return_code=0,
        expected_output_exists=True,
        solver_log=("CalculiX analysis completed successfully."),
        max_stress_pa=200e6,
        mode_1_frequency_hz=50.0,
    )

    result = agent.run(input_data)

    assert result.status == QAStatus.PASS
    assert result.baseline_comparison is None
    assert result.stress_check is None
    assert result.frequency_check is None
