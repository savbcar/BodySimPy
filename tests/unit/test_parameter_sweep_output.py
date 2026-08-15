from pathlib import Path

from bodysimpy.analysis.parameter_sweep import (
    SweepPoint,
    write_sweep_csv,
)


def test_write_sweep_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "sweep.csv"

    points = (
        SweepPoint(
            thickness_m=0.001,
            max_stress_pa=200e6,
            tip_deflection_m=0.010,
            mode_1_frequency_hz=45.0,
            mass_kg=2.0,
        ),
        SweepPoint(
            thickness_m=0.002,
            max_stress_pa=120e6,
            tip_deflection_m=0.006,
            mode_1_frequency_hz=55.0,
            mass_kg=3.5,
        ),
    )

    write_sweep_csv(
        points,
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")

    assert "thickness_mm,max_stress_mpa,deflection_mm,mode1_hz,mass_kg" in content

    assert "1.0,200.0,10.0,45.0,2.0" in content
