from __future__ import annotations

import types
from functools import cache
from typing import TYPE_CHECKING

from ..real_kind import RealKind
from .catalogue_spec import get_registry

if TYPE_CHECKING:
    from .catalogue_spec import KindSpec


@cache
def spec_to_domain(spec: KindSpec) -> type[RealKind]:
    """Create a ``RealKind`` from a ``KindSpec``.

    Args:
        spec: The specification of a kind to turn into a domain kind

    Returns:
        The domain kind
    """
    if spec.alias:
        alias_spec = get_registry().get(spec.alias)
        if alias_spec is None:
            raise AttributeError(
                f"{spec.name!r} aliases {spec.alias!r} which doesn't exist"
            )

        return spec_to_domain(alias_spec)

    if spec.inherits is not None:
        inherits_spec = get_registry().get(spec.inherits)
        if inherits_spec is None:
            raise AttributeError(
                f"{spec.name!r} inherits {spec.inherits!r} which doesn't exits"
            )
        inherits = spec_to_domain(inherits_spec)
    else:
        inherits = RealKind

    return types.new_class(
        spec.name,
        (inherits,),
        {"dimension": spec.dimension},
        lambda ns: ns.update(__module__=__name__),
    )
