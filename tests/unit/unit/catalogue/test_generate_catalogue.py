from __future__ import annotations

import ast

from units_lib.unit.catalogue import generate_catalogue
from units_lib.unit.catalogue.catalogue_spec import (
    build_index,
    load_specs,
)


class TestRenderStub:
    def test_render_stub_declares_every_runtime_name_exactly_once(self):
        # Arrange
        expected = set(build_index(load_specs()))

        # Act
        tree = ast.parse(generate_catalogue.render_stub())
        declared = [
            node.target.id
            for node in tree.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        ]

        # Assert
        assert len(declared) == len(set(declared))
        assert set(declared) == expected

    def test_render_stub_annotates_affine_units_as_affine(self):
        # Arrange
        stub = generate_catalogue.render_stub()

        # Act
        lines = stub.splitlines()

        # Assert
        assert "degrees_celsius: AffineUnit[Temperature]" in lines


class TestMain:
    def test_main_check_returns_one_when_stub_is_missing(self, tmp_path, monkeypatch):
        # Arrange
        monkeypatch.setattr(
            generate_catalogue, "stub_path", lambda: tmp_path / "catalogue.pyi"
        )

        # Act
        status = generate_catalogue.main(["--check"])

        # Assert
        assert status == 1

    def test_main_check_returns_zero_after_generating(self, tmp_path, monkeypatch):
        # Arrange
        monkeypatch.setattr(
            generate_catalogue, "stub_path", lambda: tmp_path / "catalogue.pyi"
        )
        generate_catalogue.main([])

        # Act
        status = generate_catalogue.main(["--check"])

        # Assert
        assert status == 0
