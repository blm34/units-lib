from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from units_lib.dimensions import Dimension

if TYPE_CHECKING:
    from .catalogue_spec import KindSpec


class KindRegistry:
    _instance = None
    _loaded_toml = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialised"):
            self._kinds: dict[str, KindSpec] = {}
            self._by_dimension: dict[Dimension, list[KindSpec]] = defaultdict(list)
            self._defaults: dict[Dimension, KindSpec] = {}

            self._initialised = True

    def register(self, spec: KindSpec) -> None:
        if spec.name in self._kinds:
            raise ValueError(f"Kind {spec.name!r} is already defined")

        dimension = spec.dimension
        if spec.default and dimension in self._defaults:
            raise TypeError(
                f"{self._defaults[dimension].name} is already the default `Kind` "
                f"for {dimension}; cannot also make {spec.name} the default."
            )

        self._kinds[spec.name] = spec
        self._by_dimension[dimension].append(spec)

        if spec.default:
            self._defaults[dimension] = spec

    def get(self, name: str) -> KindSpec | None:
        return self._kinds.get(name, None)

    def all_names(self) -> tuple[str, ...]:
        return tuple(self._kinds.keys())

    def kinds_for(self, dim: Dimension) -> tuple[KindSpec, ...]:
        return tuple(self._by_dimension.get(dim, ()))

    def default_for(self, dim: Dimension) -> KindSpec | None:
        return self._defaults.get(dim)
