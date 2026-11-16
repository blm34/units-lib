"""Parsing of ``catalogue.toml``."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from units_lib.dimensions import Dimension

from .spec_registry import KindRegistry

DATA_FILE_NAME = "catalogue.toml"

_ALLOWED_KEYS = frozenset(
    {
        "inherits",
        "alias",
        "dimension",
        "default",
    }
)


@dataclass(frozen=True, slots=True)
class KindSpec:
    """The definition of a kind of unit as read from the TOML file."""

    name: str
    dimension: Dimension
    inherits: str | None = None
    alias: str | None = None
    default: bool = False


def _parse_entry(
    name: str,
    entry: Mapping[str, Any],
) -> KindSpec:
    """Parse an entry of a kind table into a ``KindSpec``.

    Args:
        name: The name of the kind being parsed
        entry: A single kind table from catalogue.toml

    Returns:
        The parsed kind
    """
    unknown = set(entry) - _ALLOWED_KEYS
    if unknown:
        raise ValueError(f"{name}: unknown keys {sorted(unknown)}")

    if "dimension" not in entry:
        raise ValueError(f"{name}: missing required key 'dimension'")

    if "alias" in entry and "inherits" in entry:
        raise ValueError(
            f"{name}: cannot inherit {entry['inherits']} and alias {entry['alias']}"
        )

    return KindSpec(
        name=name,
        inherits=entry.get("inherits", None),
        alias=entry.get("alias", None),
        dimension=Dimension.from_dict(entry["dimension"]),
        default=entry.get("default", False),
    )


def load_specs(path: Path | None = None) -> KindRegistry:
    """Load the spec definitions, keyed by name of the kind.

    Reads the packaged ``catalogue.toml`` unless ``path`` is given.

    Args:
        path: The path to catalogue.toml (defaults to packaged file)

    Returns:
        Dictionary mapping kind names to their spec
    """
    package = __package__ or "units_lib.kind.catalogue"
    source = resources.files(package).joinpath(DATA_FILE_NAME) if path is None else path
    data = tomllib.loads(source.read_text(encoding="utf-8"))

    registry = KindRegistry()
    for name, entry in data.get("kind", []).items():
        spec = _parse_entry(name, entry)
        registry.register(spec)
    return registry


def get_registry() -> KindRegistry:
    if not KindRegistry._loaded_toml:
        KindRegistry._loaded_toml = True
        return load_specs()
    return KindRegistry()


def validate(registry: KindRegistry):
    # Check kind definitions are not circular
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(name: str):
        if name in done:
            return
        if name in visiting:
            raise ValueError(f"Circular kind definition involving {name!r}")
        spec = registry.get(name)
        if spec is None:
            raise ValueError(f"Kind {name!r} doesn't exist")

        visiting.add(name)
        for attribute in ("inherits", "alias"):
            value = getattr(spec, attribute)
            if value is not None:
                visit(value)
        visiting.remove(name)

    for name in registry.all_names():
        visit(name)

    # Check dimensions are consistent between linked specs
    for name in registry.all_names():
        spec = registry.get(name)
        assert spec is not None
        for linked in ("inherits", "alias"):
            linked_spec = registry.get(getattr(spec, linked))
            if linked_spec is None:
                continue
            if spec.dimension != linked_spec.dimension:
                raise ValueError(
                    f"{spec.name!r} and {linked_spec.name!r} are linked by {linked!r} but have different dimensions ({spec.dimension} and {linked_spec.dimension})"
                )
