from __future__ import annotations

import dataclasses
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from units_lib.dimensions import BaseDimension, Dimension

N_BASE = len(BaseDimension)


int_exponents = st.integers(min_value=-50, max_value=50)
frac_exponents = st.fractions(min_value=-50, max_value=50, max_denominator=20)
exponents = st.one_of(int_exponents, frac_exponents)

exps_tuples = st.tuples(*[exponents] * N_BASE)

# The main strategy: a random `Dimension`. Use it with `@given(dimensions)`,
# or `@given(a=dimensions, b=dimensions)` when a test needs several.
dimensions = st.builds(Dimension, exps=exps_tuples)

base_dimensions = st.sampled_from(BaseDimension)

# Powers to raise dimensions to.
powers = exponents


DIMENSIONLESS = Dimension.dimensionless()


@given(exps_tuples)
def test_construction_normalises_exponents_to_fractions(exps):
    # ACT
    dim = Dimension(exps)

    # ASSERT
    assert len(dim.exps) == N_BASE
    assert all(isinstance(e, Fraction) for e in dim.exps)
    assert dim.exps == tuple(Fraction(e) for e in exps)


@given(st.lists(exponents).filter(lambda xs: len(xs) != N_BASE))
def test_wrong_number_of_exponents_is_rejected(exps):
    # ACT & ASSERT
    with pytest.raises(ValueError):
        Dimension(tuple(exps))  # type: ignore[arg-type]


@given(st.tuples(*[int_exponents] * N_BASE))
def test_int_and_fraction_exponents_are_equivalent(int_exps):
    # ACT
    as_ints = Dimension(int_exps)
    as_fracs = Dimension(tuple(Fraction(e) for e in int_exps))  # pyright: ignore[reportArgumentType]

    # ASSERT
    assert as_ints == as_fracs
    assert hash(as_ints) == hash(as_fracs)


@given(dimensions)
def test_is_immutable(dim):
    # ACT & ASSERT
    with pytest.raises(dataclasses.FrozenInstanceError):
        dim.exps = ()  # type: ignore[misc]


@given(dimensions)
def test_repr_round_trips(dim):
    # ACT
    result = eval(repr(dim), {"Dimension": Dimension, "Fraction": Fraction})

    # ASSERT
    assert result == dim


@given(dimensions, base_dimensions)
def test_multiplying_by_a_base_increments_only_that_exponent(dim, base):
    # ARRANGE
    base_dim = Dimension.base(base)

    # ACT
    result = dim * base_dim

    # ASSERT
    for other in BaseDimension:
        delta = 1 if other is base else 0
        assert result.exps[other.index] == dim.exps[other.index] + delta


@given(base_dimensions, powers)
def test_base_to_a_power_has_that_power_as_its_exponent(base, n):
    # ARRANGE
    base_dim = Dimension.base(base)

    # ACT
    dim = base_dim**n

    # ASSERT
    assert dim.exps[base.index] == n
    assert all(e == 0 for i, e in enumerate(dim.exps) if i != base.index)


@given(dimensions, dimensions)
def test_multiplication_is_commutative(a, b):
    assert a * b == b * a


@given(dimensions, dimensions, dimensions)
def test_multiplication_is_associative(a, b, c):
    assert (a * b) * c == a * (b * c)


@given(dimensions)
def test_dimensionless_is_the_multiplicative_identity(d):
    assert d * DIMENSIONLESS == d
    assert DIMENSIONLESS * d == d


@given(dimensions)
def test_dividing_by_self_gives_dimensionless(d):
    assert d / d == DIMENSIONLESS


@given(dimensions)
def test_reciprocal_is_the_multiplicative_inverse(d):
    inv = DIMENSIONLESS / d
    assert d * inv == DIMENSIONLESS
    assert inv * d == DIMENSIONLESS


@given(dimensions, dimensions)
def test_division_is_multiplication_by_the_inverse(a, b):
    assert a / b == a * (b**-1)


@given(dimensions, dimensions)
def test_division_undoes_multiplication(a, b):
    assert (a * b) / b == a
    assert (a / b) * b == a


@given(dimensions, dimensions)
def test_swapping_division_operands_gives_the_reciprocal(a, b):
    assert a / b == (b / a) ** -1


@given(dimensions)
def test_power_zero_is_dimensionless(d):
    assert d**0 == DIMENSIONLESS


@given(dimensions)
def test_power_one_is_identity(d):
    assert d**1 == d


@given(dimensions)
def test_power_minus_one_is_reciprocal(d):
    assert d**-1 == DIMENSIONLESS / d


@given(dimensions, st.integers(min_value=0, max_value=5))
def test_integer_power_matches_repeated_multiplication(d, n):
    # ACT
    power = d**n

    multiply = DIMENSIONLESS
    for _ in range(n):
        multiply = multiply * d

    # ASSERT
    assert power == multiply


@given(dimensions, powers, powers)
def test_exponents_add_when_multiplying_powers(d, m, n):
    assert d ** (m + n) == (d**m) * (d**n)


@given(dimensions, powers, powers)
def test_power_of_a_power_multiplies_exponents(d, m, n):
    assert (d**m) ** n == d ** (m * n)


@given(dimensions, dimensions, powers)
def test_power_distributes_over_multiplication(a, b, n):
    assert (a * b) ** n == (a**n) * (b**n)


@given(dimensions, dimensions, powers)
def test_power_distributes_over_division(a, b, n):
    assert (a / b) ** n == (a**n) / (b**n)


@given(dimensions, st.integers(1, 6))
def test_root_then_power_round_trips(dim, n):
    assert (dim ** Fraction(1, n)) ** n == dim


@given(dimensions, dimensions)
def test_equal_dimensions_have_equal_hashes(a, b):
    if a == b:
        assert hash(a) == hash(b)
    else:
        assert hash(a) != hash(b)
