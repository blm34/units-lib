import math
from fractions import Fraction as F

import pytest
from hypothesis import given
from hypothesis import strategies as st

from units_lib.scale import Scale

ONE = Scale()
PI = Scale.constant("pi")


rationals = st.builds(F, st.integers(1, 10**6), st.integers(1, 10**4))

exponents = st.fractions(min_value=-3, max_value=3, max_denominator=5)
int_exponents = st.integers(-3, 3)
nonzero_exponents = exponents.filter(lambda e: e != 0)


@st.composite
def scales(draw) -> Scale:
    """Scales mixing rational powers of primes with powers of pi."""
    s = Scale.from_number(draw(rationals)) ** draw(exponents)
    s *= PI ** draw(exponents)
    return s


def is_prime(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def is_square(n: int) -> bool:
    return math.isqrt(n) ** 2 == n


def approx(x: float) -> object:
    return pytest.approx(x, rel=1e-9)


@given(rationals)
def test_from_number_roundtrips(q):
    assert Scale.from_number(q).to_fraction() == q


@given(rationals)
def test_from_number_uses_only_primes_and_nonzero_exponents(q):
    for base, exp in Scale.from_number(q).factors:
        assert isinstance(base, int) and is_prime(base)
        assert exp != 0


@given(rationals, rationals)
def test_from_number_is_injective(a, b):
    assert (Scale.from_number(a) == Scale.from_number(b)) == (a == b)


@given(rationals, rationals)
def test_from_number_is_multiplicative(a, b):
    assert Scale.from_number(a) * Scale.from_number(b) == Scale.from_number(a * b)


@given(rationals)
def test_from_number_float_matches_fraction(q):
    assert float(Scale.from_number(q)) == approx(float(q))


@given(st.integers(max_value=0))
def test_from_number_rejects_non_positive_ints(n):
    with pytest.raises(ValueError):
        Scale.from_number(n)


@given(rationals)
def test_from_number_rejects_negated_rationals(q):
    with pytest.raises(ValueError):
        Scale.from_number(-q)


@given(scales(), scales())
def test_results_never_contain_zero_exponents(a, b):
    for s in (a * b, a / b, a**2, a ** F(-1, 3)):
        assert all(exp != 0 for _, exp in s.factors)


@given(scales(), scales())
def test_mul_commutative(a, b):
    assert a * b == b * a


@given(scales(), scales(), scales())
def test_mul_associative(a, b, c):
    assert (a * b) * c == a * (b * c)


@given(scales())
def test_mul_identity(a):
    assert a * ONE == a == ONE * a


@given(scales())
def test_inverse(a):
    assert a * a**-1 == ONE
    assert a / a == ONE


@given(scales(), scales())
def test_div_is_mul_by_inverse(a, b):
    assert a / b == a * b**-1


@given(scales(), scales())
def test_div_undoes_mul(a, b):
    assert (a * b) / b == a


@given(scales(), scales())
def test_operations_do_not_mutate_operands(a, b):
    before = (a.factors, b.factors)
    _ = a * b, a / b, a**2
    assert (a.factors, b.factors) == before


@given(scales(), rationals)
def test_mul_by_number_equals_mul_by_scale(a, q):
    assert a * q == a * Scale.from_number(q)


@given(scales(), rationals)
def test_div_by_number_equals_div_by_scale(a, q):
    assert a / q == a / Scale.from_number(q)


@given(scales(), st.integers(max_value=0))
def test_mul_by_non_positive_int_raise(a, n):
    with pytest.raises(ValueError):
        _ = a * n


@given(scales(), st.integers(max_value=0))
def test_div_by_non_positive_int_raise(a, n):
    with pytest.raises(ValueError):
        _ = a / n


@given(scales())
def test_pow_one(a):
    assert a**0 == ONE


@given(scales())
def test_pow_zero(a):
    assert a**1 == a


@given(scales(), exponents, exponents)
def test_pow_adds_exponents(a, p, q):
    assert a ** (p + q) == a**p * a**q


@given(scales(), exponents, exponents)
def test_pow_of_pow_multiplies_exponents(a, p, q):
    assert (a**p) ** q == a ** (p * q)


@given(scales(), scales(), exponents)
def test_pow_distributes_over_mul(a, b, p):
    assert (a * b) ** p == a**p * b**p


@given(rationals, rationals)
def test_to_fraction_of_product_and_quotient(a, b):
    sa = Scale.from_number(a)
    sb = Scale.from_number(b)

    assert (sa * sb).to_fraction() == a * b
    assert (sa / sb).to_fraction() == a / b


@given(rationals, int_exponents)
def test_to_fraction_of_integer_power(q, n):
    assert (Scale.from_number(q) ** n).to_fraction() == q**n


@given(rationals)
def test_square_root_is_rational_iff_perfect_square(q):
    root = Scale.from_number(q) ** F(1, 2)
    expected_rational = is_square(q.numerator) and is_square(q.denominator)

    result = root.to_fraction()

    assert (result is not None) == expected_rational
    if result is not None:
        assert result * result == q

    # Squaring always recovers the original, exactly
    assert root**2 == Scale.from_number(q)


@given(rationals, nonzero_exponents)
def test_any_pi_power_makes_value_irrational(q, e):
    assert (Scale.from_number(q) * PI**e).to_fraction() is None


@given(rationals, exponents)
def test_pi_powers_cancel(q, e):
    s = Scale.from_number(q) * PI**e / PI**e
    assert s.to_fraction() == q


@given(scales())
def test_float_is_positive_finite_float(a):
    f = float(a)

    assert type(f) is float
    assert 0 < f < math.inf


@given(scales(), scales())
def test_float_of_mul_and_div(a, b):
    assert float(a * b) == approx(float(a) * float(b))
    assert float(a / b) == approx(float(a) / float(b))


@given(scales(), exponents)
def test_float_of_pow(a, p):
    assert float(a**p) == approx(float(a) ** float(p))


@given(scales())
def test_float_of_inverse(a):
    assert float(a**-1) == approx(1 / float(a))


@given(exponents)
def test_float_of_pi_power(e):
    assert float(PI**e) == approx(math.pi ** float(e))


@given(scales(), scales())
def test_equal_scales_hash_equal(a, b):
    assert (a * b) == (b * a)
    assert hash(a * b) == hash(b * a)


@given(scales(), scales())
def test_set_membership_matches_equality(a, b):
    assert (len({a, b}) == 1) == (a == b)
