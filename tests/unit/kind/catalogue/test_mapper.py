import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind.catalogue import mapper
from units_lib.kind.catalogue.catalogue_spec import KindSpec
from units_lib.kind.catalogue.mapper import spec_to_domain
from units_lib.kind.catalogue.spec_registry import KindRegistry
from units_lib.kind.real_kind import RealKind


@pytest.fixture(autouse=True)
def clear_cache():
    spec_to_domain.cache_clear()


@pytest.fixture
def dimension():
    return Dimension.dimensionless()


@pytest.fixture
def length_dimension():
    return Dimension.base(BaseDimension.LENGTH)


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


class TestSpecToDomain:
    def test_creates_real_kind_subclass(self, dimension):
        # ARRANGE
        spec = make_spec("TestKind", dimension)

        # ACT
        result = spec_to_domain(spec)

        # ASSERT
        assert isinstance(result, type)
        assert issubclass(result, RealKind)
        assert result is not RealKind

    def test_sets_dimension(self, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)

        # ACT
        result = spec_to_domain(spec)

        # ASSERT
        assert result.dimension == length_dimension

    def test_sets_name(self, length_dimension):
        # ARRANGE
        spec = make_spec("Distance", length_dimension)

        # ACT
        result = spec_to_domain(spec)

        # ASSERT
        assert result.__name__ == "Distance"
        assert result.name == "Distance[L]"

    def test_sets_module(self, dimension):
        # ARRANGE
        spec = make_spec("TestKind", dimension)

        # ACT
        result = spec_to_domain(spec)

        # ASSERT
        assert result.__module__ == mapper.__name__

    def test_without_parent_inherits_from_real_kind(self, dimension):
        # ARRANGE
        spec = make_spec("StandaloneKind", dimension)

        # ACT
        result = spec_to_domain(spec)

        # ASSERT
        assert result.__bases__ == (RealKind,)

    def test_inherits_from_parent_kind(self, dimension, fresh_registry):
        # ARRANGE
        parent_spec = make_spec("ParentKind", dimension)
        child_spec = make_spec(
            "ChildKind",
            dimension,
            inherits="ParentKind",
        )

        registry = KindRegistry()
        registry.register(parent_spec)
        registry.register(child_spec)

        # ACT
        parent = spec_to_domain(parent_spec)
        child = spec_to_domain(child_spec)

        # ASSERT
        assert child.__bases__ == (parent,)
        assert issubclass(child, parent)

    def test_missing_parent_raises_error(self, dimension, fresh_registry):
        # ARRANGE
        spec = make_spec("ChildKind", dimension, inherits="MissingKind")
        KindRegistry().register(spec)

        # ACT / ASSERT
        with pytest.raises(AttributeError):
            spec_to_domain(spec)

    def test_alias_returns_aliased_domain_kind(self, dimension, fresh_registry):
        # ARRANGE
        target_spec = make_spec("TargetKind", dimension)
        alias_spec = make_spec(
            "AliasKind",
            dimension,
            alias="TargetKind",
        )

        registry = KindRegistry()
        registry.register(target_spec)
        registry.register(alias_spec)

        # ACT
        result = spec_to_domain(alias_spec)
        target = spec_to_domain(target_spec)

        # ASSERT
        assert result is target

    def test_alias_does_not_create_separate_domain_kind(
        self, dimension, fresh_registry
    ):
        # ARRANGE
        target_spec = make_spec("TargetKind", dimension)
        alias_spec = make_spec("AliasKind", dimension, alias="TargetKind")

        registry = KindRegistry()
        registry.register(target_spec)
        registry.register(alias_spec)

        # ACT
        result = spec_to_domain(alias_spec)

        # ASSERT
        assert result.__name__ == "TargetKind"

    def test_missing_alias_raises_attribute_error(self, dimension, fresh_registry):
        # ARRANGE
        spec = make_spec("AliasKind", dimension, alias="MissingKind")
        KindRegistry().register(spec)

        # ACT / ASSERT
        with pytest.raises(
            AttributeError,
            match=r"'AliasKind' aliases 'MissingKind' which doesn't exist",
        ):
            spec_to_domain(spec)

    def test_alias_to_alias_resolves_transitively(self, dimension, fresh_registry):
        # ARRANGE
        target_spec = make_spec("TargetKind", dimension)
        middle_spec = make_spec("MiddleAlias", dimension, alias="TargetKind")
        outer_spec = make_spec("OuterAlias", dimension, alias="MiddleAlias")

        for spec in (target_spec, middle_spec, outer_spec):
            KindRegistry().register(spec)

        # ACT
        result = spec_to_domain(outer_spec)
        target = spec_to_domain(target_spec)

        # ASSERT
        assert result is target


class TestCaching:
    def test_same_spec_returns_same_class(self, dimension):
        # ARRANGE
        spec = make_spec("CachedKind", dimension)

        # ACT
        first = mapper.spec_to_domain(spec)
        second = mapper.spec_to_domain(spec)

        # ASSERT
        assert first is second

    def test_different_specs_create_different_classes(self, dimension):
        # ARRANGE
        first_spec = make_spec("FirstKind", dimension)
        second_spec = make_spec("SecondKind", dimension)

        # ACT
        first = mapper.spec_to_domain(first_spec)
        second = mapper.spec_to_domain(second_spec)

        # ASSERT
        assert first is not second

    def test_equal_specs_share_cached_class(self, dimension):
        # ARRANGE
        first_spec = make_spec("CachedKind", dimension)
        second_spec = make_spec("CachedKind", dimension)

        # ACT
        first = mapper.spec_to_domain(first_spec)
        second = mapper.spec_to_domain(second_spec)

        # ASSERT
        assert first is second

    def test_alias_resolution_is_cached(self, dimension, fresh_registry):
        # ARRANGE
        target_spec = make_spec("TargetKind", dimension)
        alias_spec = make_spec("AliasKind", dimension, alias="TargetKind")

        registry = KindRegistry()
        registry.register(target_spec)
        registry.register(alias_spec)

        # ACT
        first = mapper.spec_to_domain(alias_spec)
        second = mapper.spec_to_domain(alias_spec)

        # ASSERT
        assert first is second
        assert first.__name__ == "TargetKind"
