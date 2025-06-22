# ha_divera247 Home Assistant Custom Component

This custom component integrates [DIVERA 24/7](https://www.divera247.com/) with Home Assistant.  
It provides a sensor that checks for active alarms and displays their details.

## Installation

1. Copy the `custom_components/ha_divera247` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
ha_divera247:
  accesskey: YOUR_ACCESSKEY
  scan_interval: 60  # Optional, interval in seconds (default: 60)
```

- `accesskey`: Your personal API access key from divera247.
- `scan_interval`: (Optional) How often the API should be polled (in seconds).

## Sensor

After setup, a sensor named `sensor.divera247_letzter_einsatz` will be available.  
It shows the title of the last alarm and provides additional attributes like `id`, `details`, and `timestamp`.

---

# ha_divera247 Home Assistant Custom Component (Deutsch)

Diese Custom Component integriert [DIVERA 24/7](https://www.divera247.com/) in Home Assistant.  
Sie stellt einen Sensor bereit, der auf aktive Einsätze prüft und deren Details anzeigt.

## Installation

1. Kopiere den Ordner `custom_components/ha_divera247` in dein Home Assistant `custom_components` Verzeichnis.
2. Starte Home Assistant neu.

## Konfiguration

Füge Folgendes zu deiner `configuration.yaml` hinzu:

```yaml
ha_divera247:
  accesskey: DEIN_ACCESSKEY
  scan_interval: 60  # Optional, Intervall in Sekunden (Standard: 60)
```

- `accesskey`: Dein persönlicher API Accesskey von divera247.
- `scan_interval`: (Optional) Wie oft die API abgefragt werden soll (in Sekunden).

## Sensor

Nach der Einrichtung steht ein Sensor mit dem Namen `sensor.divera247_letzter_einsatz` zur Verfügung.  
Er zeigt den Titel des letzten Einsatzes und weitere Attribute wie `id`, `details` und `timestamp`.