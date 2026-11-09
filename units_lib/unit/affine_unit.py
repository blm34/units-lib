from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Generic

from units_lib._types import NumericClass, V
from units_lib.dimensions import Dimension
from units_lib.kind.null_kind import NullKind
from units_lib.kind.typing import K, Kind
from units_lib.quantity.affine_quantity import AffineQuantity
from units_lib.scale import Scale

from .typing import UnitLike
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

    def __rmul__(self, value: V) -> AffineQuantity[K, V]:
        if not isinstance(value, NumericClass):
            return NotImplemented
        return AffineQuantity(value, self)

    def common_kind_with(self, other: UnitLike) -> Kind:
        return self.kind.common_with(other.kind)

    def is_compatible_with(self, other: UnitLike) -> bool:
        return self.kind.is_compatible(other.kind)

    def conversion_to(self, other: AffineUnit[K]) -> tuple[Scale, Fraction | float]:
        if not self.is_compatible_with(other):
            raise ValueError("Cannot convert between units with incompatible kinds")

        scale = self.scale / other.scale

        denominator = (
            other.scale.as_fraction
            if other.scale.as_fraction is not None
            else float(other.scale)
        )
        offset = (self.offset - other.offset) / denominator

        return scale, offset
