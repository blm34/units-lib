import itertools

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind.catalogue import catalogue as kind_catalogue
from units_lib.kind.operations import kinds_for
from units_lib.kind.real_kind import RealKind


def _discover_standard_kinds() -> tuple[type[RealKind], ...]:
    """Every kind defined at module level in `units_lib.kind`."""
    return tuple(
        obj
        for name in dir(kind_catalogue)
        if isinstance(obj := getattr(kind_catalogue, name), type)
        and issubclass(obj, RealKind)
        and obj is not RealKind
    )


@pytest.fixture(scope="session")
def standard_kinds() -> tuple[type[RealKind], ...]:
    """All standard kinds."""
    return _discover_standard_kinds()


@pytest.fixture(scope="session")
def standard_kind_pairs(
    standard_kinds,
) -> tuple[tuple[type[RealKind], type[RealKind]], ...]:
    return tuple(itertools.product(standard_kinds, repeat=2))


@pytest.fixture(params=_discover_standard_kinds())
def standard_kind(request) -> type[RealKind]:
    return request.param


@pytest.fixture
def fresh_dim():
    """A dimension that no standard kind uses."""
    dim = (
        Dimension.base(BaseDimension.LENGTH) ** 5
        * Dimension.base(BaseDimension.TIME) ** -7
    )

    assert kinds_for(dim) == ()
    return dim


@pytest.fixture
def other_dim():
    """A second dimension that no standard kind uses, distinct from `fresh_dim`."""
    dim = (
        Dimension.base(BaseDimension.MASS) ** 5
        * Dimension.base(BaseDimension.TIME) ** -3
    )

    assert kinds_for(dim) == ()
    return dim
