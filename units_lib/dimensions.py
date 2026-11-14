# TODO: Apply a flyweight pattern to dimensions?
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from fractions import Fraction
from typing import Self, cast

PowersTuple = tuple[
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
]


@unique
class BaseDimension(Enum):
    """Represents each of the 7 SI base unit dimensions."""

    symbol: str

    def __new__(cls, index: int, symbol: str):
        obj = object.__new__(cls)
        obj._value_ = index
        obj.symbol = symbol
        return obj

    TIME = (0, "T")
    LENGTH = (1, "L")
    MASS = (2, "M")
    ELECTRIC_CURRENT = (3, "I")
    TEMPERATURE = (4, "Θ")
    AMOUNT_OF_SUBSTANCE = (5, "N")
    LUMINOUS_INTENSITY = (6, "J")

    @property
    def index(self) -> int:
        """Position of this dimension in a `Dimension`'s exponent tuple."""
        return self._value_


_ZERO = cast(
    PowersTuple,
    tuple(Fraction(0) for _ in BaseDimension),
)


@dataclass(frozen=True, slots=True)
class Dimension:
    """Represents the dimension of a unit."""

    exps: PowersTuple

    def __post_init__(self):
        if len(self.exps) != len(BaseDimension):
            raise ValueError("A dimension must contain 7 base dimensions.")

        frac_exps = tuple(Fraction(exp) for exp in self.exps)
        object.__setattr__(self, "exps", frac_exps)

    @classmethod
    def base(cls, dim: BaseDimension) -> Self:
        """Get the `Dimension` representing the given dimension to the first power."""
        exps = cast(
            PowersTuple,
            tuple(Fraction(int(dim == d)) for d in BaseDimension),
        )
        return cls(exps)

    @classmethod
    def dimensionless(cls) -> Self:
        """Get a dimensionless `Dimension`."""
        return cls(_ZERO)

    @classmethod
    def from_dict(cls, dictionary: dict[str, Fraction]) -> Self:
        """Create a dimension from a dictionary of (base, power) pairs.

        Dictionary of the format {'time': Fraction(1, 2)}, i.e. keys are all
        lowercase with '_' seperated words.

        Args:
            dictionary: The dictionary defining the dimension

        Returns:
            The corresponding Dimension
        """
        powers: list[Fraction] = []
        for idx in range(len(BaseDimension)):
            name = BaseDimension(idx).name.lower()
            powers.append(dictionary.pop(name, Fraction(0)))

        if len(dictionary) != 0:
            raise ValueError(
                f"Unrecognised keys in powers dictionary: {sorted(dictionary.keys())!r}"
            )

        power_tuple = cast(
            PowersTuple,
            tuple(powers),
        )
        return cls(power_tuple)

    def __mul__(self, other: Dimension) -> Dimension:
        """Result of multiplying two dimensions together."""
        if not isinstance(other, Dimension):
            return NotImplemented

        exps = cast(
            PowersTuple,
            tuple(a + b for a, b in zip(self.exps, other.exps, strict=True)),
        )
        return Dimension(exps)

    def __truediv__(self, other: Dimension) -> Dimension:
        """Result of dividing a dimension by a dimension."""
        if not isinstance(other, Dimension):
            return NotImplemented

        exps = cast(
            PowersTuple,
            tuple(a - b for a, b in zip(self.exps, other.exps, strict=True)),
        )
        return Dimension(exps)

    def __pow__(self, exponent: int | Fraction) -> Dimension:
        """Result of raising a dimension to a power."""
        if not isinstance(exponent, (int, Fraction)):
            return NotImplemented

        exps = cast(
            PowersTuple,
            tuple(d * exponent for d in self.exps),
        )
        return Dimension(exps)

    def __repr__(self) -> str:
        return f"Dimension({self.exps!r})"

    def __str__(self) -> str:
        res = []

        for base in BaseDimension:
            exp = self.exps[base.index]
            if exp == 0:
                continue

            symbol = base.symbol
            res.append(symbol if exp == 1 else f"{symbol}^{exp}")

        return "·".join(res)
