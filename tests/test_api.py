"""Tests for parsing DIVERA API responses."""

from custom_components.ha_divera247.api import parse_groups


def test_groups_as_object():
    payload = {
        "success": True,
        "data": {
            "cluster": {
                "group": {
                    "177769": {"id": 177769, "name": "Maschinisten"},
                    "177768": {"id": 177768, "name": "Löschzug"},
                }
            }
        },
    }
    assert parse_groups(payload) == {"177768": "Löschzug", "177769": "Maschinisten"}


def test_groups_as_list_and_missing_names():
    payload = {"data": {"cluster": {"group": [{"id": 1, "name": "A"}, {"id": 2}]}}}
    assert parse_groups(payload) == {"1": "A", "2": "Gruppe 2"}


def test_groups_missing():
    assert parse_groups({"data": {}}) == {}
    assert parse_groups(None) == {}
