import pytest

from units_lib.dimensions import BaseDimension, Dimension
from units_lib.kind.catalogue import generate_catalogue as generator
from units_lib.kind.catalogue.catalogue_spec import KindSpec
from units_lib.kind.catalogue.spec_registry import KindRegistry


def make_spec(
    name: str,
    dimension: Dimension,
    *,
    inherits: str | None = None,
    alias: str | None = None,
) -> KindSpec:
    return KindSpec(
        name=name,
        dimension=dimension,
        inherits=inherits,
        alias=alias,
    )


@pytest.fixture
def length_dimension():
    return Dimension.base(BaseDimension.LENGTH)


@pytest.fixture
def time_dimension():
    return Dimension.base(BaseDimension.TIME)


@pytest.fixture
def load_specs(fresh_registry, monkeypatch):
    monkeypatch.setattr(generator, "load_specs", lambda: fresh_registry)


class TestStubPath:
    def test_returns_catalogue_stub_path(self, monkeypatch, tmp_path):
        # ARRANGE
        catalogue_path = tmp_path / "catalogue.py"
        expected = tmp_path / "catalogue.pyi"

        monkeypatch.setattr(
            generator.catalogue,
            "__file__",
            str(catalogue_path),
        )

        # ACT
        result = generator.stub_path()

        # ASSERT
        assert result == expected


@pytest.mark.usefixtures("fresh_registry")
class TestRenderStub:
    def test_returns_header_for_empty_registry(self, load_specs):
        # ACT
        result = generator.render_stub()

        # ASSERT
        assert result == generator.HEADER + "\n"

    def test_generates_standalone_kind(self, load_specs, length_dimension):
        # ARRANGE
        spec = make_spec("LengthKind", length_dimension)
        registry = KindRegistry()
        registry.register(spec)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert "class LengthKind(RealKind): ..." in result

    def test_generates_inherited_kind(self, load_specs, length_dimension):
        # ARRANGE
        parent = make_spec("ParentKind", length_dimension)
        child = make_spec("ChildKind", length_dimension, inherits="ParentKind")

        registry = KindRegistry()
        registry.register(parent)
        registry.register(child)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert "class ParentKind(RealKind): ..." in result
        assert "class ChildKind(ParentKind): ..." in result

    def test_generates_alias(self, load_specs, length_dimension):
        # ARRANGE
        target = make_spec("TargetKind", length_dimension)
        alias = make_spec("AliasKind", length_dimension, alias="TargetKind")

        registry = KindRegistry()
        registry.register(target)
        registry.register(alias)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert "class TargetKind(RealKind): ..." in result
        assert "AliasKind = TargetKind" in result

    def test_generates_alias_target_before_alias(self, load_specs, length_dimension):
        # ARRANGE
        alias = make_spec("AliasKind", length_dimension, alias="TargetKind")
        target = make_spec("TargetKind", length_dimension)

        registry = KindRegistry()
        registry.register(alias)
        registry.register(target)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert result.index("class TargetKind") < result.index("AliasKind = TargetKind")

    def test_generates_parent_before_child(self, load_specs, length_dimension):
        # ARRANGE
        child = make_spec("ChildKind", length_dimension, inherits="ParentKind")
        parent = make_spec("ParentKind", length_dimension)

        registry = KindRegistry()
        registry.register(child)
        registry.register(parent)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert result.index("class ParentKind") < result.index("class ChildKind")

    def test_does_not_generate_same_kind_twice(self, load_specs, length_dimension):
        # ARRANGE
        parent = make_spec("ParentKind", length_dimension)
        child = make_spec("ChildKind", length_dimension, inherits="ParentKind")

        registry = KindRegistry()
        registry.register(child)
        registry.register(parent)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert result.count("class ParentKind") == 1

    def test_preserves_registry_order_for_unrelated_kinds(
        self, load_specs, length_dimension, time_dimension
    ):
        # ARRANGE
        first = make_spec("FirstKind", length_dimension)
        second = make_spec("SecondKind", time_dimension)

        registry = KindRegistry()
        registry.register(first)
        registry.register(second)

        # ACT
        result = generator.render_stub()

        # ASSERT
        assert result.index("class FirstKind") < result.index("class SecondKind")

    def test_calls_validate_with_loaded_registry(self, monkeypatch):
        # ARRANGE
        registry = KindRegistry()
        loaded = []
        validated = []

        def fake_load_specs():
            loaded.append(True)
            return registry

        def fake_validate(value):
            validated.append(value)

        monkeypatch.setattr(generator, "load_specs", fake_load_specs)
        monkeypatch.setattr(generator, "validate", fake_validate)

        # ACT
        generator.render_stub()

        # ASSERT
        assert loaded == [True]
        assert validated == [registry]

    def test_does_not_render_when_validation_fails(self, monkeypatch):
        # ARRANGE
        registry = KindRegistry()

        def fail_validation(value):
            raise ValueError("Invalid catalogue")

        monkeypatch.setattr(generator, "load_specs", lambda: registry)
        monkeypatch.setattr(generator, "validate", fail_validation)

        # ACT / ASSERT
        with pytest.raises(ValueError, match="Invalid catalogue"):
            generator.render_stub()


class TestMain:
    def test_writes_generated_stub(self, monkeypatch, tmp_path, capsys):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"
        expected_stub = "generated stub content"

        monkeypatch.setattr(generator, "stub_path", lambda: path)
        monkeypatch.setattr(generator, "render_stub", lambda: expected_stub)

        # ACT
        result = generator.main([])

        # ASSERT
        assert result == 0
        assert path.read_text(encoding="utf-8") == expected_stub

        captured = capsys.readouterr()
        assert captured.out == f"Wrote {path}\n"

    def test_check_returns_zero_when_stub_is_up_to_date(
        self, monkeypatch, tmp_path, capsys
    ):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"
        expected_stub = "generated stub content"
        path.write_text(expected_stub, encoding="utf-8")

        monkeypatch.setattr(generator, "stub_path", lambda: path)
        monkeypatch.setattr(generator, "render_stub", lambda: expected_stub)

        # ACT
        result = generator.main(["--check"])

        # ASSERT
        assert result == 0

        captured = capsys.readouterr()
        assert captured.out == f"{path} is up to date\n"

    def test_check_returns_one_when_stub_is_out_of_date(
        self, monkeypatch, tmp_path, capsys
    ):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"
        path.write_text("old content", encoding="utf-8")

        expected_stub = "new content"

        monkeypatch.setattr(generator, "stub_path", lambda: path)
        monkeypatch.setattr(generator, "render_stub", lambda: expected_stub)

        # ACT
        result = generator.main(["--check"])

        # ASSERT
        assert result == 1

        captured = capsys.readouterr()
        assert captured.out == (
            f"{path} is out of date; run `generate-kind-catalogue`\n"
        )

    def test_check_returns_one_when_stub_does_not_exist(
        self, monkeypatch, tmp_path, capsys
    ):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"
        expected_stub = "generated stub content"

        monkeypatch.setattr(generator, "stub_path", lambda: path)
        monkeypatch.setattr(generator, "render_stub", lambda: expected_stub)

        # ACT
        result = generator.main(["--check"])

        # ASSERT
        assert result == 1
        assert not path.exists()

        captured = capsys.readouterr()
        assert captured.out == (
            f"{path} is out of date; run `generate-kind-catalogue`\n"
        )

    def test_check_does_not_modify_existing_file(self, monkeypatch, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"
        original_content = "old content"
        path.write_text(original_content, encoding="utf-8")

        monkeypatch.setattr(generator, "stub_path", lambda: path)
        monkeypatch.setattr(generator, "render_stub", lambda: "new content")

        # ACT
        generator.main(["--check"])

        # ASSERT
        assert path.read_text(encoding="utf-8") == original_content

    def test_write_mode_overwrites_existing_file(self, monkeypatch, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"
        path.write_text("old content", encoding="utf-8")

        expected_stub = "new content"

        monkeypatch.setattr(generator, "stub_path", lambda: path)
        monkeypatch.setattr(generator, "render_stub", lambda: expected_stub)

        # ACT
        result = generator.main([])

        # ASSERT
        assert result == 0
        assert path.read_text(encoding="utf-8") == expected_stub

    def test_invalid_arguments_raise_system_exit(self):
        # ARRANGE
        argv = ["--unknown-option"]

        # ACT / ASSERT
        with pytest.raises(SystemExit) as exc_info:
            generator.main(argv)

        # ASSERT
        assert exc_info.value.code == 2

    def test_render_failure_does_not_write_file(self, monkeypatch, tmp_path):
        # ARRANGE
        path = tmp_path / "catalogue.pyi"

        monkeypatch.setattr(generator, "stub_path", lambda: path)

        def fail_render():
            raise ValueError("Invalid catalogue")

        monkeypatch.setattr(generator, "render_stub", fail_render)

        # ACT / ASSERT
        with pytest.raises(ValueError, match="Invalid catalogue"):
            generator.main([])

        # ASSERT
        assert not path.exists()


def test_renders_expected_stub(fresh_registry, load_specs, length_dimension):
    # ARRANGE
    registry = KindRegistry()
    registry.register(make_spec("LengthKind", length_dimension))
    registry.register(
        make_spec(
            "DistanceKind",
            length_dimension,
            inherits="LengthKind",
        )
    )
    registry.register(
        make_spec(
            "DistanceAlias",
            length_dimension,
            alias="DistanceKind",
        )
    )

    expected_body = """\
class LengthKind(RealKind): ...
class DistanceKind(LengthKind): ...

DistanceAlias = DistanceKind

"""

    expected = generator.HEADER + expected_body

    # ACT
    result = generator.render_stub()

    # ASSERT
    assert result == expected
