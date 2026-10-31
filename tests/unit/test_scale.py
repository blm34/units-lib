import dataclasses
import math
from fractions import Fraction as F

import pytest

from units_lib.scale import _CONSTANTS, Scale


def factors(s: Scale) -> dict:
    return dict(s.factors)


class TestScale:
    @pytest.fixture
    def pi(self):
        return Scale.constant("pi")

    @pytest.fixture
    def one(self):
        return Scale.from_number(1)

    def test_one_is_identity(self, one):
        # ACT
        scale = Scale()

        # ASSERT
        assert scale == one
        assert scale.factors == frozenset()

    @pytest.mark.parametrize(
        "value, expected",
        [
            (2, {2: F(1)}),
            (12, {2: F(2), 3: F(1)}),
            (7, {7: F(1)}),
            (F(1, 2), {2: F(-1)}),
            (F(3, 4), {2: F(-2), 3: F(1)}),
            (F(9, 4), {2: F(-2), 3: F(2)}),
            (F(5, 7), {5: F(1), 7: F(-1)}),
            (F(7, 101), {7: F(1), 101: F(-1)}),
        ],
    )
    def test_factors(self, value, expected):
        # ACT
        scale = Scale.from_number(value)

        # ASSERT
        assert factors(scale) == expected

    def test_equal_values_give_equal_scales(self):
        # ARRANGE
        first = F(6, 4)
        second = F(3, 2)

        # ACT
        first_scale = Scale.from_number(first)
        second_scale = Scale.from_number(second)

        # ASSERT
        assert first_scale == second_scale

    @pytest.mark.parametrize("value", [0, -1, F(-1, 2)])
    def test_from_number_non_positive_raises(self, value):
        with pytest.raises(ValueError):
            Scale.from_number(value)

    def test_no_zero_exponents_stored(self):
        # ACT
        scale = Scale.from_number(F(6, 6))

        # ASSERT
        assert all(exp != 0 for _, exp in scale.factors)

    @pytest.mark.parametrize(
        "value",
        [1, 2, 10, 97, 101, 360, 10201, F(22, 7), F(1, 1000)],
    )
    def test_roundtrip_through_to_fraction(self, value):
        # ACT
        scale = Scale.from_number(value)
        result = scale.to_fraction()

        # ASSERT
        assert result == F(value)

    def test_constant_pi_factors(self):
        # ACT
        pi = Scale.constant("pi")

        # ASSERT
        assert factors(pi) == {"pi": F(1)}

    def test_constant_matches_manual_construction(self):
        # ARRANGE
        manual = Scale(frozenset({("pi", F(1))}))

        # ACT
        constant = Scale.constant("pi")

        # ASSERT
        assert constant == manual

    @pytest.mark.parametrize("name", ["tau", "", "PI", "2"])
    def test_constant_unknown_name_raises(self, name):
        with pytest.raises(ValueError, match="not known"):
            Scale.constant(name)

    @pytest.mark.parametrize("name", _CONSTANTS.keys())
    def test_every_known_constant_is_constructible_and_floatable(self, name):
        # ARRANGE
        value = _CONSTANTS[name]

        # ACT
        result = float(Scale.constant(name))

        # ASSERT
        assert result == pytest.approx(value)

    def test_simple_multiplication(self):
        # ARRANGE
        two = Scale.from_number(2)
        three = Scale.from_number(3)
        six = Scale.from_number(6)

        # ACT
        result = two * three

        # ASSERT
        assert result == six

    def test_multiplication_adds_exponents(self):
        # ARRANGE
        two = Scale.from_number(2)
        four = Scale.from_number(4)

        # ACT
        result = two * four

        # ASSERT
        assert factors(result) == {2: F(3)}

    def test_multiplicitive_identity(self, one):
        # ARRANGE
        a = Scale.from_number(F(3, 5))

        # ACT
        first = a * one
        second = one * a

        # ASSERT
        assert first == a
        assert second == a

    def test_multiplication_is_commutative(self):
        # ARRANGE
        a = Scale.from_number(F(3, 5))
        b = Scale.from_number(10)

        # ACT
        same = a * b == b * a

        # ASSERT
        assert same

    def test_multiplication_isassociative(self):
        # ARRANGE
        a, b, c = (Scale.from_number(n) for n in (2, 3, 5))

        # ACT
        same = (a * b) * c == a * (b * c)

        # ASSERT
        assert same

    def test_multiplicitive_inverse_cancels_to_identity(self, one):
        # ARRANGE
        a = Scale.from_number(F(7, 12))

        # ACT
        result = a * a**-1

        # ASSERT
        assert result == one

    def test_cancelled_factors_are_removed(self):
        assert Scale.from_number(6) * Scale.from_number(F(1, 3)) == Scale.from_number(2)

    def test_multiplication_with_constant(self, pi):
        # ARRANGE
        two = Scale.from_number(2)

        # ACT
        result = pi * two

        # ASSERT
        assert factors(result) == {"pi": F(1), 2: F(1)}

    def test_matches_rational_multiplication(self):
        # ARRANGE
        a = F(15, 4)
        b = F(8, 25)

        expected = a * b

        # ACT
        result = Scale.from_number(a) * Scale.from_number(b)

        # ASSERT
        assert result.to_fraction() == expected

    def test_multiplication_int_operand(self):
        assert Scale.from_number(3) * 4 == Scale.from_number(12)

    def test_multiplication_fraction_operand(self):
        assert Scale.from_number(3) * F(2, 9) == Scale.from_number(F(2, 3))

    def test_multiplication_int_operand_matches_scale_operand(self):
        # ARRANGE
        a = Scale.from_number(F(5, 7))

        # ACT & ASSERT
        assert a * 6 == a * Scale.from_number(6)

    def test_int_operand_with_constant(self, pi):
        assert factors(pi * 2) == {"pi": F(1), 2: F(1)}

    def test_chained_with_numbers(self, one):
        assert (one * 2 * F(3, 4) * 8).to_fraction() == 12

    @pytest.mark.parametrize("value", [0, -3, F(-1, 2)])
    def test_multiplication_non_positive_number_raises(self, one, value):
        with pytest.raises(ValueError):
            _ = one * value

    @pytest.mark.parametrize("value", [1.5, "2", None])
    def test_multiplication_unsupported_operand_returns_not_implemented(
        self, one, value
    ):
        assert Scale.__mul__(one, value) is NotImplemented

        with pytest.raises(TypeError):
            _ = one * value

    def test_multiplication_reflected_int_operand(self):
        assert 4 * Scale.from_number(3) == Scale.from_number(12)

    def test_multiplication_reflected_fraction_operand(self):
        assert F(1, 2) * Scale.from_number(6) == Scale.from_number(3)

    def test_truediv(self):
        # ARRANGE
        a = Scale.from_number(6)
        b = Scale.from_number(3)

        # ACT & ASSERT
        assert a / b == Scale.from_number(2)

    def test_self_division_is_identity(self, one):
        # ARRANGE
        a = Scale.from_number(F(5, 9))

        # ACT & ASSERT
        assert a / a == one

    def test_division_by_pi(self, pi):
        assert factors(Scale.from_number(2) / pi) == {2: F(1), "pi": F(-1)}

    def test_division_int_operand(self):
        assert Scale.from_number(12) / 4 == Scale.from_number(3)

    def test_division_fraction_operand(self):
        assert Scale.from_number(3) / F(3, 4) == Scale.from_number(4)

    def test_division_int_operand_matches_scale_operand(self):
        # ARRANGE
        a = Scale.from_number(F(5, 7))

        # ACT & ASSERT
        assert a / 6 == a / Scale.from_number(6)

    def test_constant_divided_by_itself(self, pi, one):
        assert pi / pi == one

    @pytest.mark.parametrize("value", [0, -3, F(-1, 2)])
    def test_division_non_positive_number_raises(self, one, value):
        # ASSERT
        with pytest.raises(ValueError):
            _ = one / value

    @pytest.mark.parametrize("value", [1.5, "2", None])
    def test_division_unsupported_operand_returns_not_implemented(self, one, value):
        assert Scale.__truediv__(one, value) is NotImplemented

        with pytest.raises(TypeError):
            _ = one / value

    def test_division_reflected_int_operand(self):
        assert 12 / Scale.from_number(4) == Scale.from_number(3)

    def test_division_reflected_fraction_operand(self):
        assert F(1, 2) / Scale.from_number(4) == Scale.from_number(F(1, 8))

    def test_power_zero_gives_identity(self, one):
        assert Scale.from_number(12) ** 0 == one

    def test_power_one_is_noop(self):
        # ARRANGE
        a = Scale.from_number(12)

        # ACT & ASSERT
        assert a**1 == a

    def test_integer_power(self):
        assert Scale.from_number(2) ** 3 == Scale.from_number(8)

    def test_negative_power(self):
        assert Scale.from_number(2) ** -2 == Scale.from_number(F(1, 4))

    def test_fractional_power_stays_exact(self):
        # ACT
        s = Scale.from_number(4) ** F(1, 2)

        # ASSERT
        assert s == Scale.from_number(2)

    def test_irrational_result_has_no_fraction(self):
        # ASSERT
        assert (Scale.from_number(2) ** F(1, 2)).to_fraction() is None

    def test_power_of_power(self):
        # ARRANGE
        a = Scale.from_number(F(3, 2))

        # ACT & ASSERT
        assert (a**2) ** 3 == a**6

    def test_power_distributes_over_mul(self):
        # ARRANGE
        a = Scale.from_number(6)
        b = Scale.from_number(F(5, 3))

        # ACT & ASSERT
        assert (a * b) ** 2 == a**2 * b**2

    def test_pi_power(self, pi):
        assert factors(pi**3) == {"pi": F(3)}

    def test_from_number_to_fraction_round_trip_integer(self):
        assert Scale.from_number(1).to_fraction() == 1

    def test_from_number_to_fraction_round_trip_fraction(self):
        assert Scale.from_number(F(3, 4)).to_fraction() == F(3, 4)

    def test_pi_is_not_rational(self, pi):
        assert pi.to_fraction() is None

    def test_fractional_exponent_is_not_rational(self):
        assert (Scale.from_number(3) ** F(1, 3)).to_fraction() is None

    def test_constants_cancelling_become_rational(self, pi):
        assert (pi * Scale.from_number(5) / pi).to_fraction() == 5

    def test_fractional_exponents_combining_to_integer(self):
        # ARRANGE
        root2 = Scale.from_number(2) ** F(1, 2)

        # ACT & ASSERT
        assert (root2 * root2).to_fraction() == 2

    @pytest.mark.parametrize("value", [2, F(1, 2), 1])
    def test_returns_a_float(self, value):
        # ACT
        result = float(Scale.from_number(value))

        # ASSERT
        assert type(result) is float

    @pytest.mark.parametrize(
        "value", [1, 2, 12, F(1, 2), F(22, 7), F(1, 1000), 101 * 103]
    )
    def test_rational_values(self, value):
        assert float(Scale.from_number(value)) == pytest.approx(float(value))

    def test_float_pi(self, pi):
        assert float(pi) == pytest.approx(math.pi)

    @pytest.mark.parametrize("power", [-2, -1, 2, 3, F(1, 2), F(-1, 2)])
    def test_pi_powers(self, pi, power):
        assert float(pi**power) == pytest.approx(math.pi ** float(power))

    @pytest.mark.parametrize("power", [-3, -1, 2, F(1, 3), F(-3, 2)])
    def test_rational_powers(self, power):
        # ACT
        s = Scale.from_number(F(5, 3)) ** power

        # ASSERT
        assert float(s) == pytest.approx((5 / 3) ** float(power))

    def test_large_value(self):
        assert float(Scale.from_number(10**30)) == pytest.approx(1e30)

    def test_tiny_value(self):
        assert float(Scale.from_number(F(1, 10**30))) == pytest.approx(1e-30)

    def test_sqrt(self):
        assert float(Scale.from_number(2) ** F(1, 2)) == pytest.approx(math.sqrt(2))

    def test_mixed(self, pi):
        # ARRANGE
        s = Scale.from_number(F(3, 2)) * pi**2

        # ASSERT
        assert float(s) == pytest.approx(1.5 * math.pi**2)

    def test_float_of_product_matches_product_of_floats(self, pi):
        # ARRANGE
        a = Scale.from_number(F(7, 3))
        b = pi

        # ACT & ASSERT
        assert float(a * b) == pytest.approx(float(a) * float(b))

    def test_hashable_and_equal_hash(self):
        # ARRANGE
        a = Scale.from_number(F(3, 2))
        b = Scale.from_number(F(6, 4))

        # ASSERT
        assert hash(a) == hash(b)
        assert len({a, b}) == 1

    def test_different_values_not_equal(self):
        assert Scale.from_number(2) != Scale.from_number(3)

    def test_frozen(self, one):
        with pytest.raises(dataclasses.FrozenInstanceError):
            one.factors = frozenset()  # type: ignore[misc]

    def test_operations_do_not_mutate_operands(self):
        # ARRANGE
        a = Scale.from_number(6)
        b = Scale.from_number(10)

        before = (a.factors, b.factors)

        # ACT
        _ = a * b
        _ = a**2

        # ASSERT
        assert (a.factors, b.factors) == before
