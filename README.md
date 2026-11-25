# ha_divera247 – DIVERA 24/7 für Home Assistant

Diese Custom Integration bindet [DIVERA 24/7](https://www.divera247.com/) in Home Assistant ein.
Sie fragt regelmäßig den letzten Einsatz ab und stellt ihn als Sensor bereit.

## Installation

**Über HACS (empfohlen):** Dieses Repository in HACS als benutzerdefiniertes Repository
(Typ „Integration“) hinzufügen, „Divera247 Integration“ installieren und Home Assistant neu starten.

**Manuell:** Den Ordner `custom_components/ha_divera247` in dein `custom_components`-Verzeichnis
kopieren und Home Assistant neu starten.

## Einrichtung

*Einstellungen → Geräte & Dienste → Integration hinzufügen → „Divera247 Integration“*

- **Accesskey:** dein persönlicher oder Einheits-Accesskey aus der DIVERA-Web-App
  (Einstellungen → Debug → API). Er wird beim Einrichten geprüft.
- **Abfrageintervall:** in Sekunden (10–3600, Standard 60). Lässt sich später über
  „Konfigurieren“ ändern.

- **Gruppenfilter (optional, unter „Konfigurieren“):** kommagetrennte DIVERA-Gruppen-IDs,
  z. B. `177768, 177769, 177770`. Dann schaltet `Einsatz aktiv` nur bei Alarmen für diese
  Gruppen ein. Leer = alle Alarme.

Wird der Accesskey ungültig, fordert Home Assistant automatisch zur Neuanmeldung auf.

## Entitäten

| Entität | Inhalt |
|---|---|
| `sensor.divera247_letzter_einsatz` | Stichwort des letzten Einsatzes |
| `binary_sensor.divera247_einsatz_aktiv` | `an`, solange der letzte Einsatz offen und höchstens 60 Minuten alt ist |

Attribute Sensor: `id`, `text`, `address`, `latitude`, `longitude`, `priority`, `closed`, `groups`, `date`, `ts_update`.

Attribute Binärsensor: `id`, `title`, `groups`, `group_filter`, `matched_groups`.

## Entwicklung

```bash
pip install -r requirements_test.txt
pytest
```
