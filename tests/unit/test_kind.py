from __future__ import annotations

import itertools
from types import SimpleNamespace

import pytest

from units_lib import kind as k
from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind import _Kind, get_common_kind, kinds_for, resolve_kind


def _discover_standard_kinds() -> tuple[type[_Kind], ...]:
    """Every kind defined at module level in `units_lib.kind`."""
    return tuple(
        obj
        for obj in vars(k).values()
        if isinstance(obj, type) and issubclass(obj, _Kind) and obj is not _Kind
    )


@pytest.fixture(scope="session")
def standard_kinds() -> tuple[type[_Kind], ...]:
    """All standard kinds."""
    return _discover_standard_kinds()


@pytest.fixture(scope="session")
def standard_kind_pairs(standard_kinds) -> tuple[tuple[type[_Kind], type[_Kind]], ...]:
    return tuple(itertools.product(standard_kinds, repeat=2))


@pytest.fixture(params=_discover_standard_kinds())
def standard_kind(request) -> type[_Kind]:
    return request.param


@pytest.fixture
def fresh_dim():
    """A dimension that no standard kind uses."""
    dim = (
        Dimension.base(BaseDimension.LENGTH) ** 5
        * Dimension.base(BaseDimension.TIME) ** -7
    )

    assert kinds_for(dim) == ()
    return dim


@pytest.fixture
def other_dim():
    """A second dimension that no standard kind uses, distinct from `fresh_dim`."""
    dim = (
        Dimension.base(BaseDimension.MASS) ** 5
        * Dimension.base(BaseDimension.TIME) ** -3
    )

    assert kinds_for(dim) == ()
    return dim


@pytest.fixture
def isolated_registry():
    """Restore the registry and the defaults after the test."""
    registry_snapshot = {dim: list(kinds) for dim, kinds in k._registry.items()}
    defaults_snapshot = dict(k._defaults)

    yield

    k._registry.clear()
    k._registry.update(registry_snapshot)
    k._defaults.clear()
    k._defaults.update(defaults_snapshot)


@pytest.fixture
def kind_tree(isolated_registry, fresh_dim, other_dim):
    """A small kind hierarchy, plus a kind unrelated to it.

    Base
    ├── MidA
    │   ├── LeafA
    │   └── LeafA2
    └── MidB
        └── LeafB

    Unrelated  (different dimension, no shared ancestor)
    """

    class Base(_Kind, dim=fresh_dim): ...

    class MidA(Base, dim=fresh_dim): ...

    class MidB(Base, dim=fresh_dim): ...

    class LeafA(MidA, dim=fresh_dim): ...

    class LeafA2(MidA, dim=fresh_dim): ...

    class LeafB(MidB, dim=fresh_dim): ...

    class Unrelated(_Kind, dim=other_dim): ...

    return SimpleNamespace(
        base=Base,
        mid_a=MidA,
        mid_b=MidB,
        leaf_a=LeafA,
        leaf_a2=LeafA2,
        leaf_b=LeafB,
        unrelated=Unrelated,
    )


def _snapshot_registry():
    return {dim: list(kinds) for dim, kinds in k._registry.items()}


# Building blocks for the physics expressions below.
DIMENSIONLESS = Dimension.dimensionless()
TIME = k.Time.dimension
LENGTH = k.Length.dimension
MASS = k.Mass.dimension
CURRENT = k.ElectricCurrent.dimension
AMOUNT = k.AmountOfSubstance.dimension
LUMINOUS = k.LuminousIntensity.dimension


PHYSICS_LAW_CASES = [
    # Geometry and kinematics
    pytest.param(
        k.Area.dimension,
        LENGTH * LENGTH,
        id="A = L*L",
    ),
    pytest.param(
        k.Volume.dimension,
        k.Area.dimension * LENGTH,
        id="V = A*L",
    ),
    pytest.param(
        k.Velocity.dimension,
        LENGTH / TIME,
        id="v = d/t",
    ),
    pytest.param(
        k.Acceleration.dimension,
        k.Velocity.dimension / TIME,
        id="a = v/t",
    ),
    pytest.param(
        k.Acceleration.dimension,
        LENGTH / TIME**2,
        id="a = d/t^2",
    ),
    pytest.param(
        k.Jerk.dimension,
        k.Acceleration.dimension / TIME,
        id="j = a/t",
    ),
    pytest.param(
        k.Jounce.dimension,
        k.Jerk.dimension / TIME,
        id="Jounce: s = j/t",
    ),
    pytest.param(
        k.Snap.dimension,
        k.Jerk.dimension / TIME,
        id="Snap: s = j/t",
    ),
    pytest.param(
        k.Crackle.dimension,
        k.Snap.dimension / TIME,
        id="c = s/t",
    ),
    pytest.param(
        k.Pop.dimension,
        k.Crackle.dimension / TIME,
        id="p = c/t",
    ),
    # Angles are ratios of lengths, solid angles ratios of are,as
    pytest.param(
        k.Angle.dimension,
        LENGTH / LENGTH,
        id="angle = arc/radius",
    ),
    pytest.param(
        k.SolidAngle.dimension,
        k.Area.dimension / LENGTH**2,
        id="sr = A/r^2",
    ),
    pytest.param(
        k.Dimensionless.dimension,
        LENGTH / LENGTH,
        id="ratio of lengths",
    ),
    # Mechanics
    pytest.param(
        k.Force.dimension,
        k.Mass.dimension * k.Acceleration.dimension,
        id="F = ma",
    ),
    pytest.param(
        k.Work.dimension,
        k.Force.dimension * LENGTH,
        id="E = F*d",
    ),
    pytest.param(
        k.Energy.dimension,
        MASS * k.Velocity.dimension**2,
        id="E = m*v^2",
    ),
    pytest.param(
        k.Energy.dimension,
        k.Pressure.dimension * k.Volume.dimension,
        id="E = P*V",
    ),
    pytest.param(
        k.Power.dimension,
        k.Energy.dimension / TIME,
        id="P = E/t",
    ),
    pytest.param(
        k.Power.dimension,
        k.Force.dimension * k.Velocity.dimension,
        id="P = F*v",
    ),
    pytest.param(
        k.Pressure.dimension,
        k.Force.dimension / k.Area.dimension,
        id="Pressure: P = F/A",
    ),
    pytest.param(
        k.Stress.dimension,
        k.Force.dimension / k.Area.dimension,
        id="Stress: P = F/A",
    ),
    pytest.param(
        k.Intensity.dimension,
        k.Power.dimension / k.Area.dimension,
        id="I = P/A",
    ),
    pytest.param(
        k.Intensity.dimension,
        k.Pressure.dimension * k.Velocity.dimension,
        id="I = P*v",
    ),
    # Frequency
    pytest.param(
        DIMENSIONLESS,
        k.Frequency.dimension * TIME,
        id="Frequency: f*t = 1",
    ),
    pytest.param(
        DIMENSIONLESS,
        k.Radioactivity.dimension * TIME,
        id="Radioactivity: f*t = 1",
    ),
    # Electricity
    pytest.param(
        k.ElectricCharge.dimension,
        CURRENT * TIME,
        id="Q = I*t",
    ),
    pytest.param(
        k.ElectricPotentialDifference.dimension,
        k.Energy.dimension / k.ElectricCharge.dimension,
        id="V = E/Q",
    ),
    pytest.param(
        k.ElectricPotentialDifference.dimension,
        k.ElectricResistance.dimension * CURRENT,
        id="V = I*R",
    ),
    pytest.param(
        k.Power.dimension,
        k.ElectricPotentialDifference.dimension * CURRENT,
        id="P = V*I",
    ),
    pytest.param(
        k.Power.dimension,
        CURRENT**2 * k.ElectricResistance.dimension,
        id="P = I^2*R",
    ),
    pytest.param(
        DIMENSIONLESS,
        k.ElectricResistance.dimension * k.ElectricConductance.dimension,
        id="R*G = 1",
    ),
    pytest.param(
        k.Capacitance.dimension,
        k.ElectricCharge.dimension / k.ElectricPotentialDifference.dimension,
        id="C = Q/V",
    ),
    pytest.param(
        k.Capacitance.dimension * k.ElectricResistance.dimension,
        TIME,
        id="RC time constant",
    ),
    pytest.param(
        k.Inductance.dimension / k.ElectricResistance.dimension,
        TIME,
        id="L/R time constant",
    ),
    pytest.param(
        k.Energy.dimension,
        k.Capacitance.dimension * k.ElectricPotentialDifference.dimension**2,
        id="E = C*V^2",
    ),
    pytest.param(
        k.Energy.dimension, k.Inductance.dimension * CURRENT**2, id="E = L*I^2"
    ),
    # Magnetism
    pytest.param(
        k.MagneticFlux.dimension,
        k.ElectricPotentialDifference.dimension * TIME,
        id="flux = V*t",
    ),
    pytest.param(
        k.MagneticFlux.dimension,
        k.Inductance.dimension * CURRENT,
        id="flux = L*I",
    ),
    pytest.param(
        k.MagneticFlux.dimension,
        k.MagneticFluxDensity.dimension * k.Area.dimension,
        id="flux = B*A",
    ),
    # Photometry
    pytest.param(
        k.Illuminance.dimension * k.Area.dimension,
        k.LuminousFlux.dimension,
        id="E_v*A = luminous flux",
    ),
    pytest.param(
        k.LuminousFlux.dimension,
        LUMINOUS * k.SolidAngle.dimension,
        id="flux = I_v*sr",
    ),
    # Radiation and chemistry
    pytest.param(
        k.Kerma.dimension,
        k.Energy.dimension / MASS,
        id="Kerma: D = E/m",
    ),
    pytest.param(
        k.DoseEquivalent.dimension,
        k.Energy.dimension / MASS,
        id="Dose Equivalent: D = E/m",
    ),
    pytest.param(
        k.AbsorbedDose.dimension,
        k.Energy.dimension / MASS,
        id="Absorbed Dose: D = E/m",
    ),
    pytest.param(
        k.CatalyticActivity.dimension * TIME,
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
        k.Area,
        id="Area",
    ),
    pytest.param(
        k.Area.dimension * LENGTH,
        k.Volume,
        id="Volume",
    ),
    pytest.param(
        LENGTH / TIME,
        k.Velocity,
        id="Velocity",
    ),
    pytest.param(
        k.Velocity.dimension / TIME,
        k.Acceleration,
        id="Acceleration",
    ),
    pytest.param(
        MASS * k.Acceleration.dimension,
        k.Force,
        id="Force",
    ),
    pytest.param(
        k.Power.dimension / k.Area.dimension,
        k.Intensity,
        id="Intensity",
    ),
    pytest.param(
        CURRENT * TIME,
        k.ElectricCharge,
        id="ElectricCharge",
    ),
    pytest.param(
        k.Power.dimension / CURRENT,
        k.ElectricPotentialDifference,
        id="ElectricPotentialDifference",
    ),
    pytest.param(
        k.ElectricPotentialDifference.dimension / CURRENT,
        k.ElectricResistance,
        id="ElectricResistance",
    ),
    pytest.param(
        DIMENSIONLESS / k.ElectricResistance.dimension,
        k.ElectricConductance,
        id="ElectricConductance",
    ),
    pytest.param(
        k.ElectricCharge.dimension / k.ElectricPotentialDifference.dimension,
        k.Capacitance,
        id="Capacitance",
    ),
    pytest.param(
        k.ElectricPotentialDifference.dimension * TIME,
        k.MagneticFlux,
        id="MagneticFlux",
    ),
    pytest.param(
        k.MagneticFlux.dimension / k.Area.dimension,
        k.MagneticFluxDensity,
        id="MagneticFluxDensity",
    ),
    pytest.param(
        k.MagneticFlux.dimension / CURRENT,
        k.Inductance,
        id="Inductance",
    ),
    pytest.param(
        LUMINOUS / k.Area.dimension,
        k.Illuminance,
        id="Illuminance",
    ),
    pytest.param(
        AMOUNT / TIME,
        k.CatalyticActivity,
        id="CatalyticActivity",
    ),
]


@pytest.mark.parametrize(("dim", "expected"), UNAMBIGUOUS_RESULT_CASES)
def test_dimension_from_physics_expression_resolves_to_expected_kind(dim, expected):
    # Act
    resolved = resolve_kind(dim)

    # Assert
    assert resolved is expected


def test_standard_kind_has_dimension_instance(standard_kind):
    # Act
    dim = standard_kind.dimension

    # Assert
    assert isinstance(dim, Dimension)


def test_standard_kind_name_matches_class_name(standard_kind):
    # Arrange
    expected = standard_kind.__name__

    # Act
    actual = standard_kind.name

    # Assert
    assert actual == expected


def test_standard_kind_is_registered_exactly_once(standard_kind):
    # Arrange
    dim = standard_kind.dimension

    # Act
    registered = kinds_for(dim)

    # Assert
    assert registered.count(standard_kind) == 1


def test_standard_kind_shares_dimension_with_every_kind_ancestor(
    standard_kind, standard_kinds
):
    # Arrange
    ancestors = [other for other in standard_kinds if issubclass(standard_kind, other)]

    # Act
    mismatched = [
        base for base in ancestors if base.dimension != standard_kind.dimension
    ]

    # Assert
    assert len(mismatched) == 0


def test_standard_kind_names_are_unique(standard_kinds):
    # Arrange
    names = [kind.name for kind in standard_kinds]

    # Act
    unique_names = set(names)

    # Assert
    assert len(unique_names) == len(names)


def test_kinds_for_returns_empty_tuple_for_unknown_dimension(fresh_dim):
    # Act
    result = kinds_for(fresh_dim)

    # Assert
    assert result == ()


def test_kinds_for_returns_a_tuple():
    # Arrange
    dim = k.Length.dimension

    # Act
    result = kinds_for(dim)

    # Assert
    assert isinstance(result, tuple)


def test_kinds_for_unknown_dimension_does_not_modify_registry(fresh_dim):
    # Arrange
    before = _snapshot_registry()

    # Act
    kinds_for(fresh_dim)

    # Assert
    assert fresh_dim not in k._registry
    assert _snapshot_registry() == before


def test_kinds_for_returns_all_kinds_sharing_a_dimension_in_definition_order(
    isolated_registry, fresh_dim
):
    # Arrange
    class First(_Kind, dim=fresh_dim): ...

    class Second(_Kind, dim=fresh_dim): ...

    class Third(_Kind, dim=fresh_dim): ...

    # Act
    result = kinds_for(fresh_dim)

    # Assert
    assert result == (First, Second, Third)


def test_kinds_for_only_returns_kinds_of_the_requested_dimension(
    isolated_registry, fresh_dim, other_dim
):
    # Arrange
    class InFresh(_Kind, dim=fresh_dim): ...

    class InOther(_Kind, dim=other_dim): ...

    # Act
    fresh_result = kinds_for(fresh_dim)
    other_result = kinds_for(other_dim)

    # Assert
    assert fresh_result == (InFresh,)
    assert other_result == (InOther,)


def test_kinds_for_result_is_not_changed_by_later_registrations(
    isolated_registry, fresh_dim
):
    # Arrange
    class First(_Kind, dim=fresh_dim): ...

    earlier_result = kinds_for(fresh_dim)

    # Act
    class Second(_Kind, dim=fresh_dim): ...

    # Assert
    assert earlier_result == (First,)
    assert kinds_for(fresh_dim) == (First, Second)


def test_kinds_for_includes_subclass_aliases_alongside_their_parent(
    isolated_registry, fresh_dim
):
    # Arrange
    class Parent(_Kind, dim=fresh_dim): ...

    class Alias(Parent, dim=fresh_dim): ...

    # Act
    result = kinds_for(fresh_dim)

    # Assert
    assert result == (Parent, Alias)


def test_resolve_kind_returns_none_for_unknown_dimension(fresh_dim):
    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is None


def test_resolve_kind_returns_the_only_kind_when_dimension_is_unique(
    isolated_registry, fresh_dim
):
    # Arrange
    class Only(_Kind, dim=fresh_dim): ...

    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is Only


def test_resolve_kind_returns_none_when_ambiguous_and_no_default(
    isolated_registry, fresh_dim
):
    # Arrange
    class First(_Kind, dim=fresh_dim): ...

    class Second(_Kind, dim=fresh_dim): ...

    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is None


def test_resolve_kind_returns_default_declared_last(isolated_registry, fresh_dim):
    # Arrange
    class First(_Kind, dim=fresh_dim): ...

    class Second(_Kind, dim=fresh_dim, default=True): ...

    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is Second


def test_resolve_kind_returns_default_declared_first(isolated_registry, fresh_dim):
    # Arrange
    class First(_Kind, dim=fresh_dim, default=True): ...

    class Second(_Kind, dim=fresh_dim): ...

    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is First


def test_resolve_kind_returns_default_when_it_is_the_only_kind(
    isolated_registry, fresh_dim
):
    # Arrange
    class Only(_Kind, dim=fresh_dim, default=True): ...

    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is Only


def test_resolve_kind_default_false_does_not_make_a_default(
    isolated_registry, fresh_dim
):
    # Arrange
    class First(_Kind, dim=fresh_dim, default=False): ...

    class Second(_Kind, dim=fresh_dim, default=False): ...

    # Act
    result = resolve_kind(fresh_dim)

    # Assert
    assert result is None


def test_resolve_kind_defaults_are_per_dimension(
    isolated_registry, fresh_dim, other_dim
):
    # Arrange
    class FreshDefault(_Kind, dim=fresh_dim, default=True): ...

    class FreshOther(_Kind, dim=fresh_dim): ...

    class OtherFirst(_Kind, dim=other_dim): ...

    class OtherSecond(_Kind, dim=other_dim): ...

    # Act
    fresh_result = resolve_kind(fresh_dim)
    other_result = resolve_kind(other_dim)

    # Assert
    assert fresh_result is FreshDefault
    assert other_result is None


TREE_COMMON_KIND_CASES = [
    pytest.param("leaf_a", "leaf_a2", "mid_a", id="siblings->parent"),
    pytest.param("leaf_a", "leaf_b", "base", id="cousins->grandparent"),
    pytest.param("mid_a", "mid_b", "base", id="mid-siblings->parent"),
    pytest.param("leaf_a", "mid_a", "mid_a", id="child+parent->parent"),
    pytest.param("mid_a", "leaf_a", "mid_a", id="parent+child->parent"),
    pytest.param("leaf_a", "base", "base", id="grandchild+ancestor->ancestor"),
    pytest.param("leaf_a", "leaf_a", "leaf_a", id="leaf+itself->leaf"),
    pytest.param("base", "base", "base", id="root+itself->root"),
    pytest.param("leaf_a", "unrelated", None, id="unrelated->None"),
    pytest.param("base", "unrelated", None, id="root+unrelated->None"),
]


@pytest.mark.parametrize(("first", "second", "expected"), TREE_COMMON_KIND_CASES)
def test_get_common_kind_returns_lowest_common_ancestor(
    kind_tree, first, second, expected
):
    # Arrange
    a = getattr(kind_tree, first)
    b = getattr(kind_tree, second)
    expected_kind = None if expected is None else getattr(kind_tree, expected)

    # Act
    result = get_common_kind(a, b)

    # Assert
    assert result is expected_kind


def test_get_common_kind_never_returns_the_base_kind_class(kind_tree):
    # Arrange
    a = kind_tree.leaf_a
    b = kind_tree.unrelated

    # Act
    result = get_common_kind(a, b)

    # Assert
    assert result is not _Kind
    assert result is None


STANDARD_COMMON_KIND_CASES = [
    pytest.param(k.Work, k.AmountOfHeat, k.Energy, id="Work+AmountOfHeat"),
    pytest.param(k.Work, k.Energy, k.Energy, id="Work+Energy"),
    pytest.param(k.Energy, k.Work, k.Energy, id="Energy+Work"),
    pytest.param(k.Jounce, k.Snap, k.Snap, id="Jounce+Snap"),
    pytest.param(k.RadiantFlux, k.Power, k.Power, id="RadiantFlux+Power"),
    pytest.param(k.Length, k.Length, k.Length, id="Length+Length"),
    pytest.param(k.Torque, k.Energy, None, id="Torque+Energy"),
    pytest.param(k.Torque, k.Work, None, id="Torque+Work"),
    pytest.param(k.Angle, k.Dimensionless, None, id="Angle+Dimensionless"),
    pytest.param(k.Length, k.Time, None, id="Length+Time"),
]


@pytest.mark.parametrize(("first", "second", "expected"), STANDARD_COMMON_KIND_CASES)
def test_get_common_kind_for_standard_kinds(first, second, expected):
    # Act
    result = get_common_kind(first, second)

    # Assert
    assert result is expected


def test_get_common_kind_of_a_standard_kind_with_itself_is_itself(standard_kind):
    # Act
    result = get_common_kind(standard_kind, standard_kind)

    # Assert
    assert result is standard_kind


def test_get_common_kind_is_symmetric_for_all_standard_kinds(standard_kind_pairs):
    # Act
    asymmetric = [
        (a.__name__, b.__name__)
        for a, b in standard_kind_pairs
        if get_common_kind(a, b) is not get_common_kind(b, a)
    ]

    # Assert
    assert len(asymmetric) == 0


def test_get_common_kind_result_is_an_ancestor_of_both_inputs(standard_kind_pairs):
    # Act
    violations = []
    for a, b in standard_kind_pairs:
        common = get_common_kind(a, b)
        if common is not None and not (issubclass(a, common) and issubclass(b, common)):
            violations.append((a.__name__, b.__name__, common.__name__))

    # Assert
    assert len(violations) == 0


def test_get_common_kind_result_shares_dimension_with_both_inputs(standard_kind_pairs):
    # Act
    violations = []
    for a, b in standard_kind_pairs:
        common = get_common_kind(a, b)
        if common is not None and not (common.dimension == a.dimension == b.dimension):
            violations.append((a.__name__, b.__name__, common.__name__))

    # Assert
    assert violations == []


def test_get_common_kind_is_none_for_kinds_of_different_dimensions(standard_kind_pairs):
    # Arrange
    pairs = [(a, b) for a, b in standard_kind_pairs if a.dimension != b.dimension]

    # Act
    violations = [
        (a.__name__, b.__name__) for a, b in pairs if get_common_kind(a, b) is not None
    ]

    # Assert
    assert len(violations) == 0


def test_subclass_gets_dimension_class_variable(isolated_registry, fresh_dim):
    # Act
    class Thing(_Kind, dim=fresh_dim): ...

    # Assert
    assert Thing.dimension == fresh_dim


def test_subclass_gets_name_class_variable(isolated_registry, fresh_dim):
    # Act
    class Thing(_Kind, dim=fresh_dim): ...

    # Assert
    assert Thing.name == "Thing"


def test_subclass_of_a_kind_gets_its_own_name(isolated_registry, fresh_dim):
    # Arrange
    class Parent(_Kind, dim=fresh_dim): ...

    # Act
    class Child(Parent, dim=fresh_dim): ...

    # Assert
    assert Child.name == "Child"
    assert Parent.name == "Parent"


def test_new_kind_does_not_displace_existing_kinds(isolated_registry):
    # Arrange
    dim = k.Length.dimension
    before = kinds_for(dim)

    # Act
    class AnotherLength(_Kind, dim=dim): ...

    # Assert
    assert kinds_for(dim) == (*before, AnotherLength)


def test_default_is_not_inherited_by_subclasses(isolated_registry, fresh_dim):
    # Arrange
    class Base(_Kind, dim=fresh_dim, default=True): ...

    # Act
    class Alias(Base, dim=fresh_dim): ...

    # Assert
    assert resolve_kind(fresh_dim) is Base


def test_second_default_for_same_dimension_raises_type_error(
    isolated_registry, fresh_dim
):
    # Arrange
    class First(_Kind, dim=fresh_dim, default=True): ...

    # Act
    with pytest.raises(TypeError) as exc_info:

        class Second(_Kind, dim=fresh_dim, default=True): ...

    # Assert
    assert "already the default" in str(exc_info.value)


def test_duplicate_default_error_message_names_both_kinds(isolated_registry, fresh_dim):
    # Arrange
    class First(_Kind, dim=fresh_dim, default=True): ...

    # Act
    with pytest.raises(TypeError) as exc_info:

        class Second(_Kind, dim=fresh_dim, default=True): ...

    # Assert
    message = str(exc_info.value)
    assert "First" in message
    assert "Second" in message


def test_subclass_without_dim_raises_and_registers_nothing(isolated_registry):
    # Arrange
    before = _snapshot_registry()

    # Act
    with pytest.raises(TypeError):

        class Bad(_Kind): ...  # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]

    # Assert
    assert _snapshot_registry() == before


def test_unexpected_class_keyword_raises_and_registers_nothing(
    isolated_registry, fresh_dim
):
    # Arrange
    before = _snapshot_registry()

    # Act
    with pytest.raises(TypeError):

        class Bad(_Kind, dim=fresh_dim, not_a_real_option=True): ...

    # Assert
    assert _snapshot_registry() == before
    assert kinds_for(fresh_dim) == ()
