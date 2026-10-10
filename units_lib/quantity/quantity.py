from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Any, Generic, TypeVar

from units_lib.unit.unit import Unit

Numeric = float | Decimal | Fraction


D = TypeVar("D")
V = TypeVar("V", bound=Numeric)


@dataclass(frozen=True, slots=True)
class Quantity(Generic[D, V]):
    value: V
    unit: Unit[D]

    @property
    def value_type(self) -> type[V]:
        return type(self.value)

    def convert_to(self, target: Unit[D]) -> Quantity[D, V]:
        """Convert this quantity to a compatible unit."""
        if self.unit.dimension != target.dimension:
            # TODO: Make this a DimensionError which inherits from TypeError
            raise ValueError(
                f"Cannot convert {self.unit.symbol} to {target.symbol}: incompatible dimensions"
            )

        ratio = self._coerce_type(self.unit.scale / target.scale)

        return Quantity(self.value * ratio, target)

    def _coerce_type(self, value: Fraction):
        if isinstance(self.value, Fraction):
            return value
        if isinstance(self.value, Decimal):
            return Decimal(value.numerator) / Decimal(value.denominator)
        if isinstance(self.value, float):
            return float(value)
        raise TypeError(f"Cannot coerce a `Fraction` into {self.value_type.__name__}")

    def _coerce_additive_operand(self, value: Quantity[D, V]) -> Quantity[D, V]:
        if not isinstance(value, Quantity):
            raise TypeError(
                f"Cannot use type of {type(value)} with Quantity[..., {self._value_type}]"
            )

        if self.unit.dimension != value.unit.dimension:
            # TODO: Make this a DimensionError which inherits from TypeError
            raise ValueError(
                f"Cannot perform additive operations on different dimensions ({self.unit.dimension} and {value.unit.dimension})"
            )

        return value.convert_to(self.unit)

    def __mul__(self, other):
        if isinstance(other, (self.value_type, int)):
            return Quantity(self.value * other, self.unit)

        if not isinstance(other, Quantity):
            return NotImplemented

        return Quantity(
            value=self.value * other.value,
            unit=self.unit * other.unit,
        )

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other: Quantity[Any, V] | V) -> Quantity[Any, V]:
        if isinstance(other, self.value_type):
            return Quantity(self.value / other, self.unit)

        if not isinstance(other, Quantity):
            return NotImplemented

        return Quantity(
            value=self.value / other.value,
            unit=self.unit / other.unit,
        )

    def __rtruediv__(self, other):
        return Quantity(other, Unit(())) / self

    def __pow__(self, exponent: int | Fraction):
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            return NotImplemented

        new_value = self.value**exponent

        return Quantity(
            value=new_value,
            unit=self.unit**exponent,
        )

    def __add__(self, other):
        other = self._coerce_additive_operand(other)

        return Quantity(
            value=self.value + other.value,
            unit=self.unit,
        )

    def __sub__(self, other):
        other = self._coerce_additive_operand(other)

        return Quantity(
            value=self.value - other.value,
            unit=self.unit,
        )
