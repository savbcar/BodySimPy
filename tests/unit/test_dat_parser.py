from pathlib import Path

import pytest

from bodysimpy.solvers.parsers.dat_parser import parse_tip_displacement


def test_parse_tip_displacement(tmp_path: Path) -> None:
    dat_path = tmp_path / "beam.dat"

    dat_path.write_text(
        """
 displacements (vx,vy,vz) for set TIP and time  0.1000000E+01

       21  0.000000E+00  0.000000E+00  1.561640E-02
""",
        encoding="utf-8",
    )

    displacement = parse_tip_displacement(
        dat_path,
        tip_node_id=21,
        component=3,
    )

    assert displacement == pytest.approx(0.01561640)
