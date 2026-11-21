from __future__ import annotations

import types
from abc import ABCMeta
from functools import cache
from typing import ClassVar

from units_lib.dimensions import Dimension
from units_lib.exceptions import IncompatibleKindsError

from .base_kind import BaseKind
from .typing import Kind


class _NullKindMeta(ABCMeta):
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

    @classmethod
    def common_with(cls, other: Kind) -> Kind:
        """Get the closest ``Kind`` that is common to the given kind.

        As this is a null kind, the closest common kind is a null kind.

        Args:
            other: The ``Kind`` to find a common kind with

        Returns:
            A null kind with the given dimension

        Raises:
            IncompatibleDimensionError if the dimensions don't match
        """
        if cls.dimension != other.dimension:
            raise IncompatibleKindsError(
                cls,
                other,
                "Kinds with different dimensions cannot share a common kind",
            )

        return cls

    @classmethod
    def is_compatible(cls, other: Kind) -> bool:
        """True if the kinds share a dimension.

        A null kind is compatible with any kind of the same dimension.

        Args:
            other: The kind to check for compatibility

        Returns:
            True if the kinds are compatible
        """
        return cls.dimension == other.dimension


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
