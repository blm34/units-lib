"""Parsing and validation of ``catalogue.toml``.

This module deliberately never constructs ``Unit`` objects. It only turns the
TOML definitions into plain data and works out which catalogue names exist, so
that both the lazy runtime catalogue and the stub generator can build on it.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from importlib import resources
from pathlib import Path
from typing import Any

from units_lib import kind
from units_lib.kind import Kind
from units_lib.unit import si_prefix
from units_lib.unit.si_prefix import SIPrefix, iter_prefixes

DATA_FILE_NAME = "catalogue.toml"

FALLBACK_MIN_PREFIX = "QUECTO"
FALLBACK_MAX_PREFIX = "QUETTA"

_ALLOWED_KEYS = frozenset(
    {
        "name",
        "symbol",
        "kind",
        "scale",
        "offset",
        "min_prefix",
        "max_prefix",
    }
)


@dataclass(frozen=True, slots=True)
class UnitSpec:
    """The definition of one base (unprefixed) unit, as read from the TOML file.

    Exactly one of ``dimension`` and ``terms`` is not ``None``.
    """

    name: str
    symbol: str
    kind: type[Kind]
    min_prefix: str
    max_prefix: str
    scale: Fraction = Fraction(1)
    offset: Fraction | None = None

    @property
    def is_affine(self) -> bool:
        return self.offset is not None


@dataclass
class CatalogueUnit:
    """One concrete name in the catalogue: a base unit plus a prefix."""

    spec: UnitSpec
    prefix: SIPrefix


def _attribute_name(*parts: str) -> str:
    """Join name parts into the identifier used as the module attribute."""
    name = "".join(parts).replace(" ", "_")
    return name.lower()


def _get_prefix(key: str) -> SIPrefix:
    """Look up an SI prefix by its constant name in ``si_prefix`` (e.g. "KILO")."""
    prefix = getattr(si_prefix, key, None)
    if prefix is None:
        raise ValueError(f"Unknown SI prefix {key!r}")
    if not isinstance(prefix, SIPrefix):
        raise TypeError(f"{key!r} is not an SI prefix")
    return prefix


def _get_kind(key: str) -> type[Kind]:
    """Look up a kinD oF usint by its name in ``kind``."""
    unit_kind = getattr(kind, key, None)
    if unit_kind is None:
        raise ValueError(f"Unknown uniT kind {key!r}")
    if not issubclass(unit_kind, Kind):
        raise TypeError(f"{key!r} is not a kind of unit")
    return unit_kind


def _fraction(value: int | str, context: str) -> Fraction:
    """Convert `value` to a Fraction.

    Args:
        value: The value to convert to a fraction
        context: The context that `value` has come from (for error messages)

    Returns:
        The parsed fraction
    """
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError(
            f"{context}: expected an int or a fraction string such as '1/1000', "
            f"got {value!r}"
        )
    try:
        return Fraction(value)
    except ValueError as error:
        raise ValueError(f"{context}: invalid fraction {value!r}") from error


def _parse_entry(
    entry: Mapping[str, Any],
    defaults: Mapping[str, str],
    position: int,
) -> UnitSpec:
    """Parse an entry of a unit table into a ``UnitSpec``.

    Args:
        entry: A single unit table from catalogue.toml
        defaults: Default values for min and max SI prefixes
        position: The position of the table in the list of units

    Returns:
        The parsed unit
    """
    label = str(entry.get("name", f"unit #{position}"))

    unknown = set(entry) - _ALLOWED_KEYS
    if unknown:
        raise ValueError(f"{label}: unknown keys {sorted(unknown)}")

    for required in ("name", "symbol", "kind"):
        if required not in entry:
            raise ValueError(f"{label}: missing required key {required!r}")

    unit_kind = _get_kind(entry["kind"])

    min_prefix = entry.get(
        "min_prefix",
        defaults.get("min_prefix", FALLBACK_MIN_PREFIX),
    )
    max_prefix = entry.get(
        "max_prefix",
        defaults.get("max_prefix", FALLBACK_MAX_PREFIX),
    )
    _get_prefix(min_prefix)
    _get_prefix(max_prefix)

    offset = entry.get("offset")

    return UnitSpec(
        name=entry["name"],
        symbol=entry["symbol"],
        kind=unit_kind,
        min_prefix=min_prefix,
        max_prefix=max_prefix,
        scale=_fraction(entry.get("scale", 1), f"{label}.scale"),
        offset=None if offset is None else _fraction(offset, f"{label}.offset"),
    )


def load_specs(path: Path | None = None) -> dict[str, UnitSpec]:
    """Load the unit definitions, keyed by attribute name of the base unit.

    Reads the packaged ``catalogue.toml`` unless ``path`` is given.

    Args:
        path: The path to catalogue.toml (defaults to packaged file)

    Returns:
        Dictionary mapping unit names to their spec
    """
    # TODO: Can this if/else be tidied up to just get path if None?
    if path is None:
        package = __package__ or "units_lib"
        raw = (resources.files(package) / DATA_FILE_NAME).read_bytes()
    else:
        raw = path.read_bytes()

    data = tomllib.loads(raw.decode("utf-8"))
    defaults = data.get("defaults", {})

    specs: dict[str, UnitSpec] = {}
    for position, entry in enumerate(data.get("unit", [])):
        spec = _parse_entry(entry, defaults, position)
        key = _attribute_name(spec.name)
        if key in specs:
            raise ValueError(f"Unit {spec.name!r} is defined more than once")
        specs[key] = spec
    return specs


def build_index(specs: Mapping[str, UnitSpec]) -> dict[str, CatalogueUnit]:
    """Map every valid catalogue attribute name to its base unit and prefix.

    Only strings and existing prefix constants are touched here; no units are
    constructed.

    Args:
        specs: A mapping of unit names to their specs

    Returns:
        A dictionary of unit names to their catalogue entry
    """
    index: dict[str, CatalogueUnit] = {}
    for spec in specs.values():
        prefixes = iter_prefixes(
            _get_prefix(spec.min_prefix),
            _get_prefix(spec.max_prefix),
        )
        for prefix in prefixes:
            name = _attribute_name(prefix.name, spec.name)
            if name in index:
                raise ValueError(
                    f"Catalogue name {name!r} is produced by both "
                    f"{index[name].spec.name!r} and {spec.name!r}"
                )
            index[name] = CatalogueUnit(spec, prefix)
    return index


# TODO: This can be used to validate the auto generated kinds once implemented

# def validate_specs(
#     specs: Mapping[str, UnitSpec],
#     catalogue: Mapping[str, CatalogueUnit],
# ) -> None:
#     """Check that derived units refer to real, non-affine units and have no cycles.
#
#     Args:
#         specs: The unit specs defined in the toml
#         catalogue: All the units derived from the toml
#     """
#     # Check specs don't refer to non-existing units
#     for spec in specs.values():
#         for ref, _ in spec.terms or ():
#             if ref not in catalogue:
#                 raise ValueError(f"{spec.name!r} refers to unknown unit {ref!r}")
#             if catalogue[ref].spec.is_affine:
#                 raise ValueError(
#                     f"{spec.name!r} cannot be derived from affine unit {ref!r}"
#                 )
#
#     # Check unit definitions are not circular
#     visiting: set[str] = set()
#     done: set[str] = set()
#
#     def visit(key: str) -> None:
#         if key in done:
#             return
#         if key in visiting:
#             raise ValueError(f"Circular unit definition involving {key!r}")
#         visiting.add(key)
#         for ref, _ in specs[key].terms or ():
#             visit(attribute_name(catalogue[ref].spec.name))
#         visiting.remove(key)
#         done.add(key)
#
#     for key in specs:
#         visit(key)
