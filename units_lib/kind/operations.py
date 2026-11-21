from __future__ import annotations

from units_lib.dimensions import Dimension

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
