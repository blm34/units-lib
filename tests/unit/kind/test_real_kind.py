import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.exceptions import IncompatibleDimensionError
from units_lib.kind.real_kind import RealKind


class TestRealKind:
    @pytest.fixture
    def length_dimension(self):
        return Dimension.base(BaseDimension.LENGTH)

    @pytest.fixture
    def time_dimension(self):
        return Dimension.base(BaseDimension.TIME)

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
