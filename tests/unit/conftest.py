from fractions import Fraction

import pytest

from units_lib.dimensions import BaseDimension, Dimension


@pytest.fixture
def make_dim():
    """Factory building a `Dimension` from keyword exponents.

    Keywords are lower-cased `BaseDimension` names, e.g.
    ``make_dim(mass=1, length=2, time=-2)``. Omitted dimensions default to 0.
    """

    def _make(**powers: int | Fraction) -> Dimension:
        remaining = dict(powers)
        exps = tuple(
            Fraction(remaining.pop(base.name.lower(), 0)) for base in BaseDimension
        )
        if remaining:
            raise ValueError(f"Unknown base dimensions: {sorted(remaining)}")
        return Dimension(exps)  # pyright: ignore[reportArgumentType]

    return _make
