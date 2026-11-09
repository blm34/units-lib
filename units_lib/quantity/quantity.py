from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
from typing import TYPE_CHECKING, Any, Generic

from units_lib._types import Numeric, NumericClass, V
from units_lib.exceptions import IncompatibleDimensionError
from units_lib.kind.typing import K2, K
from units_lib.scale.multiplication import maintain_type_multiply

if TYPE_CHECKING:
    from units_lib.unit.unit import Unit


@total_ordering
@dataclass(frozen=True, slots=True, eq=False)
class Quantity(Generic[K, V]):
    value: V
    unit: Unit[K]

    def __post_init__(self):
        if not isinstance(self.value, NumericClass):
            raise TypeError(f"Unsupported value type {type(self.value).__name__}")

    # ===== CONVERSION =====

    def _value_in(self, unit: Unit[K]) -> Numeric:
        """Get the value in the given unit."""
        if not self.unit.is_compatible_with(unit):
            # TODO: state unit kinds in error message
            raise ValueError("Cannot convert to this unit")

        return maintain_type_multiply(self.value, self.unit.scale_to(unit))

    # TODO: Define precise overloads in a stub
    def convert_to(self, unit: Unit[K]) -> Quantity[K, Numeric]:
        """Convert to a quantity using the given unit."""
        return Quantity(self._value_in(unit), unit)

    def with_kind(self, kind: type[K2]) -> Quantity[K2, V]:
        """Set the kind of unit."""
        if self.unit.dimension != kind.dimension:
            raise IncompatibleDimensionError(
                self.unit.dimension,
                kind.dimension,
                "Cannot cast to a kind that has a different dimension",
            )
        return Quantity(self.value, self.unit.with_kind(kind))

    # ===== ARITHMETIC =====

    def _require_compatible_kind(self, other: Quantity[Any, Any]):
        """Raise an error if the given unit is incompatible with this unit."""
        if not self.unit.is_compatible_with(other.unit):
            # TODO: Raise a dimension error
            raise ValueError("These units are not compatible")

    def __add__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        self._require_compatible_kind(other)

        other_value = other._value_in(self.unit)
        return Quantity(self.value + other_value, self.unit)

    def __sub__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        self._require_compatible_kind(other)

        other_value = other._value_in(self.unit)
        return Quantity(self.value - other_value, self.unit)

    def __mul__(self, other):
        if isinstance(other, Quantity):
            return Quantity(
                self.value * other.value,
                self.unit * other.unit,
            )
        if isinstance(other, NumericClass):
            return Quantity(
                self.value * other,
                self.unit,
            )
        return NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Quantity):
            return Quantity(
                self.value / other.value,
                self.unit / other.unit,
            )
        if isinstance(other, NumericClass):
            return Quantity(
                self.value / other,
                self.unit,
            )
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, NumericClass):
            return Quantity(
                other / self.value,
                self.unit**-1,
            )
        return NotImplemented

    def __pow__(self, n: int | Fraction):
        return Quantity(
            self.value**n,
            self.unit**n,
        )

    def __neg__(self):
        return Quantity(-self.value, self.unit)

    def __abs__(self):
        return Quantity(abs(self.value), self.unit)

    # ===== COMPARISON =====

    def __eq__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        same_kind = self.unit.is_compatible_with(other.unit)
        same_value = self.value == other._value_in(self.unit)
        return same_kind and same_value

    def __lt__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        self._require_compatible_kind(other)
        return self.value < other._value_in(self.unit)
