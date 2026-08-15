from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """Base model for strict BodySimPy configuration."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class MeshConfig(StrictModel):
    elements: int = Field(gt=0)


class ProjectConfig(StrictModel):
    name: str = Field(min_length=1)


class GeometryConfig(StrictModel):
    type: Literal["rectangular_hollow_section"]
    length_m: float = Field(gt=0.0)
    width_m: float = Field(gt=0.0)
    height_m: float = Field(gt=0.0)
    thickness_m: float = Field(gt=0.0)

    @model_validator(mode="after")
    def validate_section_geometry(self) -> Self:
        if 2.0 * self.thickness_m >= min(self.width_m, self.height_m):
            raise ValueError("Wall thickness is too large for the rectangular hollow section.")

        return self


class MaterialConfig(StrictModel):
    youngs_modulus_pa: float = Field(gt=0.0)
    poisson_ratio: float = Field(gt=-1.0, lt=0.5)
    density_kg_m3: float = Field(gt=0.0)


class LoadingConfig(StrictModel):
    tip_force_n: float


class ModalConfig(StrictModel):
    modes: int = Field(gt=0)


class AnalysisConfig(StrictModel):
    static: bool
    modal: ModalConfig


class NormalDistributionConfig(StrictModel):
    mean: float
    standard_deviation: float = Field(gt=0.0)


class StochasticConfig(StrictModel):
    samples: int = Field(gt=0)
    seed: int
    stress_threshold_pa: float = Field(gt=0.0)
    thickness_m: NormalDistributionConfig
    youngs_modulus_pa: NormalDistributionConfig
    tip_force_n: NormalDistributionConfig


class SimulationConfig(StrictModel):
    project: ProjectConfig
    geometry: GeometryConfig
    material: MaterialConfig
    loading: LoadingConfig
    analysis: AnalysisConfig
    mesh: MeshConfig
    stochastic: StochasticConfig | None = None


class ThicknessSweepConfig(StrictModel):
    """Configuration for a wall-thickness parameter sweep."""

    base_config: str = Field(min_length=1)
    thickness_values_m: tuple[float, ...]
    output_csv: str = Field(min_length=1)
    max_workers: int = Field(default=1, gt=0)

    @model_validator(mode="after")
    def validate_thickness_values(self) -> Self:
        if not self.thickness_values_m:
            raise ValueError("At least one thickness value is required.")

        if any(thickness <= 0.0 for thickness in self.thickness_values_m):
            raise ValueError("All thickness values must be positive.")

        if len(set(self.thickness_values_m)) != len(self.thickness_values_m):
            raise ValueError("Thickness sweep values must be unique.")

        return self


class SimulationQAConfig(StrictModel):
    stress_limit_pa: float = Field(gt=0.0)

    maximum_frequency_shift_percent: float = Field(ge=0.0)

    outlier_z_threshold: float = Field(
        default=3.0,
        gt=0.0,
    )
