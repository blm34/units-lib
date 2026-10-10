from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Generic, TypeAlias, TypeVar

from units_lib.unit import Unit

Numeric: TypeAlias = float | Decimal | Fraction

_D = TypeVar("_D")
_V = TypeVar("_V", bound=Numeric)

@dataclass(frozen=True, slots=True)
class Quantity(Generic[_D, _V]):
    value: _V
    unit: Unit

    @property
    def value_type(self) -> type[_V]: ...
    def convert_to(self, target: Unit[_D]) -> Quantity[_D, _V]: ...
    def _coerce_type(self, value: Fraction) -> _V: ...
    def _coerce_additive_operand(
        self, value: Quantity[_D, _V] | _V
    ) -> Quantity[_D, _V]: ...
