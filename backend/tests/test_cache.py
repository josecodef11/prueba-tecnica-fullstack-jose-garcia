from cache import build_key


def test_build_key_is_stable_for_same_inputs():
    first = build_key("list", 1, 10, "2025-01-01", "2025-01-31")
    second = build_key("list", 1, 10, "2025-01-01", "2025-01-31")

    assert first == second
    assert first.startswith("events:")


def test_build_key_changes_when_inputs_change():
    base = build_key("detail", 10)
    changed = build_key("detail", 11)

    assert base != changed