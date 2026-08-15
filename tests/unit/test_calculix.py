from bodysimpy.domain.materials import IsotropicMaterial
from bodysimpy.domain.sections import RectangularHollowSection
from bodysimpy.domain.structural_model import StructuralModel
from bodysimpy.solvers.calculix import (
    build_input_deck,
    build_modal_input_deck,
)


def test_build_input_deck() -> None:
    model = StructuralModel(
        name="baseline_crossmember",
        section=RectangularHollowSection(
            width_m=0.080,
            height_m=0.040,
            thickness_m=0.0015,
        ),
        material=IsotropicMaterial(
            name="Generic structural steel",
            youngs_modulus_pa=210e9,
            poisson_ratio=0.30,
            density_kg_m3=7850.0,
            yield_strength_pa=350e6,
        ),
        length_m=1.0,
        tip_force_n=1000.0,
        mesh_elements=10,
    )

    deck = build_input_deck(model)

    assert "*ELEMENT,TYPE=B32R" in deck
    assert "SECTION=BOX" in deck
    assert "*STATIC" in deck
    assert "*CLOAD" in deck
    assert "*NODE PRINT,NSET=TIP" in deck
    assert "*EL FILE,OUTPUT=3D" in deck
    assert "S,NOE" in deck


def test_build_modal_input_deck() -> None:
    model = StructuralModel(
        name="baseline_modal",
        section=RectangularHollowSection(
            width_m=0.080,
            height_m=0.040,
            thickness_m=0.0015,
        ),
        material=IsotropicMaterial(
            name="Generic structural steel",
            youngs_modulus_pa=210e9,
            poisson_ratio=0.30,
            density_kg_m3=7850.0,
            yield_strength_pa=350e6,
        ),
        length_m=1.0,
        tip_force_n=1000.0,
        mesh_elements=20,
    )

    deck = build_modal_input_deck(
        model,
        modes=10,
    )

    assert "*FREQUENCY" in deck
    assert "\n10\n" in deck
    assert "*NODE FILE" in deck
    assert "\nU\n" in deck
    assert "*CLOAD" not in deck
    assert "*STATIC" not in deck
