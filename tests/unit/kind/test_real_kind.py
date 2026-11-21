import types

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.exceptions import IncompatibleDimensionError, IncompatibleKindsError
from units_lib.kind.null_kind import NullKind, null_kind_for
from units_lib.kind.real_kind import RealKind


def make_kind(
    name: str,
    dimension: Dimension,
    inherits: type[RealKind] | None = None,
) -> type[RealKind]:
    base = inherits or RealKind

    return types.new_class(
        name,
        (base,),
        {"dimension": dimension},
        lambda ns: ns.update(__module__=__name__),
    )


@pytest.fixture
def length_dimension():
    return Dimension.base(BaseDimension.LENGTH)


@pytest.fixture
def time_dimension():
    return Dimension.base(BaseDimension.TIME)


class TestRealKind:
    def test_can_create_kind_with_explicit_dimension(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        # ACT
        result = LengthKind.dimension

        # ASSERT
        assert result == length_dimension

    def test_can_inherit_dimension_from_parent(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        class DerivedLengthKind(LengthKind):
            pass

        # ACT
        result = DerivedLengthKind.dimension

        # ASSERT
        assert result == length_dimension

    def test_can_explicitly_pass_inherited_dimension(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        class DerivedLengthKind(LengthKind, dimension=length_dimension):
            pass

        # ACT
        result = DerivedLengthKind.dimension

        # ASSERT
        assert result == length_dimension

    def test_cannot_create_kind_without_dimension_or_parent(self):
        # ARRANGE & ACT
        with pytest.raises(TypeError) as error:

            class InvalidKind(RealKind):
                pass

        # ASSERT
        assert str(error.value) == (
            "InvalidKind must pass `dimension` as it has no `Kind` to inherit one from"
        )

    def test_cannot_inherit_different_dimension_from_parent(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        # ACT
        with pytest.raises(IncompatibleDimensionError):

            class InvalidKind(LengthKind, dimension=time_dimension):
                pass

    def test_cannot_inherit_from_parents_with_different_dimensions(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        class TimeKind(RealKind, dimension=time_dimension):
            pass

        # ACT
        with pytest.raises(TypeError) as error:

            class InvalidKind(LengthKind, TimeKind):
                pass

        # ASSERT
        assert str(error.value) == (
            "InvalidKind inherits from `Kind`s with different dimensions"
        )

    def test_can_inherit_from_multiple_parents_with_same_dimension(
        self, length_dimension
    ):
        # ARRANGE
        class LengthKindA(RealKind, dimension=length_dimension):
            pass

        class LengthKindB(RealKind, dimension=length_dimension):
            pass

        class CombinedLengthKind(LengthKindA, LengthKindB):
            pass

        # ACT
        result = CombinedLengthKind.dimension

        # ASSERT
        assert result == length_dimension

    def test_name_is_set_from_class_name_and_dimension(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        # ACT
        result = LengthKind.name

        # ASSERT
        assert result == "LengthKind[L]"

    def test_inherited_kind_gets_its_own_name(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        class DerivedLengthKind(LengthKind):
            pass

        # ACT
        result = DerivedLengthKind.name

        # ASSERT
        assert result == "DerivedLengthKind[L]"

    def test_is_null_defaults_to_false(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        # ACT
        result = LengthKind.is_null

        # ASSERT
        assert result is False

    def test_real_kind_is_truthy(self, length_dimension):
        # ARRANGE
        class LengthKind(RealKind, dimension=length_dimension):
            pass

        # ACT
        result = bool(LengthKind)

        # ASSERT
        assert result == True


class TestIsCompatible:
    def test_returns_false_for_different_dimensions(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = make_kind("LengthKind", length_dimension)
        time_kind = make_kind("TimeKind", time_dimension)

        # ACT
        result = length_kind.is_compatible(time_kind)

        # ASSERT
        assert result is False

    def test_returns_true_when_second_kind_is_null(self, length_dimension):
        # ARRANGE
        real_kind = make_kind("LengthKind", length_dimension)
        null_kind = null_kind_for(length_dimension)

        # ACT
        result = real_kind.is_compatible(null_kind)

        # ASSERT
        assert result is True

    def test_returns_true_when_kinds_share_common_ancestor(self, length_dimension):
        # ARRANGE
        parent = make_kind("ParentKind", length_dimension)
        first = make_kind("FirstKind", length_dimension, parent)
        second = make_kind("SecondKind", length_dimension, parent)

        # ACT
        result = first.is_compatible(second)

        # ASSERT
        assert result is True

    def test_returns_false_when_kinds_have_no_common_ancestor(self, length_dimension):
        # ARRANGE
        first = make_kind("FirstKind", length_dimension)
        second = make_kind("SecondKind", length_dimension)

        # ACT
        result = first.is_compatible(second)

        # ASSERT
        assert result is False

    def test_returns_true_when_kind_is_compatible_with_itself(self, length_dimension):
        # ARRANGE
        kind = make_kind("LengthKind", length_dimension)

        # ACT
        result = kind.is_compatible(kind)

        # ASSERT
        assert result is True


class TestCommonWith:
    def test_returns_shared_parent_for_sibling_kinds(self, length_dimension):
        # ARRANGE
        parent = make_kind("ParentKind", length_dimension)
        first = make_kind("FirstKind", length_dimension, parent)
        second = make_kind("SecondKind", length_dimension, parent)

        # ACT
        result = first.common_with(second)

        # ASSERT
        assert result is parent

    def test_returns_nearest_common_ancestor(self, length_dimension):
        # ARRANGE
        grandparent = make_kind("Grandparent", length_dimension)
        parent = make_kind("Parent", length_dimension, grandparent)
        child = make_kind("Child", length_dimension, parent)
        sibling = make_kind("Sibling", length_dimension, parent)

        # ACT
        result = child.common_with(sibling)

        # ASSERT
        assert result is parent

    def test_returns_parent_when_one_kind_inherits_from_other(self, length_dimension):
        # ARRANGE
        parent = make_kind("ParentKind", length_dimension)
        child = make_kind("ChildKind", length_dimension, parent)

        # ACT
        result = child.common_with(parent)

        # ASSERT
        assert result is parent

    def test_returns_kind_itself_when_both_arguments_are_same(self, length_dimension):
        # ARRANGE
        kind = make_kind("LengthKind", length_dimension)

        # ACT
        result = kind.common_with(kind)

        # ASSERT
        assert result is kind

    def test_returns_null_kind_when_no_common_ancestor_exists(self, length_dimension):
        # ARRANGE
        first = make_kind("FirstKind", length_dimension)
        second = make_kind("SecondKind", length_dimension)

        # ACT
        result = first.common_with(second)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.is_null is True
        assert result.dimension == length_dimension

    def test_returns_null_kind_when_second_kind_is_null(self, length_dimension):
        # ARRANGE
        real_kind = make_kind("LengthKind", length_dimension)
        null_kind = null_kind_for(length_dimension)

        # ACT
        result = real_kind.common_with(null_kind)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.dimension == length_dimension

    def test_raises_for_different_dimensions(self, length_dimension, time_dimension):
        # ARRANGE
        length_kind = make_kind("LengthKind", length_dimension)
        time_kind = make_kind("TimeKind", time_dimension)

        # ACT / ASSERT
        with pytest.raises(IncompatibleKindsError):
            length_kind.common_with(time_kind)

    def test_error_message_includes_kind_names_and_dimensions(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = make_kind("LengthKind", length_dimension)
        time_kind = make_kind("TimeKind", time_dimension)

        # ACT
        with pytest.raises(IncompatibleKindsError) as exc_info:
            length_kind.common_with(time_kind)

        # ASSERT
        message = str(exc_info.value)
        assert length_kind.name in message
        assert time_kind.name in message
        assert str(length_dimension) in message
        assert str(time_dimension) in message
