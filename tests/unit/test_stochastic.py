import numpy as np
import pytest

from bodysimpy.analysis.stochastic import (
    calculate_sensitivity_ranking,
    generate_stochastic_inputs,
    summarize_distribution,
)
from bodysimpy.config.models import StochasticConfig


def build_stochastic_config() -> StochasticConfig:
    return StochasticConfig.model_validate(
        {
            "samples": 5,
            "seed": 42,
            "stress_threshold_pa": 350e6,
            "thickness_m": {
                "mean": 0.0015,
                "standard_deviation": 0.00005,
            },
            "youngs_modulus_pa": {
                "mean": 210e9,
                "standard_deviation": 5e9,
            },
            "tip_force_n": {
                "mean": 1000.0,
                "standard_deviation": 80.0,
            },
        }
    )


def test_distribution_summary() -> None:
    values = np.array(
        [
            10.0,
            20.0,
            30.0,
            40.0,
            50.0,
        ],
        dtype=float,
    )

    summary = summarize_distribution(values)

    assert summary.mean == pytest.approx(30.0)

    assert summary.standard_deviation > 0.0

    assert summary.percentile_5 < summary.mean

    assert summary.percentile_95 > summary.mean


def test_stochastic_inputs_are_reproducible() -> None:
    config = build_stochastic_config()

    first = generate_stochastic_inputs(config)

    second = generate_stochastic_inputs(config)

    assert first == second
    assert len(first) == 5


def test_stochastic_inputs_are_physically_positive() -> None:
    inputs = generate_stochastic_inputs(build_stochastic_config())

    for sample in inputs:
        assert sample.thickness_m > 0.0

        assert sample.youngs_modulus_pa > 0.0

        assert sample.tip_force_n > 0.0


def test_sample_count_override() -> None:
    inputs = generate_stochastic_inputs(
        build_stochastic_config(),
        sample_count=3,
    )

    assert len(inputs) == 3

    assert [sample.sample_index for sample in inputs] == [
        1,
        2,
        3,
    ]


def test_sensitivity_ranking() -> None:
    inputs = np.array(
        [
            [1.0, 10.0, 100.0],
            [2.0, 8.0, 110.0],
            [3.0, 6.0, 90.0],
            [4.0, 4.0, 120.0],
            [5.0, 2.0, 80.0],
        ],
        dtype=float,
    )

    output = np.array(
        [
            2.0,
            4.0,
            6.0,
            8.0,
            10.0,
        ],
        dtype=float,
    )

    ranking = calculate_sensitivity_ranking(
        inputs,
        output,
        parameter_names=(
            "parameter_a",
            "parameter_b",
            "parameter_c",
        ),
    )

    assert len(ranking) == 3

    assert {item.parameter for item in ranking} == {
        "parameter_a",
        "parameter_b",
        "parameter_c",
    }

    assert abs(ranking[0].coefficient) >= abs(ranking[1].coefficient) >= abs(ranking[2].coefficient)
