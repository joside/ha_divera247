"""Constants for the DIVERA 24/7 integration."""

DOMAIN = "ha_divera247"

CONF_ACCESSKEY = "accesskey"

DEFAULT_SCAN_INTERVAL = 60  # seconds
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 3600

API_BASE_URL = "https://app.divera247.com/api"
API_LAST_ALARM = f"{API_BASE_URL}/last-alarm"

# An alarm counts as active for this many minutes unless it is closed earlier.
ACTIVE_ALARM_WINDOW = 60

# Optional filter: only alarms for these DIVERA group ids count as active.
CONF_GROUPS = "groups"


def parse_group_ids(value) -> list[str]:
    """Turn '177768, 177769 177770' (or a list) into ['177768', '177769', '177770']."""
    if not value:
        return []
    if isinstance(value, (list, tuple, set)):
        items = value
    else:
        items = str(value).replace(";", ",").replace(" ", ",").split(",")
    return sorted({str(item).strip() for item in items if str(item).strip()})


def alarm_group_ids(alarm: dict | None) -> list[str]:
    """Group ids of an alarm as strings (DIVERA sends a list of ints)."""
    if not alarm:
        return []
    return parse_group_ids(alarm.get("group"))
