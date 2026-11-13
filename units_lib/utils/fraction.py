from fractions import Fraction


def convert_to_fraction(value: int | str, context: str) -> Fraction:
    """Convert `value` to a Fraction.

    Takes an integer or a string of the form '1/1000' and converts it into a
    ``Fraction`` object.

    Args:
        value: The value to convert to a fraction
        context: The context that `value` has come from (for error messages)

    Returns:
        The parsed fraction
    """
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError(
            f"{context}: expected an int or a fraction string such as '1/1000', "
            f"got {value!r}"
        )
    try:
        return Fraction(value)
    except ValueError as exc:
        raise ValueError(f"{context}: invalid fraction {value!r}") from exc
    except ZeroDivisionError as exc:
        raise ZeroDivisionError(
            f"{context}: converting {value!r} to a fraction causes a divide by zero"
        ) from exc
