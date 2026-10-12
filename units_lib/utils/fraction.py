from fractions import Fraction


def _iroot(n: int, k: int) -> int | None:
    """Calculate the `k`th root of `n` if it is an integer."""
    r = round(n ** (1 / k))
    return next(
        (c for c in (r - 1, r, r + 1) if c >= 0 and c**k == n),
        None,
    )


def frac_pow(base: Fraction, exp: Fraction) -> Fraction | float:
    """Calculate a fractional power of a fraction.

    If the result is rational, return a fraction, else return a float.

    Args:
        base: The base fraction to raise to a power
        exp: The power to raise the base to

    Returns:
        The value of the base raised to the power of the exponent
    """
    p = exp.denominator
    q = exp.denominator

    if q != 1:
        n = _iroot(base.numerator, q)
        d = _iroot(base.denominator, q)

        if n is None or d is None:
            return float(base) ** float(exp)
        base = Fraction(n, d)

    return base**p
