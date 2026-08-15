from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from numpy.typing import NDArray

from bodysimpy.config.models import StochasticConfig
from bodysimpy.domain.structural_model import StructuralModel
from bodysimpy.solvers.calculix import CalculiXSolver


@dataclass(frozen=True, slots=True)
class StochasticInput:
    """One randomized Monte Carlo input sample."""

    sample_index: int
    thickness_m: float
    youngs_modulus_pa: float
    tip_force_n: float


@dataclass(frozen=True, slots=True)
class DistributionSummary:
    """Summary statistics for a sampled distribution."""

    mean: float
    standard_deviation: float
    percentile_5: float
    percentile_95: float


@dataclass(frozen=True, slots=True)
class SensitivityCoefficient:
    """Standardized linear sensitivity coefficient."""

    parameter: str
    coefficient: float


@dataclass(frozen=True, slots=True)
class StochasticSample:
    """Inputs and FEA outputs for one Monte Carlo realization."""

    sample_index: int
    thickness_m: float
    youngs_modulus_pa: float
    tip_force_n: float
    max_stress_pa: float
    mode_1_frequency_hz: float


@dataclass(frozen=True, slots=True)
class StochasticStudyResult:
    """Aggregated result of a Monte Carlo FEA study."""

    samples: tuple[StochasticSample, ...]
    stress_summary: DistributionSummary
    frequency_summary: DistributionSummary
    stress_exceedance_probability_percent: float
    stress_sensitivity: tuple[SensitivityCoefficient, ...]
    frequency_sensitivity: tuple[SensitivityCoefficient, ...]


def _sample_positive_normal(
    rng: np.random.Generator,
    *,
    mean: float,
    standard_deviation: float,
) -> float:
    """Draw from a normal distribution while enforcing positivity."""

    while True:
        value = float(
            rng.normal(
                loc=mean,
                scale=standard_deviation,
            )
        )

        if value > 0.0:
            return value


def generate_stochastic_inputs(
    config: StochasticConfig,
    *,
    sample_count: int | None = None,
) -> tuple[StochasticInput, ...]:
    """Generate reproducible randomized engineering inputs."""

    count = config.samples if sample_count is None else sample_count

    if count <= 0:
        raise ValueError("Stochastic sample count must be positive.")

    rng = np.random.default_rng(config.seed)

    samples: list[StochasticInput] = []

    for sample_index in range(
        1,
        count + 1,
    ):
        thickness_m = _sample_positive_normal(
            rng,
            mean=config.thickness_m.mean,
            standard_deviation=(config.thickness_m.standard_deviation),
        )

        youngs_modulus_pa = _sample_positive_normal(
            rng,
            mean=config.youngs_modulus_pa.mean,
            standard_deviation=(config.youngs_modulus_pa.standard_deviation),
        )

        tip_force_n = _sample_positive_normal(
            rng,
            mean=config.tip_force_n.mean,
            standard_deviation=(config.tip_force_n.standard_deviation),
        )

        samples.append(
            StochasticInput(
                sample_index=sample_index,
                thickness_m=thickness_m,
                youngs_modulus_pa=youngs_modulus_pa,
                tip_force_n=tip_force_n,
            )
        )

    return tuple(samples)


def summarize_distribution(
    values: NDArray[np.float64],
) -> DistributionSummary:
    """Calculate summary statistics for a sampled distribution."""

    if values.ndim != 1:
        raise ValueError("Distribution values must be one-dimensional.")

    if values.size == 0:
        raise ValueError("Distribution values must not be empty.")

    if values.size > 1:
        standard_deviation = float(
            np.std(
                values,
                ddof=1,
            )
        )
    else:
        standard_deviation = 0.0

    return DistributionSummary(
        mean=float(np.mean(values)),
        standard_deviation=standard_deviation,
        percentile_5=float(
            np.percentile(
                values,
                5,
            )
        ),
        percentile_95=float(
            np.percentile(
                values,
                95,
            )
        ),
    )


def calculate_sensitivity_ranking(
    inputs: NDArray[np.float64],
    output: NDArray[np.float64],
    *,
    parameter_names: tuple[str, ...],
) -> tuple[SensitivityCoefficient, ...]:
    """Calculate standardized linear sensitivity coefficients."""

    if inputs.ndim != 2:
        raise ValueError("Sensitivity inputs must be a two-dimensional array.")

    if output.ndim != 1:
        raise ValueError("Sensitivity output must be one-dimensional.")

    if inputs.shape[0] != output.shape[0]:
        raise ValueError("Input and output sample counts must match.")

    if inputs.shape[1] != len(parameter_names):
        raise ValueError("Parameter-name count must match input columns.")

    if inputs.shape[0] < 2:
        raise ValueError("At least two samples are required for sensitivity analysis.")

    input_standard_deviation = np.std(
        inputs,
        axis=0,
        ddof=1,
    )

    output_standard_deviation = float(
        np.std(
            output,
            ddof=1,
        )
    )

    if np.any(input_standard_deviation == 0.0):
        raise ValueError("Sensitivity inputs must vary.")

    if output_standard_deviation == 0.0:
        raise ValueError("Sensitivity output must vary.")

    standardized_inputs = (
        inputs
        - np.mean(
            inputs,
            axis=0,
        )
    ) / input_standard_deviation

    standardized_output = (output - np.mean(output)) / output_standard_deviation

    coefficients, _, _, _ = np.linalg.lstsq(
        standardized_inputs,
        standardized_output,
        rcond=None,
    )

    ranking = [
        SensitivityCoefficient(
            parameter=name,
            coefficient=float(coefficient),
        )
        for name, coefficient in zip(
            parameter_names,
            coefficients,
            strict=True,
        )
    ]

    ranking.sort(
        key=lambda item: abs(item.coefficient),
        reverse=True,
    )

    return tuple(ranking)


def run_stochastic_study(
    model: StructuralModel,
    config: StochasticConfig,
    *,
    sample_count: int | None = None,
) -> StochasticStudyResult:
    """Run Monte Carlo static and mode-1 FEA analyses."""

    inputs = generate_stochastic_inputs(
        config,
        sample_count=sample_count,
    )

    solver = CalculiXSolver()

    samples: list[StochasticSample] = []

    total = len(inputs)

    for input_sample in inputs:
        section = replace(
            model.section,
            thickness_m=(input_sample.thickness_m),
        )

        material = replace(
            model.material,
            youngs_modulus_pa=(input_sample.youngs_modulus_pa),
        )

        sample_model = replace(
            model,
            name=(f"{model.name}_mc_{input_sample.sample_index:04d}"),
            section=section,
            material=material,
            tip_force_n=(input_sample.tip_force_n),
        )

        static_result = solver.run(sample_model)

        modal_result = solver.run_modal(
            sample_model,
            modes=1,
        )

        if static_result.max_axial_stress_pa is None:
            raise ValueError("Static FEA returned no axial stress.")

        samples.append(
            StochasticSample(
                sample_index=(input_sample.sample_index),
                thickness_m=(input_sample.thickness_m),
                youngs_modulus_pa=(input_sample.youngs_modulus_pa),
                tip_force_n=(input_sample.tip_force_n),
                max_stress_pa=(static_result.max_axial_stress_pa),
                mode_1_frequency_hz=(modal_result.natural_frequencies_hz[0]),
            )
        )

        if (
            input_sample.sample_index == 1
            or input_sample.sample_index % 25 == 0
            or input_sample.sample_index == total
        ):
            print(f"Monte Carlo: {input_sample.sample_index}/{total}")

    stress_values = np.array(
        [sample.max_stress_pa for sample in samples],
        dtype=float,
    )

    frequency_values = np.array(
        [sample.mode_1_frequency_hz for sample in samples],
        dtype=float,
    )

    input_matrix = np.array(
        [
            [
                sample.thickness_m,
                sample.youngs_modulus_pa,
                sample.tip_force_n,
            ]
            for sample in samples
        ],
        dtype=float,
    )

    exceedance_probability = float(np.mean(stress_values > config.stress_threshold_pa) * 100.0)

    parameter_names = (
        "thickness",
        "youngs_modulus",
        "tip_force",
    )

    return StochasticStudyResult(
        samples=tuple(samples),
        stress_summary=summarize_distribution(stress_values),
        frequency_summary=summarize_distribution(frequency_values),
        stress_exceedance_probability_percent=(exceedance_probability),
        stress_sensitivity=(
            calculate_sensitivity_ranking(
                input_matrix,
                stress_values,
                parameter_names=parameter_names,
            )
        ),
        frequency_sensitivity=(
            calculate_sensitivity_ranking(
                input_matrix,
                frequency_values,
                parameter_names=parameter_names,
            )
        ),
    )
