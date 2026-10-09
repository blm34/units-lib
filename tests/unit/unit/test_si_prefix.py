from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError, dataclass
from fractions import Fraction

import pytest

from units_lib.scale import Scale
from units_lib.unit import si_prefix


@pytest.fixture(autouse=True)
def fresh_si_prefix():
    return importlib.reload(si_prefix)


@pytest.fixture
def prefix_constants(fresh_si_prefix) -> list[si_prefix.SIPrefix]:
    """Every `SIPrefix` defined at module level, smallest scale first.

    Discovered from the module rather than hand-listed, so it is independent of
    `iter_prefixes` and of the internal prefix list.
    """
    found = [
        obj
        for obj in vars(fresh_si_prefix).values()
        if isinstance(obj, fresh_si_prefix.SIPrefix)
    ]
    return sorted(found, key=lambda prefix: prefix.scale)


@pytest.fixture
def make_prefix(fresh_si_prefix):
    """Factory for a prefix with an arbitrary scale (not a real SI prefix)."""

    @dataclass
    class FakeSIPrefix:
        scale: Scale
        name: str = "custom"
        symbol: str = "?"

    def _make(scale: int | Fraction):
        return FakeSIPrefix(scale=Scale.from_number(scale))

    return _make


def _is_power_of_ten(n: int) -> bool:
    text = str(n)
    return text == "1" + "0" * (len(text) - 1)


def test_prefixes_with_the_same_fields_are_equal(fresh_si_prefix):
    # Arrange
    rebuilt = fresh_si_prefix.SIPrefix("k", "kilo", Scale.from_number(1000))

    # Act
    equal = rebuilt == fresh_si_prefix.KILO

    # Assert
    assert equal


def test_prefixes_with_different_scales_are_not_equal(fresh_si_prefix):
    # Arrange
    other = fresh_si_prefix.SIPrefix("k", "kilo", Scale.from_number(1024))

    # Act
    equal = other == fresh_si_prefix.KILO

    # Assert
    assert not equal


def test_equal_prefixes_collapse_in_a_set(fresh_si_prefix):
    # Arrange
    rebuilt = fresh_si_prefix.SIPrefix("k", "kilo", Scale.from_number(1000))

    # Act
    unique = {fresh_si_prefix.KILO, rebuilt}

    # Assert
    assert len(unique) == 1


def test_prefix_fields_cannot_be_reassigned(fresh_si_prefix):
    # Arrange
    prefix = fresh_si_prefix.SIPrefix("k", "kilo", Scale.from_number(1000))

    # Act
    with pytest.raises(FrozenInstanceError):
        prefix.symbol = "K"  # type: ignore[misc]

    # Assert
    assert prefix.symbol == "k"


def test_repr_can_be_evaluated_back_into_an_equal_prefix(fresh_si_prefix):
    # Arrange
    namespace = {
        "SIPrefix": fresh_si_prefix.SIPrefix,
        "Scale": Scale,
        "Fraction": Fraction,
    }

    # Act
    rebuilt = eval(repr(fresh_si_prefix.MICRO), namespace)

    # Assert
    assert rebuilt == fresh_si_prefix.MICRO


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
        pytest.param(
            si_prefix.QUETTA, "Q", "quetta", Scale.from_number(10**30), id="quetta"
        ),
        pytest.param(
            si_prefix.MEGA, "M", "mega", Scale.from_number(1_000_000), id="mega"
        ),
        pytest.param(si_prefix.KILO, "k", "kilo", Scale.from_number(1000), id="kilo"),
        pytest.param(si_prefix.NONE, "", "", Scale.from_number(1), id="none"),
        pytest.param(
            si_prefix.MILLI,
            "m",
            "milli",
            Scale.from_number(Fraction(1, 1000)),
            id="milli",
        ),
        pytest.param(
            si_prefix.QUECTO,
            "q",
            "quecto",
            Scale.from_number(Fraction(1, 10**30)),
            id="quecto",
        ),
    ],
)
def test_well_known_prefixes_have_their_standard_values(prefix, symbol, name, scale):
    # Act
    actual = (prefix.symbol, prefix.name, prefix.scale)

    # Assert
    assert actual == (symbol, name, scale)


def test_micro_has_a_micro_or_mu_symbol_not_ascii_u(fresh_si_prefix):
    # Arrange
    expected = "\u00b5"  # micro sign

    # Act
    symbol = fresh_si_prefix.MICRO.symbol

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


def test_only_the_none_prefix_has_scale_one(prefix_constants, fresh_si_prefix):
    # Act
    with_unit_scale = [
        prefix for prefix in prefix_constants if prefix.scale.to_fraction() == 1
    ]

    # Assert
    assert with_unit_scale == [fresh_si_prefix.NONE]


def test_only_the_none_prefix_has_empty_symbol_and_name(
    prefix_constants, fresh_si_prefix
):
    # Arrange
    others = [
        prefix for prefix in prefix_constants if prefix is not fresh_si_prefix.NONE
    ]

    # Act
    blank = [prefix for prefix in others if not prefix.symbol or not prefix.name]

    # Assert
    assert (fresh_si_prefix.NONE.symbol, fresh_si_prefix.NONE.name) == ("", "")
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


def test_iter_prefixes_by_default_yields_every_defined_prefix_once(
    prefix_constants, fresh_si_prefix
):
    # Act
    yielded = list(fresh_si_prefix.iter_prefixes())

    # Assert
    assert len(yielded) == len(prefix_constants)
    assert set(yielded) == set(prefix_constants)


@pytest.mark.parametrize(
    ("min_prefix", "max_prefix", "expected"),
    [
        pytest.param(
            si_prefix.MILLI,
            si_prefix.KILO,
            [
                si_prefix.MILLI,
                si_prefix.CENTI,
                si_prefix.DECI,
                si_prefix.NONE,
                si_prefix.DECA,
                si_prefix.HECTO,
                si_prefix.KILO,
            ],
            id="milli-to-kilo",
        ),
        pytest.param(
            si_prefix.MICRO,
            si_prefix.MILLI,
            [si_prefix.MICRO, si_prefix.MILLI],
            id="adjacent-pair",
        ),
        pytest.param(
            si_prefix.QUECTO,
            si_prefix.RONTO,
            [si_prefix.QUECTO, si_prefix.RONTO],
            id="smallest-pair",
        ),
        pytest.param(
            si_prefix.KILO, si_prefix.KILO, [si_prefix.KILO], id="single-prefix"
        ),
        pytest.param(
            si_prefix.NONE, si_prefix.NONE, [si_prefix.NONE], id="single-none"
        ),
    ],
)
def test_iter_prefixes_includes_both_bounds(
    fresh_si_prefix, min_prefix, max_prefix, expected
):
    # Act
    yielded = list(fresh_si_prefix.iter_prefixes(min_prefix, max_prefix))

    # Assert
    for res, exp in zip(yielded, expected, strict=True):
        assert res.name == exp.name
        assert res.symbol == exp.symbol
        assert res.scale == exp.scale


def test_iter_prefixes_with_only_a_minimum_runs_up_to_the_largest_prefix(
    fresh_si_prefix,
):
    # Arrange
    minimum = fresh_si_prefix.KILO

    # Act
    yielded = list(fresh_si_prefix.iter_prefixes(min_prefix=minimum))

    # Assert
    assert fresh_si_prefix.QUETTA in yielded
    assert fresh_si_prefix.KILO in yielded
    assert all(prefix.scale >= minimum.scale for prefix in yielded)


def test_iter_prefixes_with_only_a_maximum_runs_down_to_the_smallest_prefix(
    fresh_si_prefix,
):
    # Arrange
    maximum = fresh_si_prefix.MILLI

    # Act
    yielded = list(fresh_si_prefix.iter_prefixes(max_prefix=maximum))

    # Assert
    assert fresh_si_prefix.MILLI in yielded
    assert fresh_si_prefix.QUECTO in yielded
    assert all(prefix.scale <= maximum.scale for prefix in yielded)


def test_iter_prefixes_with_minimum_above_maximum_yields_nothing(fresh_si_prefix):
    # Arrange
    min_prefix = fresh_si_prefix.KILO
    max_prefix = fresh_si_prefix.MILLI

    # Act
    yielded = list(fresh_si_prefix.iter_prefixes(min_prefix, max_prefix))

    # Assert
    assert yielded == []


def test_iter_prefixes_accepts_bounds_that_are_not_standard_prefixes(
    make_prefix, fresh_si_prefix
):
    # Arrange
    min_prefix = make_prefix(5)  # between none and deca
    max_prefix = make_prefix(2000)  # between kilo and mega

    expected_names = ["deca", "hecto", "kilo"]

    # Act
    yielded = list(fresh_si_prefix.iter_prefixes(min_prefix, max_prefix))

    # Assert
    assert all(
        result.name == expected
        for result, expected in zip(yielded, expected_names, strict=True)
    )


def test_iter_prefixes_returns_a_fresh_iteration_on_every_call(fresh_si_prefix):
    # Arrange
    first = list(
        fresh_si_prefix.iter_prefixes(fresh_si_prefix.MILLI, fresh_si_prefix.KILO)
    )

    # Act
    second = list(
        fresh_si_prefix.iter_prefixes(fresh_si_prefix.MILLI, fresh_si_prefix.KILO)
    )

    # Assert
    assert first == second
    assert len(second) > 0
