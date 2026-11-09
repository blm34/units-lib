from __future__ import annotations

import math
from fractions import Fraction

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.quantity.affine_quantity import AffineQuantity
from units_lib.scale import Scale
from units_lib.unit.affine_unit import AffineUnit
from units_lib.unit.unit import NamedUnit, Unit, UnitTerm


def make_length() -> Dimension:
    return Dimension.base(BaseDimension.LENGTH)


def make_time() -> Dimension:
    return Dimension.base(BaseDimension.TIME)


def make_scale(factor: int | Fraction) -> Scale:
    return Scale.from_number(factor)


def make_affine(
    delta: Unit,
    offset: int | Fraction = 0,
    name: str = "affine",
    symbol: str = "a",
) -> AffineUnit:
    return AffineUnit(name=name, symbol=symbol, delta=delta, offset=Fraction(offset))


def make_kind(
    name: str,
    dimension: Dimension,
    *,
    compatible: bool = True,
    common: object = None,
):
    """Build a stub kind whose compatibility behaviour is fixed by the caller."""

    class StubKind:
        is_null = False

        @classmethod
        def is_compatible(cls, other) -> bool:
            return compatible

        @classmethod
        def common_with(cls, other):
            return common

    StubKind.name = name  # type: ignore[attr-defined]
    StubKind.dimension = dimension  # type: ignore[attr-defined]
    return StubKind


class StubDelta:
    """Minimal stand-in for ``Unit`` exposing only what ``AffineUnit`` reads."""

    def __init__(self, scale, kind):
        self.scale = scale
        self.kind = kind
        self.dimension = make_length()


@pytest.fixture
def metre() -> NamedUnit:
    return NamedUnit(name="metre", symbol="m", dimension=make_length())


@pytest.fixture
def second() -> NamedUnit:
    return NamedUnit(name="second", symbol="s", dimension=make_time())


@pytest.fixture
def kilometre() -> NamedUnit:
    """A non-SI-prefixed unit with a non-trivial reference scale."""
    return NamedUnit(
        name="kilometre-like",
        symbol="km",
        dimension=make_length(),
        ref_scale=make_scale(1000),
    )


@pytest.fixture
def metre_unit(metre) -> Unit:
    return Unit((UnitTerm(metre),))


@pytest.fixture
def kilometre_unit(kilometre) -> Unit:
    return Unit((UnitTerm(kilometre),))


@pytest.fixture
def second_unit(second) -> Unit:
    return Unit((UnitTerm(second),))


class TestAffineUnitInit:
    def test_init_stores_name_symbol_delta_and_offset(self, metre_unit):
        # ACT
        unit = AffineUnit("shifted", "sh", metre_unit, Fraction(5))

        # ASSERT
        assert unit.name == "shifted"
        assert unit.symbol == "sh"
        assert unit.delta == metre_unit
        assert unit.offset == Fraction(5)

    def test_eq_returns_true_for_identical_fields(self, metre_unit):
        # ARRANGE
        a = make_affine(metre_unit, offset=3)
        b = make_affine(metre_unit, offset=3)

        # ACT
        result = a == b

        # ASSERT
        assert result is True

    def test_eq_returns_false_for_different_offsets(self, metre_unit):
        # ARRANGE
        a = make_affine(metre_unit, offset=3)
        b = make_affine(metre_unit, offset=4)

        # ACT
        result = a == b

        # ASSERT
        assert result is False

    def test_hash_is_equal_for_equal_instances(self, metre_unit):
        # ARRANGE
        a = make_affine(metre_unit, offset=3)
        b = make_affine(metre_unit, offset=3)

        # ACT
        hash_a = hash(a)
        hash_b = hash(b)

        # ASSERT
        assert hash_a == hash_b


class TestAffineUnitDelegatedProperties:
    def test_scale_is_the_delta_scale(self, kilometre_unit):
        # ARRANGE
        unit = make_affine(kilometre_unit, offset=7)

        # ACT
        scale = unit.scale

        # ASSERT
        assert scale == kilometre_unit.scale

    def test_scale_ignores_offset(self, metre_unit):
        # ARRANGE
        unit = make_affine(metre_unit, offset=100)

        # ACT
        scale = unit.scale

        # ASSERT
        assert scale == Scale()

    def test_dimension_is_the_delta_dimension(self, metre_unit):
        # ARRANGE
        unit = make_affine(metre_unit)

        # ACT
        dimension = unit.dimension

        # ASSERT
        assert dimension == make_length()

    def test_kind_is_the_delta_kind(self, metre_unit):
        # ARRANGE
        unit = make_affine(metre_unit)

        # ACT
        kind = unit.kind

        # ASSERT
        assert kind is metre_unit.kind


class TestAffineUnitRmul:
    @pytest.mark.parametrize("value", [5, 2.5, Fraction(1, 3)])
    def test_rmul_returns_affine_quantity_for_numeric_value(self, metre_unit, value):
        # ARRANGE
        unit = make_affine(metre_unit)

        # ACT
        result = value * unit

        # ASSERT
        assert isinstance(result, AffineQuantity)

    def test_rmul_quantity_holds_value_and_unit(self, metre_unit):
        # ARRANGE
        unit = make_affine(metre_unit)

        # ACT
        result = 5 * unit

        # ASSERT
        assert result.value == 5
        assert result.unit == unit

    def test_rmul_returns_not_implemented_for_non_numeric_value(self, metre_unit):
        # ARRANGE
        unit = make_affine(metre_unit)

        # ACT
        result = unit.__rmul__("2")  # pyright: ignore[reportArgumentType]

        # ASSERT
        assert result is NotImplemented

    def test_rmul_with_non_numeric_operator_raises_type_error(self, metre_unit):
        # ARRANGE
        unit = make_affine(metre_unit)

        # ACT / Assert
        with pytest.raises(TypeError):
            "2" * unit  # type: ignore[operator]


class TestAffineUnitKindCompatibility:
    def test_is_compatible_with_true_for_same_kind_but_different_scale(
        self, metre_unit, kilometre_unit
    ):
        # ARRANGE
        a = make_affine(metre_unit)
        b = make_affine(kilometre_unit)

        # ACT
        result = a.is_compatible_with(b)

        # ASSERT
        assert result is True

    def test_is_compatible_with_false_for_different_dimensions(
        self, metre_unit, second_unit
    ):
        # ARRANGE
        a = make_affine(metre_unit)
        b = make_affine(second_unit)

        # ACT
        result = a.is_compatible_with(b)

        # ASSERT
        assert result is False

    def test_is_compatible_with_accepts_a_plain_unit(self, metre_unit, kilometre_unit):
        # ARRANGE
        affine = make_affine(metre_unit)

        # ACT
        result = affine.is_compatible_with(kilometre_unit)

        # ASSERT
        assert result is True

    def test_is_compatible_with_delegates_to_kind_when_compatible(self, metre):
        # ARRANGE
        sentinel = object()
        kind = make_kind("Length", make_length(), compatible=sentinel)
        delta = Unit((UnitTerm(metre),), kind=kind)  # type: ignore[arg-type]
        unit = make_affine(delta)

        # ACT
        result = unit.is_compatible_with(unit)

        # ASSERT
        assert result is sentinel

    def test_is_compatible_with_delegates_to_kind_when_incompatible(self, metre):
        # ARRANGE
        sentinel = object()
        kind = make_kind("Length", make_length(), compatible=sentinel)
        delta = Unit((UnitTerm(metre),), kind=kind)  # type: ignore[arg-type]
        unit = make_affine(delta)

        # ACT
        result = unit.is_compatible_with(unit)

        # ASSERT
        assert result is sentinel

    def test_common_kind_with_returns_kind_from_kind_common_with(self, metre):
        # ARRANGE
        sentinel = object()
        kind = make_kind("Length", make_length(), common=sentinel)
        delta = Unit((UnitTerm(metre),), kind=kind)  # type: ignore[arg-type]
        unit = make_affine(delta)

        # ACT
        result = unit.common_kind_with(unit)

        # ASSERT
        assert result is sentinel

    def test_common_kind_with_same_kind_returns_that_kind(
        self, metre_unit, kilometre_unit
    ):
        # ARRANGE
        a = make_affine(metre_unit)
        b = make_affine(kilometre_unit)

        # ACT
        result = a.common_kind_with(b)

        # ASSERT
        assert result == a.kind


class TestAffineUnitConversionTo:
    def test_conversion_to_same_unit_gives_identity_scale_and_zero_offset(
        self, metre_unit
    ):
        # ARRANGE
        unit = make_affine(metre_unit, offset=10)

        # ACT
        scale, offset = unit.conversion_to(unit)

        # ASSERT
        assert scale == Scale()
        assert offset == 0

    def test_conversion_to_scale_is_ratio_of_scales(self, metre_unit, kilometre_unit):
        # ARRANGE
        small = make_affine(metre_unit)
        large = make_affine(kilometre_unit)

        # ACT
        scale, _ = small.conversion_to(large)

        # ASSERT
        assert scale == make_scale(Fraction(1, 1000))

    def test_conversion_to_scale_for_larger_source_unit(
        self, metre_unit, kilometre_unit
    ):
        # ARRANGE
        small = make_affine(metre_unit)
        large = make_affine(kilometre_unit)

        # ACT
        scale, _ = large.conversion_to(small)

        # ASSERT
        assert scale == make_scale(1000)

    def test_conversion_to_offset_is_difference_when_target_scale_is_one(
        self, metre_unit
    ):
        # ARRANGE
        source = make_affine(metre_unit, offset=10)
        target = make_affine(metre_unit, offset=4)

        # ACT
        _, offset = source.conversion_to(target)

        # ASSERT
        assert offset == Fraction(6)

    def test_conversion_to_offset_is_negative_when_target_offset_is_larger(
        self, metre_unit
    ):
        # ARRANGE
        source = make_affine(metre_unit, offset=4)
        target = make_affine(metre_unit, offset=10)

        # ACT
        _, offset = source.conversion_to(target)

        # ASSERT
        assert offset == Fraction(-6)

    def test_conversion_to_offset_is_divided_by_target_scale(
        self, metre_unit, kilometre_unit
    ):
        # ARRANGE
        source = make_affine(metre_unit, offset=500)
        target = make_affine(kilometre_unit, offset=0)

        # ACT
        _, offset = source.conversion_to(target)

        # ASSERT
        assert offset == Fraction(500, 1000)

    def test_conversion_to_offset_is_fraction_for_exact_scales(
        self, metre_unit, kilometre_unit
    ):
        # ARRANGE
        source = make_affine(metre_unit, offset=1)
        target = make_affine(kilometre_unit, offset=0)

        # ACT
        _, offset = source.conversion_to(target)

        # ASSERT
        assert isinstance(offset, Fraction)
        assert offset == Fraction(1, 1000)

    def test_conversion_to_uses_float_when_target_scale_has_no_fraction(self, metre):
        # ARRANGE
        kind = Unit((UnitTerm(metre),)).kind
        source = make_affine(StubDelta(Scale(), kind), offset=3)  # type: ignore[arg-type]
        target = make_affine(StubDelta(Scale.constant("pi"), kind), offset=1)  # type: ignore[arg-type]

        # ACT
        _, offset = source.conversion_to(target)

        # ASSERT
        assert isinstance(offset, float)
        assert offset == pytest.approx(2 / math.pi)

    def test_conversion_to_float_fallback_still_returns_scale_ratio(self, metre):
        # ARRANGE
        kind = Unit((UnitTerm(metre),)).kind
        source = make_affine(StubDelta(Scale(), kind))  # type: ignore[arg-type]
        target = make_affine(StubDelta(Scale.constant("pi"), kind))  # type: ignore[arg-type]

        # ACT
        scale, _ = source.conversion_to(target)

        # ASSERT
        assert float(scale) == pytest.approx(1 / math.pi)

    def test_conversion_to_raises_value_error_for_incompatible_kinds(
        self, metre_unit, second_unit
    ):
        # ARRANGE
        a = make_affine(metre_unit)
        b = make_affine(second_unit)

        # ACT / Assert
        with pytest.raises(ValueError, match="incompatible kinds"):
            a.conversion_to(b)

    def test_conversion_to_raises_value_error_when_kind_reports_incompatible(
        self, metre
    ):
        # ARRANGE
        kind = make_kind("Length", make_length(), compatible=False)
        delta = Unit((UnitTerm(metre),), kind=kind)  # type: ignore[arg-type]
        unit = make_affine(delta)

        # ACT / Assert
        with pytest.raises(ValueError, match="incompatible kinds"):
            unit.conversion_to(unit)
