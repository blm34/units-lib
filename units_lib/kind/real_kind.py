from __future__ import annotations

from typing import ClassVar

from units_lib.dimensions import Dimension
from units_lib.exceptions import IncompatibleDimensionError

from .typing import BaseKind


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
