from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import cast

from units_lib.unit import Unit


@dataclass(frozen=True, slots=True)
class Quantity[T: (float, Decimal, Fraction)]:
    value: T
    unit: Unit

    @property
    def value_type(self) -> type[T]:
        return type(self.value)

    def convert_to(self, target: Unit) -> Quantity[T]:
        """Convert this quantity to a compatible unit."""
        if self.unit.dimension != target.dimension:
            raise ValueError(
                f"Cannot convert {self.unit.symbol} to {target.symbol}: incompatible dimensions"
            )

        base = self.value_type(10)
        exponent = self.unit.scale_exp - target.scale_exp
        scale = cast(T, base**exponent)
        converted_value = self.value * scale

        return Quantity(converted_value, target)

    def _coerce_additive_operand(self, other: Quantity[T] | T) -> Quantity[T]:
        if isinstance(other, self.value_type):
            return Quantity(other, self.unit)

        if not isinstance(other, Quantity):
            raise TypeError(f"Unsupported operand type: {type(other).__name__}")

        if self.unit.dimension != other.unit.dimension:
            raise ValueError("Cannot combine quantities with incompatible dimensions")

        return other.convert_to(self.unit)

    def __mul__(self, other: Quantity[T] | T) -> Quantity[T]:
        if isinstance(other, self.value_type):
            return Quantity(self.value * other, self.unit)

        if not isinstance(other, Quantity):
            return NotImplemented

        return Quantity(
            value=self.value * other.value,
            unit=self.unit * other.unit,
        )

    def __rmul__(self, other: T) -> Quantity[T]:
        return self * other

    def __truediv__(self, other: Quantity[T] | T) -> Quantity[T]:
        if isinstance(other, self.value_type):
            return Quantity(self.value / other, self.unit)

        if not isinstance(other, Quantity):
            return NotImplemented

        return Quantity(
            value=self.value / other.value,
            unit=self.unit / other.unit,
        )

    def __rtruediv__(self, other: T) -> Quantity[T]:
        return Quantity(other, Unit(())) / self

    def __pow__(self, exponent: int) -> Quantity[T]:
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            return NotImplemented

        new_value = cast(T, self.value**exponent)

        return Quantity(
            value=new_value,
            unit=self.unit**exponent,
        )

    def __add__(self, other: Quantity[T] | T) -> Quantity[T]:
        other = self._coerce_additive_operand(other)

        return Quantity(
            value=self.value + other.value,
            unit=self.unit,
        )

    def __sub__(self, other: Quantity[T] | T) -> Quantity[T]:
        other = self._coerce_additive_operand(other)

        return Quantity(
            value=self.value - other.value,
            unit=self.unit,
        )
