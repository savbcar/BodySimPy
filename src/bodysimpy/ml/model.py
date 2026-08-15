from typing import cast

from torch import Tensor, nn


class StructuralSurrogate(nn.Module):
    """MLP surrogate for structural FEA responses."""

    def __init__(self) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(6, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3),
        )

    def forward(
        self,
        features: Tensor,
    ) -> Tensor:
        return cast(
            Tensor,
            self.network(features),
        )