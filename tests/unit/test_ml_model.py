import torch

from bodysimpy.ml.model import StructuralSurrogate


def test_surrogate_model_output_shape() -> None:
    model = StructuralSurrogate()

    batch = torch.randn(
        8,
        6,
    )

    output = model(batch)

    assert tuple(output.shape) == (
        8,
        3,
    )
