import math
from decimal import Decimal
from fractions import Fraction as F

import pytest

from units_lib.scale import Scale
from units_lib.scale.multiplication import maintain_type_multiply


class TestMaintainTypeMultiply:
    @pytest.fixture
    def pi(self) -> Scale:
        return Scale.constant("pi")

    @pytest.fixture
    def root_two(self) -> Scale:
        return Scale.from_number(2) ** F(1, 2)

    @pytest.fixture
    def one(self) -> Scale:
        return Scale.from_number(1)

    @pytest.fixture
    def three(self) -> Scale:
        return Scale.from_number(3)

    @pytest.fixture
    def half(self) -> Scale:
        return Scale.from_number(F(1, 2))

    @pytest.mark.parametrize("value", [2, F(1, 2), 2.5, -3, 0])
    def test_irrational_scale_value(self, pi, value):
        # ACT
        result = maintain_type_multiply(value, pi)

        # ASSERT
        assert type(result) is float
        assert result == pytest.approx(float(value) * math.pi)

    def test_irrational_root_scale(self, root_two):
        # ACT
        result = maintain_type_multiply(3, root_two)

        # ASSERT
        assert type(result) is float
        assert result == pytest.approx(3 * math.sqrt(2))

    def test_irrational_scale_with_rational_part(self, pi):
        # ARRANGE
        scale = pi * F(3, 2)

        # ACT
        result = maintain_type_multiply(4, scale)

        # ASSERT
        assert result == pytest.approx(6 * math.pi)

    def test_float_with_integer_scale_stays_float(self, three):
        # ACT
        result = maintain_type_multiply(1.5, three)

        # ASSERT
        assert type(result) is float
        assert result == pytest.approx(4.5)

    def test_float_with_fractional_scale_stays_float(self, half):
        # ACT
        result = maintain_type_multiply(5.0, half)

        # ASSERT
        assert type(result) is float
        assert result == pytest.approx(2.5)

    def test_float_with_identity_scale(self, one):
        # ACT
        result = maintain_type_multiply(1.25, one)

        # ASSERT
        assert type(result) is float
        assert result == 1.25

    def test_float_subclass_stays_float(self, three):
        # ARRANGE
        class MyFloat(float):
            pass

        # ACT
        result = maintain_type_multiply(MyFloat(2.0), three)

        # ASSERT
        assert isinstance(result, float)
        assert result == pytest.approx(6.0)

    def test_fraction_with_integer_scale_stays_fraction(self, three):
        # ACT
        result = maintain_type_multiply(F(1, 2), three)

        # ASSERT
        assert type(result) is F
        assert result == F(3, 2)

    def test_fraction_with_fractional_scale_is_exact(self):
        # ARRANGE
        scale = Scale.from_number(F(2, 3))

        # ACT
        result = maintain_type_multiply(F(3, 4), scale)

        # ASSERT
        assert type(result) is F
        assert result == F(1, 2)

    def test_fraction_with_whole_result_stays_fraction(self, half):
        # ACT
        result = maintain_type_multiply(F(4, 1), half)

        # ASSERT
        assert type(result) is F
        assert result == 2

    def test_fraction_with_identity_scale(self, one):
        # ACT
        result = maintain_type_multiply(F(7, 9), one)

        # ASSERT
        assert type(result) is F
        assert result == F(7, 9)

    def test_int_with_integer_scale_stays_int(self, three):
        # ACT
        result = maintain_type_multiply(4, three)

        # ASSERT
        assert type(result) is int
        assert result == 12

    def test_int_with_identity_scale_stays_int(self, one):
        # ACT
        result = maintain_type_multiply(5, one)

        # ASSERT
        assert type(result) is int
        assert result == 5

    def test_int_with_fractional_scale_becomes_fraction(self, half):
        # ACT
        result = maintain_type_multiply(3, half)

        # ASSERT
        assert type(result) is F
        assert result == F(3, 2)

    def test_int_with_fractional_scale_giving_whole_number_gives_int(self, half):
        # ACT
        result = maintain_type_multiply(4, half)

        # ASSERT
        assert type(result) is int
        assert result == 2

    @pytest.mark.parametrize("value", [0, -3])
    def test_int_edge_values_with_integer_scale(self, three, value):
        # ACT
        result = maintain_type_multiply(value, three)

        # ASSERT
        assert type(result) is int
        assert result == value * 3

    def test_negative_int_with_fractional_scale(self, half):
        # ACT
        result = maintain_type_multiply(-3, half)

        # ASSERT
        assert result == F(-3, 2)

    def test_bool_is_not_handled_as_int(self, three):
        # ACT & ASSERT
        with pytest.raises(TypeError):
            _ = maintain_type_multiply(True, three)

    @pytest.mark.parametrize("value", [2, F(5, 3), 0.75])
    @pytest.mark.parametrize("scale_value", [1, 6, F(1, 4), F(22, 7)])
    def test_matches_plain_multiplication(self, value, scale_value):
        # ARRANGE
        scale = Scale.from_number(scale_value)

        # ACT
        result = maintain_type_multiply(value, scale)

        # ASSERT
        assert float(result) == pytest.approx(float(value) * float(scale_value))

    @pytest.mark.parametrize("value", [Decimal("1.5"), "2", None, [1]])
    def test_unsupported_type_with_rational_scale_raises(self, three, value):
        with pytest.raises(TypeError, match="not supported"):
            maintain_type_multiply(value, three)  # type: ignore[arg-type]

    def test_unsupported_type_error_message_includes_value_and_type(self, three):
        # ARRANGE
        value = Decimal("1.5")

        # ACT
        with pytest.raises(TypeError) as exc_info:
            maintain_type_multiply(value, three)  # type: ignore[arg-type]

        # ASSERT
        assert repr(value) in str(exc_info.value)
        assert str(type(value)) in str(exc_info.value)
