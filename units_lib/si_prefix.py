from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class SIPrefix:
    symbol: str
    name: str
    scale: Fraction

    def __repr__(self):
        return f"SIPrefix(symbol={self.symbol!r}, name={self.name!r}, scale={self.scale!r})"


QUETTA = SIPrefix("Q", "quetta", Fraction(10) ** 30)
RONNA = SIPrefix("R", "ronna", Fraction(10) ** 27)
YOTTA = SIPrefix("Y", "yotta", Fraction(10) ** 24)
ZETTA = SIPrefix("Z", "zetta", Fraction(10) ** 21)
EXA = SIPrefix("E", "exa", Fraction(10) ** 18)
PETA = SIPrefix("P", "peta", Fraction(10) ** 15)
TERA = SIPrefix("T", "tera", Fraction(10) ** 12)
GIGA = SIPrefix("G", "giga", Fraction(10) ** 9)
MEGA = SIPrefix("M", "mega", Fraction(10) ** 6)
KILO = SIPrefix("k", "kilo", Fraction(10) ** 3)
HECTO = SIPrefix("h", "hecto", Fraction(10) ** 2)
DECA = SIPrefix("da", "deca", Fraction(10) ** 1)
NONE = SIPrefix("", "", Fraction(10) ** 0)
DECI = SIPrefix("d", "deci", Fraction(10) ** -1)
CENTI = SIPrefix("c", "centi", Fraction(10) ** -2)
MILLI = SIPrefix("m", "milli", Fraction(10) ** -3)
MICRO = SIPrefix("µ", "micro", Fraction(10) ** -6)
NANO = SIPrefix("n", "nano", Fraction(10) ** -9)
PICO = SIPrefix("p", "pico", Fraction(10) ** -12)
FEMTO = SIPrefix("f", "femto", Fraction(10) ** -15)
ATTO = SIPrefix("a", "atto", Fraction(10) ** -18)
ZEPTO = SIPrefix("z", "zepto", Fraction(10) ** -21)
YOCTO = SIPrefix("y", "yocto", Fraction(10) ** -24)
RONTO = SIPrefix("r", "ronto", Fraction(10) ** -27)
QUECTO = SIPrefix("q", "quecto", Fraction(10) ** -30)

_prefixes = [
    QUETTA,
    RONNA,
    YOTTA,
    ZETTA,
    EXA,
    PETA,
    TERA,
    GIGA,
    MEGA,
    KILO,
    HECTO,
    DECA,
    NONE,
    DECI,
    CENTI,
    MILLI,
    MICRO,
    NANO,
    PICO,
    FEMTO,
    ATTO,
    ZEPTO,
    YOCTO,
    RONTO,
    QUECTO,
]


def iter_prefixes(
    min_prefix: SIPrefix = QUECTO,
    max_prefix: SIPrefix = QUETTA,
) -> Generator[SIPrefix, None, None]:
    for prefix in _prefixes:
        if min_prefix.scale <= prefix.scale <= max_prefix.scale:
            yield prefix
