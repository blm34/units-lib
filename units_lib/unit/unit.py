from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import TYPE_CHECKING, Generic, TypeVar

import units_lib.si_prefix as prefix
from units_lib.dimensions.dimensions import Dimension
from units_lib.utils.fraction import frac_pow

if TYPE_CHECKING:
    from units_lib.quantity.quantity import Quantity

Numeric = float | Decimal | Fraction

D = TypeVar("D")
V = TypeVar("V", bound=Numeric)


@dataclass(frozen=True, slots=True)
class NamedUnit:
    name: str
    symbol: str
    dimension: Dimension

    # Scale to convert to a reference unit: ref = value * scale
    ref_scale: Fraction = Fraction(1)

    def __repr__(self):
        return f"NamedUnit(name={self.name!r}, symbol={self.symbol!r}, dimension={self.dimension!r}, ref_scale={self.ref_scale!r})"


@dataclass(frozen=True, slots=True)
class UnitTerm:
    unit: NamedUnit
    prefix: prefix.SIPrefix = prefix.NONE
    power: Fraction = Fraction(1)

    def __post_init__(self):
        if self.power == 0:
            raise ValueError("A unit term's power cannot be zero")

    @property
    def symbol(self) -> str:
        sym = f"{self.prefix.symbol}{self.unit.symbol}"

        # TODO: Generalise this power logic with name
        if self.power != 1:
            sym += f"^{self.power}"

        return sym

    @property
    def name(self) -> str:
        name = f"{self.prefix.name}{self.unit.name}"

        if self.power != 1:
            name += f"^{self.power}"

        return name

    @property
    def scale(self) -> Fraction | float:
        single_scale = self.prefix.scale * self.unit.ref_scale
        scale = frac_pow(single_scale, self.power)
        return scale

    @property
    def inverted(self) -> UnitTerm:
        return UnitTerm(
            self.unit,
            self.prefix,
            -self.power,
        )

    def __repr__(self):
        return f"UnitTerm(unit={self.unit!r}, prefix={self.prefix!r}, power={self.power!r})"


@dataclass(frozen=True, slots=True, eq=False)
class Unit(Generic[D]):
    terms: tuple[UnitTerm, ...]

    def __post_init__(self):
        object.__setattr__(self, "terms", self._simplify(self.terms))

    @staticmethod
    def _simplify(terms: tuple[UnitTerm, ...]) -> tuple[UnitTerm, ...]:
        # TODO: This should apply cannonical ordering
        powers: dict[tuple[NamedUnit, prefix.SIPrefix], Fraction] = {}

        for term in terms:
            key = (term.unit, term.prefix)
            powers[key] = powers.get(key, Fraction(0)) + term.power

        return tuple(
            UnitTerm(unit=unit, prefix=prefix, power=power)
            for (unit, prefix), power in powers.items()
            if power != 0
        )

    @property
    def symbol(self) -> str:
        numerator: list[str] = []
        denominator: list[str] = []

        for term in self.terms:
            abs_symbol = UnitTerm(
                unit=term.unit,
                prefix=term.prefix,
                power=abs(term.power),
            ).symbol

            if term.power > 0:
                numerator.append(abs_symbol)
            else:
                denominator.append(abs_symbol)

        top = "·".join(numerator)
        bottom = "·".join(denominator)

        symbol = f"{top}/{bottom}" if bottom else top

        return symbol

    @property
    def dimension(self) -> Dimension:
        result = Dimension.dimensionless()

        for term in self.terms:
            result = result * (term.unit.dimension**term.power)

        return result

    @property
    def scale(self) -> Fraction | float:
        result = Fraction(1)

        for term in self.terms:
            result *= term.scale

        return result

    def inverted(self) -> Unit:
        terms = tuple(term.inverted for term in self.terms)
        return Unit(terms)

    def __mul__(self, other: Unit) -> Unit:
        if not isinstance(other, Unit):
            return NotImplemented

        return Unit(self.terms + other.terms)

    def __truediv__(self, other: Unit) -> Unit:
        if not isinstance(other, Unit):
            return NotImplemented

        inverted = other.inverted()
        return Unit(self.terms + inverted.terms)

    def __pow__(self, exponent: int | Fraction) -> Unit:
        if not isinstance(exponent, (int, Fraction)) or isinstance(exponent, bool):
            return NotImplemented

        terms = tuple(
            UnitTerm(term.unit, term.prefix, term.power * exponent)
            for term in self.terms
        )
        return Unit(terms)

    def __rmul__(self, value: V) -> Quantity[D, V]:
        from units_lib.quantity.quantity import Quantity

        return Quantity(value, self)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Unit) and (self.dimension, self.scale) == (
            other.dimension,
            other.scale,
        )

    def __hash__(self):
        return hash((self.dimension, self.scale))

    def __repr__(self):
        return f"Unit(terms={self.terms!r})"
