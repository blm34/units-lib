from __future__ import annotations

from fractions import Fraction

import pytest
from units_lib.dimensions.catalogue import REGISTRY, DimType
from units_lib.dimensions.dimensions import BaseDimension, Dimension

from units_lib.dimensions import catalogue

# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #



@pytest.fixture
def isolated_registry():
    """Yield the global registry, restoring its contents after the test."""
    snapshot = dict(REGISTRY)
    yield REGISTRY
    REGISTRY.clear()
    REGISTRY.update(snapshot)


# --------------------------------------------------------------------------- #
# Test data
# --------------------------------------------------------------------------- #

# (DimType subclass, exponents by base dimension)
DIMENSION_CASES = [
    # Dimensionless
    pytest.param(catalogue.Dimensionless, {}, id="Dimensionless"),
    # SI base dimensions
    pytest.param(catalogue.Time, {"time": 1}, id="Time"),
    pytest.param(catalogue.Length, {"length": 1}, id="Length"),
    pytest.param(catalogue.Mass, {"mass": 1}, id="Mass"),
    pytest.param(
        catalogue.ElectricCurrent, {"electric_current": 1}, id="ElectricCurrent"
    ),
    pytest.param(catalogue.Temperature, {"temperature": 1}, id="Temperature"),
    pytest.param(
        catalogue.AmountOfSubstance, {"amount_of_substance": 1}, id="AmountOfSubstance"
    ),
    pytest.param(
        catalogue.LuminousIntensity, {"luminous_intensity": 1}, id="LuminousIntensity"
    ),
    # Kinematics
    pytest.param(catalogue.Frequency, {"time": -1}, id="Frequency"),
    pytest.param(catalogue.Velocity, {"length": 1, "time": -1}, id="Velocity"),
    pytest.param(catalogue.Acceleration, {"length": 1, "time": -2}, id="Acceleration"),
    pytest.param(catalogue.Jerk, {"length": 1, "time": -3}, id="Jerk"),
    pytest.param(catalogue.Snap, {"length": 1, "time": -4}, id="Snap"),
    pytest.param(catalogue.Crackle, {"length": 1, "time": -5}, id="Crackle"),
    pytest.param(catalogue.Pop, {"length": 1, "time": -6}, id="Pop"),
    # Mechanics
    pytest.param(catalogue.Force, {"mass": 1, "length": 1, "time": -2}, id="Force"),
    pytest.param(catalogue.Energy, {"mass": 1, "length": 2, "time": -2}, id="Energy"),
    pytest.param(catalogue.Power, {"mass": 1, "length": 2, "time": -3}, id="Power"),
    pytest.param(catalogue.Intensity, {"mass": 1, "time": -3}, id="Intensity"),
    pytest.param(
        catalogue.Pressure, {"mass": 1, "length": -1, "time": -2}, id="Pressure"
    ),
    # Electromagnetism
    pytest.param(
        catalogue.ElectricCharge,
        {"time": 1, "electric_current": 1},
        id="ElectricCharge",
    ),
    pytest.param(
        catalogue.ElectricPotentialDifference,
        {"mass": 1, "length": 2, "time": -3, "electric_current": -1},
        id="ElectricPotentialDifference",
    ),
    pytest.param(
        catalogue.ElectricResistance,
        {"mass": 1, "length": 2, "time": -3, "electric_current": -2},
        id="ElectricResistance",
    ),
    pytest.param(
        catalogue.ElectricConductance,
        {"mass": -1, "length": -2, "time": 3, "electric_current": 2},
        id="ElectricConductance",
    ),
    pytest.param(
        catalogue.Capacitance,
        {"mass": -1, "length": -2, "time": 4, "electric_current": 2},
        id="Capacitance",
    ),
    pytest.param(
        catalogue.MagneticFlux,
        {"mass": 1, "length": 2, "time": -2, "electric_current": -1},
        id="MagneticFlux",
    ),
    pytest.param(
        catalogue.MagneticFluxDensity,
        {"mass": 1, "time": -2, "electric_current": -1},
        id="MagneticFluxDensity",
    ),
    pytest.param(
        catalogue.Inductance,
        {"mass": 1, "length": 2, "time": -2, "electric_current": -2},
        id="Inductance",
    ),
    # Photometry
    pytest.param(catalogue.LuminousFlux, {"luminous_intensity": 1}, id="LuminousFlux"),
    pytest.param(
        catalogue.Illuminance, {"luminous_intensity": 1, "length": -2}, id="Illuminance"
    ),
    # Radiation / chemistry
    pytest.param(catalogue.AbsorbedDose, {"length": 2, "time": -2}, id="AbsorbedDose"),
    pytest.param(
        catalogue.CatalyticActivity,
        {"amount_of_substance": 1, "time": -1},
        id="CatalyticActivity",
    ),
]

# (alias, canonical class it should refer to)
ALIAS_CASES = [
    pytest.param(catalogue.Angle, catalogue.Dimensionless, id="Angle"),
    pytest.param(catalogue.SolidAngle, catalogue.Dimensionless, id="SolidAngle"),
    pytest.param(catalogue.Radioactivity, catalogue.Frequency, id="Radioactivity"),
    pytest.param(catalogue.Jounce, catalogue.Snap, id="Jounce"),
    pytest.param(catalogue.Work, catalogue.Energy, id="Work"),
    pytest.param(catalogue.Torque, catalogue.Energy, id="Torque"),
    pytest.param(catalogue.AmountOfHeat, catalogue.Energy, id="AmountOfHeat"),
    pytest.param(catalogue.RadiantFlux, catalogue.Power, id="RadiantFlux"),
    pytest.param(catalogue.Stress, catalogue.Pressure, id="Stress"),
    pytest.param(catalogue.Kerma, catalogue.AbsorbedDose, id="Kerma"),
    pytest.param(catalogue.DoseEquivalent, catalogue.AbsorbedDose, id="DoseEquivalent"),
]

# Classes that share a dimension with another class, and so lose the registry
# slot to whichever was defined first.
SHADOWED_IN_REGISTRY = {catalogue.LuminousFlux}

REGISTERED_CASES = [
    case for case in DIMENSION_CASES if case.values[0] not in SHADOWED_IN_REGISTRY
]

# (description, left-hand dimension, right-hand dimension) relationships that
# should hold physically, written independently of how the classes are defined.
RELATIONSHIP_CASES = [
    pytest.param(
        lambda: catalogue.Force.dimension,
        lambda: catalogue.Mass.dimension * catalogue.Acceleration.dimension,
        id="F=ma",
    ),
    pytest.param(
        lambda: catalogue.Energy.dimension,
        lambda: catalogue.Force.dimension * catalogue.Length.dimension,
        id="E=Fd",
    ),
    pytest.param(
        lambda: catalogue.Energy.dimension,
        lambda: catalogue.Mass.dimension * catalogue.Velocity.dimension**2,
        id="E=mv^2",
    ),
    pytest.param(
        lambda: catalogue.Power.dimension,
        lambda: catalogue.Energy.dimension / catalogue.Time.dimension,
        id="P=E/t",
    ),
    pytest.param(
        lambda: catalogue.Power.dimension,
        lambda: (
            catalogue.ElectricPotentialDifference.dimension
            * catalogue.ElectricCurrent.dimension
        ),
        id="P=VI",
    ),
    pytest.param(
        lambda: catalogue.ElectricPotentialDifference.dimension,
        lambda: catalogue.Energy.dimension / catalogue.ElectricCharge.dimension,
        id="V=E/Q",
    ),
    pytest.param(
        lambda: catalogue.ElectricPotentialDifference.dimension,
        lambda: (
            catalogue.ElectricCurrent.dimension * catalogue.ElectricResistance.dimension
        ),
        id="V=IR",
    ),
    pytest.param(
        lambda: catalogue.Pressure.dimension * catalogue.Length.dimension**3,
        lambda: catalogue.Energy.dimension,
        id="P*V=E",
    ),
    pytest.param(
        lambda: catalogue.Intensity.dimension,
        lambda: catalogue.Pressure.dimension * catalogue.Velocity.dimension,
        id="I=P*v",
    ),
    pytest.param(
        lambda: (
            catalogue.Capacitance.dimension * catalogue.ElectricResistance.dimension
        ),
        lambda: catalogue.Time.dimension,
        id="RC=time",
    ),
    pytest.param(
        lambda: catalogue.Inductance.dimension / catalogue.ElectricResistance.dimension,
        lambda: catalogue.Time.dimension,
        id="L/R=time",
    ),
    pytest.param(
        lambda: (
            catalogue.ElectricResistance.dimension
            * catalogue.ElectricConductance.dimension
        ),
        lambda: catalogue.Dimensionless.dimension,
        id="R*G=1",
    ),
    pytest.param(
        lambda: catalogue.Frequency.dimension * catalogue.Time.dimension,
        lambda: catalogue.Dimensionless.dimension,
        id="f*t=1",
    ),
    pytest.param(
        lambda: catalogue.MagneticFluxDensity.dimension * catalogue.Length.dimension**2,
        lambda: catalogue.MagneticFlux.dimension,
        id="B*A=flux",
    ),
    pytest.param(
        lambda: catalogue.AbsorbedDose.dimension * catalogue.Mass.dimension,
        lambda: catalogue.Energy.dimension,
        id="dose*m=E",
    ),
]


# --------------------------------------------------------------------------- #
# Dimension values
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(("dim_type", "powers"), DIMENSION_CASES)
def test_dimension_has_expected_exponents(make_dim, dim_type, powers):
    # Arrange
    expected = make_dim(**powers)

    # Act
    actual = dim_type.dimension

    # Assert
    assert actual == expected


@pytest.mark.parametrize(("dim_type", "powers"), DIMENSION_CASES)
def test_dimension_is_a_dimension_instance(dim_type, powers):
    # Act
    actual = dim_type.dimension

    # Assert
    assert isinstance(actual, Dimension)


@pytest.mark.parametrize(("dim_type", "powers"), DIMENSION_CASES)
def test_dimension_exponents_are_fractions(dim_type, powers):
    # Arrange
    expected_length = len(BaseDimension)

    # Act
    exps = dim_type.dimension.exps

    # Assert
    assert len(exps) == expected_length
    assert all(isinstance(exp, Fraction) for exp in exps)


@pytest.mark.parametrize(("dim_type", "powers"), DIMENSION_CASES)
def test_dimension_type_is_a_dimtype_subclass(dim_type, powers):
    # Act
    result = issubclass(dim_type, DimType)

    # Assert
    assert result


# --------------------------------------------------------------------------- #
# Aliases
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(("alias", "canonical"), ALIAS_CASES)
def test_alias_is_the_same_class_as_canonical(alias, canonical):
    # Arrange
    # (alias and canonical class supplied by parametrisation)

    # Act
    result = alias is canonical

    # Assert
    assert result


@pytest.mark.parametrize(("alias", "canonical"), ALIAS_CASES)
def test_alias_has_same_dimension_as_canonical(alias, canonical):
    # Arrange
    expected = canonical.dimension

    # Act
    actual = alias.dimension

    # Assert
    assert actual == expected


# --------------------------------------------------------------------------- #
# Physical relationships between dimensions
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(("lhs", "rhs"), RELATIONSHIP_CASES)
def test_dimensions_satisfy_physical_relationship(lhs, rhs):
    # Act
    left = lhs()
    right = rhs()

    # Assert
    assert left == right


def test_luminous_flux_shares_dimension_with_luminous_intensity():
    # Arrange
    # (steradian is dimensionless, so lumen and candela share a dimension)
    intensity_dim = catalogue.LuminousIntensity.dimension

    # Act
    flux_dim = catalogue.LuminousFlux.dimension

    # Assert
    assert flux_dim == intensity_dim


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(("dim_type", "powers"), REGISTERED_CASES)
def test_standard_dimension_is_registered_under_its_dimension(dim_type, powers):
    # Arrange
    key = dim_type.dimension

    # Act
    registered = REGISTRY.get(key)

    # Assert
    assert registered is dim_type


def test_registry_keys_match_their_class_dimension():
    # Arrange
    items = list(REGISTRY.items())

    # Act
    mismatches = [(k, v) for k, v in items if v.dimension != k]

    # Assert
    assert mismatches == []


def test_first_defined_class_wins_when_dimensions_collide():
    # Arrange
    key = catalogue.LuminousFlux.dimension

    # Act
    registered = REGISTRY[key]

    # Assert
    assert registered is catalogue.LuminousIntensity
    assert registered is not catalogue.LuminousFlux


@pytest.mark.parametrize(("alias", "canonical"), ALIAS_CASES)
def test_alias_dimension_resolves_to_canonical_class_in_registry(alias, canonical):
    # Arrange
    key = alias.dimension

    # Act
    registered = REGISTRY[key]

    # Assert
    assert registered is canonical


# --------------------------------------------------------------------------- #
# DimType.__init_subclass__
# --------------------------------------------------------------------------- #


def test_subclass_gets_dimension_class_variable(isolated_registry, make_dim):
    # Arrange
    dim = make_dim(length=3)

    # Act
    class Volume(DimType, dim=dim): ...

    # Assert
    assert Volume.dimension == dim


def test_subclass_is_added_to_registry(isolated_registry, make_dim):
    # Arrange
    dim = make_dim(length=3)
    assert dim not in isolated_registry

    # Act
    class Volume(DimType, dim=dim): ...

    # Assert
    assert isolated_registry[dim] is Volume


def test_subclass_does_not_overwrite_existing_registry_entry(isolated_registry):
    # Arrange
    dim = catalogue.Length.dimension

    # Act
    class AnotherLength(DimType, dim=dim): ...

    # Assert
    assert AnotherLength.dimension == dim
    assert isolated_registry[dim] is catalogue.Length


def test_subclass_without_dim_raises_type_error(isolated_registry):
    # Arrange
    registry_before = dict(isolated_registry)

    # Act
    with pytest.raises(TypeError):

        class Bad(DimType): ...

    # Assert
    assert isolated_registry == registry_before


def test_subclasses_do_not_share_dimension_attribute(isolated_registry, make_dim):
    # Arrange
    dim_a = make_dim(length=3)
    dim_b = make_dim(mass=3)

    # Act
    class A(DimType, dim=dim_a): ...

    class B(DimType, dim=dim_b): ...

    # Assert
    assert A.dimension == dim_a
    assert B.dimension == dim_b
    assert A.dimension != B.dimension
