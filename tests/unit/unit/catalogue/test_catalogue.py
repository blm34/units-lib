from __future__ import annotations

import importlib
import sys
from fractions import Fraction

import pytest

from units_lib import kind
from units_lib.dimensions import BaseDimension, Dimension
from units_lib.scale import Scale
from units_lib.unit import si_prefix
from units_lib.unit.affine_unit import AffineUnit
from units_lib.unit.catalogue import catalogue
from units_lib.unit.catalogue.catalogue import (
    _catalogue_index,
    _catalogue_to_domain,
    _named_unit,
)
from units_lib.unit.catalogue.catalogue_spec import CatalogueUnit, UnitSpec
from units_lib.unit.unit import NamedUnit, Unit

SINGLE_PREFIX = """\
[defaults]
min_prefix = "NONE"
max_prefix = "NONE"
"""


@pytest.fixture(autouse=True)
def fresh_catalogue(monkeypatch):
    """Reload the runtime module so nothing is cached from earlier tests."""
    name = catalogue.__name__
    parent = importlib.import_module(name.rpartition(".")[0])

    monkeypatch.delitem(sys.modules, name)
    monkeypatch.setattr(parent, "catalogue", catalogue)

    return importlib.import_module(name)


@pytest.fixture
def unit_spec():
    return UnitSpec("name", "symbol", kind.Temperature, "MILLI", "KILO")


@pytest.fixture
def affine_unit_spec():
    return UnitSpec(
        "name", "symbol", kind.Temperature, "MILLI", "KILO", offset=Fraction(5)
    )


@pytest.fixture
def catalogue_unit(unit_spec):
    return CatalogueUnit(unit_spec, si_prefix.KILO)


@pytest.fixture
def affine_catalogue_unit(affine_unit_spec):
    return CatalogueUnit(affine_unit_spec, si_prefix.MILLI)


def test_import_does_not_create_any_units(fresh_catalogue):
    # Arrange
    module = fresh_catalogue

    # Act
    created = [v for v in vars(module).values() if isinstance(v, (Unit, AffineUnit))]

    # Assert
    assert created == []


def test_getattr_creates_prefixed_unit_with_expected_scale(fresh_catalogue):
    # Arrange
    module = fresh_catalogue

    # Act
    millimeter = module.millimeter

    # Assert
    assert isinstance(millimeter, Unit)
    assert millimeter.dimension == Dimension.base(BaseDimension.LENGTH)
    assert millimeter.scale == Scale.from_number(Fraction(1, 1000))


def test_getattr_caches_the_unit_as_a_module_attribute(fresh_catalogue):
    # Arrange
    module = fresh_catalogue
    assert "kilometer" not in vars(module)

    # Act
    first = module.kilometer
    second = module.kilometer

    # Assert
    assert "kilometer" in vars(module)
    assert first is second


def test_getattr_kilogram_has_the_reference_scale(fresh_catalogue):
    # Arrange
    module = fresh_catalogue

    # Act
    kilogram = module.kilogram

    # Assert
    assert kilogram.scale == Scale()


def test_getattr_derived_unit_combines_referenced_dimensions(fresh_catalogue):
    # Arrange
    module = fresh_catalogue
    expected = module.kilogram * module.meter / module.second**2

    # Act
    newton = module.newton

    # Assert
    assert newton.dimension == expected.dimension
    assert newton.scale == expected.scale


def test_getattr_affine_unit_returns_affine_unit_with_offset(fresh_catalogue):
    # Arrange
    module = fresh_catalogue

    # Act
    celsius = module.degrees_celsius

    # Assert
    assert isinstance(celsius, AffineUnit)


def test_getattr_raises_attribute_error_for_unknown_name(fresh_catalogue):
    # Arrange
    module = fresh_catalogue

    # Act / Assert
    with pytest.raises(AttributeError, match="no attribute 'fake'"):
        _ = module.fake


def test_getattr_raises_attribute_error_for_prefix_outside_range(fresh_catalogue):
    # Arrange: degrees celsius is defined with no prefixes.
    module = fresh_catalogue

    # Act
    exists = hasattr(module, "kilodegrees_celsius")

    # Assert
    assert exists is False


def test_dir_lists_names_that_have_not_been_created_yet(fresh_catalogue):
    # Arrange
    module = fresh_catalogue

    # Act
    names = dir(module)

    # Assert
    assert "kilometer" in names
    assert "newton" in names


def test_catalogue_index_returns_dict_or_str_to_catalogue_index():
    # ACT
    result = _catalogue_index()

    # ASSERT
    assert isinstance(result, dict)


def test_catalogue_index_is_cached():
    # ACT
    first = _catalogue_index()
    second = _catalogue_index()

    # ASSERT
    assert first is second


def test_named_unit_creates_named_unit(unit_spec):
    # ACT
    result = _named_unit(unit_spec)

    # ASSERT
    assert isinstance(result, NamedUnit)
    assert result.name == unit_spec.name
    assert result.symbol == unit_spec.symbol
    assert result.dimension == unit_spec.kind.dimension


def test_named_unit_is_cached(unit_spec):
    # ACT
    first = _named_unit(unit_spec)
    second = _named_unit(unit_spec)

    # ASSERT
    assert first is second


def test_catalogue_to_domain_returns_unit(catalogue_unit):
    # ACT
    result = _catalogue_to_domain(catalogue_unit)

    # ASSERT
    assert isinstance(result, Unit)
    assert not isinstance(result, AffineUnit)


def test_catalogue_to_domain_preserves_unit_properties(catalogue_unit):
    # ACT
    result = _catalogue_to_domain(catalogue_unit)

    # ASSERT
    assert len(result.terms) == 1
    assert result.terms[0].prefix == catalogue_unit.prefix
    assert result.kind == catalogue_unit.spec.kind


def test_catalogue_to_domain_returns_affine_unit(affine_catalogue_unit):
    # ACT
    result = _catalogue_to_domain(affine_catalogue_unit)

    # ASSERT
    assert isinstance(result, AffineUnit)
    assert not isinstance(result, Unit)


def test_catalogue_to_domain_preserves_affine_properties(affine_catalogue_unit):
    # ACT
    result = _catalogue_to_domain(affine_catalogue_unit)

    # ASSERT
    assert result.offset == affine_catalogue_unit.spec.offset
    assert result.kind == affine_catalogue_unit.spec.kind
