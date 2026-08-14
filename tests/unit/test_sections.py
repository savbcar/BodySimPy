import pytest

from bodysimpy.domain.sections import RectangularHollowSection


def test_rectangular_hollow_section_area() -> None:
    section = RectangularHollowSection(
        width_m=0.080,
        height_m=0.040,
        thickness_m=0.0015,
    )

    assert section.area_m2 == pytest.approx(3.51e-4, rel=1e-8)


def test_rectangular_hollow_section_second_moment() -> None:
    section = RectangularHollowSection(
        width_m=0.080,
        height_m=0.040,
        thickness_m=0.0015,
    )

    assert section.second_moment_y_m4 == pytest.approx(
        1.0164325e-7,
        rel=1e-8,
    )


def test_rectangular_hollow_section_rejects_impossible_thickness() -> None:
    with pytest.raises(ValueError):
        RectangularHollowSection(
            width_m=0.040,
            height_m=0.040,
            thickness_m=0.025,
        )
