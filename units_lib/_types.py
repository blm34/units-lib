from fractions import Fraction
from typing import TypeVar

Numeric = int | float | Fraction

NumericClass = (int, float, Fraction)

V = TypeVar("V", bound=Numeric)

# TODO: Add a unit protocol that covers both ``Unit`` and ``AffineUnit``
