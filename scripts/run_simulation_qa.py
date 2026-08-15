from bodysimpy.agents.qa_tools import summarize_results
from bodysimpy.agents.simulation_qa import (
    SimulationQAAgent,
    SimulationQAInput,
)


def main() -> None:
    agent = SimulationQAAgent()

    input_data = SimulationQAInput(
        simulation_name=("crossmember_thickness_1p0mm"),
        solver_return_code=0,
        expected_output_exists=True,
        solver_log=("CalculiX analysis completed successfully."),
        max_stress_pa=223.4e6,
        mode_1_frequency_hz=40.85,
        baseline_stress_pa=200.0e6,
        baseline_frequency_hz=50.0,
        stress_limit_pa=350e6,
        maximum_frequency_shift_percent=10.0,
        historical_stress_values_pa=(
            198e6,
            201e6,
            199e6,
            202e6,
            200e6,
        ),
        historical_frequency_values_hz=(
            48.5,
            49.2,
            50.0,
            50.4,
            49.8,
        ),
        outlier_z_threshold=3.0,
    )

    result = agent.run(input_data)

    summary = summarize_results(
        status=result.status.value,
        simulation_name=(result.simulation_name),
        findings=result.findings,
        recommended_action=(result.recommended_action),
    )

    print()
    print(summary)
    print()


if __name__ == "__main__":
    main()
