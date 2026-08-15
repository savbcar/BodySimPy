from bodysimpy.analysis.fatigue import (
    FatigueLoadBlock,
    SNModel,
    calculate_miner_damage,
)


def main() -> None:
    sn_model = SNModel(
        reference_stress_amplitude_pa=200e6,
        reference_cycles=1.0e6,
        slope_exponent=5.0,
    )

    loading_blocks = (
        FatigueLoadBlock(
            name="normal_operation",
            stress_amplitude_pa=120e6,
            cycles=500_000,
        ),
        FatigueLoadBlock(
            name="elevated_load",
            stress_amplitude_pa=180e6,
            cycles=100_000,
        ),
        FatigueLoadBlock(
            name="severe_load",
            stress_amplitude_pa=240e6,
            cycles=10_000,
        ),
    )

    result = calculate_miner_damage(
        blocks=loading_blocks,
        sn_model=sn_model,
    )

    print()
    print("BodySimPy Fatigue Assessment")
    print("=" * 65)

    for block in result.block_results:
        print()
        print(block.name)
        print(f"  Stress amplitude: {block.stress_amplitude_pa / 1e6:.3f} MPa")
        print(f"  Applied cycles:   {block.applied_cycles:,}")
        print(f"  Cycles to failure: {block.cycles_to_failure:,.0f}")
        print(f"  Miner damage:     {block.damage_fraction:.6f}")

    print()
    print("-" * 65)
    print(f"Total Miner damage: {result.total_damage_fraction:.6f}")
    print(f"Estimated spectrum repeats to D=1: {result.estimated_spectrum_repeats_to_failure:.3f}")
    print(f"Estimated cycles to D=1: {result.estimated_cycles_to_failure:,.0f}")
    print(f"Critical loading block: {result.critical_block_name}")


if __name__ == "__main__":
    main()
