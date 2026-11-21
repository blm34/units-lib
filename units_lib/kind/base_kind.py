from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from units_lib.dimensions import Dimension


class BaseKind(ABC):
    """What both real kinds and null kinds provide."""

    name: ClassVar[str]
    dimension: ClassVar[Dimension]
    is_null: ClassVar[bool]

    @classmethod
    @abstractmethod
    def common_with(cls, other: type[BaseKind]) -> type[BaseKind]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def is_compatible(cls, other: type[BaseKind]) -> bool:
        raise NotImplementedError
