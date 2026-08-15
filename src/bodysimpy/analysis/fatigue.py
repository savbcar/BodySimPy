from dataclasses import dataclass
from math import pow


@dataclass(frozen=True, slots=True)
class SNModel:
    """Power-law S-N fatigue model.

    The implemented relation is:

        N = N_ref * (sigma_ref / sigma_a) ** m

    where N is the predicted cycles to failure and sigma_a is the
    stress amplitude.
    """

    reference_stress_amplitude_pa: float
    reference_cycles: float
    slope_exponent: float

    def __post_init__(self) -> None:
        if self.reference_stress_amplitude_pa <= 0.0:
            raise ValueError("Reference stress amplitude must be positive.")

        if self.reference_cycles <= 0.0:
            raise ValueError("Reference cycle count must be positive.")

        if self.slope_exponent <= 0.0:
            raise ValueError("S-N slope exponent must be positive.")


@dataclass(frozen=True, slots=True)
class FatigueLoadBlock:
    """Constant-amplitude fatigue loading block."""

    name: str
    stress_amplitude_pa: float
    cycles: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Fatigue loading block name must not be empty.")

        if self.stress_amplitude_pa <= 0.0:
            raise ValueError("Stress amplitude must be positive.")

        if self.cycles < 0:
            raise ValueError("Cycle count must not be negative.")


@dataclass(frozen=True, slots=True)
class FatigueBlockResult:
    """Calculated fatigue contribution from one loading block."""

    name: str
    stress_amplitude_pa: float
    applied_cycles: int
    cycles_to_failure: float
    damage_fraction: float


@dataclass(frozen=True, slots=True)
class FatigueResult:
    """Palmgren-Miner cumulative fatigue assessment."""

    total_damage_fraction: float
    estimated_spectrum_repeats_to_failure: float
    estimated_cycles_to_failure: float
    critical_block_name: str
    block_results: tuple[FatigueBlockResult, ...]


def calculate_cycles_to_failure(
    *,
    stress_amplitude_pa: float,
    sn_model: SNModel,
) -> float:
    """Return predicted cycles to failure from the S-N relation."""

    if stress_amplitude_pa <= 0.0:
        raise ValueError("Stress amplitude must be positive.")

    stress_ratio = sn_model.reference_stress_amplitude_pa / stress_amplitude_pa

    cycles_to_failure = sn_model.reference_cycles * pow(
        stress_ratio,
        sn_model.slope_exponent,
    )

    return cycles_to_failure


def calculate_miner_damage(
    *,
    blocks: tuple[FatigueLoadBlock, ...],
    sn_model: SNModel,
) -> FatigueResult:
    """Calculate cumulative damage using the Palmgren-Miner rule."""

    if not blocks:
        raise ValueError("At least one fatigue loading block is required.")

    block_results: list[FatigueBlockResult] = []

    for block in blocks:
        cycles_to_failure = calculate_cycles_to_failure(
            stress_amplitude_pa=block.stress_amplitude_pa,
            sn_model=sn_model,
        )

        damage_fraction = block.cycles / cycles_to_failure

        block_results.append(
            FatigueBlockResult(
                name=block.name,
                stress_amplitude_pa=block.stress_amplitude_pa,
                applied_cycles=block.cycles,
                cycles_to_failure=cycles_to_failure,
                damage_fraction=damage_fraction,
            )
        )

    total_damage = sum(block.damage_fraction for block in block_results)

    critical_block = max(
        block_results,
        key=lambda block: block.damage_fraction,
    )

    total_cycles_per_spectrum = sum(block.applied_cycles for block in block_results)

    if total_damage == 0.0:
        estimated_spectrum_repeats = float("inf")
        estimated_cycles = float("inf")
    else:
        estimated_spectrum_repeats = 1.0 / total_damage

        estimated_cycles = total_cycles_per_spectrum * estimated_spectrum_repeats

    return FatigueResult(
        total_damage_fraction=total_damage,
        estimated_spectrum_repeats_to_failure=(estimated_spectrum_repeats),
        estimated_cycles_to_failure=estimated_cycles,
        critical_block_name=critical_block.name,
        block_results=tuple(block_results),
    )
