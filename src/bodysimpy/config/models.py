from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """Base model for strict BodySimPy configuration."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
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


class SimulationConfig(StrictModel):
    project: ProjectConfig
    geometry: GeometryConfig
    material: MaterialConfig
    loading: LoadingConfig
    analysis: AnalysisConfig
    mesh: MeshConfig
