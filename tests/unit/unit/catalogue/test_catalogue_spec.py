from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from units_lib import kind
from units_lib.unit.catalogue.catalogue_spec import (
    UnitSpec,
    build_index,
    load_specs,
)

SINGLE_PREFIX = """\
[defaults]
min_prefix = "NONE"
max_prefix = "NONE"
"""


def write_toml(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "catalogue.toml"
    path.write_text(body, encoding="utf-8")
    return path


class TestLoadSpecs:
    def test_load_specs_parses_kind_scale_and_offset(self, tmp_path):
        # Arrange
        path = write_toml(
            tmp_path,
            SINGLE_PREFIX
            + """
[[unit]]
name = "degrees celsius"
symbol = "C"
kind = "Temperature"
scale = "1/2"
offset = "27315/100"
""",
        )

        # Act
        specs = load_specs(path)

        # Assert
        spec = specs["degrees_celsius"]
        assert spec.kind.name == "Temperature"
        assert spec.scale == Fraction(1, 2)
        assert spec.offset == Fraction(27315, 100)
        assert spec.is_affine

    def test_load_specs_applies_default_prefix_range_when_not_overridden(
        self, tmp_path
    ):
        # Arrange
        path = write_toml(
            tmp_path,
            """
[defaults]
min_prefix = "MILLI"
max_prefix = "KILO"

[[unit]]
name = "second"
symbol = "s"
kind = "Time"
""",
        )

        # Act
        spec = load_specs(path)["second"]

        # Assert
        assert spec.min_prefix == "MILLI"
        assert spec.max_prefix == "KILO"

    @pytest.mark.parametrize(
        ("body", "message", "error"),
        [
            (
                'name = "x"\nsymbol = "x"\nkind = "Length"\nmin_prefix = "BOGUS"\n',
                "Unknown SI prefix",
                ValueError,
            ),
            (
                'name = "x"\nsymbol = "x"\nkind = "Length"\nmin_prefix = "_registry"\n',
                "not an SI prefix",
                TypeError,
            ),
            (
                'name = "x"\nsymbol = "x"\nkind = "Other"\n',
                "Unknown unit kind",
                ValueError,
            ),
            (
                'name = "x"\nsymbol = "x"\nkind = "Dimension"\n',
                "not a kind of unit",
                TypeError,
            ),
            (
                'name = "x"\nsymbol = "x"\nkind = "Mass"\nscale = 0.5\n',
                "expected an int or a fraction",
                TypeError,
            ),
            (
                'name = "x"\nsymbol = "x"\nkind = "Mass"\nscale = "1/2/3"\n',
                "invalid fraction",
                ValueError,
            ),
            (
                'name = "x"\nsymbol = "x"\nkind = "Length"\ncolour = "red"\n',
                "unknown keys",
                ValueError,
            ),
            (
                'name = "x"\nsymbol = "x"\n',
                "missing required key",
                ValueError,
            ),
            (
                'name = "x"\nkind = "Mass"\n',
                "missing required key",
                ValueError,
            ),
            (
                'symbol = "x"\nkind = "Mass"\n',
                "missing required key",
                ValueError,
            ),
        ],
    )
    def test_load_specs_raises_for_invalid_entries(
        self, tmp_path, body, message, error
    ):
        # Arrange
        path = write_toml(tmp_path, SINGLE_PREFIX + "\n[[unit]]\n" + body)

        # Act / Assert
        with pytest.raises(error, match=message):
            load_specs(path)

    def test_load_specs_raises_for_duplicate_unit_names(self, tmp_path):
        # Arrange
        entry = '\n[[unit]]\nname = "second"\nsymbol = "s"\nkind = "Time"\n'
        path = write_toml(tmp_path, SINGLE_PREFIX + entry + entry)

        # Act / Assert
        with pytest.raises(ValueError, match="defined more than once"):
            load_specs(path)

    def test_load_specs_loads_the_packaged_catalogue(self):
        # Arrange / Act
        specs = load_specs()

        # Assert
        assert "meter" in specs
        assert "newton" in specs


class TestBuildIndex:
    def test_build_index_prefixes_names_and_replaces_spaces(self):
        # Arrange
        specs = {
            "degrees_celsius": UnitSpec(
                name="degrees celsius",
                symbol="C",
                kind=kind.Temperature,
                min_prefix="NONE",
                max_prefix="KILO",
            ),
        }

        # Act
        index = build_index(specs)

        # Assert
        assert "degrees_celsius" in index
        assert "kilodegrees_celsius" in index
        assert " " not in "".join(index)

    def test_build_index_respects_the_prefix_range(self):
        # Arrange
        specs = {
            "second": UnitSpec(
                name="second",
                symbol="s",
                kind=kind.Time,
                min_prefix="NONE",
                max_prefix="KILO",
            ),
        }

        # Act
        index = build_index(specs)

        # Assert
        assert "kilosecond" in index
        assert "millisecond" not in index
        assert "megasecond" not in index

    def test_build_index_raises_when_two_units_produce_the_same_name(self):
        # Arrange
        specs = {
            "gram": UnitSpec(
                name="gram",
                symbol="g",
                kind=kind.Mass,
                min_prefix="NONE",
                max_prefix="KILO",
            ),
            "kilogram": UnitSpec(
                name="kilogram",
                symbol="kg",
                kind=kind.Mass,
                min_prefix="NONE",
                max_prefix="NONE",
            ),
        }

        # Act / Assert
        with pytest.raises(ValueError, match="produced by both"):
            build_index(specs)
