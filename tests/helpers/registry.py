from collections import defaultdict

from units_lib.kind.catalogue.spec_registry import KindRegistry


def clear_registry() -> None:
    """Reset the singleton registry to its initial state."""
    KindRegistry._instance = None
    KindRegistry._loaded_toml = False


def get_registry_state():
    """Capture the singleton registry's current state."""
    instance = KindRegistry._instance

    if instance is None:
        return None

    return {
        "instance": instance,
        "kinds": instance._kinds.copy(),
        "by_dimension": {
            dimension: specs.copy()
            for dimension, specs in instance._by_dimension.items()
        },
        "defaults": instance._defaults.copy(),
        "initialised": instance._initialised,
        "loaded_toml": KindRegistry._loaded_toml,
    }


def restore_registry_state(state) -> None:
    """Restore a previously captured registry state."""
    if state is None:
        clear_registry()
        return

    instance = state["instance"]

    instance._kinds = state["kinds"]
    instance._by_dimension = defaultdict(
        list,
        state["by_dimension"],
    )
    instance._defaults = state["defaults"]
    instance._initialised = state["initialised"]

    KindRegistry._instance = instance
    KindRegistry._loaded_toml = state["loaded_toml"]
