from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Self


type PowersTuple = tuple[int, int, int, int, int, int, int]


class BaseDimension(IntEnum):
    TIME = 0
    LENGTH = 1
    MASS = 2
    ELECTRIC_CURRENT = 3
    TEMPERATURE = 4
    AMOUNT_OF_SUBSTANCE = 5
    LUMINOUS_INTENSITY = 6


@dataclass(frozen=True, slots=True, init=False)
class Dimension:
    _powers: PowersTuple

    def __init__(self, dimensions: Mapping[BaseDimension, int]):
        powers = [0] * len(BaseDimension)

        if dimensions is not None:
            for dimension, power in dimensions.items():
                if not isinstance(dimension, BaseDimension):
                    raise TypeError(f"Invalid base dimension {dimension!r}")
                if not isinstance(power, int):
                    raise TypeError(f"Power must be an integer: {power!r}")

                powers[dimension] = power

        powers = cast(PowersTuple, tuple(powers))
        object.__setattr__(self, "_powers", powers)

    def __mul__(self, other: Self) -> Self:
        powers = cast(
            PowersTuple,
            tuple(a + b for a, b in zip(self._powers, other._powers, strict=True)),
        )
        return type(self)._from_powers(powers)

    def __truediv__(self, other: Self) -> Self:
        powers = cast(
            PowersTuple,
            tuple(a - b for a, b in zip(self._powers, other._powers, strict=True)),
        )
        return type(self)._from_powers(powers)

    def __pow__(self, exponent: int) -> Self:
        powers = cast(
            PowersTuple,
            tuple(d * exponent for d in self._powers),
        )
        return type(self)._from_powers(powers)

    @classmethod
    def _from_powers(cls, powers: PowersTuple) -> Self:
        result = cls({})
        object.__setattr__(result, "_powers", powers)
        return result

    @classmethod
    def dimensionless(cls) -> Self:
        return cls({})
