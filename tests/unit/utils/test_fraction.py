from fractions import Fraction

import pytest

from units_lib.utils.fraction import convert_to_fraction


def test_convert_integer_to_fraction():
    # Arrange
    value = 5
    context = "test context"

    # Act
    result = convert_to_fraction(value, context)

    # Assert
    assert result == Fraction(5, 1)
    assert isinstance(result, Fraction)


def test_convert_fraction_string_to_fraction():
    # Arrange
    value = "1/1000"
    context = "test context"

    # Act
    result = convert_to_fraction(value, context)

    # Assert
    assert result == Fraction(1, 1000)
    assert isinstance(result, Fraction)


def test_convert_whole_number_string_to_fraction():
    # Arrange
    value = "10"
    context = "test context"

    # Act
    result = convert_to_fraction(value, context)

    # Assert
    assert result == Fraction(10, 1)


def test_convert_zero_to_fraction():
    # Arrange
    value = 0
    context = "test context"

    # Act
    result = convert_to_fraction(value, context)

    # Assert
    assert result == Fraction(0, 1)


def test_convert_negative_integer_to_fraction():
    # Arrange
    value = -5
    context = "test context"

    # Act
    result = convert_to_fraction(value, context)

    # Assert
    assert result == Fraction(-5, 1)


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        1.5,
        1.0,
        None,
        [],
        {},
    ],
)
def test_invalid_type_raises_type_error(value):
    # Arrange
    context = "test context"

    # Act
    with pytest.raises(TypeError) as error:
        convert_to_fraction(value, context)

    # Assert
    assert str(error.value) == (
        f"{context}: expected an int or a fraction string such as '1/1000', "
        f"got {value!r}"
    )


@pytest.mark.parametrize(
    "value",
    [
        "invalid",
        "1/2/3",
        "",
        "abc/123",
    ],
)
def test_invalid_fraction_string_raises_value_error(value):
    # Arrange
    context = "test context"

    # Act
    with pytest.raises(ValueError) as error:
        convert_to_fraction(value, context)

    # Assert
    assert str(error.value) == (f"{context}: invalid fraction {value!r}")


def test_divide_by_zero_raises_as_error():
    # Arrange
    context = "test context"
    value = "1/0"

    # Act
    with pytest.raises(ZeroDivisionError) as error:
        convert_to_fraction(value, context)

    # Assert
    assert (
        str(error.value)
        == "test context: converting '1/0' to a fraction causes a divide by zero"
    )


def test_value_error_preserves_original_exception():
    # Arrange
    value = "invalid"
    context = "test context"

    # Act
    with pytest.raises(ValueError) as error:
        convert_to_fraction(value, context)

    # Assert
    assert isinstance(error.value.__cause__, ValueError)
    assert str(error.value.__cause__) == "Invalid literal for Fraction: 'invalid'"
