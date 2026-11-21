from __future__ import annotations

from typing import TypeAlias, TypeVar

from .base_kind import BaseKind

Kind: TypeAlias = type[BaseKind]
K = TypeVar("K", bound=BaseKind)
K2 = TypeVar("K2", bound=BaseKind)
