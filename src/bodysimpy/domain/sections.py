from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RectangularHollowSection:
    """Rectangular hollow structural section.

    All geometric quantities are expressed in SI units.
    """

    width_m: float
    height_m: float
    thickness_m: float

    def __post_init__(self) -> None:
        if self.width_m <= 0.0:
            raise ValueError("Width must be positive.")

        if self.height_m <= 0.0:
            raise ValueError("Height must be positive.")

        if self.thickness_m <= 0.0:
            raise ValueError("Thickness must be positive.")

        if 2.0 * self.thickness_m >= min(self.width_m, self.height_m):
            raise ValueError("Thickness is too large for the specified hollow section.")

    @property
    def area_m2(self) -> float:
        """Cross-sectional area."""

        outer_area = self.width_m * self.height_m

        inner_width = self.width_m - 2.0 * self.thickness_m
        inner_height = self.height_m - 2.0 * self.thickness_m

        inner_area = inner_width * inner_height

        return outer_area - inner_area

    @property
    def second_moment_y_m4(self) -> float:
        """Second moment of area about the centroidal y-axis."""

        outer = self.width_m * self.height_m**3 / 12.0

        inner_width = self.width_m - 2.0 * self.thickness_m
        inner_height = self.height_m - 2.0 * self.thickness_m

        inner = inner_width * inner_height**3 / 12.0

        return outer - inner
