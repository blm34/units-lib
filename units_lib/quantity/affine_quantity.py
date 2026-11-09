from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import TYPE_CHECKING, Any, Generic

from units_lib._types import Numeric, NumericClass, V
from units_lib.kind.typing import K
from units_lib.scale.multiplication import maintain_type_multiply

from .quantity import Quantity

if TYPE_CHECKING:
    from units_lib.unit.affine_unit import AffineUnit


@total_ordering
@dataclass(frozen=True, slots=True, eq=False)
class AffineQuantity(Generic[K, V]):
    value: V
    unit: AffineUnit[K]

    def __post_init__(self):
        if not isinstance(self.value, NumericClass):
            raise TypeError(f"Unsupported value type {type(self.value).__name__}")

    # ===== CONVERSION =====

    def _value_in(self, unit: AffineUnit[K]) -> Numeric:
        """Get the value in the given unit."""
        if not self.unit.is_compatible_with(unit):
            raise ValueError("Cannot convert to this unit")

        scale, offset = self.unit.conversion_to(unit)
        return maintain_type_multiply(self.value, scale) + offset

    # TODO: Define precise overloads in a stub
    def convert_to(self, unit: AffineUnit[K]) -> AffineQuantity[K, Numeric]:
        """Convert to a quantity using the given unit."""
        return AffineQuantity(self._value_in(unit), unit)

    # ===== ARITHMETIC =====

    def _require_compatible_kind(
        self, other: Quantity[K, Any] | AffineQuantity[K, Any]
    ):
        """Raise an error if the given unit is incompatible with this unit."""
        if not self.unit.is_compatible_with(other.unit):
            # TODO: Raise a dimension error
            raise ValueError("These units are not compatible")

    def __add__(self, other: Quantity) -> AffineQuantity[K, Numeric]:
        if not isinstance(other, Quantity):
            return NotImplemented

        self._require_compatible_kind(other)
        return AffineQuantity(
            # TODO: Fix this ignored ty issue
            self.value + other._value_in(self.unit.delta),  # ty: ignore[unsupported-operator]
            self.unit,
        )

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, AffineQuantity):
            self._require_compatible_kind(other)
            return Quantity(
                self.value - other.convert_to(self.unit).value,
                self.unit.delta,
            )
        if isinstance(other, Quantity):
            self._require_compatible_kind(other)
            return AffineQuantity(
                self.value - other._value_in(self.unit.delta),
                self.unit,
            )
        return NotImplemented

    # ===== COMPARISON =====

    def __eq__(self, other):
        if not isinstance(other, AffineQuantity):
            return NotImplemented
        same_kind = self.unit.is_compatible_with(other.unit)
        same_value = self.value == other._value_in(self.unit)
        return same_kind and same_value

    def __lt__(self, other):
        if not isinstance(other, AffineQuantity):
            return NotImplemented
        self._require_compatible_kind(other)
        return self.value < other._value_in(self.unit)
