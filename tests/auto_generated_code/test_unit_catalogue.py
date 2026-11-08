from units_lib.unit.catalogue import generate_catalogue


def test_committed_stub_is_up_to_date():
    # Arrange / Act
    status = generate_catalogue.main(["--check"])

    # Assert
    assert status == 0
