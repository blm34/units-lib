from fractions import Fraction
from functools import singledispatch

from units_lib._types import Numeric
from units_lib.scale import Scale


def maintain_type_multiply(value: Numeric, scale: Scale) -> Numeric:
    """Multiply a value by a ``Scale``, preserving the value's type where possible.

    If ``scale`` is not rational, the result will be a float. Otherwise, the type
    of ``value`` will be preserved with the exception of ``int`` being cast to
    ``Fraction`` when required.

    Args:
        value: The value to multiply whose type will be attempted to be kept
        scale: The scale to multiply by

    Returns:
        The product as the same type as `value`
    """
    if not scale.is_rational:
        return float(value) * float(scale)

    frac = scale.as_fraction
    assert frac is not None

    return _multiply_by_fraction(value, frac)


@singledispatch
def _multiply_by_fraction(value: Numeric, frac: Fraction) -> Numeric:
    raise TypeError(f"{value!r} has type {type(value)} which is not supported")


@_multiply_by_fraction.register
def _(value: bool, frac: Fraction):
    raise TypeError(f"{value!r} has type {type(value)} which is not supported")


@_multiply_by_fraction.register
def _(value: float, frac: Fraction) -> float:
    return value * float(frac)


@_multiply_by_fraction.register
def _(value: Fraction, frac: Fraction) -> Fraction:
    return value * frac


@_multiply_by_fraction.register
def _(value: int, frac: Fraction) -> int | Fraction:
    result = value * frac

    if result.denominator == 1:
        return result.numerator
    else:
        return result
