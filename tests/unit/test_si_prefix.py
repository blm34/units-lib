from __future__ import annotations

import dataclasses
from fractions import Fraction

import pytest

from units_lib import si_prefix as p
from units_lib.si_prefix import (
    CENTI,
    DECA,
    DECI,
    HECTO,
    KILO,
    MEGA,
    MICRO,
    MILLI,
    NONE,
    QUECTO,
    QUETTA,
    RONTO,
    SIPrefix,
    iter_prefixes,
)


@pytest.fixture(scope="module")
def prefix_constants() -> list[SIPrefix]:
    """Every `SIPrefix` defined at module level, largest scale first.

    Discovered from the module rather than hand-listed, so it is independent of
    `iter_prefixes` and of the internal prefix list.
    """
    found = [obj for obj in vars(p).values() if isinstance(obj, SIPrefix)]
    return sorted(found, key=lambda prefix: prefix.scale)


@pytest.fixture
def make_prefix():
    """Factory for a prefix with an arbitrary scale (not a real SI prefix)."""

    def _make(scale: int | Fraction) -> SIPrefix:
        return SIPrefix("?", "custom", Fraction(scale))

    return _make


def _is_power_of_ten(n: int) -> bool:
    text = str(n)
    return text == "1" + "0" * (len(text) - 1)


def test_prefixes_with_the_same_fields_are_equal():
    # Arrange
    rebuilt = SIPrefix("k", "kilo", Fraction(1000))

    # Act
    equal = rebuilt == KILO

    # Assert
    assert equal


def test_prefixes_with_different_scales_are_not_equal():
    # Arrange
    other = SIPrefix("k", "kilo", Fraction(1024))

    # Act
    equal = other == KILO

    # Assert
    assert not equal


def test_equal_prefixes_collapse_in_a_set():
    # Arrange
    rebuilt = SIPrefix("k", "kilo", Fraction(1000))

    # Act
    unique = {KILO, rebuilt}

    # Assert
    assert len(unique) == 1


def test_prefix_fields_cannot_be_reassigned():
    # Arrange
    prefix = SIPrefix("k", "kilo", Fraction(1000))

    # Act
    with pytest.raises(dataclasses.FrozenInstanceError):
        prefix.symbol = "K"  # type: ignore[misc]

    # Assert
    assert prefix.symbol == "k"


def test_repr_can_be_evaluated_back_into_an_equal_prefix():
    # Arrange
    namespace = {"SIPrefix": SIPrefix, "Fraction": Fraction}

    # Act
    rebuilt = eval(repr(MICRO), namespace)

    # Assert
    assert rebuilt == MICRO


def test_prefix_constants_were_discovered(prefix_constants):
    # Arrange
    minimum_expected = 1

    # Act
    count = len(prefix_constants)

    # Assert
    assert count >= minimum_expected


@pytest.mark.parametrize(
    ("prefix", "symbol", "name", "scale"),
    [
        pytest.param(QUETTA, "Q", "quetta", Fraction(10**30), id="quetta"),
        pytest.param(MEGA, "M", "mega", Fraction(1_000_000), id="mega"),
        pytest.param(KILO, "k", "kilo", Fraction(1000), id="kilo"),
        pytest.param(NONE, "", "", Fraction(1), id="none"),
        pytest.param(MILLI, "m", "milli", Fraction(1, 1000), id="milli"),
        pytest.param(QUECTO, "q", "quecto", Fraction(1, 10**30), id="quecto"),
    ],
)
def test_well_known_prefixes_have_their_standard_values(prefix, symbol, name, scale):
    # Act
    actual = (prefix.symbol, prefix.name, prefix.scale)

    # Assert
    assert actual == (symbol, name, scale)


def test_micro_has_a_micro_or_mu_symbol_not_ascii_u():
    # Arrange
    expected = "\u00b5"  # micro sign

    # Act
    symbol = MICRO.symbol

    # Assert
    assert symbol in expected


def test_prefix_symbols_are_unique(prefix_constants):
    # Arrange
    symbols = [prefix.symbol for prefix in prefix_constants]

    # Act
    unique = set(symbols)

    # Assert
    assert len(unique) == len(symbols)


def test_prefix_names_are_unique(prefix_constants):
    # Arrange
    names = [prefix.name for prefix in prefix_constants]

    # Act
    unique = set(names)

    # Assert
    assert len(unique) == len(names)


def test_prefix_scales_are_unique(prefix_constants):
    # Arrange
    scales = [prefix.scale for prefix in prefix_constants]

    # Act
    unique = set(scales)

    # Assert
    assert len(unique) == len(scales)


def test_only_the_none_prefix_has_scale_one(prefix_constants):
    # Act
    with_unit_scale = [prefix for prefix in prefix_constants if prefix.scale == 1]

    # Assert
    assert with_unit_scale == [NONE]


def test_only_the_none_prefix_has_empty_symbol_and_name(prefix_constants):
    # Arrange
    others = [prefix for prefix in prefix_constants if prefix is not NONE]

    # Act
    blank = [prefix for prefix in others if not prefix.symbol or not prefix.name]

    # Assert
    assert (NONE.symbol, NONE.name) == ("", "")
    assert blank == []


def test_every_prefix_has_an_exact_reciprocal(prefix_constants):
    # Arrange
    scales = {prefix.scale for prefix in prefix_constants}

    # Act
    unpaired = [
        prefix.name for prefix in prefix_constants if 1 / prefix.scale not in scales
    ]

    # Assert
    assert unpaired == []


def test_iter_prefixes_by_default_yields_every_defined_prefix_once(prefix_constants):
    # Act
    yielded = list(iter_prefixes())

    # Assert
    assert len(yielded) == len(prefix_constants)
    assert set(yielded) == set(prefix_constants)


@pytest.mark.parametrize(
    ("min_prefix", "max_prefix", "expected"),
    [
        pytest.param(
            MILLI,
            KILO,
            [KILO, HECTO, DECA, NONE, DECI, CENTI, MILLI],
            id="milli-to-kilo",
        ),
        pytest.param(MICRO, MILLI, [MILLI, MICRO], id="adjacent-pair"),
        pytest.param(QUECTO, RONTO, [RONTO, QUECTO], id="smallest-pair"),
        pytest.param(KILO, KILO, [KILO], id="single-prefix"),
        pytest.param(NONE, NONE, [NONE], id="single-none"),
    ],
)
def test_iter_prefixes_includes_both_bounds(min_prefix, max_prefix, expected):
    # Act
    yielded = list(iter_prefixes(min_prefix, max_prefix))

    # Assert
    assert yielded == expected


def test_iter_prefixes_with_only_a_minimum_runs_up_to_the_largest_prefix():
    # Arrange
    minimum = KILO

    # Act
    yielded = list(iter_prefixes(min_prefix=minimum))

    # Assert
    assert QUETTA in yielded
    assert KILO in yielded
    assert all(prefix.scale >= minimum.scale for prefix in yielded)


def test_iter_prefixes_with_only_a_maximum_runs_down_to_the_smallest_prefix():
    # Arrange
    maximum = MILLI

    # Act
    yielded = list(iter_prefixes(max_prefix=maximum))

    # Assert
    assert MILLI in yielded
    assert QUECTO in yielded
    assert all(prefix.scale <= maximum.scale for prefix in yielded)


def test_iter_prefixes_with_minimum_above_maximum_yields_nothing():
    # Arrange
    min_prefix = KILO
    max_prefix = MILLI

    # Act
    yielded = list(iter_prefixes(min_prefix, max_prefix))

    # Assert
    assert yielded == []


def test_iter_prefixes_accepts_bounds_that_are_not_standard_prefixes(make_prefix):
    # Arrange
    min_prefix = make_prefix(5)  # between none and deca
    max_prefix = make_prefix(2000)  # between kilo and mega

    # Act
    yielded = list(iter_prefixes(min_prefix, max_prefix))

    # Assert
    assert yielded == [KILO, HECTO, DECA]


def test_iter_prefixes_returns_a_fresh_iteration_on_every_call():
    # Arrange
    first = list(iter_prefixes(MILLI, KILO))

    # Act
    second = list(iter_prefixes(MILLI, KILO))

    # Assert
    assert first == second
    assert len(second) > 0
