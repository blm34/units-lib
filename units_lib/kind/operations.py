from __future__ import annotations

from units_lib.dimensions import Dimension
from units_lib.exceptions import IncompatibleDimensionError

from .catalogue.mapper import spec_to_domain
from .catalogue.spec_registry import KindRegistry
from .null_kind import null_kind_for
from .real_kind import RealKind
from .typing import Kind


def kinds_for(dim: Dimension) -> tuple[type[RealKind], ...]:
    """All ``Kind``s sharing the given dimension.

    Args:
        dim: The dimension that returned kinds will have

    Returns:
        All kinds that have the given dimension
    """
    registry = KindRegistry()
    return tuple({spec_to_domain(spec) for spec in registry.kinds_for(dim)})


def resolve_kind(dim: Dimension) -> Kind:
    """Get the default `Kind` for the given dimension.

    If there is a default defined for the given dimension, return it. Otherwise,
    if there is only one ``RealKind`` defined for the given dimension return that.
    Else, return a ``NullKind`` with the given dimension.

    Args:
        dim: The dimension to get the default kind for

    Returns:
        The default kind for the given dimension
    """
    registry = KindRegistry()
    defined_default = registry.default_for(dim)
    if defined_default is not None:
        return spec_to_domain(defined_default)

    kinds = kinds_for(dim)
    if len(kinds) == 1:
        return kinds[0]

    return null_kind_for(dim)


def kinds_compatible(kind_1: Kind, kind_2: Kind) -> bool:
    """True if the kinds share a dimension and they share a common inherited class.

    Having different dimensions makes them incompatible. If either are null kinds
    then they could be compatible - return True. Otherwise check if there is a
    shared inherited class that makes them compatible.
    """
    if kind_1.dimension != kind_2.dimension:
        return False

    if kind_1.is_null or kind_2.is_null:
        return True

    return not get_common_kind(kind_1, kind_2).is_null


def get_common_kind(kind_1: Kind, kind_2: Kind) -> Kind:
    """Get the closest ``Kind`` that is common to both given kinds.

    If kinds have different dimensions, raises an ``IncompatibleDimensionError``.
    If either kind is a null kind or there is no common kind, returns a null kind
    with the given dimension.

    Args:
        kind_1: The first kind in the pair
        kind_2: The second kind in the pair

    Returns:
        The closest common kind between the two given kinds

    Raises:
        IncompatibleDimensionError if the two kinds have different dimensions
    """
    if kind_1.dimension != kind_2.dimension:
        raise IncompatibleDimensionError(
            kind_1.dimension,
            kind_2.dimension,
            f"{kind_1.name} and {kind_2.name} are different dimensions",
        )

    if kind_1.is_null or kind_2.is_null:
        return null_kind_for(kind_1.dimension)

    for cls in kind_2.__mro__:
        if cls is RealKind:
            break

        if issubclass(cls, RealKind) and issubclass(kind_1, cls):
            return cls

    return null_kind_for(kind_1.dimension)
