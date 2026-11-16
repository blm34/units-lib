from __future__ import annotations

from units_lib.kind.real_kind import RealKind

from .catalogue_spec import get_registry
from .mapper import spec_to_domain


def __getattr__(name: str) -> type[RealKind]:
    spec = get_registry().get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    value = spec_to_domain(spec)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *get_registry().all_names()})
