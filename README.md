# ha_divera247 – DIVERA 24/7 für Home Assistant

[![Validate](https://github.com/joside/ha_divera247/actions/workflows/validate.yml/badge.svg)](https://github.com/joside/ha_divera247/actions/workflows/validate.yml)
[![Tests](https://github.com/joside/ha_divera247/actions/workflows/tests.yml/badge.svg)](https://github.com/joside/ha_divera247/actions/workflows/tests.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

> Inoffizielle Integration, nicht mit der DIVERA GmbH verbunden.

Diese Custom Integration bindet [DIVERA 24/7](https://www.divera247.com/) in Home Assistant ein.
Sie fragt regelmäßig den letzten Einsatz ab und stellt ihn als Sensor bereit.

## Installation

**Über HACS (empfohlen):** In HACS nach „Divera247 Integration“ suchen, herunterladen
und Home Assistant neu starten.

Falls die Integration in HACS (noch) nicht gefunden wird: über *⋮ → Benutzerdefinierte
Repositories* `https://github.com/joside/ha_divera247` als Typ „Integration“ hinzufügen,
danach wie oben herunterladen.

**Manuell:** Den Ordner `custom_components/ha_divera247` in dein `custom_components`-Verzeichnis
kopieren und Home Assistant neu starten.

## Einrichtung

*Einstellungen → Geräte & Dienste → Integration hinzufügen → „Divera247 Integration“*

- **Accesskey:** dein persönlicher oder Einheits-Accesskey aus der DIVERA-Web-App
  (Einstellungen → Debug → API). Er wird beim Einrichten geprüft.
- **Abfrageintervall:** in Sekunden (10–3600, Standard 60). Lässt sich später über
  „Konfigurieren“ ändern.

- **Gruppenfilter (optional, unter „Konfigurieren“):** Die Integration liest die Gruppen
  deiner Einheit aus DIVERA (`/api/v2/pull/all`) und zeigt sie als Auswahlliste mit Namen.
  Ausgewählte Gruppen schalten `Einsatz aktiv` ein, keine Auswahl = alle Alarme.
  Gefiltert wird auf das Alarmfeld `group`. Enthält es andere Nummern als die Liste
  (z. B. RIC-basierte IDs), können diese direkt ins Auswahlfeld getippt werden. Liefert
  DIVERA für deinen Accesskey keine Gruppen, erscheint stattdessen ein Textfeld für
  kommagetrennte IDs.

Wird der Accesskey ungültig, fordert Home Assistant automatisch zur Neuanmeldung auf.
Den Accesskey wechseln kannst du jederzeit über **⋮ → Neu konfigurieren** an der Integration,
ohne sie zu löschen. Fehlen Alarme, nimm den Einheits-Accesskey: Ein persönlicher
Accesskey sieht nur Alarme, bei denen du selbst alarmiert wurdest.

## Entitäten

| Entität | Inhalt |
|---|---|
| `sensor.divera247_letzter_einsatz` | Stichwort des letzten Einsatzes |
| `binary_sensor.divera247_einsatz_aktiv` | `an`, solange der letzte Einsatz offen und höchstens 60 Minuten alt ist. Fehlt ein auswertbarer Zeitstempel, gilt ein offener Einsatz als aktiv (lieber einmal zu viel als gar nicht alarmieren). |

Attribute Sensor: `id`, `text`, `address`, `latitude`, `longitude`, `priority`, `closed`, `groups`, `group_names`, `date`, `ts_update`.

Attribute Binärsensor: `id`, `title`, `groups`, `group_filter`, `matched_groups`, `matched_group_names`.

## Entwicklung

```bash
pip install -r requirements_test.txt
pytest
```

## Datenschutz

Der Accesskey wird nur in der Home-Assistant-Konfiguration gespeichert und ausschließlich
an `app.divera247.com` gesendet. Alarmtexte können personenbezogene Daten enthalten –
überlege, wo du sie anzeigen oder ansagen lässt.
