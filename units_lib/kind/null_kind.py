from __future__ import annotations

import types
from functools import cache
from typing import ClassVar

from units_lib.dimensions import Dimension

from .typing import BaseKind


class _NullKindMeta(type):
    """Lets null kinds be truth tested: they are always falsey."""

    def __bool__(cls) -> bool:
        return False


class NullKind(BaseKind, metaclass=_NullKindMeta):
    """Base of all null kinds (where the kind is unknown)."""

    name: ClassVar[str]
    dimension: ClassVar[Dimension]
    is_null: ClassVar[bool] = True

    def __init_subclass__(cls, dimension: Dimension, **kwargs):
        """Set the ``dimension`` and ``name`` class variables.

        Args:
            dimension: The dimension of the null kind
        """
        super().__init_subclass__(**kwargs)
        cls.dimension = dimension
        cls.name = f"{cls.__name__}[{dimension}]"


@cache
def null_kind_for(dimension: Dimension) -> type[NullKind]:
    """Get the null kind for the given dimension.

    One null kind is created per dimension on the first request and cached.

    Args:
        dimension: The dimension for the ``NullKind``

    Returns:
        A subclass of ``NullKind`` whose dimension is ``dimension``
    """
    return types.new_class(
        "NullKind",
        (NullKind,),
        {"dimension": dimension},
        lambda ns: ns.update(__module__=__name__),
    )
