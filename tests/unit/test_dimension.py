from __future__ import annotations

from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from units_lib.dimensions import BaseDimension, Dimension


class TestBaseDimension:
    def test_has_seven_members(self):
        # ACT
        length = len(BaseDimension)

        # ASSERT
        assert length == 7

    def test_indexes_are_contiguous_from_zero(self):
        # ASSERT
        assert [d.index for d in BaseDimension] == [0, 1, 2, 3, 4, 5, 6]

    def test_symbols_are_unique(self):
        # ARRANGE
        symbols = {dim.symbol for dim in BaseDimension}

        # ASSERT
        assert len(symbols) == len(BaseDimension)


class TestDimension:
    @pytest.fixture
    def time(self):
        return Dimension.base(BaseDimension.TIME)

    @pytest.fixture
    def length(self):
        return Dimension.base(BaseDimension.LENGTH)

    @pytest.fixture
    def mass(self):
        return Dimension.base(BaseDimension.MASS)

    @pytest.fixture
    def dimensionless(self):
        return Dimension.dimensionless()

    def test_direct_construction_stores_exps(self):
        # ARRANGE
        exps = tuple(Fraction(i) for i in range(7))

        # ACT
        dimension = Dimension(exps)  # type: ignore[arg-type]

        # ASSERT
        assert dimension.exps == exps

    @pytest.mark.parametrize("length", (0, 1, 3, 6, 8, 9, 10))
    def test_wrong_length_of_exps_raises_value_error(self, length):
        # ARRANGE
        exps = (Fraction(1),) * length

        # ACT & ASSERT
        with pytest.raises(ValueError):
            Dimension(exps)

    def test_exps_are_converted_to_fractions(self):
        # ARRANGE
        exps = (0, 1, 2, 3, 4, 5, 6)

        # ACT
        result = Dimension(exps)

        # ASSERT
        assert all(isinstance(e, Fraction) for e in result.exps)

    @pytest.mark.parametrize("dim", list(BaseDimension))
    def test_base_has_one_in_its_own_slot_and_zero_elsewhere(self, dim):
        # ACT
        result = Dimension.base(dim)

        # ASSERT
        assert result.exps.count(Fraction(0)) == 6
        assert result.exps[dim.index] == Fraction(1)

    def test_dimensionless_is_all_zero(self):
        # ARRANGE
        dimensionless = Dimension.dimensionless()

        # ASSERT
        assert all(exp == Fraction(0) for exp in dimensionless.exps)

    def test_dimensionless_returns_equal_instances(self):
        # ACT
        dim1 = Dimension.dimensionless()
        dim2 = Dimension.dimensionless()

        # ASSERT
        assert dim1 == dim2

    def test_equal_dimensions_compare_equal(self, make_dim):
        # ARRANGE
        first = make_dim(length=1, time=-1)
        second = make_dim(length=1, time=-1)

        # ACT
        same = first == second

        # ASSERT
        assert same

    def test_different_dimensions_compare_unequal(self, length, time):
        # ACT
        same = length == time

        # ASSERT
        assert not same

    def test_equal_dimensions_have_equal_hashes(self, make_dim):
        # ARRANGE
        first = make_dim(length=1, time=-1)
        second = make_dim(length=1, time=-1)

        # ACT
        first_hash = hash(first)
        second_hash = hash(second)

        # ASSERT
        assert first_hash == second_hash

    def test_cannot_reassign_exps(self, length, dimensionless):
        with pytest.raises(FrozenInstanceError):
            # ACT
            length.exps = dimensionless.exps  # type: ignore[misc]

    def test_multiplication_with_same_base_adds_exponents(self, length):
        # ACT
        result = length * length

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == 2

    def test_multiplication_with_different_bases_combine(self, length, time):
        # ACT
        result = length * time

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == 1
        assert result.exps[BaseDimension.TIME.index] == 1

    @pytest.mark.parametrize("dim", list(BaseDimension))
    def test_multiplication_with_dimensionless_is_multiplicative_identity(
        self, dimensionless, dim
    ):
        # ARRANGE
        dimension = Dimension.base(dim)

        # ASSERT
        assert dimension * dimensionless == dimension
        assert dimensionless * dimension == dimension

    def test_multiplication_is_commutative(self, length, mass):
        # ASSERT
        assert length * mass == mass * length

    def test_multiplication_is_associative(self, length, mass, time):
        # ASSERT
        assert (length * mass) * time == length * (mass * time)

    def test_multiplication_with_inverse_gives_dimensionless(
        self, dimensionless, make_dim
    ):
        # ARRANGE
        dim = make_dim(mass=1)
        inverse = make_dim(mass=-1)

        # ACT
        result = dim * inverse

        # ASSERT
        assert result == dimensionless

    def test_multiplication_with_fractional_exponents(self, length, make_dim):
        # ARRANGE
        half = make_dim(length=Fraction(1, 2))

        # ACT
        result = half * half

        # ASSERT
        assert result == length

    def test_multiplication_does_not_mutate_operands(self, length, time):
        # ARRANGE
        before = length.exps

        # ACT
        _ = length * time

        # ASSERT
        assert length.exps == before

    def test_multiplication_returns_dimension(self, length, time):
        # ACT
        result = length * time

        # ASSERT
        assert isinstance(result, Dimension)

    def test_division_subtracts_exponents(self, length, time):
        # ACT
        result = length / time

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == 1
        assert result.exps[BaseDimension.TIME.index] == -1

    def test_division_self_division_is_dimensionless(self, length, dimensionless):
        # ACT
        result = length / length

        # ASSERT
        assert result == dimensionless

    def test_division_divide_by_dimensionless_is_identity(self, length, dimensionless):
        # ACT
        result = length / dimensionless

        # ASSERT
        assert result == length

    def test_division_dimensionless_divided_by_x_is_inverse(
        self, length, dimensionless
    ):
        # ACT
        result = dimensionless / length

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == -1

    def test_division_not_commutative(self, length, time):
        # ACT
        first = length / time
        second = time / length

        # ASSERT
        assert first != second

    def test_division_inverse_of_multiplication(self, length, time):
        # ACT
        result = (length * time) / time

        # ASSERT
        assert result == length

    def test_power_of_zero_is_dimensionless(self, dimensionless, make_dim):
        # ARRANGE
        dimension = make_dim(mass=2, time=-1, temperature=4)

        # ACT
        result = dimension**0

        assert result == dimensionless

    def test_power_one_is_identity(self, make_dim):
        # ASSERT
        dimension = make_dim(mass=2, time=-1, temperature=3)

        # ACT
        result = dimension**1

        assert result == dimension

    def test_power_positive_int(self, make_dim):
        # ARRANGE
        dimension = make_dim(electric_current=1)
        expected_result = make_dim(electric_current=3)

        # ACT
        result = dimension**3

        # ASSERT
        assert result == expected_result

    def test_power_negative_int(self, length):
        # ACT
        result = length**-2

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == -2

    def test_power_fraction(self, length):
        # ARRANGE
        half = Fraction(1, 2)

        # ACT
        result = length**half

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == half

    def test_power_applies_to_all_exponents(self, make_dim):
        # ARRANGE
        half = Fraction(1, 2)

        dimension = make_dim(length=1, mass=2, time=half)
        expected_result = make_dim(length=2, mass=4, time=1)

        # ACT
        result = dimension**2

        # ASSERT
        assert result == expected_result

    def test_power_matches_repeated_multiplication(self, length):
        # ACT
        power = length**3
        multiplied = length * length * length

        # ASSERT
        assert power == multiplied

    def test_power_fraction_then_inverse_fraction_round_trips(self, make_dim):
        # ARRANGE
        dimension = make_dim(length=1, time=-3)

        # ACT
        result = (dimension ** Fraction(1, 3)) ** 3

        # ASSERT
        assert result == dimension

    def test_power_dimensionless_to_any_power_is_dimensionless(self, dimensionless):
        # ACT
        result = dimensionless**5

        # ASSERT
        assert result == dimensionless

    def test_power_no_float_precision_loss(self, length):
        # ARRANGE
        third = Fraction(1, 3)

        # ACT
        result = length**third

        # ASSERT
        assert result.exps[BaseDimension.LENGTH.index] == third

    def test_repr_starts_with_class_name(self, length):
        # ACT
        result = repr(length)

        # ASSERT
        assert result.startswith("Dimension(")

    def test_repr_round_trips_via_eval(self, make_dim):
        # ARRANGE
        dimension = make_dim(length=1, mass=3, time=Fraction(1, 2), temperature=4)

        # ACT
        result = eval(repr(dimension))

        # ASSERT
        assert result == dimension

    def test_string_dimensionless_is_empty_string(self, dimensionless):
        # ACT
        result = str(dimensionless)

        # ASSERT
        assert result == ""

    def test_string_negative_exponent(self, time):
        # ARRANGE
        dimension = time**-1

        # ACT
        result = str(dimension)

        # ASSERT
        assert result == "T^-1"

    def test_string_fractional_exponent(self, length):
        # ARRANGE
        dimension = length ** Fraction(1, 2)

        # ACT
        result = str(dimension)

        # ASSERT
        assert result == "L^1/2"

    def test_string_zero_exponents_are_omitted(self, length, time):
        # ARRANGE
        dimension = length / time

        # ACT
        result = str(dimension)

        # ASSERT
        assert "M" not in result

    def test_string_joined_with_middle_dot(self, length, time):
        # ARRANGE
        dimension = length * time

        # ACT
        result = str(dimension)

        # ASSERT
        assert "·" in result

    def test_string_follows_base_dimension_order_not_construction_order(
        self, length, time, mass
    ):
        # Order is T, L, M, I, ϴ, N, J regardless of how it was built.
        assert str(mass * length * time) == "T·L·M"
        assert str(time * length * mass) == "T·L·M"

    def test_string_force(self, mass, length, time):
        # ARRANGE
        dim = mass * length / time**2

        # ACT
        string = str(dim)

        # ASSERT
        assert string == "T^-2·L·M"

    def test_string_all_seven_dimensions(self):
        # ARRANGE
        dim = Dimension((1, 1, 1, 1, 1, 1, 1))

        # ACT
        string = str(dim)

        # ASSERT
        assert string == "T·L·M·I·Θ·N·J"
