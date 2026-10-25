from __future__ import annotations

from functools import cache

from units_lib.scale import Scale
from units_lib.unit.affine_unit import AffineUnit
from units_lib.unit.unit import NamedUnit, Unit, UnitTerm

from .catalogue_spec import (
    CatalogueUnit,
    UnitSpec,
    build_index,
    load_specs,
)


@cache
def _catalogue_index() -> dict[str, CatalogueUnit]:
    """Map of every unit in the catalogue indexed by name."""
    return build_index(load_specs())


@cache
def _named_unit(spec: UnitSpec) -> NamedUnit:
    """Create a ``NamedUnit`` from a ``UnitSpec``.

    Args:
        spec: The unit specification

    Returns:
        The domain object named unit.
    """
    dimension = spec.kind.dimension
    ref_scale = Scale.from_number(spec.scale)

    return NamedUnit(
        name=spec.name,
        symbol=spec.symbol,
        dimension=dimension,
        ref_scale=ref_scale,
    )


def _catalogue_to_domain(entry: CatalogueUnit) -> Unit | AffineUnit:
    """Create a ``Unit`` or ``AffineUnit`` from a ``CatalogueEntry``.

    Args:
        entry: The catalogue unit to turn into a domain unit.

    Returns:
        The domain unit
    """
    spec = entry.spec

    named_unit = _named_unit(spec)
    unit_term = UnitTerm(named_unit, entry.prefix)
    unit = Unit(terms=(unit_term,), kind=spec.kind)

    if spec.offset is None:
        return unit

    return AffineUnit(
        name=unit_term.name,
        symbol=unit_term.symbol,
        delta=unit,
        offset=spec.offset,
    )


def __getattr__(name: str) -> Unit | AffineUnit:
    entry = _catalogue_index().get(name)
    if entry is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    value = _catalogue_to_domain(entry)
    globals()[name] = value  # cache: __getattr__ is only called on a miss
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *_catalogue_index()})
