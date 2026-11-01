from fractions import Fraction

from units_lib.scale import Scale, constants


def test_one():
    # ARRANGE
    expected = Scale(frozenset())

    # ACT
    assert constants.one == expected


def test_pi():
    # ARRANGE
    expected = Scale(frozenset((("pi", Fraction(1)),)))

    # ACT
    assert constants.pi == expected
