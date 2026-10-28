from collections.abc import Generator

# fmt: off
_PRIMES = [
    2, 3, 5, 7,
    11, 13, 17, 19,
    23, 29, 31, 37,
    41, 43, 47,
    53, 59,
    61, 67,
    71, 73, 79,
    83, 89,
    97,
]
# fmt: on


def factorise(value: int) -> Generator[tuple[int, int], None, None]:
    """Calculate the prime factorisation on `value`.

    Yields pairs of (prime, power) that make up the prime factorisation.

    Args:
        value: The number to calculate the prime factorisation of

    Returns:
        A generator of tuples containing (prime, power) pairs
    """
    if value < 1:
        raise ValueError(f"Number must be positive - {value!r} is not valid")

    for prime in _PRIMES:
        if prime * prime > value:
            break

        exp = 0
        while value % prime == 0:
            value //= prime
            exp += 1

        if exp != 0:
            yield prime, exp

    # Handle any remaining factors beyond the precomputed prime list
    div = 101
    step = 2

    while div * div <= value:
        exp = 0
        while value % div == 0:
            exp += 1
            value //= div

        if exp != 0:
            yield div, exp

        div += step
        # Alternate between steps of 2 and 4
        step = 6 - step

    if value != 1:
        yield value, 1
