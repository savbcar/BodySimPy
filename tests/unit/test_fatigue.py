import pytest

from bodysimpy.analysis.fatigue import (
    FatigueLoadBlock,
    SNModel,
    calculate_cycles_to_failure,
    calculate_miner_damage,
)


def test_sn_model_returns_reference_cycles_at_reference_stress() -> None:
    model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    cycles = calculate_cycles_to_failure(
        stress_amplitude_pa=200e6,
        sn_model=model,
    )

    assert cycles == pytest.approx(1.0e6)


def test_lower_stress_amplitude_increases_predicted_life() -> None:
    model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    reference_life = calculate_cycles_to_failure(
        stress_amplitude_pa=200e6,
        sn_model=model,
    )

    lower_stress_life = calculate_cycles_to_failure(
        stress_amplitude_pa=150e6,
        sn_model=model,
    )

    assert lower_stress_life > reference_life


def test_miner_damage_accumulates_multiple_loading_blocks() -> None:
    model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    blocks = (
        FatigueLoadBlock(
            name="normal_operation",
            stress_amplitude_pa=160e6,
            cycles=100_000,
        ),
        FatigueLoadBlock(
            name="high_load",
            stress_amplitude_pa=220e6,
            cycles=20_000,
        ),
    )

    result = calculate_miner_damage(
        blocks=blocks,
        sn_model=model,
    )

    assert result.total_damage_fraction > 0.0

    expected_damage = sum(block.damage_fraction for block in result.block_results)

    assert result.total_damage_fraction == pytest.approx(expected_damage)


def test_miner_damage_identifies_critical_loading_block() -> None:
    model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    blocks = (
        FatigueLoadBlock(
            name="low_stress",
            stress_amplitude_pa=120e6,
            cycles=50_000,
        ),
        FatigueLoadBlock(
            name="high_stress",
            stress_amplitude_pa=240e6,
            cycles=50_000,
        ),
    )

    result = calculate_miner_damage(
        blocks=blocks,
        sn_model=model,
    )

    assert result.critical_block_name == "high_stress"


def test_miner_damage_estimates_repeated_spectrum_life() -> None:
    model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    blocks = (
        FatigueLoadBlock(
            name="baseline",
            stress_amplitude_pa=200e6,
            cycles=100_000,
        ),
    )

    result = calculate_miner_damage(
        blocks=blocks,
        sn_model=model,
    )

    assert result.total_damage_fraction == pytest.approx(0.1)
    assert result.estimated_spectrum_repeats_to_failure == pytest.approx(10.0)
    assert result.estimated_cycles_to_failure == pytest.approx(1.0e6)


def test_fatigue_model_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        SNModel(
            reference_stress_amplitude_pa=-1.0,
            reference_cycles=1.0e6,
            slope_exponent=5.0,
        )

    with pytest.raises(ValueError):
        FatigueLoadBlock(
            name="invalid",
            stress_amplitude_pa=100e6,
            cycles=-1,
        )


def test_zero_cycle_block_contributes_zero_damage() -> None:
    model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    result = calculate_miner_damage(
        blocks=(
            FatigueLoadBlock(
                name="unused_load_case",
                stress_amplitude_pa=250e6,
                cycles=0,
            ),
        ),
        sn_model=model,
    )

    assert result.total_damage_fraction == pytest.approx(0.0)
    assert result.estimated_spectrum_repeats_to_failure == float("inf")
