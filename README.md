# bsefi2326_klima_projekt_api

# Dokumentation: Flask-basierte Temperatur-API

## Einleitung
Diese Flask-Anwendung stellt eine REST-API zur Verfügung, die Temperaturwerte in einer SQLite-Datenbank speichert, ausliest und als JSON zurückgibt. Zudem können Temperaturwerte simuliert werden.

---

## Voraussetzungen
- **Python-Pakete:**
  - `flask` (Web-Framework für die API)
  - `flask_cors` (CORS-Unterstützung für externe Anfragen)
  - `sqlite3` (Datenbankanbindung)
  - `time` (Zeitstempelgenerierung)
  - `random` (Zufallsgenerierung für simulierte Werte)


## Setup
```python
from flask import Flask, jsonify, request, g
from flask_cors import CORS, cross_origin
import time
import random
import sqlite3
```
- `Flask`: Hauptmodul für die API
- `CORS`: Ermöglicht Cross-Origin-Requests
- `sqlite3`: Zugriff auf die SQLite-Datenbank
- `time`: Zeitstempel für Datenbankeinträge
- `random`: Generierung zufälliger Temperaturwerte (Simulation)

---

## Initialisierung der App
```python
app = Flask(__name__)
CORS(app, support_credentials=True)

database = "database.db"
```
- Erstellt eine Flask-App-Instanz
- Aktiviert CORS für externe Anfragen
- Definiert den Namen der SQLite-Datenbank

---

## Datenbankverbindung
```python
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    return db
```
- Erstellt eine Datenbankverbindung pro Anfrage
- Nutzt Flask's `g`-Objekt für den Zugriff

```python
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
```
- Schließt die Datenbankverbindung nach Abschluss der Anfrage

---

## API-Endpunkte

### Startseite
```python
@app.route("/")
def page_index():
    return "Hier gibt es nichts zu sehen..."
```
- Gibt eine einfache Textnachricht zurück

### Aktuelle Temperatur abrufen
```python
@app.route("/api/temp/get")
@cross_origin(supports_credentials=True)
def api_get_current_temp():
    cursor = get_db().cursor()
    currentTemp = cursor.execute("SELECT timestamp, value FROM temp ORDER BY timestamp DESC LIMIT 1").fetchone()
    if currentTemp == None:
        return jsonify({ 'status': False, 'error': 'Aktuell gibt es keine Werte in der Datenbank.' }), 400
    return jsonify({ 'timestamp': currentTemp[0], 'value': currentTemp[1] })
```
- Holt den zuletzt gespeicherten Temperaturwert aus der Datenbank
- Falls keine Werte vorhanden sind, wird ein Fehler zurückgegeben

### Temperaturwert einfügen
```python
@app.route("/api/temp/insert", methods=['POST'])
@cross_origin(supports_credentials=True)
def api_insert_temp():
    temp = None
    try:
        temp = float(request.get_json()['value'])
    except:
        temp = None

    if temp is None:
        return jsonify({ 'status': False, 'error': 'Im Request muss { \"value\": \"19.9\" } enthalten sein.' }), 400

    db = get_db()
    db.cursor().execute("INSERT INTO temp (timestamp, value) VALUES (?, ?)", (int(time.time()), temp))
    db.commit()
    return jsonify({ 'result': temp })
```
- Erwartet eine JSON-Nachricht mit einem `value`-Schlüssel
- Speichert den Temperaturwert in der Datenbank
- Gibt den gespeicherten Wert zurück

### Temperaturverlauf abrufen
```python
@app.route("/api/chart/get", methods=['GET'])
@cross_origin(supports_credentials=True)
def api_get_chart_data():
    days = request.args.get('days', default=1, type=int)
    currentTimestamp = int(time.time())
    minTimestamp = int(currentTimestamp - (days * 24 * 60 * 60))

    # Simulation von Temperaturwerten steht unten!

    db = get_db()
    db.row_factory = sqlite3.Row
    rows = db.cursor().execute(f"SELECT timestamp, value FROM temp WHERE timestamp >= { minTimestamp }").fetchall()

    return jsonify([dict(ix) for ix in rows])
```
- Berechnet das Startdatum basierend auf dem Parameter `days`
- Holt Temperaturwerte aus der Datenbank für den gewünschten Zeitraum
- Konvertiert die Ergebnisse in JSON

#### Simulation von Temperaturwerten
```python
    simulate = request.args.get("simulate", default=None, type=bool)
    if simulate == True:
        simValues = []
        for i in range(days * 24 * 60 * 60):
            timestamp = currentTimestamp - i
            value = 0

            if i == 0:
                value = round(random.uniform(15.0, 25.0), 2)
            else:
                value = round(random.uniform(simValues[i - 1]['value'] - 0.25, simValues[i - 1]['value'] + 0.25), 2)
                if value > 25.0:
                    value -= value - 25.0
                elif value < 10.0:
                    value += 10.0 - value
            
            simValues.insert(0, { 'timestamp': timestamp, 'value': value })
        return jsonify(simValues)
```
- Falls `simulate=True`, werden zufällige Temperaturwerte generiert und zurückgegeben

## Start des Servers
```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```
- Startet die Flask-Anwendung auf Port 5000
- `debug=True` aktiviert den Debug-Modus
- `host="0.0.0.0"` ermöglicht den Zugriff von anderen Geräten

---

## Funktionen
Diese Flask-API bietet folgende Funktionen:
- Speichern von Temperaturwerten
- Abrufen der aktuellen Temperatur
- Abrufen historischer Temperaturwerte (inkl. Simulation)
- Nutzung von SQLite zur Speicherung der Daten
- Unterstützung von CORS für externe Zugriffe

Die API eignet sich für IoT-Projekte zur Temperaturüberwachung oder zur Datenanalyse historischer Messwerte.


# Dokumentation: SQLite-Datenbankeinrichtung

## Einleitung
Dieses Skript erstellt eine SQLite-Datenbank und eine Tabelle zur Speicherung von Temperaturwerten. Es stellt sicher, dass die Tabelle nur erstellt wird, falls sie noch nicht existiert.

---

## Voraussetzungen
- **Python-Pakete:**
  - `sqlite3`: Standardmodul zur Interaktion mit SQLite-Datenbanken

## Code-Erklärung
### Datenbankverbindung herstellen
```python
import sqlite3

connection = sqlite3.connect("../database.db")
print(connection.total_changes)
```
- Erstellt eine Verbindung zur SQLite-Datenbank `database.db`
- Falls die Datei nicht existiert, wird sie automatisch erstellt
- Gibt die Anzahl der Änderungen in der Datenbank aus (`total_changes`)

### Tabelle erstellen
```python
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS temp (id INTEGER PRIMARY KEY NOT NULL, timestamp INTEGER, value REAL)")
```
- Erstellt ein Cursor-Objekt für die Datenbankinteraktion
- Führt eine SQL-Anweisung aus, um die Tabelle `temp` zu erstellen, falls sie noch nicht existiert
- **Tabellenstruktur:**
  - `id`: Primärschlüssel (automatisch inkrementiert)
  - `timestamp`: Speichert den Zeitstempel der Messung
  - `value`: Speichert den Temperaturwert als Gleitkommazahl

### Verbindung schließen
```python
connection.close()
```
- Schließt die Datenbankverbindung, um Speicher freizugeben und Daten zu sichern

---


# Dokumentation: SQLite-Datenbank mit Zufallswerten füllen

## Einleitung
Dieses Skript generiert zufällige Temperaturwerte über einen Zeitraum von 30 Tagen und speichert diese in einer SQLite-Datenbank. Die Werte werden in einem festgelegten Intervall in die Tabelle `temp` eingefügt.

---

## Voraussetzungen
- **Python-Pakete:**
  - `sqlite3`: Datenbankanbindung
  - `time`: Zeitstempelberechnungen
  - `random`: Generierung zufälliger Werte

## Code-Erklärung
### Datenbankverbindung herstellen
```python
import sqlite3
import time
import random

connection = sqlite3.connect("../database.db")
print(connection.total_changes)
cursor = connection.cursor()
```
- Erstellt eine Verbindung zur SQLite-Datenbank `database.db`
- Gibt die Anzahl der bisherigen Änderungen in der Datenbank aus

### Parameter festlegen
```python
days = 30
probeIntervall = 1 # <- in Sekunden
amountOfValues = int((days * 24 * 60 * 60) / probeIntervall)
```
- Legt die Anzahl der Tage und das Messintervall fest
- Berechnet die Gesamtanzahl der zu speichernden Werte

### Zufallswerte generieren
```python
currentTimestamp = int(time.time())
oldValue = round(random.uniform(15.0, 30.0), 2)

print(f"Es werden {amountOfValues} Werte erstellt, mit einem Intervall von {probeIntervall} Sekunden.")
```
- Ermittelt den aktuellen Zeitstempel
- Setzt einen Startwert zwischen 15.0 und 30.0 Grad Celsius

### Werte in die Datenbank schreiben
```python
for i in range(amountOfValues):
    timestamp = currentTimestamp - (i * probeIntervall)
    value = round(random.uniform(oldValue - random.uniform(1.0, 2.5), oldValue + random.uniform(1.0, 2.5)), 2)
    
    if value > 30.0:
        value -= value - 30.0
    elif value < 10.0:
        value += 10.0 - value

    cursor.execute("INSERT INTO temp (timestamp, value) VALUES (?, ?)", (timestamp, value))
```
- Berechnet den Zeitstempel für jeden Wert
- Generiert eine neue Temperatur basierend auf dem vorherigen Wert mit einer zufälligen Abweichung
- Begrenzung der Werte auf den Bereich 10.0 - 30.0 Grad Celsius
- Speichert die Werte in der Datenbank

### Daten speichern und Verbindung schließen
```python
connection.commit()
connection.close()
```
- Bestätigt die Änderungen in der Datenbank
- Schließt die Verbindung zur Datenbank

---

## Fazit
Dieses Skript erzeugt eine realistische Simulation von Temperaturveränderungen über einen längeren Zeitraum und speichert diese in einer SQLite-Datenbank.


## GET /api/temp/get

Dieser Endpunkt wird zum Abrufen von Temperaturdaten verwendet.
### Request
Für diesen Endpunkt ist kein Request Body erforderlich.

### Response

Status: 200

Content-Type: application/json
```json
{
    "timestamp": 0,
    "value": 0
}
```

Die Antwort enthält die Temperaturdaten in dem Feld „Ergebnis“.


## POST /api/temp/insert

Dieser Endpunkt wird zum Einfügen von Temperaturdaten verwendet.
### Request
Body (raw, application/json)
* value: (number) Der Temperaturwert, der eingefügt werden soll.



### Response

Die Antwort auf diese Anfrage ist ein leeres JSON-Objekt.

Content-Type: application/json
```json
{
    "result": ""
}
```


## GET /api/chart/get

Dieser Endpunkt ruft Diagrammdaten für eine bestimmte Anzahl von Tagen ab und kann die Daten bei Bedarf simulieren.
### Request
days (integer) - Die Anzahl der Tage, für die die Diagrammdaten angefordert werden.
simulate (boolean) - Gibt an, ob die Daten simuliert werden sollen.

### Response

Die Antwort ist ein JSON-Array mit Objekten, die die folgenden Felder enthalten:
* timestamp (number) - Der Zeitstempel des Datenpunkts.
* value (number) - Der Wert des Datenpunktes.



Content-Type: application/json
```json
[
    { "timestamp": 0, "value": 0 }
]
```

### JSON Schema
```json
{
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "timestamp": {
                "type": "number"
            },
            "value": {
                "type": "number"
            }
        },
        "required": ["timestamp", "value"]
    }
}
```