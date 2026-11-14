from fractions import Fraction
from tomllib import TOMLDecodeError

import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind.catalogue import catalogue_spec
from units_lib.kind.catalogue.catalogue_spec import (
    KindSpec,
    _parse_entry,
    get_registry,
    load_specs,
    validate,
)
from units_lib.kind.catalogue.spec_registry import KindRegistry


class TestParseEntry:
    def test_parse_single_dimension(self):
        # ARRANGE
        name = "Length"
        entry = {"dimension": {"length": 1}}

        # ACT
        result = _parse_entry(name, entry)

        # ASSERT
        assert result == KindSpec(
            name="Length",
            dimension=Dimension.base(BaseDimension.LENGTH),
        )

    def test_parse_multiple_dimensions(self):
        # ARRANGE
        name = "Velocity"
        entry = {
            "dimension": {
                "length": 1,
                "time": -1,
            }
        }

        # ACT
        result = _parse_entry(name, entry)

        # ASSERT
        assert result.dimension == (
            Dimension.base(BaseDimension.LENGTH) / Dimension.base(BaseDimension.TIME)
        )

    def test_parse_fractional_exponents(self):
        # ARRANGE
        name = "TestKind"
        entry = {
            "dimension": {
                "length": Fraction(1, 2),
                "time": Fraction(-1, 3),
            }
        }

        # ACT
        result = _parse_entry(name, entry)

        # ASSERT
        assert result.dimension.exps[BaseDimension.LENGTH.index] == Fraction(1, 2)
        assert result.dimension.exps[BaseDimension.TIME.index] == Fraction(-1, 3)

    def test_parse_inherits(self):
        # ARRANGE
        name = "DerivedKind"
        entry = {
            "dimension": {"length": 1},
            "inherits": "Length",
        }

        # ACT
        result = _parse_entry(name, entry)

        # ASSERT
        assert result.inherits == "Length"

    def test_parse_alias(self):
        # ARRANGE
        name = "AlternativeKind"
        entry = {
            "dimension": {"length": 1},
            "alias": "Length",
        }

        # ACT
        result = _parse_entry(name, entry)

        # ASSERT
        assert result.alias == "Length"

    def test_parse_default(self):
        # ARRANGE
        name = "Length"
        entry = {
            "dimension": {"length": 1},
            "default": True,
        }

        # ACT
        result = _parse_entry(name, entry)

        # ASSERT
        assert result.default is True

    def test_default_is_false_when_not_specified(self):
        # ARRANGE
        entry = {"dimension": {"length": 1}}

        # ACT
        result = _parse_entry("Length", entry)

        # ASSERT
        assert result.default is False

    def test_missing_optional_keys_default_to_none(self):
        # ARRANGE
        entry = {"dimension": {"length": 1}}

        # ACT
        result = _parse_entry("Length", entry)

        # ASSERT
        assert result.inherits is None
        assert result.alias is None

    def test_empty_dimension_is_dimensionless(self):
        # ARRANGE
        entry = {"dimension": {}}

        # ACT
        result = _parse_entry("Dimensionless", entry)

        # ASSERT
        assert result.dimension == Dimension.dimensionless()

    def test_missing_dimension_raises_value_error(self):
        # ARRANGE
        entry = {"inherits": "Length"}

        # ACT
        with pytest.raises(ValueError) as error:
            _parse_entry("DerivedKind", entry)

        # ASSERT
        assert str(error.value) == ("DerivedKind: missing required key 'dimension'")

    def test_unknown_key_raises_value_error(self):
        # ARRANGE
        entry = {
            "dimension": {"length": 1},
            "unknown": True,
        }

        # ACT
        with pytest.raises(ValueError) as error:
            _parse_entry("Length", entry)

        # ASSERT
        assert str(error.value) == "Length: unknown keys ['unknown']"

    def test_multiple_unknown_keys_are_sorted(self):
        # ARRANGE
        entry = {
            "dimension": {"length": 1},
            "zebra": True,
            "apple": True,
        }

        # ACT
        with pytest.raises(ValueError) as error:
            _parse_entry("Length", entry)

        # ASSERT
        assert str(error.value) == "Length: unknown keys ['apple', 'zebra']"

    def test_cannot_specify_both_inherits_and_alias(self):
        # ARRANGE
        entry = {
            "dimension": {"length": 1},
            "inherits": "Length",
            "alias": "Distance",
        }

        # ACT
        with pytest.raises(ValueError) as error:
            _parse_entry("DerivedKind", entry)

        # ASSERT
        assert str(error.value) == (
            "DerivedKind: cannot inherit Length and alias Distance"
        )


@pytest.mark.usefixtures("fresh_registry")
class TestLoadSpecs:
    def test_load_single_kind(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length]
dimension = { length = 1 }
""",
            encoding="utf-8",
        )

        # ACT
        result = load_specs(path)

        # ASSERT
        spec = result.get("Length")
        assert spec is not None
        assert spec.name == "Length"
        assert spec.dimension == Dimension.base(BaseDimension.LENGTH)

    def test_load_multiple_kinds(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length]
dimension = { length = 1 }

[kind.Time]
dimension = { time = 1 }

[kind.Velocity]
dimension = { length = 1, time = -1 }
""",
            encoding="utf-8",
        )

        # ACT
        result = load_specs(path)

        # ASSERT
        assert result.get("Length") is not None
        assert result.get("Time") is not None
        assert result.get("Velocity") is not None

    def test_load_kind_with_inherits(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length]
dimension = { length = 1 }

[kind.Distance]
dimension = { length = 1 }
inherits = "Length"
""",
            encoding="utf-8",
        )

        # ACT
        result = load_specs(path)

        # ASSERT
        spec = result.get("Distance")
        assert spec is not None
        assert spec.inherits == "Length"

    def test_load_kind_with_alias(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length]
dimension = { length = 1 }

[kind.Distance]
dimension = { length = 1 }
alias = "Length"
""",
            encoding="utf-8",
        )

        # ACT
        result = load_specs(path)

        # ASSERT
        spec = result.get("Distance")
        assert spec is not None
        assert spec.alias == "Length"

    def test_load_kind_with_default(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length]
dimension = { length = 1 }
default = true
""",
            encoding="utf-8",
        )

        # ACT
        result = load_specs(path)

        # ASSERT
        spec = result.get("Length")
        assert spec is not None
        assert spec.default is True

    def test_load_empty_catalogue(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind]
""",
            encoding="utf-8",
        )

        # ACT
        result = load_specs(path)

        # ASSERT
        assert result.all_names() == ()

    def test_invalid_toml_raises_error(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length
dimension = { length = 1 }
""",
            encoding="utf-8",
        )

        # ACT & ASSERT
        with pytest.raises(TOMLDecodeError):
            load_specs(path)

    def test_invalid_entry_raises_value_error(self, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.toml"
        path.write_text(
            """
[kind.Length]
unknown = true
""",
            encoding="utf-8",
        )

        # ACT & ASSERT
        with pytest.raises(ValueError):
            load_specs(path)


class TestGetRegistry:
    def test_loads_specs_when_not_already_loaded(self, monkeypatch):
        # ARRANGE
        expected = object()
        monkeypatch.setattr(KindRegistry, "_loaded_toml", False)
        monkeypatch.setattr(catalogue_spec, "load_specs", lambda: expected)

        # ACT
        result = get_registry()

        # ASSERT
        assert result is expected
        assert KindRegistry._loaded_toml is True

    def test_does_not_reload_specs_when_already_loaded(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr(KindRegistry, "_loaded_toml", True)

        def unexpected_load():
            pytest.fail("load_specs should not be called")

        monkeypatch.setattr(catalogue_spec, "load_specs", unexpected_load)

        # ACT
        result = get_registry()

        # ASSERT
        assert isinstance(result, KindRegistry)


class TestValidate:
    @pytest.fixture
    def length_dimension(self):
        return Dimension.base(BaseDimension.LENGTH)

    @pytest.fixture
    def time_dimension(self):
        return Dimension.base(BaseDimension.TIME)

    @pytest.fixture
    def make_registry(self, fresh_registry):
        def factory(*specs):
            registry = KindRegistry()
            for spec in specs:
                registry.register(spec)
            return registry

        return factory

    def test_valid_standalone_kind(self, make_registry, length_dimension):
        # ARRANGE
        registry = make_registry(KindSpec("Length", length_dimension))

        # ACT
        result = validate(registry)

        # ASSERT
        assert result is None

    def test_valid_inheritance(self, make_registry, length_dimension):
        # ARRANGE
        registry = make_registry(
            KindSpec("Length", length_dimension),
            KindSpec("Distance", length_dimension, inherits="Length"),
        )

        # ACT
        result = validate(registry)

        # ASSERT
        assert result is None

    def test_valid_alias(self, make_registry, length_dimension):
        # ARRANGE
        registry = make_registry(
            KindSpec("Length", length_dimension),
            KindSpec("Distance", length_dimension, alias="Length"),
        )

        # ACT
        result = validate(registry)

        # ASSERT
        assert result is None

    def test_circular_inheritance_raises_value_error(
        self, make_registry, length_dimension
    ):
        # ARRANGE
        registry = make_registry(
            KindSpec("Length", length_dimension, inherits="Distance"),
            KindSpec("Distance", length_dimension, inherits="Length"),
        )

        # ACT
        with pytest.raises(ValueError) as error:
            validate(registry)

        # ASSERT
        assert str(error.value) == ("Circular kind definition involving 'Length'")

    def test_circular_alias_raises_value_error(self, make_registry, length_dimension):
        # ARRANGE
        registry = make_registry(
            KindSpec("Length", length_dimension, alias="Distance"),
            KindSpec("Distance", length_dimension, alias="Length"),
        )

        # ACT
        with pytest.raises(ValueError) as error:
            validate(registry)

        # ASSERT
        assert "Circular kind definition involving" in str(error.value)

    def test_missing_inherited_kind_raises_value_error(
        self, make_registry, length_dimension
    ):
        # ARRANGE
        registry = make_registry(
            KindSpec("Distance", length_dimension, inherits="Length"),
        )

        # ACT
        with pytest.raises(ValueError) as error:
            validate(registry)

        # ASSERT
        assert str(error.value) == "Kind 'Length' doesn't exist"

    def test_missing_aliased_kind_raises_value_error(
        self, make_registry, length_dimension
    ):
        # ARRANGE
        registry = make_registry(
            KindSpec("Distance", length_dimension, alias="Length"),
        )

        # ACT
        with pytest.raises(ValueError) as error:
            validate(registry)

        # ASSERT
        assert str(error.value) == "Kind 'Length' doesn't exist"

    def test_inherited_kinds_must_have_matching_dimensions(
        self, make_registry, length_dimension, time_dimension
    ):
        # ARRANGE
        registry = make_registry(
            KindSpec("Length", length_dimension),
            KindSpec("Time", time_dimension, inherits="Length"),
        )

        # ACT
        with pytest.raises(ValueError) as error:
            validate(registry)

        # ASSERT
        assert str(error.value) == (
            "'Time' and 'Length' are linked by 'inherits' but have different "
            "dimensions (T and L)"
        )

    def test_aliased_kinds_must_have_matching_dimensions(
        self, make_registry, length_dimension, time_dimension
    ):
        # ARRANGE
        registry = make_registry(
            KindSpec("Length", length_dimension),
            KindSpec("Time", time_dimension, alias="Length"),
        )

        # ACT
        with pytest.raises(ValueError) as error:
            validate(registry)

        # ASSERT
        assert str(error.value) == (
            "'Time' and 'Length' are linked by 'alias' but have different "
            f"dimensions ({time_dimension} and {length_dimension})"
        )
