import types

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind import operations
from units_lib.kind.catalogue.catalogue_spec import KindSpec
from units_lib.kind.null_kind import NullKind
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
