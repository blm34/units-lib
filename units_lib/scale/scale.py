from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Self

from units_lib.utils.factors import factorise

Base = int | str  # primes or names of constants (e.g. 'pi')

_CONSTANTS = {
    "pi": math.pi,
}


@dataclass(frozen=True, slots=True)
class Scale:
    """A positive real number represented as a product of independant values raised to powers."""

    factors: frozenset[tuple[Base, Fraction]] = frozenset()

    @classmethod
    def _build(cls, exps: dict[Base, Fraction]) -> Self:
        return cls(frozenset((base, exp) for base, exp in exps.items() if exp != 0))

    @classmethod
    def from_number(cls, value: int | Fraction) -> Self:
        """Produce a `Scale` from a number."""
        value = Fraction(value)

        if value <= 0:
            raise ValueError("A `Scale` must be positive")

        exps: dict[Base, Fraction] = {}

        for prime, power in factorise(value.numerator):
            exps[prime] = Fraction(power)

        for prime, power in factorise(value.denominator):
            exps[prime] = exps.get(prime, Fraction(0)) - power

        return cls._build(exps)

    @classmethod
    def constant(cls, value: str) -> Self:
        """Produce a `Scale` from a constant value."""
        if value not in _CONSTANTS:
            raise ValueError(f"Constant value {value!r} is not known")

        return cls._build({value: Fraction(1)})

    def __mul__(self, other: Scale | int | Fraction) -> Scale:
        if isinstance(other, (int, Fraction)) and not isinstance(other, bool):
            other = self.from_number(other)

        if not isinstance(other, Scale):
            return NotImplemented

        exps = dict(self.factors)
        for base, exp in other.factors:
            exps[base] = exps.get(base, Fraction(0)) + exp
        return self._build(exps)

    __rmul__ = __mul__

    def __truediv__(self, other: Scale | int | Fraction) -> Scale:
        if isinstance(other, (int, Fraction)) and not isinstance(other, bool):
            other = self.from_number(other)

        if not isinstance(other, Scale):
            return NotImplemented

        return self * other**-1

    def __rtruediv__(self, other: int | Fraction) -> Scale:
        return other * self**-1

    def __pow__(self, p: int | Fraction) -> Scale:
        exps = {base: exp * p for base, exp in self.factors}
        return self._build(exps)

    def to_fraction(self) -> Fraction | None:
        """The exact rational value, or None if it isn't rational."""
        result = Fraction(1)

        for base, exp in self.factors:
            if not isinstance(base, int) or exp.denominator != 1:
                return None
            result *= Fraction(base) ** int(exp)
        return result

    def __float__(self) -> float:
        result = 1.0

        for base, exp in self.factors:
            if isinstance(base, str):
                base = _CONSTANTS[base]
            result *= float(base**exp)

        return result
