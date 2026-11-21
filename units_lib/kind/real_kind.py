from __future__ import annotations

from typing import ClassVar

from units_lib.dimensions import Dimension
from units_lib.exceptions import IncompatibleDimensionError, IncompatibleKindsError

from .base_kind import BaseKind
from .null_kind import null_kind_for
from .typing import Kind


class RealKind(BaseKind):
    name: ClassVar[str]
    dimension: ClassVar[Dimension]
    is_null: ClassVar[bool] = False

    def __init_subclass__(
        cls,
        dimension: Dimension | None = None,
        **kwargs,
    ):
        """Configure and register the class.

        Also checks inherited ``Kind``s share the same dimension.

        Args:
            dimension: The dimension of the kind

        Raises:
            IncompatibleDimensionError: if an inherited ``Kind`` has a different dimension
            TypeError: if ``dim`` is neither passed nor available from an inherited ``Kind``
        """
        super().__init_subclass__(**kwargs)

        # Check parent classes for mismatched/inherited dimension
        parents = [
            base
            for base in cls.__bases__
            if issubclass(base, RealKind) and base is not RealKind
        ]

        if dimension is not None:
            cls.dimension = dimension

            for base in parents:
                if base.dimension != dimension:
                    raise IncompatibleDimensionError(
                        dimension,
                        base.dimension,
                        f"{cls.__name__} has a different dimension to its parent {base.__name__}",
                    )
        else:
            parent_dims = {base.dimension for base in parents}
            if len(parent_dims) == 0:
                raise TypeError(
                    f"{cls.__name__} must pass `dimension` as it has no `Kind` to inherit one from"
                )
            if len(parent_dims) > 1:
                raise TypeError(
                    f"{cls.__name__} inherits from `Kind`s with different dimensions"
                )
            cls.dimension = parent_dims.pop()

        # Set class vars
        cls.name = f"{cls.__name__}[{cls.dimension}]"

    @classmethod
    def common_with(cls, other: Kind) -> Kind:
        """Get the closest ``Kind`` that is common to the given kind.

        If kinds have different dimensions, raises an ``IncompatibleDimensionError``.
        If either kind is a null kind or there is no common kind, returns a null kind
        with the given dimension.

        Args:
            other: The ``Kind`` to find a common kind with

        Returns:
            The closest common kind with the given kind

        Raises:
            IncompatibleDimensionError if the kind has a different dimension
        """
        if cls.dimension != other.dimension:
            raise IncompatibleKindsError(
                cls,
                other,
                "Kinds with different dimensions cannot share a common kind",
            )

        if other.is_null:
            return null_kind_for(cls.dimension)

        for parent in other.__mro__:
            if parent is RealKind:
                break

            if issubclass(parent, RealKind) and issubclass(cls, parent):
                return parent

        return null_kind_for(cls.dimension)

    @classmethod
    def is_compatible(cls, other: Kind) -> bool:
        """True if the kinds share a dimension and a common inherited class.

        Having different dimensions makes them incompatible. If ``other`` is a
        are null kind then they could be compatible - return True. Otherwise,
        check if there is a shared inherited class that makes them compatible.
        """
        if cls.dimension != other.dimension:
            return False

        if other.is_null:
            return True

        return not cls.common_with(other).is_null
