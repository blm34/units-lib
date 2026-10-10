from __future__ import annotations

import dataclasses
from fractions import Fraction

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind import resolve_kind
from units_lib.scale import Scale
from units_lib.unit.si_prefix import NONE as NO_PREFIX
from units_lib.unit.si_prefix import SIPrefix
from units_lib.unit.unit import NamedUnit, Unit, UnitTerm


def make_length() -> Dimension:
    return Dimension.base(BaseDimension.LENGTH)


def make_time() -> Dimension:
    return Dimension.base(BaseDimension.TIME)


def make_scale(factor: int | Fraction) -> Scale:
    return Scale.from_number(factor)


def make_prefix(name: str, symbol: str, factor: int | Fraction) -> SIPrefix:
    return SIPrefix(name=name, symbol=symbol, scale=make_scale(factor))


@pytest.fixture
def metre() -> NamedUnit:
    return NamedUnit(name="metre", symbol="m", dimension=make_length())


@pytest.fixture
def second() -> NamedUnit:
    return NamedUnit(name="second", symbol="s", dimension=make_time())


@pytest.fixture
def kilo() -> SIPrefix:
    return make_prefix("kilo", "k", 1000)


@pytest.fixture
def kilometre() -> NamedUnit:
    """A non-SI-prefixed unit with a non-trivial reference scale."""
    return NamedUnit(
        name="kilometre-like",
        symbol="km",
        dimension=make_length(),
        ref_scale=make_scale(1000),
    )


class TestNamedUnit:
    def test_init_stores_name_symbol_and_dimension(self):
        # ARRANGE
        dimension = make_length()

        # ACT
        unit = NamedUnit(name="metre", symbol="m", dimension=dimension)

        # ASSERT
        assert unit.name == "metre"
        assert unit.symbol == "m"
        assert unit.dimension == dimension

    def test_init_defaults_ref_scale_to_identity_scale(self, metre):
        # ARRANGE
        expected = Scale.from_number(1)

        # ACT
        actual = metre.ref_scale

        # ASSERT
        assert actual == expected

    def test_init_stores_explicit_ref_scale(self):
        # ARRANGE
        scale = make_scale(1000)

        # ACT
        unit = NamedUnit("km", "km", make_length(), ref_scale=scale)

        # ASSERT
        assert unit.ref_scale == scale

    def test_setattr_raises_because_dataclass_is_frozen(self, metre):
        # ACT / Assert
        with pytest.raises(dataclasses.FrozenInstanceError):
            metre.name = "meter"

    def test_eq_returns_true_for_identical_fields(self):
        # ARRANGE
        a = NamedUnit("metre", "m", make_length())
        b = NamedUnit("metre", "m", make_length())

        # ACT
        result = a == b

        # ASSERT
        assert result is True

    def test_hash_is_equal_for_equal_instances(self):
        # ARRANGE
        a = NamedUnit("metre", "m", make_length())
        b = NamedUnit("metre", "m", make_length())

        # ACT
        hash_a = hash(a)
        hash_b = hash(b)

        # ASSERT
        assert hash_a == hash_b


class TestUnitTerm:
    def test_defaults_to_no_prefix_and_power_one(self, metre):
        # ACT
        term = UnitTerm(metre)

        # ASSERT
        assert term.prefix == NO_PREFIX
        assert term.power == Fraction(1)

    def test_post_init_raises_value_error_when_power_is_zero(self, metre):
        # ARRANGE
        power = 0

        # ACT / Assert
        with pytest.raises(ValueError, match="cannot be zero"):
            UnitTerm(metre, power=power)

    @pytest.mark.parametrize("bad_power", [0.5, "2", None, 1.0])
    def test_post_init_raises_type_error_for_non_int_or_fraction_power(
        self, metre, bad_power
    ):
        # ACT / Assert
        with pytest.raises(TypeError, match="must be an `int` or a `fraction`"):
            UnitTerm(metre, power=bad_power)

    def test_post_init_coerces_int_power_to_fraction(self, metre):
        # ARRANGE
        power = 3

        # ACT
        term = UnitTerm(metre, power=power)

        # ASSERT
        assert isinstance(term.power, Fraction)
        assert term.power == Fraction(3)

    def test_post_init_keeps_fractional_power(self, metre):
        # ARRANGE
        power = Fraction(1, 2)

        # ACT
        term = UnitTerm(metre, power=power)

        # ASSERT
        assert term.power == Fraction(1, 2)

    def test_symbol_has_no_suffix_when_power_is_one(self, metre):
        # ARRANGE
        term = UnitTerm(metre)

        # ACT
        symbol = term.symbol

        # ASSERT
        assert symbol == "m"

    def test_symbol_includes_prefix_symbol(self, metre, kilo):
        # ARRANGE
        term = UnitTerm(metre, prefix=kilo)

        # ACT
        symbol = term.symbol

        # ASSERT
        assert symbol == "km"

    def test_symbol_does_not_wrap_integer_power_in_parentheses(self, metre):
        # ARRANGE
        term = UnitTerm(metre, power=2)

        # ACT
        symbol = term.symbol

        # ASSERT
        assert symbol == "m^2"

    def test_symbol_wraps_negative_integer_power_in_parentheses(self, metre):
        # ARRANGE
        term = UnitTerm(metre, power=-1)

        # ACT
        symbol = term.symbol

        # ASSERT
        assert symbol == "m^(-1)"

    def test_symbol_renders_fractional_power_with_parentheses(self, metre):
        # ARRANGE
        term = UnitTerm(metre, power=Fraction(1, 2))

        # ACT
        symbol = term.symbol

        # ASSERT
        assert symbol == "m^(1/2)"

    def test_name_has_no_suffix_when_power_is_one(self, metre):
        # ARRANGE
        term = UnitTerm(metre)

        # ACT
        name = term.name

        # ASSERT
        assert name == "metre"

    def test_name_includes_prefix_name_and_power(self, metre, kilo):
        # ARRANGE
        term = UnitTerm(metre, prefix=kilo, power=2)

        # ACT
        name = term.name

        # ASSERT
        assert name == "kilometre^2"

    def test_scale_is_identity_for_unprefixed_unit_with_default_ref_scale(self, metre):
        # ARRANGE
        term = UnitTerm(metre)

        # ACT
        scale = term.scale

        # ASSERT
        assert scale == Scale()

    def test_scale_combines_prefix_and_unit_ref_scale(self, kilometre, kilo):
        # ARRANGE
        term = UnitTerm(kilometre, prefix=kilo)

        # ACT
        scale = term.scale

        # ASSERT
        assert scale == make_scale(1000 * 1000)

    def test_scale_is_raised_to_the_term_power(self, kilometre):
        # ARRANGE
        term = UnitTerm(kilometre, power=2)

        # ACT
        scale = term.scale

        # ASSERT
        assert scale == make_scale(1000**2)

    def test_inverted_negates_power(self, metre):
        # ARRANGE
        term = UnitTerm(metre, power=2)

        # ACT
        inverted = term.inverted

        # ASSERT
        assert inverted.power == Fraction(-2)

    def test_inverted_preserves_unit_and_prefix(self, metre, kilo):
        # ARRANGE
        term = UnitTerm(metre, prefix=kilo, power=3)

        # ACT
        inverted = term.inverted

        # ASSERT
        assert inverted.unit == metre
        assert inverted.prefix == kilo

    def test_inverted_twice_returns_equal_term(self, metre, kilo):
        # ARRANGE
        term = UnitTerm(metre, prefix=kilo, power=Fraction(3, 2))

        # ACT
        result = term.inverted.inverted

        # ASSERT
        assert result == term

    def test_setattr_raises_because_dataclass_is_frozen(self, metre):
        # ARRANGE
        term = UnitTerm(metre)

        # ACT / Assert
        with pytest.raises(dataclasses.FrozenInstanceError):
            term.power = Fraction(2)  # pyright: ignore[reportAttributeAccessIssue]


class TestUnit:
    def test_post_init_computes_dimension_from_terms(self, metre, second):
        # ARRANGE
        terms = (UnitTerm(metre), UnitTerm(second, power=-1))
        expected = make_length() * (make_time() ** -1)

        # ACT
        unit = Unit(terms)

        # ASSERT
        assert unit.dimension == expected

    def test_post_init_computes_scale_from_terms(self, kilometre, second):
        # ARRANGE
        terms = (UnitTerm(kilometre), UnitTerm(second, power=-1))

        # ACT
        unit = Unit(terms)

        # ASSERT
        assert unit.scale == make_scale(1000)

    def test_post_init_empty_terms_is_dimensionless_with_identity_scale(self):
        # ARRANGE
        terms = ()

        # ACT
        unit = Unit(terms)

        # ASSERT
        assert unit.dimension == Dimension.dimensionless()
        assert unit.scale == Scale()

    def test_post_init_resolves_kind_from_dimension_when_not_given(self, metre):
        # ARRANGE
        terms = (UnitTerm(metre),)

        # ACT
        unit = Unit(terms)

        # ASSERT
        assert unit.kind == resolve_kind(unit.dimension)

    def test_post_init_keeps_explicit_kind_with_matching_dimension(self, metre):
        # ARRANGE
        class LengthKind:
            name = "Length"
            dimension = make_length()

        # ACT
        unit = Unit((UnitTerm(metre),), kind=LengthKind)  # type: ignore[arg-type]

        # ASSERT
        assert unit.kind is LengthKind

    def test_post_init_raises_value_error_when_kind_dimension_mismatches(self, metre):
        # ARRANGE
        class TimeKind:
            name = "Time"
            dimension = make_time()

        # ACT / Assert
        with pytest.raises(ValueError, match="cannot have a kind of"):
            Unit((UnitTerm(metre),), kind=TimeKind)  # type: ignore[arg-type]

    def test_post_init_simplifies_terms(self, metre):
        # ARRANGE
        terms = (UnitTerm(metre), UnitTerm(metre))

        # ACT
        unit = Unit(terms)

        # ASSERT
        assert unit.terms == (UnitTerm(metre, power=2),)

    def test_simplify_combines_like_terms_by_adding_powers(self, metre):
        # ARRANGE
        terms = (UnitTerm(metre, power=2), UnitTerm(metre, power=3))

        # ACT
        result = Unit._simplify(terms)

        # ASSERT
        assert result == (UnitTerm(metre, power=5),)

    def test_simplify_removes_terms_whose_powers_cancel(self, metre):
        # ARRANGE
        terms = (UnitTerm(metre, power=2), UnitTerm(metre, power=-2))

        # ACT
        result = Unit._simplify(terms)

        # ASSERT
        assert result == ()

    def test_simplify_does_not_combine_terms_with_different_prefixes(self, metre, kilo):
        # ARRANGE
        terms = (UnitTerm(metre), UnitTerm(metre, prefix=kilo))

        # ACT
        result = Unit._simplify(terms)

        # ASSERT
        assert len(result) == 2

    def test_simplify_preserves_first_seen_order(self, metre, second):
        # ARRANGE
        terms = (UnitTerm(second), UnitTerm(metre), UnitTerm(second))

        # ACT
        result = Unit._simplify(terms)

        # ASSERT
        assert [t.unit for t in result] == [second, metre]

    def test_symbol_of_empty_unit_is_empty_string(self):
        # ARRANGE
        unit = Unit(())

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == ""

    def test_symbol_of_single_term(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == "m"

    def test_symbol_joins_numerator_terms_with_middle_dot(self, metre, second):
        # ARRANGE
        unit = Unit((UnitTerm(metre), UnitTerm(second)))

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == "m·s"

    def test_symbol_places_negative_power_terms_in_denominator(self, metre, second):
        # ARRANGE
        unit = Unit((UnitTerm(metre), UnitTerm(second, power=-1)))

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == "m/s"

    def test_symbol_uses_one_as_numerator_when_only_denominator_terms(self, second):
        # ARRANGE
        unit = Unit((UnitTerm(second, power=-1),))

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == "1/s"

    def test_symbol_parenthesises_multiple_denominator_terms(self, metre, second):
        # ARRANGE
        unit = Unit(
            (
                UnitTerm(NamedUnit("kilogram", "kg", make_length())),
                UnitTerm(metre, power=-1),
                UnitTerm(second, power=-1),
            )
        )

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == "kg/(m·s)"

    def test_symbol_uses_absolute_power_for_denominator_terms(self, metre, second):
        # ARRANGE
        unit = Unit((UnitTerm(metre), UnitTerm(second, power=-2)))

        # ACT
        symbol = unit.symbol

        # ASSERT
        assert symbol == "m/(s^2)"

    def test_inverted_negates_every_term_power(self, metre, second):
        # ARRANGE
        unit = Unit((UnitTerm(metre), UnitTerm(second, power=-1)))

        # ACT
        inverted = unit.inverted

        # ASSERT
        assert inverted.terms == (
            UnitTerm(metre, power=-1),
            UnitTerm(second, power=1),
        )

    def test_inverted_inverts_dimension(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        inverted = unit.inverted

        # ASSERT
        assert inverted.dimension == unit.dimension**-1

    def test_inverted_twice_equals_original(self, kilometre, second):
        # ARRANGE
        unit = Unit((UnitTerm(kilometre), UnitTerm(second, power=-1)))

        # ACT
        result = unit.inverted.inverted

        # ASSERT
        assert result == unit

    def test_mul_concatenates_and_simplifies_terms(self, metre, second):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(second),))

        # ACT
        result = a * b

        # ASSERT
        assert result.terms == (UnitTerm(metre), UnitTerm(second))

    def test_mul_combines_like_terms(self, metre):
        # ARRANGE
        a = Unit((UnitTerm(metre),))

        # ACT
        result = a * a

        # ASSERT
        assert result.terms == (UnitTerm(metre, power=2),)

    def test_mul_multiplies_dimensions(self, metre, second):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(second),))

        # ACT
        result = a * b

        # ASSERT
        assert result.dimension == a.dimension * b.dimension

    def test_mul_returns_not_implemented_for_non_unit(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit.__mul__(2)  # pyright: ignore[reportArgumentType]

        # ASSERT
        assert result is NotImplemented

    def test_mul_with_non_unit_operator_raises_type_error(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT / Assert
        with pytest.raises(TypeError):
            unit * 2  # type: ignore[operator]

    def test_truediv_inverts_the_divisor_terms(self, metre, second):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(second),))

        # ACT
        result = a / b

        # ASSERT
        assert result.terms == (UnitTerm(metre), UnitTerm(second, power=-1))

    def test_truediv_by_self_gives_dimensionless_unit(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit / unit

        # ASSERT
        assert result.terms == ()
        assert result.dimension == Dimension.dimensionless()

    def test_truediv_returns_not_implemented_for_non_unit(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit.__truediv__(3)  # pyright: ignore[reportArgumentType]

        # ASSERT
        assert result is NotImplemented

    def test_pow_multiplies_each_term_power_by_exponent(self, metre, second):
        # ARRANGE
        unit = Unit((UnitTerm(metre), UnitTerm(second, power=-1)))

        # ACT
        result = unit**2

        # ASSERT
        assert result.terms == (
            UnitTerm(metre, power=2),
            UnitTerm(second, power=-2),
        )

    def test_pow_accepts_fractional_exponent(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre, power=2),))

        # ACT
        result = unit ** Fraction(1, 2)

        # ASSERT
        assert result.terms == (UnitTerm(metre, power=1),)

    def test_pow_with_negative_exponent_matches_inverted(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre, power=2),))

        # ACT
        result = unit**-1

        # ASSERT
        assert result == unit.inverted

    def test_pow_zero_returns_dimensionless_unit(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit**0

        # ASSERT
        assert result.terms == ()
        assert result.dimension == Dimension.dimensionless()

    @pytest.mark.parametrize("bad_exponent", [1.5, "2", None, True])
    def test_pow_returns_not_implemented_for_invalid_exponent(
        self, metre, bad_exponent
    ):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit.__pow__(bad_exponent)

        # ASSERT
        assert result is NotImplemented

    def test_eq_true_for_units_with_same_dimension_and_scale(self, metre):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(metre),))

        # ACT
        result = a == b

        # ASSERT
        assert result is True

    def test_eq_true_for_differently_composed_but_equivalent_units(self, metre):
        # ARRANGE
        a = Unit((UnitTerm(metre), UnitTerm(metre)))
        b = Unit((UnitTerm(metre, power=2),))

        # ACT
        result = a == b

        # ASSERT
        assert result is True

    def test_eq_false_for_different_dimensions(self, metre, second):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(second),))

        # ACT
        result = a == b

        # ASSERT
        assert result is False

    def test_eq_false_for_same_dimension_but_different_scale(self, metre, kilometre):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(kilometre),))

        # ACT
        result = a == b

        # ASSERT
        assert result is False

    def test_eq_returns_not_implemented_for_non_unit(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit.__eq__("m")

        # ASSERT
        assert result is NotImplemented

    def test_eq_operator_is_false_when_compared_to_non_unit(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))

        # ACT
        result = unit == "m"

        # ASSERT
        assert result is False

    def test_hash_is_equal_for_equal_units(self, metre):
        # ARRANGE
        a = Unit((UnitTerm(metre), UnitTerm(metre)))
        b = Unit((UnitTerm(metre, power=2),))

        # ACT
        hash_a = hash(a)
        hash_b = hash(b)

        # ASSERT
        assert hash_a == hash_b

    def test_hash_allows_equal_units_to_collapse_in_a_set(self, metre):
        # ARRANGE
        a = Unit((UnitTerm(metre),))
        b = Unit((UnitTerm(metre),))

        # ACT
        unique = {a, b}

        # ASSERT
        assert len(unique) == 1

    def test_repr_includes_terms_and_kind_name(self, metre):
        # ARRANGE
        class LengthKind:
            name = "Length"
            dimension = make_length()

        unit = Unit((UnitTerm(metre),), kind=LengthKind)  # type: ignore[arg-type]

        # ACT
        text = repr(unit)

        # ASSERT
        assert text.startswith("Unit(terms=")
        assert "kind=Length" in text

    def test_repr_shows_none_when_kind_is_none(self):
        # ARRANGE
        unit = Unit(())
        object.__setattr__(unit, "kind", None)

        # ACT
        text = repr(unit)

        # ASSERT
        assert text.endswith("kind=None)")

    def test_repr_does_not_include_dimension_or_scale(self, metre):
        # ARRANGE
        unit = Unit((UnitTerm(metre),))
        object.__setattr__(unit, "terms", "terms")

        # ACT
        text = repr(unit)

        # ASSERT
        assert "dimension=" not in text
        assert "scale=" not in text
