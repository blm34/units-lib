import types

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.exceptions import IncompatibleKindsError
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


class TestNullKind:
    def test_can_create_null_kind_with_explicit_dimension(self, length_dimension):
        # ARRANGE
        class LengthNullKind(NullKind, dimension=length_dimension):
            pass

        # ACT
        result = LengthNullKind.dimension

        # ASSERT
        assert result == length_dimension

    def test_name_is_set_from_class_name(self, length_dimension):
        # ARRANGE
        class LengthNullKind(NullKind, dimension=length_dimension):
            pass

        # ACT
        result = LengthNullKind.name

        # ASSERT
        assert result == "LengthNullKind[L]"

    def test_is_null_is_true(self, length_dimension):
        # ARRANGE
        class LengthNullKind(NullKind, dimension=length_dimension):
            pass

        # ACT
        result = LengthNullKind.is_null

        # ASSERT
        assert result is True

    def test_null_kind_is_falsey(self, length_dimension):
        # ARRANGE
        class LengthNullKind(NullKind, dimension=length_dimension):
            pass

        # ACT
        result = bool(LengthNullKind)

        # ASSERT
        assert result is False

    def test_base_null_kind_is_falsey(self):
        # ARRANGE
        null_kind = NullKind

        # ACT
        result = bool(null_kind)

        # ASSERT
        assert result is False


class TestNullKindFor:
    def test_null_kind_for_creates_kind_with_correct_dimension(self, length_dimension):
        # ACT
        result = null_kind_for(length_dimension)

        # ASSERT
        assert result.dimension == length_dimension

    def test_null_kind_for_sets_name_from_dimension(self, length_dimension):
        # ACT
        result = null_kind_for(length_dimension)

        # ASSERT
        assert result.__name__ == "NullKind"
        assert result.name == "NullKind[L]"

    def test_null_kind_for_sets_module(self, length_dimension):
        # ACT
        result = null_kind_for(length_dimension)

        # ASSERT
        assert result.__module__ == NullKind.__module__

    def test_null_kind_for_returns_null_kind_subclass(self, length_dimension):
        # ACT
        result = null_kind_for(length_dimension)

        # ASSERT
        assert issubclass(result, NullKind)

    def test_null_kind_for_sets_is_null(self, length_dimension):
        # ACT
        result = null_kind_for(length_dimension)

        # ASSERT
        assert result.is_null is True

    def test_null_kind_for_returns_falsey_kind(self, length_dimension):
        # ACT
        result = bool(null_kind_for(length_dimension))

        # ASSERT
        assert result is False

    def test_null_kind_for_returns_same_kind_for_same_dimension(self, length_dimension):
        # ACT
        first = null_kind_for(length_dimension)
        second = null_kind_for(length_dimension)

        # ASSERT
        assert first is second

    def test_null_kind_for_returns_same_kind_for_equal_dimensions(self):
        # ARRANGE
        first_dimension = Dimension.base(BaseDimension.LENGTH)
        second_dimension = Dimension.from_dict({"length": 1})

        # ACT
        first = null_kind_for(first_dimension)
        second = null_kind_for(second_dimension)

        # ASSERT
        assert first_dimension == second_dimension
        assert first is second

    def test_null_kind_for_returns_different_kinds_for_different_dimensions(
        self, length_dimension, time_dimension
    ):
        # ACT
        length_kind = null_kind_for(length_dimension)
        time_kind = null_kind_for(time_dimension)

        # ASSERT
        assert length_kind is not time_kind

    def test_null_kind_for_different_dimensions_have_correct_dimensions(
        self, length_dimension, time_dimension
    ):
        # ACT
        length_kind = null_kind_for(length_dimension)
        time_kind = null_kind_for(time_dimension)

        # ASSERT
        assert length_kind.dimension == length_dimension
        assert time_kind.dimension == time_dimension

    def test_subclass_of_null_kind_is_falsey(self, length_dimension):
        # ARRANGE
        base = null_kind_for(length_dimension)

        class DerivedNullKind(base, dimension=base.dimension):
            pass

        # ACT
        result = bool(DerivedNullKind)

        # ASSERT
        assert result is False


class TestIsCompatible:
    def test_returns_false_for_different_dimensions_of_null(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = null_kind_for(length_dimension)
        time_kind = null_kind_for(time_dimension)

        # ACT
        result = length_kind.is_compatible(time_kind)

        # ASSERT
        assert result is False

    def test_returns_false_for_different_dimensions_of_real(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = null_kind_for(length_dimension)
        time_kind = make_kind("Time", time_dimension)

        # ACT
        result = length_kind.is_compatible(time_kind)

        # ASSERT
        assert result is False

    def test_returns_true_when_dimension_is_the_same_for_null(self, length_dimension):
        # ARRANGE
        first = null_kind_for(length_dimension)
        second = null_kind_for(length_dimension)

        # ACT
        result = first.is_compatible(second)

        # ASSERT
        assert result is True

    def test_returns_true_when_dimension_is_the_same_for_real(self, length_dimension):
        # ARRANGE
        first = null_kind_for(length_dimension)
        second = make_kind("RealLength", length_dimension)

        # ACT
        result = first.is_compatible(second)

        # ASSERT
        assert result is True


class TestCommonWith:
    def test_returns_null_kind_when_dimensions_match_null(self, length_dimension):
        # ARRANGE
        first = null_kind_for(length_dimension)
        second = null_kind_for(length_dimension)

        # ACT
        result = first.common_with(second)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.dimension == length_dimension

    def test_returns_null_kind_when_dimensions_match_real(self, length_dimension):
        # ARRANGE
        first = null_kind_for(length_dimension)
        second = make_kind("RealLength", length_dimension)

        # ACT
        result = first.common_with(second)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.dimension == length_dimension

    def test_raises_for_different_dimensions_null(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = null_kind_for(length_dimension)
        time_kind = null_kind_for(time_dimension)

        # ACT / ASSERT
        with pytest.raises(IncompatibleKindsError):
            length_kind.common_with(time_kind)

    def test_raises_for_different_dimensions_real(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = null_kind_for(length_dimension)
        time_kind = make_kind("RealTime", time_dimension)

        # ACT / ASSERT
        with pytest.raises(IncompatibleKindsError):
            length_kind.common_with(time_kind)

    def test_error_message_includes_kind_names_and_dimensions(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = null_kind_for(length_dimension)
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
