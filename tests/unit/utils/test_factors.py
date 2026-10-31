import math
from collections.abc import Generator

import pytest

from units_lib.utils.factors import factorise


def is_prime(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def as_dict(generator: Generator[tuple[int, int], None, None]) -> dict[int, int]:
    return dict(generator)


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, {}),
        (2, {2: 1}),
        (3, {3: 1}),
        (4, {2: 2}),
        (6, {2: 1, 3: 1}),
        (7, {7: 1}),
        (12, {2: 2, 3: 1}),
        (97, {97: 1}),
        (97 * 97, {97: 2}),
        (101, {101: 1}),
        (101 * 101, {101: 2}),
        (101 * 103, {101: 1, 103: 1}),
        (2**10, {2: 10}),
        (2**3 * 3**2 * 5 * 101, {2: 3, 3: 2, 5: 1, 101: 1}),
        (1_000_003, {1_000_003: 1}),
        (999_983 * 2, {2: 1, 999_983: 1}),
        (97 * 101, {97: 1, 101: 1}),
    ],
)
def test_known_factorisations(value, expected):
    # ACT
    factorisation = factorise(value)

    # ASSERT
    assert as_dict(factorisation) == expected


@pytest.mark.parametrize(
    "value",
    list(range(1, 200)) + [10201, 123456, 999_999, 1_030_301],
)
def test_product_reconstructs_value(value):
    # ACT
    result = factorise(value)

    # ASSERT
    reconstructed = math.prod(p**e for p, e in result)
    assert reconstructed == value


@pytest.mark.parametrize("value", list(range(1, 500)) + [10201, 1_030_301])
def test_all_factors_prime_with_positive_powers(value):
    # ACT
    factorisation = factorise(value)

    # ASSERT
    for prime, power in factorisation:
        assert is_prime(prime)
        assert power >= 1


@pytest.mark.parametrize("value", [2 * 3 * 5 * 7 * 101, 12, 360, 10201])
def test_primes_unique_and_ascending(value):
    # ACT
    primes = [p for p, _ in factorise(value)]

    # ASSERT
    assert primes == sorted(set(primes))


@pytest.mark.parametrize("value", [0, -1, -100])
def test_non_positive_raises(value):
    with pytest.raises(ValueError):
        list(factorise(value))


def test_error_message_is_formatted_properly():
    with pytest.raises(ValueError, match="-5 is not valid"):
        list(factorise(-5))
