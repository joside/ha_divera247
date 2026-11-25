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
