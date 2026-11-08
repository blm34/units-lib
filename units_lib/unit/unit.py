from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Generic

from units_lib._types import K
from units_lib.dimensions import Dimension
from units_lib.kind import resolve_kind
from units_lib.scale import Scale
from units_lib.unit.si_prefix import NONE as prefixless
from units_lib.unit.si_prefix import SIPrefix


@dataclass(frozen=True, slots=True)
class NamedUnit:
    """A named unit with a symbol and dimension."""

    name: str
    symbol: str
    dimension: Dimension

    # Scale to convert to a reference unit: ref = value * scale
    ref_scale: Scale = field(default_factory=Scale)


@dataclass(frozen=True, slots=True)
class UnitTerm:
    """A named unit with a prefix and optionally raised to a power."""

    unit: NamedUnit
    prefix: SIPrefix = prefixless
    power: int | Fraction = 1

    def __post_init__(self):
        if self.power == 0:
            raise ValueError("A unit term's power cannot be zero")

        if not isinstance(self.power, (int, Fraction)):
            raise TypeError(
                "A units term's power must be an `int` or a `fraction`, "
                f"not {type(self.power).__name__}."
            )

        object.__setattr__(self, "power", Fraction(self.power))

    @property
    def symbol(self) -> str:
        "The symbol for the unit (including prefix and power)."
        return f"{self.prefix.symbol}{self.unit.symbol}{self._get_power_string()}"

    @property
    def name(self) -> str:
        "The full name for the unit (including prefix and power)."
        return f"{self.prefix.name}{self.unit.name}{self._get_power_string()}"

    def _get_power_string(self) -> str:
        """Produce the string representation of the power of this unit."""
        if self.power == 1:
            return ""

        if self.power.denominator == 1 and self.power > 0:
            power = self.power
        else:
            power = f"({self.power})"

        return f"^{power}"

    @property
    def scale(self) -> Scale:
        """Calculate the scale of the given unit to convert to a reference unit."""
        single_scale = self.prefix.scale * self.unit.ref_scale
        scale = single_scale**self.power
        return scale

    @property
    def inverted(self) -> UnitTerm:
        """The multiplicative inverse of the current unit."""
        return UnitTerm(
            self.unit,
            self.prefix,
            -self.power,
        )


@dataclass(frozen=True, slots=True, eq=False)
class Unit(Generic[K]):
    """A unit - can be an aggregation of various named units."""

    terms: tuple[UnitTerm, ...]
    kind: type[K] | None = None

    dimension: Dimension = field(init=False, repr=False)
    scale: Scale = field(init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, "terms", self._simplify(self.terms))

        dimension = Dimension.dimensionless()
        scale = Scale()

        for term in self.terms:
            dimension = dimension * (term.unit.dimension**term.power)
            scale *= term.scale

        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "scale", scale)

        if self.kind is None:
            object.__setattr__(self, "kind", resolve_kind(self.dimension))

        if self.kind is not None and self.dimension != self.kind.dimension:
            raise ValueError(
                f"Unit with dimension {self.dimension} cannot have a kind of "
                f"{self.kind.name} (dimension {self.kind.dimension})"
            )

    @staticmethod
    def _simplify(terms: tuple[UnitTerm, ...]) -> tuple[UnitTerm, ...]:
        """Combine like units and remove those with a power of zero."""
        # TODO: This should apply canonical ordering
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
        if not denominator:
            return top
        bottom = "·".join(denominator)

        if len(denominator) > 1 or "^" in bottom:
            bottom = f"({bottom})"

        symbol = f"{top or '1'}/{bottom}"

        return symbol

    @property
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

        inverted = other.inverted
        return Unit(self.terms + inverted.terms)

    def __pow__(self, exponent: int | Fraction) -> Unit:
        if not isinstance(exponent, (int, Fraction)) or isinstance(exponent, bool):
            return NotImplemented

        if exponent == 0:
            return Unit(())

        terms = tuple(
            UnitTerm(term.unit, term.prefix, term.power * exponent)
            for term in self.terms
        )
        return Unit(terms)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unit):
            return NotImplemented

        return (self.dimension, self.scale) == (other.dimension, other.scale)

    def __hash__(self):
        return hash((self.dimension, self.scale))

    def __repr__(self) -> str:
        kind = self.kind.name if self.kind is not None else "None"
        return f"Unit(terms={self.terms!r}, kind={kind})"
