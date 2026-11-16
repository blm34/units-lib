from typing import ClassVar, TypeAlias, TypeVar

from units_lib.dimensions import Dimension


class BaseKind:
    """What both real kinds and null kinds provide."""

    name: ClassVar[str]
    dimension: ClassVar[Dimension]
    is_null: ClassVar[bool]


Kind: TypeAlias = type[BaseKind]
K = TypeVar("K", bound=BaseKind)
