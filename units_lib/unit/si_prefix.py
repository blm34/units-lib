from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from units_lib.scale import Scale


@dataclass(frozen=True, slots=True)
class SIPrefix:
    symbol: str
    name: str
    scale: Scale


QUETTA = SIPrefix("Q", "quetta", Scale.from_number(10) ** 30)
RONNA = SIPrefix("R", "ronna", Scale.from_number(10) ** 27)
YOTTA = SIPrefix("Y", "yotta", Scale.from_number(10) ** 24)
ZETTA = SIPrefix("Z", "zetta", Scale.from_number(10) ** 21)
EXA = SIPrefix("E", "exa", Scale.from_number(10) ** 18)
PETA = SIPrefix("P", "peta", Scale.from_number(10) ** 15)
TERA = SIPrefix("T", "tera", Scale.from_number(10) ** 12)
GIGA = SIPrefix("G", "giga", Scale.from_number(10) ** 9)
MEGA = SIPrefix("M", "mega", Scale.from_number(10) ** 6)
KILO = SIPrefix("k", "kilo", Scale.from_number(10) ** 3)
HECTO = SIPrefix("h", "hecto", Scale.from_number(10) ** 2)
DECA = SIPrefix("da", "deca", Scale.from_number(10) ** 1)
NONE = SIPrefix("", "", Scale.from_number(10) ** 0)
DECI = SIPrefix("d", "deci", Scale.from_number(10) ** -1)
CENTI = SIPrefix("c", "centi", Scale.from_number(10) ** -2)
MILLI = SIPrefix("m", "milli", Scale.from_number(10) ** -3)
MICRO = SIPrefix("µ", "micro", Scale.from_number(10) ** -6)
NANO = SIPrefix("n", "nano", Scale.from_number(10) ** -9)
PICO = SIPrefix("p", "pico", Scale.from_number(10) ** -12)
FEMTO = SIPrefix("f", "femto", Scale.from_number(10) ** -15)
ATTO = SIPrefix("a", "atto", Scale.from_number(10) ** -18)
ZEPTO = SIPrefix("z", "zepto", Scale.from_number(10) ** -21)
YOCTO = SIPrefix("y", "yocto", Scale.from_number(10) ** -24)
RONTO = SIPrefix("r", "ronto", Scale.from_number(10) ** -27)
QUECTO = SIPrefix("q", "quecto", Scale.from_number(10) ** -30)

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
