from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from units_lib.dimensions import Dimension
    from units_lib.kind.typing import Kind
    from units_lib.unit.unit import Unit


class UnitsError(Exception):
    """Base exception for all exceptions from ``units_lib``."""


class IncompatibleDimensionError(UnitsError, ValueError):
    def __init__(self, dim_1: Dimension, dim_2: Dimension, context: str):
        self.dim_1 = dim_1
        self.dim_2 = dim_2

        message = f"{context} ({dim_1} and {dim_2})"
        super().__init__(message)


class InvalidUnitConversionError(IncompatibleDimensionError):
    def __init__(self, unit_1: Unit, unit_2: Unit):
        super().__init__(
            unit_1.dimension,
            unit_2.dimension,
            context="Cannot convert between units with different dimensions",
        )


class IncompatibleKindsError(UnitsError, ValueError):
    def __init__(self, kind_1: Kind, kind_2: Kind, context: str):
        self.kind_1 = kind_1
        self.kind_2 = kind_2

        message = f"{context} ({kind_1.name} and {kind_2.name})"
        super().__init__(message)
