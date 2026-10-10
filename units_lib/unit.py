from __future__ import annotations

from dataclasses import dataclass

from units_lib.dimensions import Dimension
from units_lib.si_prefix import SIPrefix


@dataclass(frozen=True, slots=True)
class BaseUnit:
    name: str
    symbol: str
    dimension: Dimension


@dataclass(frozen=True, slots=True)
class UnitTerm:
    unit: BaseUnit
    prefix: SIPrefix = SIPrefix.NONE
    power: int = 1

    def __post_init__(self):
        if self.power == 0:
            raise ValueError("A unit term's power cannot be zero")

    @property
    def symbol(self) -> str:
        sym = f"{self.prefix.symbol}{self.unit.symbol}"

        if self.power != 1:
            sym += f"^{self.power}"

        return sym

    @property
    def scale_exp(self) -> int:
        return self.prefix.value * self.power


@dataclass(frozen=True, slots=True)
class Unit:
    terms: tuple[UnitTerm, ...]

    def __post_init__(self):
        object.__setattr__(self, "terms", self._simplify(self.terms))

    @staticmethod
    def _simplify(terms: tuple[UnitTerm, ...]) -> tuple[UnitTerm, ...]:
        powers: dict[tuple[BaseUnit, SIPrefix], int] = {}

        for term in terms:
            key = (term.unit, term.prefix)
            powers[key] = powers.get(key, 0) + term.power

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
            rendered = UnitTerm(
                unit=term.unit,
                prefix=term.prefix,
                power=abs(term.power),
            ).symbol

            if term.power > 0:
                numerator.append(rendered)
            else:
                denominator.append(rendered)

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
    def scale_exp(self) -> int:
        return sum(term.scale_exp for term in self.terms)

    def inverted(self) -> Unit:
        terms = tuple(
            UnitTerm(term.unit, term.prefix, -term.power) for term in self.terms
        )
        return Unit(terms)

    def __mul__(self, other: Unit) -> Unit:
        return Unit(self.terms + other.terms)

    def __truediv__(self, other: Unit) -> Unit:
        inverted = other.inverted()
        return Unit(self.terms + inverted.terms)

    def __pow__(self, exponent: int) -> Unit:
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            return NotImplemented

        terms = tuple(
            UnitTerm(term.unit, term.prefix, term.power * exponent)
            for term in self.terms
        )
        return Unit(terms)
