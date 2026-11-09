from dataclasses import dataclass
from fractions import Fraction
from typing import Generic

from units_lib.dimensions import Dimension
from units_lib.kind.null_kind import NullKind
from units_lib.kind.typing import K
from units_lib.scale import Scale

from .unit import Unit


@dataclass(frozen=True, slots=True)
class AffineUnit(Generic[K]):
    name: str
    symbol: str
    delta: Unit[K]
    offset: Fraction

    @property
    def scale(self) -> Scale:
        return self.delta.scale

    @property
    def dimension(self) -> Dimension:
        return self.delta.dimension

    @property
    def kind(self) -> type[K | NullKind]:
        return self.delta.kind
