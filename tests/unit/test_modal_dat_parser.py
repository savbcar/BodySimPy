from pathlib import Path

import pytest

from bodysimpy.solvers.parsers.dat_parser import (
    parse_eigenfrequencies,
)


def test_parse_eigenfrequencies(tmp_path: Path) -> None:
    dat_path = tmp_path / "modal.dat"

    dat_path.write_text(
        """
 E I G E N V A L U E O U T P U T

 MODE NO    EIGENVALUE              FREQUENCY
                                RAD/TIME       CYCLES/TIME

      1     9.576000E+04       3.094511E+02       4.925290E+01
      2     4.500000E+05       6.708204E+02       1.067632E+02
      3     7.000000E+05       8.366600E+02       1.331575E+02

""",
        encoding="utf-8",
    )

    frequencies = parse_eigenfrequencies(dat_path)

    assert frequencies == pytest.approx(
        (
            49.25290,
            106.7632,
            133.1575,
        )
    )
