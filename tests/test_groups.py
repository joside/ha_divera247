"""Tests for the group filter helpers."""

from custom_components.ha_divera247.const import alarm_group_ids, parse_group_ids


def test_parse_group_ids():
    assert parse_group_ids("177768, 177769 177770;177771") == [
        "177768", "177769", "177770", "177771",
    ]
    assert parse_group_ids("") == []
    assert parse_group_ids(None) == []


def test_alarm_group_ids():
    assert alarm_group_ids({"group": [177771, 12]}) == ["12", "177771"]
    assert alarm_group_ids({"group": "177768"}) == ["177768"]
    assert alarm_group_ids({}) == []
    assert alarm_group_ids(None) == []
