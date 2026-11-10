from decimal import Decimal
from fractions import Fraction
from typing import TypeVar

Numeric = float | Decimal | Fraction

V = TypeVar("V", bound=Numeric)

# TODO: Add a unit protocol that covers both ``Unit`` and ``AffineUnit``
