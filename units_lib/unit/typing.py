from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from units_lib.dimensions import Dimension
    from units_lib.kind.typing import Kind
    from units_lib.scale import Scale


class UnitLike(Protocol):
    @property
    def kind(self) -> Kind: ...

    @property
    def dimension(self) -> Dimension: ...

    @property
    def scale(self) -> Scale: ...

    @property
    def symbol(self) -> str: ...

    def is_compatible_with(self, other: UnitLike) -> bool: ...

    def common_kind_with(self, other: UnitLike) -> Kind: ...
