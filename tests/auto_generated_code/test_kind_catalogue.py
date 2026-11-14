from units_lib.kind.catalogue import generate_catalogue
from units_lib.kind.catalogue.catalogue_spec import get_registry, validate


def test_committed_stub_is_up_to_date(fresh_registry):
    # Arrange / Act
    status = generate_catalogue.main(["--check"])

    # Assert
    assert status == 0


def test_toml_contains_valid_definition(fresh_registry):
    # Arrange
    registry = get_registry()

    # Act
    validate(registry)
