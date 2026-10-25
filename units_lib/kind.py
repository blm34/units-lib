from __future__ import annotations

from collections import defaultdict
from typing import ClassVar

from .dimensions import BaseDimension, Dimension

_registry: dict[Dimension, list[type[_Kind]]] = defaultdict(list)
_defaults: dict[Dimension, type[_Kind]] = {}


class _Kind:
    """The kind of a quantity."""

    dimension: ClassVar[Dimension]
    name: ClassVar[str]

    def __init_subclass__(
        cls,
        dim: Dimension,
        default: bool = False,
        **kw,
    ):
        """Set the `dimension` class variable, and add dimension to the registry."""
        super().__init_subclass__(**kw)

        if default and dim in _defaults:
            raise TypeError(
                f"{_defaults[dim].__name__} is already the default `Kind` "
                f"for {dim}; cannot also make {cls.__name__} the default."
            )

        cls.dimension = dim
        cls.name = cls.__name__
        _registry[dim].append(cls)

        if default:
            _defaults[dim] = cls


def kinds_for(dim: Dimension) -> tuple[type[_Kind], ...]:
    """All `Kind`s sharing the given dimension.

    Args:
        dim: The dimension that returned kinds will have

    Returns:
        All kinds that have the given dimension
    """
    return tuple(_registry.get(dim, ()))


def resolve_kind(dim: Dimension) -> type[_Kind] | None:
    """Get the default `Kind` for the given dimension.

    Args:
        dim: The dimension to get the default kind for

    Returns:
        The default kind for the given dimension
    """
    kinds = kinds_for(dim)
    if len(kinds) == 1:
        return kinds[0]

    return _defaults.get(dim)


def get_common_kind(kind_1: type[_Kind], kind_2: type[_Kind]) -> type[_Kind] | None:
    """Get the lowest possible kind that both `kind_1` and `kind_2` inherit from.

    Args:
        kind_1: The first kind in the pair
        kind_2: The second kind in the pair

    Returns:
        The lowest common ancestor or None if there isn't one
    """
    for cls in kind_2.__mro__:
        if cls == _Kind:
            return None

        if issubclass(cls, _Kind) and issubclass(kind_1, cls):
            return cls


_DIMENSIONLESS = Dimension.dimensionless()
_TIME = Dimension.base(BaseDimension.TIME)
_LENGTH = Dimension.base(BaseDimension.LENGTH)
_MASS = Dimension.base(BaseDimension.MASS)
_ELECTRIC_CURRENT = Dimension.base(BaseDimension.ELECTRIC_CURRENT)
_TEMPERATURE = Dimension.base(BaseDimension.TEMPERATURE)
_AMOUNT_OF_SUBSTANCE = Dimension.base(BaseDimension.AMOUNT_OF_SUBSTANCE)
_LUMINOUS_INTENSITY = Dimension.base(BaseDimension.LUMINOUS_INTENSITY)

# fmt: off

# Dimensionless
class Dimensionless(_Kind, dim=_DIMENSIONLESS): ...
class Angle(_Kind, dim=_DIMENSIONLESS): ...
class SolidAngle(_Kind, dim=_DIMENSIONLESS): ...

# SI Base Dimensions
class Time(_Kind, dim=_TIME): ...
class Length(_Kind, dim=_LENGTH): ...
class Mass(_Kind, dim=_MASS): ...
class ElectricCurrent(_Kind, dim=_ELECTRIC_CURRENT): ...
class Temperature(_Kind, dim=_TEMPERATURE): ...
class AmountOfSubstance(_Kind, dim=_AMOUNT_OF_SUBSTANCE): ...
class LuminousIntensity(_Kind, dim=_LUMINOUS_INTENSITY): ...

# Derived Dimensions
class Frequency(_Kind, dim=_DIMENSIONLESS/ _TIME): ...
class Radioactivity(_Kind, dim=_DIMENSIONLESS/ _TIME): ...

class Area(_Kind, dim=_LENGTH**2): ...
class Volume(_Kind, dim=_LENGTH**3): ...

class Velocity(_Kind, dim=_LENGTH / _TIME): ...
class Acceleration(_Kind, dim=Velocity.dimension / _TIME): ...
class Jerk(_Kind, dim=Acceleration.dimension / _TIME): ...
class Snap(_Kind, dim=Jerk.dimension / _TIME, default=True): ...
class Jounce(Snap, dim=Snap.dimension): ...
class Crackle(_Kind, dim=Snap.dimension / _TIME): ...
class Pop(_Kind, dim=Crackle.dimension / _TIME): ...

class Force(_Kind, dim=_MASS * Acceleration.dimension): ...
class Energy(_Kind, dim=_MASS * Velocity.dimension ** 2): ...
class Work(Energy, dim=Force.dimension * _LENGTH): ...
class Torque(_Kind, dim=Force.dimension * _LENGTH): ...
class AmountOfHeat(Energy, dim=Energy.dimension): ...
class Power(_Kind, dim=Energy.dimension / _TIME, default=True): ...
class RadiantFlux(Power, dim=Power.dimension): ...
class Intensity(_Kind, dim=Power.dimension / Area.dimension): ...
class Pressure(_Kind, dim=Force.dimension / Area.dimension): ...
class Stress(_Kind, dim=Force.dimension / Area.dimension): ...

class ElectricCharge(_Kind, dim=_TIME * _ELECTRIC_CURRENT): ...
class ElectricPotentialDifference(_Kind, dim=Power.dimension / _ELECTRIC_CURRENT): ...
class ElectricResistance(_Kind, dim=ElectricPotentialDifference.dimension / _ELECTRIC_CURRENT): ...
class ElectricConductance(_Kind, dim=_DIMENSIONLESS / ElectricResistance.dimension): ...
class Capacitance(_Kind, dim=ElectricCharge.dimension / ElectricPotentialDifference.dimension): ...

class MagneticFlux(_Kind, dim=ElectricPotentialDifference.dimension * _TIME): ...
class MagneticFluxDensity(_Kind, dim=MagneticFlux.dimension / Area.dimension): ...
class Inductance(_Kind, dim=MagneticFlux.dimension / _ELECTRIC_CURRENT): ...

class LuminousFlux(_Kind, dim=_LUMINOUS_INTENSITY): ...
class Illuminance(_Kind, dim=_LUMINOUS_INTENSITY / Area.dimension): ...

class AbsorbedDose(_Kind, dim=Energy.dimension / _MASS): ...
class Kerma(_Kind, dim=Energy.dimension / _MASS): ...
class DoseEquivalent(_Kind, dim=Energy.dimension / _MASS): ...

class CatalyticActivity(_Kind, dim=_AMOUNT_OF_SUBSTANCE / _TIME): ...

# fmt: on
