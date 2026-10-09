from __future__ import annotations

from enum import IntEnum


class SIPrefix(IntEnum):
    QUETTA = 30
    RONNA = 27
    YOTTA = 24
    ZETTA = 21
    EXA = 18
    PETA = 15
    TERA = 12
    GIGA = 9
    MEGA = 6
    KILO = 3
    HECTO = 2
    DECA = 1
    NONE = 0
    DECI = -1
    CENTI = -2
    MILLI = -3
    MICRO = -6
    NANO = -9
    PICO = -12
    FEMTO = -15
    ATTO = -18
    ZEPTO = -21
    YOCTO = -24
    RONTO = -27
    QUECTO = -30

    @property
    def symbol(self) -> str:
        """Get the letter used to represent the prefix."""
        return _ENUM_TO_SYMBOL[self]

    @classmethod
    def from_symbol(cls, symbol: str) -> SIPrefix:
        symbol = symbol.strip()

        # Normalise the greek letter mu character to the micro symbol
        symbol = symbol.replace("μ", "µ")

        try:
            return _SYMBOL_TO_ENUM[symbol]
        except KeyError as err:
            raise ValueError(f"Unknown SI Prefix: {symbol!r}") from err


_ENUM_TO_SYMBOL = {
    SIPrefix.QUETTA: "Q",
    SIPrefix.RONNA: "R",
    SIPrefix.YOTTA: "Y",
    SIPrefix.ZETTA: "Z",
    SIPrefix.EXA: "E",
    SIPrefix.PETA: "P",
    SIPrefix.TERA: "T",
    SIPrefix.GIGA: "G",
    SIPrefix.MEGA: "M",
    SIPrefix.KILO: "k",
    SIPrefix.HECTO: "h",
    SIPrefix.DECA: "da",
    SIPrefix.NONE: "",
    SIPrefix.DECI: "d",
    SIPrefix.CENTI: "c",
    SIPrefix.MILLI: "m",
    SIPrefix.MICRO: "µ",
    SIPrefix.NANO: "n",
    SIPrefix.PICO: "p",
    SIPrefix.FEMTO: "f",
    SIPrefix.ATTO: "a",
    SIPrefix.ZEPTO: "z",
    SIPrefix.YOCTO: "y",
    SIPrefix.RONTO: "r",
    SIPrefix.QUECTO: "q",
}


_SYMBOL_TO_ENUM = {
    "Q": SIPrefix.QUETTA,
    "R": SIPrefix.RONNA,
    "Y": SIPrefix.YOTTA,
    "Z": SIPrefix.ZETTA,
    "E": SIPrefix.EXA,
    "P": SIPrefix.PETA,
    "T": SIPrefix.TERA,
    "G": SIPrefix.GIGA,
    "M": SIPrefix.MEGA,
    "k": SIPrefix.KILO,
    "h": SIPrefix.HECTO,
    "da": SIPrefix.DECA,
    "d": SIPrefix.DECI,
    "c": SIPrefix.CENTI,
    "m": SIPrefix.MILLI,
    "µ": SIPrefix.MICRO,
    "n": SIPrefix.NANO,
    "p": SIPrefix.PICO,
    "f": SIPrefix.FEMTO,
    "a": SIPrefix.ATTO,
    "z": SIPrefix.ZEPTO,
    "y": SIPrefix.YOCTO,
    "r": SIPrefix.RONTO,
    "q": SIPrefix.QUECTO,
}
