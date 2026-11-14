import pytest

import units_lib.kind.catalogue.catalogue as kind_module
from units_lib.dimensions import Dimension
from units_lib.kind.operations import kinds_for


class TestDynamicallyCreatedKinds:
    def test_standard_kind_has_dimension_instance(self, standard_kind):
        # Act
        dim = standard_kind.dimension

        # Assert
        assert isinstance(dim, Dimension)

    def test_standard_kind_name_starts_with_class_name(self, standard_kind):
        # Arrange
        expected = standard_kind.__name__

        # Act
        actual = standard_kind.name

        # Assert
        assert actual.startswith(expected)

    def test_standard_kind_is_registered_exactly_once(self, standard_kind):
        # Arrange
        dim = standard_kind.dimension

        # Act
        registered = kinds_for(dim)

        # Assert
        assert registered.count(standard_kind) == 1

    def test_standard_kind_shares_dimension_with_every_kind_ancestor(
        self, standard_kind, standard_kinds
    ):
        # Arrange
        ancestors = [
            other for other in standard_kinds if issubclass(standard_kind, other)
        ]

        # Act
        mismatched = [
            base for base in ancestors if base.dimension != standard_kind.dimension
        ]

        # Assert
        assert len(mismatched) == 0


class TestGetAttr:
    def test_getattr_returns_registered_kind(self, standard_kind, monkeypatch):
        # ARRANGE
        name = standard_kind.__name__

        # Ensure the attribute isn't already cached in module globals.
        monkeypatch.delitem(kind_module.__dict__, name, raising=False)

        # ACT
        result = getattr(kind_module, name)

        # ASSERT
        assert result is standard_kind

    def test_getattr_caches_resolved_kind(self, standard_kind, monkeypatch):
        # ARRANGE
        name = standard_kind.__name__
        monkeypatch.delitem(kind_module.__dict__, name, raising=False)

        # ACT
        first = getattr(kind_module, name)
        second = getattr(kind_module, name)

        # ASSERT
        assert first is second
        assert kind_module.__dict__[name] is standard_kind

    def test_getattr_unknown_name_raises_attribute_error(self):
        # ARRANGE
        name = "UnknownKind"

        # ACT
        with pytest.raises(AttributeError) as error:
            getattr(kind_module, name)

        # ASSERT
        assert str(error.value) == (
            f"module {kind_module.__name__!r} has no attribute 'UnknownKind'"
        )


class TestDir:
    def test_dir_includes_registered_kind_names(self, standard_kinds):
        # ARRANGE
        expected = {kind.__name__ for kind in standard_kinds}

        # ACT
        result = dir(kind_module)

        # ASSERT
        assert expected.issubset(set(result))

    def test_dir_includes_module_globals(self):
        # ARRANGE
        expected = set(kind_module.__dict__)

        # ACT
        result = dir(kind_module)

        # ASSERT
        assert expected.issubset(set(result))

    def test_dir_returns_sorted_names(self):
        # ACT
        result = dir(kind_module)

        # ASSERT
        assert result == sorted(result)

    def test_dir_does_not_contain_duplicate_names(self):
        # ACT
        result = dir(kind_module)

        # ASSERT
        assert len(result) == len(set(result))
