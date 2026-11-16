import pytest

from tests.helpers.registry import (
    clear_registry,
    get_registry_state,
    restore_registry_state,
)
from units_lib.kind.catalogue.spec_registry import KindRegistry


@pytest.fixture
def fresh_registry():
    original_state = get_registry_state()
    clear_registry()

    yield KindRegistry()

    restore_registry_state(original_state)
