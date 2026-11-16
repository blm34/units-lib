import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind.catalogue.catalogue_spec import KindSpec
from units_lib.kind.catalogue.spec_registry import KindRegistry


@pytest.fixture(autouse=True)
def registry(fresh_registry):
    yield KindRegistry()


@pytest.fixture
def length_dimension():
    return Dimension.base(BaseDimension.LENGTH)


@pytest.fixture
def time_dimension():
    return Dimension.base(BaseDimension.TIME)


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


class TestSingleton:
    def test_creates_single_instance(self):
        # ACT
        first = KindRegistry()
        second = KindRegistry()

        # ASSERT
        assert first is second

    def test_instance_is_shared_between_references(self, length_dimension):
        # ARRANGE
        first = KindRegistry()
        spec = make_spec("LengthKind", length_dimension)

        # ACT
        first.register(spec)
        second = KindRegistry()

        # ASSERT
        assert second.get("LengthKind") is spec

    def test_initializes_state_only_once(self, length_dimension):
        # ARRANGE
        first = KindRegistry()
        spec = make_spec("LengthKind", length_dimension)
        first.register(spec)

        # ACT
        second = KindRegistry()

        # ASSERT
        assert second.get("LengthKind") is spec
        assert second.kinds_for(length_dimension) == (spec,)


class TestInitialization:
    def test_initializes_empty_registry(self):
        # ACT
        result = KindRegistry()

        # ASSERT
        assert result.all_names() == ()
        assert result._kinds == {}
        assert result._by_dimension == {}
        assert result._defaults == {}

    def test_reinitialization_does_not_clear_existing_data(self, length_dimension):
        # ARRANGE
        instance = KindRegistry()
        spec = make_spec("LengthKind", length_dimension)
        instance.register(spec)

        # ACT
        instance.__init__()

        # ASSERT
        assert instance.get("LengthKind") is spec


class TestRegister:
    def test_registers_kind(self, registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)

        # ACT
        registry.register(spec)

        # ASSERT
        assert registry.get("LengthKind") is spec

    def test_registers_kind_name(self, registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)

        # ACT
        registry.register(spec)

        # ASSERT
        assert registry.all_names() == ("LengthKind",)

    def test_rejects_duplicate_name(self, registry, length_dimension):
        # ARRANGE
        first = make_spec("LengthKind", length_dimension)
        second = make_spec("LengthKind", length_dimension)
        registry.register(first)

        # ACT / ASSERT
        with pytest.raises(
            ValueError,
            match=r"Kind 'LengthKind' is already defined",
        ):
            registry.register(second)

    def test_duplicate_registration_preserves_original_spec(
        self, registry, length_dimension
    ):
        # ARRANGE
        first = make_spec("LengthKind", length_dimension)
        second = make_spec("LengthKind", length_dimension)
        registry.register(first)

        # ACT
        with pytest.raises(ValueError):
            registry.register(second)

        # ASSERT
        assert registry.get("LengthKind") is first

    def test_registers_multiple_kinds(self, registry, length_dimension):
        # ARRANGE
        first = make_spec("FirstKind", length_dimension)
        second = make_spec("SecondKind", length_dimension)

        # ACT
        registry.register(first)
        registry.register(second)

        # ASSERT
        assert registry.all_names() == ("FirstKind", "SecondKind")

    def test_rejects_second_default_for_same_dimension(
        self, registry, length_dimension
    ):
        # ARRANGE
        first = make_spec("FirstDefault", length_dimension, default=True)
        second = make_spec("SecondDefault", length_dimension, default=True)
        registry.register(first)

        # ACT / ASSERT
        with pytest.raises(
            TypeError,
            match="already the default",
        ):
            registry.register(second)

    def test_failed_second_default_is_not_registered(self, registry, length_dimension):
        # ARRANGE
        first = make_spec("FirstDefault", length_dimension, default=True)
        second = make_spec("SecondDefault", length_dimension, default=True)
        registry.register(first)

        # ACT
        with pytest.raises(TypeError):
            registry.register(second)

        # ASSERT
        assert registry.get("SecondDefault") is None
        assert registry.all_names() == ("FirstDefault",)
        assert registry.kinds_for(length_dimension) == (first,)

    def test_allows_defaults_for_different_dimensions(
        self, registry, length_dimension, time_dimension
    ):
        # ARRANGE
        length_default = make_spec("LengthDefault", length_dimension, default=True)
        time_default = make_spec("TimeDefault", time_dimension, default=True)

        # ACT
        registry.register(length_default)
        registry.register(time_default)

        # ASSERT
        assert registry.default_for(length_dimension) is length_default
        assert registry.default_for(time_dimension) is time_default


class TestGet:
    def test_returns_registered_spec(self, registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)
        registry.register(spec)

        # ACT
        result = registry.get("LengthKind")

        # ASSERT
        assert result is spec

    def test_returns_none_for_unknown_name(self, registry):
        # ACT
        result = registry.get("MissingKind")

        # ASSERT
        assert result is None


class TestAllNames:
    def test_returns_empty_tuple_for_empty_registry(self, registry):
        # ACT
        result = registry.all_names()

        # ASSERT
        assert result == ()

    def test_returns_names_in_registration_order(self, registry, length_dimension):
        # ARRANGE
        first = make_spec("FirstKind", length_dimension)
        second = make_spec("SecondKind", length_dimension)
        third = make_spec("ThirdKind", length_dimension)

        registry.register(first)
        registry.register(second)
        registry.register(third)

        # ACT
        result = registry.all_names()

        # ASSERT
        assert result == ("FirstKind", "SecondKind", "ThirdKind")


class TestKindsFor:
    def test_returns_kinds_for_dimension(self, registry, length_dimension):
        # ARRANGE
        first = make_spec("FirstLengthKind", length_dimension)
        second = make_spec("SecondLengthKind", length_dimension)
        registry.register(first)
        registry.register(second)

        # ACT
        result = registry.kinds_for(length_dimension)

        # ASSERT
        assert result == (first, second)

    def test_returns_empty_tuple_for_unknown_dimension(
        self, registry, length_dimension
    ):
        # ACT
        result = registry.kinds_for(length_dimension)

        # ASSERT
        assert result == ()

    def test_does_not_include_kinds_from_other_dimensions(
        self, registry, length_dimension, time_dimension
    ):
        # ARRANGE
        length_kind = make_spec("LengthKind", length_dimension)
        time_kind = make_spec("TimeKind", time_dimension)
        registry.register(length_kind)
        registry.register(time_kind)

        # ACT
        result = registry.kinds_for(length_dimension)

        # ASSERT
        assert result == (length_kind,)

    def test_returns_immutable_tuple(self, registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)
        registry.register(spec)

        # ACT
        result = registry.kinds_for(length_dimension)

        # ASSERT
        assert isinstance(result, tuple)


class TestDefaultFor:
    def test_returns_default_kind(self, registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthDefault", length_dimension, default=True)
        registry.register(spec)

        # ACT
        result = registry.default_for(length_dimension)

        # ASSERT
        assert result is spec

    def test_returns_none_when_no_default_exists(self, registry, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)
        registry.register(spec)

        # ACT
        result = registry.default_for(length_dimension)

        # ASSERT
        assert result is None

    def test_returns_none_for_unregistered_dimension(self, registry, length_dimension):
        # ACT
        result = registry.default_for(length_dimension)

        # ASSERT
        assert result is None

    def test_non_default_kind_does_not_replace_default(
        self, registry, length_dimension
    ):
        # ARRANGE
        default = make_spec("LengthDefault", length_dimension, default=True)
        non_default = make_spec("LengthKind", length_dimension)
        registry.register(default)

        # ACT
        registry.register(non_default)

        # ASSERT
        assert registry.default_for(length_dimension) is default
