from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Generic

from units_lib._types import D, V
from units_lib.dimensions import Dimension
from units_lib.si_prefix import NONE as prefixless
from units_lib.si_prefix import SIPrefix
from units_lib.utils.fraction import frac_pow


@dataclass(frozen=True, slots=True)
class NamedUnit:
    """A named unit with a symbol and dimension."""

    name: str
    symbol: str
    dimension: Dimension

    # Scale to convert to a reference unit: ref = value * scale
    ref_scale: Fraction = Fraction(1)

    def __repr__(self):
        return f"NamedUnit(name={self.name!r}, symbol={self.symbol!r}, dimension={self.dimension!r}, ref_scale={self.ref_scale!r})"


@dataclass(frozen=True, slots=True)
class UnitTerm:
    """A named unit with a prefix and optionally raised to a power."""

    unit: NamedUnit
    prefix: SIPrefix = prefixless
    power: Fraction = Fraction(1)

    def __post_init__(self):
        if self.power == 0:
            raise ValueError("A unit term's power cannot be zero")

    @property
    def symbol(self) -> str:
        "The symbol for the unit (including prefix and power)."
        return f"{self.prefix.symbol}{self.unit.symbol}{self._get_power_string()}"

    @property
    def name(self) -> str:
        "The full name for the unit (including prefiX and power)."
        return f"{self.prefix.name}{self.unit.name}{self._get_power_string()}"

    def _get_power_string(self) -> str:
        """Produce the string representation of the power of this unit."""
        if self.power == 1:
            return ""

        return f"^{self.power}"

    @property
    def scale(self) -> Fraction | float:
        """Calculate the scale of the given unit to convert to a reference unit."""
        single_scale = self.prefix.scale * self.unit.ref_scale
        scale = frac_pow(single_scale, self.power)
        return scale

    @property
    def inverted(self) -> UnitTerm:
        """The multiplicative inverse of the current unit."""
        return UnitTerm(
            self.unit,
            self.prefix,
            -self.power,
        )

    def __repr__(self):
        return f"UnitTerm(unit={self.unit!r}, prefix={self.prefix!r}, power={self.power!r})"


@dataclass(frozen=True, slots=True, eq=False)
class Unit(Generic[D]):
    """A unit - can be an aggregation of various named units."""

    terms: tuple[UnitTerm, ...]

    def __post_init__(self):
        object.__setattr__(self, "terms", self._simplify(self.terms))

    @staticmethod
    def _simplify(terms: tuple[UnitTerm, ...]) -> tuple[UnitTerm, ...]:
        """Combine like units and remove those with a power of zero."""
        # TODO: This should apply cannonical ordering
        powers: dict[tuple[NamedUnit, SIPrefix], Fraction] = {}

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
        """Produce the symbol for the unit."""
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
        """The dimension of the unit."""
        result = Dimension.dimensionless()

        for term in self.terms:
            result = result * (term.unit.dimension**term.power)

        return result

    @property
    def scale(self) -> Fraction | float:
        """The scale to convert to a reference (SI) unit."""
        result = Fraction(1)

        for term in self.terms:
            result *= term.scale

        return result

    def inverted(self) -> Unit:
        """The multiplicative inverse of the unit."""
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unit):
            return False

        return (self.dimension, self.scale) == (other.dimension, other.scale)

    def __hash__(self):
        return hash((self.dimension, self.scale))

    def __repr__(self):
        return f"Unit(terms={self.terms!r})"
