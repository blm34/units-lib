from decimal import Decimal
from fractions import Fraction
from typing import TypeVar

Numeric = float | Decimal | Fraction

D = TypeVar("D")
V = TypeVar("V", bound=Numeric)
