from decimal import Decimal
from fractions import Fraction
from typing import TypeVar

from units_lib.kind import Kind

Numeric = float | Decimal | Fraction

K = TypeVar("K", bound=Kind)
V = TypeVar("V", bound=Numeric)
