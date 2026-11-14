import types

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.exceptions import IncompatibleDimensionError
from units_lib.kind import operations
from units_lib.kind.catalogue.catalogue_spec import KindSpec
from units_lib.kind.null_kind import NullKind, null_kind_for
from units_lib.kind.real_kind import RealKind


@pytest.fixture
def length_dimension():
    return Dimension.base(BaseDimension.LENGTH)


@pytest.fixture
def time_dimension():
    return Dimension.base(BaseDimension.TIME)


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


def make_spec(
    name: str,
    dimension: Dimension,
    *,
    inherits: str | None = None,
    alias: str | None = None,
    default: bool = False,
) -> KindSpec:
    return KindSpec(
        name=name,
        dimension=dimension,
        inherits=inherits,
        alias=alias,
        default=default,
    )


class TestKindsFor:
    def test_returns_all_kinds_for_dimension(
        self, monkeypatch, fresh_registry, length_dimension
    ):
        # ARRANGE
        first_spec = make_spec("FirstKind", length_dimension)
        second_spec = make_spec("SecondKind", length_dimension)

        fresh_registry.register(first_spec)
        fresh_registry.register(second_spec)

        first_kind = make_kind("FirstKind", length_dimension)
        second_kind = make_kind("SecondKind", length_dimension)

        monkeypatch.setattr(
            operations,
            "spec_to_domain",
            lambda spec: {
                first_spec: first_kind,
                second_spec: second_kind,
            }[spec],
        )

        # ACT
        result = operations.kinds_for(length_dimension)

        # ASSERT
        assert set(result) == {first_kind, second_kind}

    def test_returns_empty_tuple_when_no_kinds_exist(
        self, monkeypatch, fresh_registry, length_dimension
    ):
        # ACT
        result = operations.kinds_for(length_dimension)

        # ASSERT
        assert result == ()

    def test_returns_tuple(self, fresh_registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)
        fresh_registry.register(spec)

        # ACT
        result = operations.kinds_for(length_dimension)

        # ASSERT
        assert isinstance(result, tuple)

    def test_removes_duplicate_domain_kinds(
        self, monkeypatch, fresh_registry, length_dimension
    ):
        # ARRANGE
        first_spec = make_spec("FirstSpec", length_dimension)
        second_spec = make_spec("SecondSpec", length_dimension, alias="FirstSpec")
        fresh_registry.register(first_spec)
        fresh_registry.register(second_spec)

        # ACT
        result = operations.kinds_for(length_dimension)

        # ASSERT
        assert len(result) == 1
        assert result[0].name.startswith("FirstSpec")


class TestResolveKind:
    def test_returns_defined_default_when_available(
        self, fresh_registry, monkeypatch, length_dimension
    ):
        # ARRANGE
        default_spec = make_spec("DefaultKind", length_dimension, default=True)
        fresh_registry.register(default_spec)
        default_kind = make_kind("DefaultKind", length_dimension)

        monkeypatch.setattr(operations, "spec_to_domain", lambda spec: default_kind)

        def fail_if_called(dim):
            pytest.fail("kinds_for should not be called when a default exists")

        monkeypatch.setattr(operations, "kinds_for", fail_if_called)

        # ACT
        result = operations.resolve_kind(length_dimension)

        # ASSERT
        assert result is default_kind

    def test_returns_only_kind_when_no_default_exists(
        self, monkeypatch, fresh_registry, length_dimension
    ):
        # ARRANGE
        only_spec = make_spec("OnlyKind", length_dimension)
        fresh_registry.register(only_spec)
        only_kind = make_kind("OnlyKind", length_dimension)

        monkeypatch.setattr(operations, "kinds_for", lambda dim: (only_kind,))

        # ACT
        result = operations.resolve_kind(length_dimension)

        # ASSERT
        assert result is only_kind

    def test_returns_null_kind_when_no_kinds_exist(
        self, fresh_registry, length_dimension
    ):
        # ACT
        result = operations.resolve_kind(length_dimension)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.is_null is True
        assert result.dimension == length_dimension

    def test_returns_null_kind_when_multiple_kinds_exist(
        self, fresh_registry, length_dimension
    ):
        # ARRANGE
        first_spec = make_spec("FirstKind", length_dimension)
        fresh_registry.register(first_spec)
        second_spec = make_spec("SecondKind", length_dimension)
        fresh_registry.register(second_spec)

        # ACT
        result = operations.resolve_kind(length_dimension)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.is_null is True
        assert result.dimension == length_dimension

    def test_returns_cached_null_kind_for_same_dimension(self, length_dimension):
        # ACT
        first = operations.resolve_kind(length_dimension)
        second = operations.resolve_kind(length_dimension)

        # ASSERT
        assert first is second


class TestKindsCompatible:
    def test_returns_false_for_different_dimensions(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = make_kind("LengthKind", length_dimension)
        time_kind = make_kind("TimeKind", time_dimension)

        # ACT
        result = operations.kinds_compatible(length_kind, time_kind)

        # ASSERT
        assert result is False

    def test_returns_true_when_first_kind_is_null(self, length_dimension):
        # ARRANGE
        null_kind = null_kind_for(length_dimension)
        real_kind = make_kind("LengthKind", length_dimension)

        # ACT
        result = operations.kinds_compatible(null_kind, real_kind)

        # ASSERT
        assert result is True

    def test_returns_true_when_second_kind_is_null(self, length_dimension):
        # ARRANGE
        real_kind = make_kind("LengthKind", length_dimension)
        null_kind = null_kind_for(length_dimension)

        # ACT
        result = operations.kinds_compatible(real_kind, null_kind)

        # ASSERT
        assert result is True

    def test_returns_true_when_kinds_share_common_ancestor(self, length_dimension):
        # ARRANGE
        parent = make_kind("ParentKind", length_dimension)
        first = make_kind("FirstKind", length_dimension, parent)
        second = make_kind("SecondKind", length_dimension, parent)

        # ACT
        result = operations.kinds_compatible(first, second)

        # ASSERT
        assert result is True

    def test_returns_false_when_kinds_have_no_common_ancestor(self, length_dimension):
        # ARRANGE
        first = make_kind("FirstKind", length_dimension)
        second = make_kind("SecondKind", length_dimension)

        # ACT
        result = operations.kinds_compatible(first, second)

        # ASSERT
        assert result is False

    def test_returns_true_when_kind_is_compatible_with_itself(self, length_dimension):
        # ARRANGE
        kind = make_kind("LengthKind", length_dimension)

        # ACT
        result = operations.kinds_compatible(kind, kind)

        # ASSERT
        assert result is True


class TestGetCommonKind:
    def test_returns_shared_parent_for_sibling_kinds(self, length_dimension):
        # ARRANGE
        parent = make_kind("ParentKind", length_dimension)
        first = make_kind("FirstKind", length_dimension, parent)
        second = make_kind("SecondKind", length_dimension, parent)

        # ACT
        result = operations.get_common_kind(first, second)

        # ASSERT
        assert result is parent

    def test_returns_nearest_common_ancestor(self, length_dimension):
        # ARRANGE
        grandparent = make_kind("Grandparent", length_dimension)
        parent = make_kind("Parent", length_dimension, grandparent)
        child = make_kind("Child", length_dimension, parent)
        sibling = make_kind("Sibling", length_dimension, parent)

        # ACT
        result = operations.get_common_kind(child, sibling)

        # ASSERT
        assert result is parent

    def test_returns_parent_when_one_kind_inherits_from_other(self, length_dimension):
        # ARRANGE
        parent = make_kind("ParentKind", length_dimension)
        child = make_kind("ChildKind", length_dimension, parent)

        # ACT
        result = operations.get_common_kind(child, parent)

        # ASSERT
        assert result is parent

    def test_returns_kind_itself_when_both_arguments_are_same(self, length_dimension):
        # ARRANGE
        kind = make_kind("LengthKind", length_dimension)

        # ACT
        result = operations.get_common_kind(kind, kind)

        # ASSERT
        assert result is kind

    def test_returns_null_kind_when_no_common_ancestor_exists(self, length_dimension):
        # ARRANGE
        first = make_kind("FirstKind", length_dimension)
        second = make_kind("SecondKind", length_dimension)

        # ACT
        result = operations.get_common_kind(first, second)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.is_null is True
        assert result.dimension == length_dimension

    def test_returns_null_kind_when_first_kind_is_null(self, length_dimension):
        # ARRANGE
        null_kind = null_kind_for(length_dimension)
        real_kind = make_kind("LengthKind", length_dimension)

        # ACT
        result = operations.get_common_kind(null_kind, real_kind)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.dimension == length_dimension

    def test_returns_null_kind_when_second_kind_is_null(self, length_dimension):
        # ARRANGE
        real_kind = make_kind("LengthKind", length_dimension)
        null_kind = null_kind_for(length_dimension)

        # ACT
        result = operations.get_common_kind(real_kind, null_kind)

        # ASSERT
        assert issubclass(result, NullKind)
        assert result.dimension == length_dimension

    def test_raises_for_different_dimensions(self, length_dimension, time_dimension):
        # ARRANGE
        length_kind = make_kind("LengthKind", length_dimension)
        time_kind = make_kind("TimeKind", time_dimension)

        # ACT / ASSERT
        with pytest.raises(IncompatibleDimensionError):
            operations.get_common_kind(length_kind, time_kind)

    def test_error_message_includes_kind_names_and_dimensions(
        self, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = make_kind("LengthKind", length_dimension)
        time_kind = make_kind("TimeKind", time_dimension)

        # ACT
        with pytest.raises(IncompatibleDimensionError) as exc_info:
            operations.get_common_kind(length_kind, time_kind)

        # ASSERT
        message = str(exc_info.value)
        assert length_kind.name in message
        assert time_kind.name in message
        assert str(length_dimension) in message
        assert str(time_dimension) in message
