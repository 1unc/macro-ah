# Macro-ah

Halb-automatisches Hilfstool fuer das `/ah`-Listing auf HugoSMP.
Per Hotkey `Strg+Leertaste` gestartet. Du bleibst vor der Tastatur.

> **Disclaimer:** Dieses Tool ist fuer den Einsatz auf **HugoSMP mit ausdruecklicher Admin-Freigabe**
> entwickelt. Auf vielen Minecraft-Servern sind Makros / Automatisierungen durch die Server-Regeln
> oder AGB verboten und koennen zu Bans fuehren. **Du bist selbst dafuer verantwortlich**, dass dein
> Einsatz den Regeln des jeweiligen Servers entspricht. Kein Anspruch auf Funktion oder Regelkonformitaet
> — siehe Apache-2.0 LICENSE, Section 7 und 8.

## Inhalt

- [Was das Tool macht](#was-das-tool-macht)
- [Voraussetzungen](#voraussetzungen)
- [Installation: AutoHotKey v2](#installation-autohotkey-v2)
- [Installation: Python](#installation-python)
- [Kalibrierung (beide Versionen)](#kalibrierung-beide-versionen)
- [Benutzung: typischer Ablauf](#benutzung-typischer-ablauf)
- [Sicherheits-Features / Abbruch](#sicherheits-features--abbruch)
- [Troubleshooting](#troubleshooting)

---

## Was das Tool macht

1. Du legst einen Stack (z.B. 64 Buecher) in dein sonst leeres Inventar.
2. Du startest das Tool, gibst den Preis pro Item ein.
3. Du wechselst zu Minecraft, druckst `Strg+Leertaste`.
4. Das Tool oeffnet dein Inventar, splittet den Stack per vanilla Rechtsklick-Drag
   (1 Item pro leerem Slot) und legt den Rest in Slot 1 (oben-links) ab = **Opferslot**.
5. Das Tool oeffnet `/ah` und listet jeden Einzel-Slot zum eingegebenen Preis.
6. Der Opferslot bleibt im Inventar zurueck (wird nie verkauft).

---

## Voraussetzungen

- **Server-Admin-Freigabe** fuer Makros (hast du bestaetigt)
- Windows 10 oder 11
- Minecraft 1.21.x Fabric, auf HugoSMP
- **Fester GUI-Scale und feste Aufloesung** — bei Aenderung komplett neu kalibrieren
- Am besten Fenstermodus, damit du schnell zu Terminal / Dialog zurueckwechseln kannst

---

## Installation: AutoHotKey v2

### 1. AutoHotKey v2 installieren

1. Auf <https://www.autohotkey.com/> gehen
2. **„Download v2.0"** klicken (NICHT v1.1)
3. Installer ausfuehren, Standardpfad uebernehmen

### 2. Skript herunterladen / platzieren

Die Datei `ahk/macro_ah.ahk` in einem beliebigen Ordner ablegen.
Die Config-Datei `config.ini` wird beim ersten Start im gleichen Ordner angelegt.

### 3. Starten

Doppelklick auf `macro_ah.ahk`.

Beim ersten Start: Kalibrierung startet automatisch (siehe [unten](#kalibrierung-beide-versionen)).
Nach Kalibrierung fragt ein Dialog nach dem Preis.
Dann ist das Skript scharf: **Strg+Leertaste** in Minecraft = Macro startet.

### 4. Neu kalibrieren

`config.ini` loeschen → bei naechstem Start laeuft die Kalibrierung wieder.

### 5. Skript beenden

Rechtsklick auf das gruene H-Symbol im Tray → **Exit**.

---

## Installation: Python

### 1. Python installieren

1. Auf <https://www.python.org/downloads/> gehen
2. **Python 3.11** oder neuer herunterladen (3.10+ sollte funktionieren)
3. Installer starten. **WICHTIG**: Haken bei **„Add Python to PATH"** setzen
4. Installation abschliessen

Verifizieren im Terminal (PowerShell oder cmd):
```
python --version
```
Sollte `Python 3.11.x` oder aehnlich zeigen.

### 2. Abhaengigkeiten installieren

Im Projektordner `python/`:
```
cd python
pip install -e .
```

Das installiert das `macro-ah`-Paket inkl. `pyautogui`, `mss`, `Pillow`, `keyboard`, `pydantic`
und legt den Entry Point `macro-ah` an.

Optional (fuer Tests und Type-Checking):
```
pip install -e ".[dev]"
```

> **Hinweis:** Die `keyboard`-Bibliothek braucht auf Windows gelegentlich **Admin-Rechte**,
> um globale Hotkeys zu lesen. Falls der Hotkey nicht reagiert: Terminal als Administrator oeffnen
> und Skript von dort starten.

### 3. Starten

```
macro-ah
```

Alternativ als Modul:
```
python -m macro_ah
```

Beim ersten Start: Kalibrierung-Dialog oeffnet sich (siehe [unten](#kalibrierung-beide-versionen)).
Danach Preis-Dialog. Danach scharf: **Strg+Leertaste** in Minecraft.
Die `config.json` wird im aktuellen Arbeitsverzeichnis abgelegt.

### 4. Neu kalibrieren

Entweder Flag nutzen:
```
macro-ah --calibrate
```
oder `config.json` loeschen. Ueber `--config <pfad>` laesst sich auch ein anderer Pfad waehlen.

### 5. Tests ausfuehren

```
pytest
```

### 6. Skript beenden

Nach dem Lauf endet das Skript von selbst. Bei Abbruch mitten im Lauf: `Strg+C` im Terminal.

---

## Kalibrierung (beide Versionen)

Du klickst dich einmalig durch **acht Positionen**. Bei jedem Schritt:
1. Der Dialog zeigt die gesuchte Stelle (z.B. „/ah GUI: Button 'Auktion erstellen'")
2. Du bewegst die Maus zu dieser Stelle **im Minecraft-Fenster**
3. Du druckst **Leertaste** → Position gespeichert, naechster Schritt
4. Abbruch jederzeit mit **Esc**

**Vorbereitung:** Bevor du die Kalibrierung startest, bring Minecraft in die richtigen States:

| Schritt | Was du vorher machen musst                                    |
|---------|---------------------------------------------------------------|
| 1       | `/ah` offen, Hauptmenue mit „Auktion erstellen"-Button sichtbar |
| 2       | Auf „Auktion erstellen" geklickt, Inventar-Auswahl sichtbar    |
| 3       | wie 2                                                          |
| 4       | Im „Stueck auswaehlen"-Menue (klickst in Minecraft ein Item an) |
| 5       | Im Preis-Eingabe-Bildschirm                                    |
| 6       | Im finalen „Angebot erstellen"-Screen                          |
| 7       | `/ah` schliessen, normales Inventar mit **E** oeffnen          |
| 8       | wie 7                                                          |

> **Wichtig:** Zwischen den Schritten musst du Minecraft **manuell** in den jeweils naechsten State bringen.
> Das Tool klickt in der Kalibrierung nichts — es merkt sich nur deine Mausposition bei Leertaste.

Die acht Positionen:

1. `/ah` GUI: Button **„Auktion erstellen"**
2. `/ah` GUI: **Oberster linker Inventar-Slot** (im Inventar-Auswahl-Screen)
3. `/ah` GUI: **Unterer rechter Slot** (Hotbar ganz rechts, im Inventar-Auswahl-Screen)
4. `/ah` GUI: **Gruener Haken** im „Stueck auswaehlen"-Menue
5. `/ah` GUI: **Preis-Eingabefeld**
6. `/ah` GUI: Button **„Angebot erstellen"**
7. Normales Inventar (E): **Oberster linker Slot**
8. Normales Inventar (E): **Unterer rechter Hotbar-Slot**

Das Tool berechnet aus den beiden Grid-Eckpunkten (2+3 bzw. 7+8) automatisch das 9x4-Slot-Raster.

---

## Benutzung: typischer Ablauf

1. **Inventar vorbereiten:** Alles raus ausser **einem Stack** (z.B. 64 Enchanted Books).
   Lass **Slot 1 (oben-links) FREI**. Der wird Opferslot.
2. **Tool starten:**
   - AHK: Doppelklick auf `macro_ah.ahk`
   - Python: `python macro_ah.py`
3. **Preis eingeben**, z.B. `1.20`. OK.
4. **Zu Minecraft wechseln.** Nicht ins Inventar gehen, nicht in den Chat.
   Nur normale Spielansicht.
5. **Strg+Leertaste druecken.**
6. Das Tool laeuft:
   - Oeffnet Inventar (E)
   - Findet den Stack
   - Splittet ihn per Rechtsklick-Drag (1 Item pro leerem Slot)
   - Legt den Rest in Slot 1 ab (Opferslot)
   - Schliesst Inventar
   - Oeffnet `/ah` via Chat
   - Listet jeden Einzel-Slot fuer den Preis
7. Wenn fertig: ToolTip „Fertig." (bei AHK) bzw. Konsolenausgabe (Python).

**Zwischen zwei Laeufen:** Neuer Stack ins Inventar, Slot 1 wieder freimachen, Tool neu starten oder
(AHK: Tool laeuft weiter) neuen Preis im Tray-Menue setzen bzw. Skript neu laden.

---

## Sicherheits-Features / Abbruch

Waehrend der Ausfuehrung:

- **Maus mehr als 60px bewegen** → sofortiger Abbruch
- **Esc druecken** → sofortiger Abbruch
- (Python) **Maus in linke obere Bildschirmecke** → harter pyautogui-FailSafe-Abbruch

Nach Abbruch:
- Rechtsklick-Drag wird sauber beendet (Maustaste losgelassen)
- Du hast wahrscheinlich halb-gesplittete Slots und einen halb-vollen Cursor →
  im Inventar alles zurueck auf einen Slot sammeln, neu starten

---

## Troubleshooting

**„Kein Stack gefunden"**
- Ist Slot 1 wirklich leer?
- Liegt der Stack im Haupt-Inventar oder in der Hotbar (beides erlaubt)?
- Stimmt die Kalibrierung? Ist das Spiel im gleichen Fenstermodus wie bei der Kalibrierung?

**Hotkey reagiert nicht (nur Python)**
- Terminal als Administrator neu oeffnen, `python macro_ah.py` dort starten
- Pruefe, ob ein anderer Prozess `Strg+Leertaste` abfaengt (Windows IME, Tastatur-Tools)

**Klickt ins Leere / verfehlt Buttons**
- GUI-Scale im Minecraft-Optionen-Menue geaendert? → neu kalibrieren
- Aufloesung geaendert? → neu kalibrieren
- Fenstermodus gewechselt? → neu kalibrieren

**Items werden nicht als „leer" erkannt**
- Shader / Resource-Pack aktiv, das Slot-Hintergruende bunt macht?
  → im Python-Code `EMPTY_STDDEV_THRESHOLD` hoeher stellen,
     in AHK `EmptySpreadThresh` hoeher stellen
- Direkte Sonneneinstrahlung auf den Monitor (Scherz, aber trotzdem: Monitor-Helligkeit / Kontrast
  aendert die Pixel-Werte zwar nicht, aber HDR-Modi koennen reinspielen — HDR abschalten)

**Tool klickt zu schnell / GUI kommt nicht hinterher**
- Delays erhoehen: in Python `after`-Werte in `list_one` verdoppeln,
  in AHK die Argumente von `DoClick` verdoppeln

**AHK-Skript startet nicht**
- Rechtsklick auf `.ahk` → „Open with AutoHotKey" — funktioniert nur wenn v2 installiert ist
- Alternativ Rechtsklick → „Run Script"

**Preis-Format**
- Das Tool sendet das, was du im Dialog eingibst (Komma wird zu Punkt konvertiert).
- HugoSMP-AH-GUI akzeptiert Dezimalpunkt: `1.20` funktioniert.
- Falls es Komma braucht: im Quellcode den `.replace(",", ".")`-Schritt entfernen bzw. umdrehen.

---

## Dateien im Repo

```
Macro-ah/
├── ahk/
│   └── macro_ah.ahk                  AutoHotKey v2 Variante
├── python/
│   ├── pyproject.toml                Paket-Metadaten + Entry Point
│   ├── src/macro_ah/
│   │   ├── __init__.py
│   │   ├── __main__.py               CLI-Entry (macro-ah)
│   │   ├── config.py                 pydantic Config + JSON-Persistenz
│   │   ├── grid.py                   reine Slot-Grid-Mathematik
│   │   ├── safety.py                 AbortGuard (Esc + Mausbewegung)
│   │   └── automation.py             Kalibrierung, Split-/Listing-Phase
│   └── tests/
│       ├── test_config.py
│       └── test_grid.py
├── config.json.example               Vorlage fuer config.json
├── LICENSE                           Apache-2.0
├── README.md                         dieses Dokument
└── .gitignore
```
