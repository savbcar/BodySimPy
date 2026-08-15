from pathlib import Path

import pytest

from bodysimpy.solvers.parsers.frd_parser import (
    parse_max_abs_stress_component,
)


def test_parse_max_abs_axial_stress(tmp_path: Path) -> None:
    frd_path = tmp_path / "beam.frd"

    frd_path.write_text(
        """
 100CL101
 -4  STRESS      6    2
 -5  SXX         1    4    1    1    0
 -5  SYY         1    4    2    2    0
 -5  SZZ         1    4    3    3    0
 -5  SXY         1    4    1    2    0
 -5  SYZ         1    4    2    3    0
 -5  SZX         1    4    3    1    0
 -1      101    1
 -2        1  1.900000E+08  0.0  0.0  0.0  0.0  0.0
 -1      102    1
 -2        1 -1.967666E+08  0.0  0.0  0.0  0.0  0.0
 -3
""",
        encoding="utf-8",
    )

    stress = parse_max_abs_stress_component(
        frd_path,
        component=1,
    )

    assert stress == pytest.approx(196.7666e6)
