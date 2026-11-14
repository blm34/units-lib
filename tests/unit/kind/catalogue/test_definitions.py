import pytest

from units_lib.dimensions import Dimension
from units_lib.kind.catalogue import catalogue as kind_catalogue
from units_lib.kind.operations import resolve_kind

# Building blocks for the physics expressions below.
DIMENSIONLESS = Dimension.dimensionless()
TIME = kind_catalogue.Time.dimension
LENGTH = kind_catalogue.Length.dimension
MASS = kind_catalogue.Mass.dimension
CURRENT = kind_catalogue.ElectricCurrent.dimension
AMOUNT = kind_catalogue.AmountOfSubstance.dimension
LUMINOUS = kind_catalogue.LuminousIntensity.dimension


PHYSICS_LAW_CASES = [
    # Geometry and kinematics
    pytest.param(
        kind_catalogue.Area.dimension,
        LENGTH * LENGTH,
        id="A = L*L",
    ),
    pytest.param(
        kind_catalogue.Volume.dimension,
        kind_catalogue.Area.dimension * LENGTH,
        id="V = A*L",
    ),
    pytest.param(
        kind_catalogue.Velocity.dimension,
        LENGTH / TIME,
        id="v = d/t",
    ),
    pytest.param(
        kind_catalogue.Acceleration.dimension,
        kind_catalogue.Velocity.dimension / TIME,
        id="a = v/t",
    ),
    pytest.param(
        kind_catalogue.Acceleration.dimension,
        LENGTH / TIME**2,
        id="a = d/t^2",
    ),
    pytest.param(
        kind_catalogue.Jerk.dimension,
        kind_catalogue.Acceleration.dimension / TIME,
        id="j = a/t",
    ),
    pytest.param(
        kind_catalogue.Jounce.dimension,
        kind_catalogue.Jerk.dimension / TIME,
        id="Jounce: s = j/t",
    ),
    pytest.param(
        kind_catalogue.Snap.dimension,
        kind_catalogue.Jerk.dimension / TIME,
        id="Snap: s = j/t",
    ),
    pytest.param(
        kind_catalogue.Crackle.dimension,
        kind_catalogue.Snap.dimension / TIME,
        id="c = s/t",
    ),
    pytest.param(
        kind_catalogue.Pop.dimension,
        kind_catalogue.Crackle.dimension / TIME,
        id="p = c/t",
    ),
    # Angles are ratios of lengths, solid angles ratios of are,as
    pytest.param(
        kind_catalogue.Angle.dimension,
        LENGTH / LENGTH,
        id="angle = arc/radius",
    ),
    pytest.param(
        kind_catalogue.SolidAngle.dimension,
        kind_catalogue.Area.dimension / LENGTH**2,
        id="sr = A/r^2",
    ),
    pytest.param(
        kind_catalogue.Dimensionless.dimension,
        LENGTH / LENGTH,
        id="ratio of lengths",
    ),
    # Mechanics
    pytest.param(
        kind_catalogue.Force.dimension,
        kind_catalogue.Mass.dimension * kind_catalogue.Acceleration.dimension,
        id="F = ma",
    ),
    pytest.param(
        kind_catalogue.Work.dimension,
        kind_catalogue.Force.dimension * LENGTH,
        id="E = F*d",
    ),
    pytest.param(
        kind_catalogue.Energy.dimension,
        MASS * kind_catalogue.Velocity.dimension**2,
        id="E = m*v^2",
    ),
    pytest.param(
        kind_catalogue.Energy.dimension,
        kind_catalogue.Pressure.dimension * kind_catalogue.Volume.dimension,
        id="E = P*V",
    ),
    pytest.param(
        kind_catalogue.Power.dimension,
        kind_catalogue.Energy.dimension / TIME,
        id="P = E/t",
    ),
    pytest.param(
        kind_catalogue.Power.dimension,
        kind_catalogue.Force.dimension * kind_catalogue.Velocity.dimension,
        id="P = F*v",
    ),
    pytest.param(
        kind_catalogue.Pressure.dimension,
        kind_catalogue.Force.dimension / kind_catalogue.Area.dimension,
        id="Pressure: P = F/A",
    ),
    pytest.param(
        kind_catalogue.Stress.dimension,
        kind_catalogue.Force.dimension / kind_catalogue.Area.dimension,
        id="Stress: P = F/A",
    ),
    pytest.param(
        kind_catalogue.Intensity.dimension,
        kind_catalogue.Power.dimension / kind_catalogue.Area.dimension,
        id="I = P/A",
    ),
    pytest.param(
        kind_catalogue.Intensity.dimension,
        kind_catalogue.Pressure.dimension * kind_catalogue.Velocity.dimension,
        id="I = P*v",
    ),
    # Frequency
    pytest.param(
        DIMENSIONLESS,
        kind_catalogue.Frequency.dimension * TIME,
        id="Frequency: f*t = 1",
    ),
    pytest.param(
        DIMENSIONLESS,
        kind_catalogue.Radioactivity.dimension * TIME,
        id="Radioactivity: f*t = 1",
    ),
    # Electricity
    pytest.param(
        kind_catalogue.ElectricCharge.dimension,
        CURRENT * TIME,
        id="Q = I*t",
    ),
    pytest.param(
        kind_catalogue.ElectricPotentialDifference.dimension,
        kind_catalogue.Energy.dimension / kind_catalogue.ElectricCharge.dimension,
        id="V = E/Q",
    ),
    pytest.param(
        kind_catalogue.ElectricPotentialDifference.dimension,
        kind_catalogue.ElectricResistance.dimension * CURRENT,
        id="V = I*R",
    ),
    pytest.param(
        kind_catalogue.Power.dimension,
        kind_catalogue.ElectricPotentialDifference.dimension * CURRENT,
        id="P = V*I",
    ),
    pytest.param(
        kind_catalogue.Power.dimension,
        CURRENT**2 * kind_catalogue.ElectricResistance.dimension,
        id="P = I^2*R",
    ),
    pytest.param(
        DIMENSIONLESS,
        kind_catalogue.ElectricResistance.dimension
        * kind_catalogue.ElectricConductance.dimension,
        id="R*G = 1",
    ),
    pytest.param(
        kind_catalogue.Capacitance.dimension,
        kind_catalogue.ElectricCharge.dimension
        / kind_catalogue.ElectricPotentialDifference.dimension,
        id="C = Q/V",
    ),
    pytest.param(
        kind_catalogue.Capacitance.dimension
        * kind_catalogue.ElectricResistance.dimension,
        TIME,
        id="RC time constant",
    ),
    pytest.param(
        kind_catalogue.Inductance.dimension
        / kind_catalogue.ElectricResistance.dimension,
        TIME,
        id="L/R time constant",
    ),
    pytest.param(
        kind_catalogue.Energy.dimension,
        kind_catalogue.Capacitance.dimension
        * kind_catalogue.ElectricPotentialDifference.dimension**2,
        id="E = C*V^2",
    ),
    pytest.param(
        kind_catalogue.Energy.dimension,
        kind_catalogue.Inductance.dimension * CURRENT**2,
        id="E = L*I^2",
    ),
    # Magnetism
    pytest.param(
        kind_catalogue.MagneticFlux.dimension,
        kind_catalogue.ElectricPotentialDifference.dimension * TIME,
        id="flux = V*t",
    ),
    pytest.param(
        kind_catalogue.MagneticFlux.dimension,
        kind_catalogue.Inductance.dimension * CURRENT,
        id="flux = L*I",
    ),
    pytest.param(
        kind_catalogue.MagneticFlux.dimension,
        kind_catalogue.MagneticFluxDensity.dimension * kind_catalogue.Area.dimension,
        id="flux = B*A",
    ),
    # Photometry
    pytest.param(
        kind_catalogue.Illuminance.dimension * kind_catalogue.Area.dimension,
        kind_catalogue.LuminousFlux.dimension,
        id="E_v*A = luminous flux",
    ),
    pytest.param(
        kind_catalogue.LuminousFlux.dimension,
        LUMINOUS * kind_catalogue.SolidAngle.dimension,
        id="flux = I_v*sr",
    ),
    # Radiation and chemistry
    pytest.param(
        kind_catalogue.Kerma.dimension,
        kind_catalogue.Energy.dimension / MASS,
        id="Kerma: D = E/m",
    ),
    pytest.param(
        kind_catalogue.DoseEquivalent.dimension,
        kind_catalogue.Energy.dimension / MASS,
        id="Dose Equivalent: D = E/m",
    ),
    pytest.param(
        kind_catalogue.AbsorbedDose.dimension,
        kind_catalogue.Energy.dimension / MASS,
        id="Absorbed Dose: D = E/m",
    ),
    pytest.param(
        kind_catalogue.CatalyticActivity.dimension * TIME,
        AMOUNT,
        id="catalytic activity * t = n",
    ),
]


@pytest.mark.parametrize(("lhs", "rhs"), PHYSICS_LAW_CASES)
def test_kind_dimensions_satisfy_physical_law(lhs, rhs):
    # Act
    equal = lhs == rhs

    # Assert
    assert equal


UNAMBIGUOUS_RESULT_CASES = [
    pytest.param(
        LENGTH * LENGTH,
        kind_catalogue.Area,
        id="Area",
    ),
    pytest.param(
        kind_catalogue.Area.dimension * LENGTH,
        kind_catalogue.Volume,
        id="Volume",
    ),
    pytest.param(
        LENGTH / TIME,
        kind_catalogue.Velocity,
        id="Velocity",
    ),
    pytest.param(
        kind_catalogue.Velocity.dimension / TIME,
        kind_catalogue.Acceleration,
        id="Acceleration",
    ),
    pytest.param(
        MASS * kind_catalogue.Acceleration.dimension,
        kind_catalogue.Force,
        id="Force",
    ),
    pytest.param(
        kind_catalogue.Power.dimension / kind_catalogue.Area.dimension,
        kind_catalogue.Intensity,
        id="Intensity",
    ),
    pytest.param(
        CURRENT * TIME,
        kind_catalogue.ElectricCharge,
        id="ElectricCharge",
    ),
    pytest.param(
        kind_catalogue.Power.dimension / CURRENT,
        kind_catalogue.ElectricPotentialDifference,
        id="ElectricPotentialDifference",
    ),
    pytest.param(
        kind_catalogue.ElectricPotentialDifference.dimension / CURRENT,
        kind_catalogue.ElectricResistance,
        id="ElectricResistance",
    ),
    pytest.param(
        DIMENSIONLESS / kind_catalogue.ElectricResistance.dimension,
        kind_catalogue.ElectricConductance,
        id="ElectricConductance",
    ),
    pytest.param(
        kind_catalogue.ElectricCharge.dimension
        / kind_catalogue.ElectricPotentialDifference.dimension,
        kind_catalogue.Capacitance,
        id="Capacitance",
    ),
    pytest.param(
        kind_catalogue.ElectricPotentialDifference.dimension * TIME,
        kind_catalogue.MagneticFlux,
        id="MagneticFlux",
    ),
    pytest.param(
        kind_catalogue.MagneticFlux.dimension / kind_catalogue.Area.dimension,
        kind_catalogue.MagneticFluxDensity,
        id="MagneticFluxDensity",
    ),
    pytest.param(
        kind_catalogue.MagneticFlux.dimension / CURRENT,
        kind_catalogue.Inductance,
        id="Inductance",
    ),
    pytest.param(
        LUMINOUS / kind_catalogue.Area.dimension,
        kind_catalogue.Illuminance,
        id="Illuminance",
    ),
    pytest.param(
        AMOUNT / TIME,
        kind_catalogue.CatalyticActivity,
        id="CatalyticActivity",
    ),
]


@pytest.mark.parametrize(("dim", "expected"), UNAMBIGUOUS_RESULT_CASES)
def test_dimension_from_physics_expression_resolves_to_expected_kind(dim, expected):
    # Act
    resolved = resolve_kind(dim)

    # Assert
    assert resolved is expected
