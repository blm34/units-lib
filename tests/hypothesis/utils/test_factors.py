import math
from collections import Counter

import pytest
from hypothesis import given
from hypothesis import strategies as st

from units_lib.utils.factors import factorise

# fmt: off
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 53, 97, 101, 103, 107, 109, 113, 997, 1009, 10007, 104729]
# fmt: on

positive_ints = st.integers(min_value=1, max_value=10**9)


def is_prime(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def as_counter(n: int) -> Counter:
    return Counter(dict(factorise(n)))


@given(positive_ints)
def test_product_of_factors_reconstructs_value(n):
    assert math.prod(p**e for p, e in factorise(n)) == n


@given(positive_ints)
def test_factors_are_prime_ascending_and_unique_with_positive_powers(n):
    result = list(factorise(n))

    primes = [p for p, _ in result]
    exponents = [e for _, e in result]

    assert all(is_prime(p) for p in primes)
    assert all(e >= 1 for e in exponents)
    assert primes == sorted(set(primes))


@given(st.lists(st.sampled_from(SMALL_PRIMES), max_size=8))
def test_recovers_constructed_factorisation(primes):
    """Build a number from known primes, and check we get exactly those back."""
    expected = Counter(primes)
    n = math.prod(primes)

    assert as_counter(n) == expected


@given(st.sampled_from(SMALL_PRIMES), st.integers(min_value=1, max_value=3))
def test_prime_powers(p, k):
    assert list(factorise(p**k)) == [(p, k)]


@given(st.integers(1, 10**4), st.integers(1, 10**4))
def test_factorisation_is_multiplicative(a, b):
    assert as_counter(a * b) == as_counter(a) + as_counter(b)


@given(st.integers(1, 10**5), st.integers(1, 4))
def test_powers_scale_exponents(n, k):
    assert as_counter(n**k) == Counter({p: e * k for p, e in factorise(n)})


@given(st.sampled_from([p for p in SMALL_PRIMES if p > 97]))
def test_primes_beyond_precomputed_list_are_found(p):
    assert list(factorise(p)) == [(p, 1)]
    assert list(factorise(p * p)) == [(p, 2)]


@given(st.integers(max_value=0))
def test_non_positive_raises(n):
    with pytest.raises(ValueError):
        list(factorise(n))
