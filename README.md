# bsefi2326_klima_projekt_api

# Dokumentation: Flask-basierte Temperatur-API

# Dokumentation: Flask API zur Temperaturüberwachung

## Einleitung
Dieses Flask-API-Skript stellt eine REST-API zur Überwachung und Speicherung von Temperaturdaten bereit. Es unterstützt das Abrufen und Einfügen von Temperaturwerten, sowie das Generieren von simulierten Verlaufsdaten.

---

## Voraussetzungen
- **Python-Bibliotheken:**
  - `Flask`: Webserver-Framework
  - `Flask-CORS`: Cross-Origin Resource Sharing
  - `sqlite3`: Datenbankverwaltung
  - `datetime`, `random`, `time`: Standardmodule für Zeit- und Zufallsfunktionen

---

## Initialisierung und Konfiguration
```python
from flask import Flask, jsonify, request, g
from flask_cors import CORS, cross_origin
import time
from datetime import datetime
import random
import sqlite3
```
- `Flask`: Initialisiert die API
- `Flask-CORS`: Erlaubt CORS-Anfragen für Cross-Origin-Zugriffe
- `sqlite3`: Datenbankverbindung
- `datetime`, `random`, `time`: Zeit- und Zufallsfunktionen

### Anwendung starten
```python
app = Flask(__name__)
CORS(app, support_credentials=True)
database = "database.db"
currentTemp = None  # Initialisierung der aktuellen Temperatur
```
- Initialisiert die Flask-App
- Aktiviert CORS für API-Zugriffe
- Setzt `currentTemp` für den aktuellen Temperaturwert

---

## Hilfsfunktionen
### Temperaturbegrenzung
```python
def minMaxTemp(temp: float) -> float:
    if temp > 30.0:
        temp -= temp - 30.0
    elif temp < 10.0:
        temp += 10.0 - temp
    return temp
```
- Stellt sicher, dass die Temperatur innerhalb des Bereichs 10°C - 30°C bleibt.

### Datenbankzugriff
```python
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    return db
```
- Erstellt eine Verbindung zur SQLite-Datenbank.

### Datenbankverbindung schließen
```python
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
```
- Stellt sicher, dass die Datenbankverbindung nach jeder Anfrage geschlossen wird.

---

## API-Endpunkte
### Root-Endpunkt
```python
@app.route("/")
def page_index():
    return "Hier gibt es nichts zu sehen..."
```
- Gibt eine einfache Nachricht aus.

### Abrufen der aktuellen Temperatur
```python
@app.route("/api/temp/get")
@cross_origin(supports_credentials=True)
def api_get_current_temp():
    if currentTemp is None:
        return jsonify({ 'status': False, 'error': 'Aktuell gibt es keine Werte in der Datenbank.' }), 400
    return jsonify(currentTemp)
```
- Gibt die aktuelle Temperatur aus, falls verfügbar.
- Falls keine Temperatur vorhanden ist, wird ein Fehler zurückgegeben.

### Einfügen eines neuen Temperaturwerts
```python
@app.route("/api/temp/insert", methods=['POST'])
@cross_origin(supports_credentials=True)
def api_insert_temp():
    global currentTemp
    timestamp = int(time.time())
    temp = None
    try:
        temp = float(request.get_json()['value'])
    except:
        temp = None

    if temp is None:
        return jsonify({ 'status': False, 'error': 'Im Request muss { \"value\": \"19.9\" } enthalten sein.' }), 400

    db = get_db()
    lastTemp = db.cursor().execute("SELECT id, timestamp, minValue, maxValue FROM temp ORDER BY timestamp DESC LIMIT 1").fetchone()

    if lastTemp is None or datetime.fromtimestamp(lastTemp[1]).strftime("%d.%m.%y %H") != datetime.fromtimestamp(timestamp).strftime("%d.%m.%y %H"):
        newDate = datetime.fromtimestamp(timestamp)
        newTimestamp = int(datetime(newDate.year, newDate.month, newDate.day, newDate.hour).timestamp())
        db.cursor().execute("INSERT INTO temp (timestamp, minValue, maxValue) VALUES (?, ?, ?)", (newTimestamp, temp, temp))
    elif min(lastTemp[2], temp) != temp or max(lastTemp[3], temp) != temp:
        db.cursor().execute("UPDATE temp SET minValue = ?, maxValue = ? WHERE id = ?", (min(lastTemp[2], temp), max(lastTemp[3], temp), lastTemp[0]))

    currentTemp = { 'timestamp': timestamp, 'value': temp }
    db.commit()
    return jsonify({ 'result': temp })
```
- Erwartet eine JSON-Anfrage mit `value` als Temperaturwert.
- Speichert die Temperatur in der Datenbank.
- Aktualisiert `currentTemp`.

### Abrufen von Temperaturverlaufsdaten
```python
@app.route("/api/chart/get", methods=['GET'])
@cross_origin(supports_credentials=True)
def api_get_chart_data():
    days = request.args.get('days', default=1, type=int)
    currentDate = datetime.fromtimestamp(time.time())
    currentTimestamp = int(datetime(currentDate.year, currentDate.month, currentDate.day, currentDate.hour).timestamp())
    minTimestamp = int(currentTimestamp - (days * 24 * 60 * 60))

    simulate = request.args.get("simulate", default=None, type=bool)
    if simulate:
        simValues = []
        for i in range(days * 24):
            timestamp = currentTimestamp - (i * 60 * 60)
            minValue = round(random.uniform(15.0, 30.0), 2)
            maxValue = round(minValue + random.uniform(1.0, 5.0), 2)
            simValues.insert(0, { 'timestamp': timestamp, 'minValue': minValue, 'maxValue': maxValue })
        return jsonify(simValues)

    db = get_db()
    db.row_factory = sqlite3.Row
    rows = db.cursor().execute(f"SELECT timestamp, minValue, maxValue FROM temp WHERE timestamp >= { minTimestamp }").fetchall()
    return jsonify([dict(ix) for ix in rows])
```
- Gibt die Temperaturwerte der letzten `days` Tage aus der Datenbank zurück.
- Falls `simulate=true`, werden zufällige Werte generiert.

---

## Start des Servers
```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```
- Startet den Flask-Server auf Port 5000.

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
cursor.execute("CREATE TABLE IF NOT EXISTS temp (id INTEGER PRIMARY KEY NOT NULL, timestamp INTEGER, minValue REAL, maxValue REAL)")
```
- Erstellt ein Cursor-Objekt für die Datenbankinteraktion
- Führt eine SQL-Anweisung aus, um die Tabelle `temp` zu erstellen, falls sie noch nicht existiert
- **Tabellenstruktur:**
  - `id`: Primärschlüssel (automatisch inkrementiert)
  - `timestamp`: Speichert den Zeitstempel der Messung
  - `minValue`: Speichert den minimalen Temperaturwert als Gleitkommazahl
  - `maxValue`: Speichert den maximalen Temperaturwert als Gleitkommazahl

### Verbindung schließen
```python
connection.close()
```
- Schließt die Datenbankverbindung, um Speicher freizugeben und Daten zu sichern

---


# Dokumentation: SQLite-Datenbank mit Zufallswerten füllen

## Beschreibung
Dieses Skript generiert Temperaturwerte für einen Zeitraum von 30 Tagen und speichert diese in einer SQLite-Datenbank. Es simuliert stündliche Minimal- und Maximaltemperaturen und stellt sicher, dass die Werte innerhalb eines bestimmten Bereichs bleiben.

## Abhängigkeiten
Das Skript verwendet die folgenden Python-Module:
- `sqlite3`: Zum Speichern der generierten Werte in einer SQLite-Datenbank.
- `time`: Zum Arbeiten mit Zeitstempeln.
- `datetime`: Zum Erzeugen und Verwalten von Datums- und Zeitinformationen.
- `random`: Zur Erzeugung zufälliger Temperaturwerte.

## Funktionsweise
### 1. Datenbankverbindung herstellen
Das Skript stellt eine Verbindung zur SQLite-Datenbank `database.db` her und erstellt ein `cursor`-Objekt für SQL-Operationen:
```python
connection = sqlite3.connect("../database.db")
cursor = connection.cursor()
```

### 2. Berechnung der Anzahl der Werte
Die Anzahl der zu generierenden Temperaturwerte basiert auf 30 Tagen mit jeweils 24 Stunden:
```python
days = 30
amountOfValues = days * 24
```

### 3. Temperaturbegrenzung
Die Funktion `minMaxTemp(temp: float) -> float` stellt sicher, dass die Temperatur innerhalb des Bereichs 10.0 bis 30.0 Grad Celsius bleibt:
```python
def minMaxTemp(temp: float) -> float:
    if temp > 30.0:
        temp -= temp - 30.0
    elif temp < 10.0:
        temp += 10.0 - temp
    
    return temp
```

### 4. Initialisierung des Zeitstempels
Der aktuelle Zeitstempel wird berechnet und auf die volle Stunde gerundet:
```python
currentDate = datetime.fromtimestamp(time.time())
currentTimestamp = int(datetime(currentDate.year, currentDate.month, currentDate.day, currentDate.hour).timestamp())
```

Ein Startwert für die Temperatur wird zufällig zwischen 15.0 und 30.0 Grad gewählt:
```python
oldValue = round(random.uniform(15.0, 30.0), 2)
```

### 5. Generierung und Speicherung der Temperaturwerte
In einer Schleife werden Temperaturwerte für jede Stunde der letzten 30 Tage generiert und gespeichert:
```python
for i in range(amountOfValues):
    timestamp = currentTimestamp - (i * 60 * 60)
```

Die Minimal- und Maximaltemperaturen werden auf Basis des vorherigen Wertes zufällig generiert und durch `minMaxTemp` begrenzt:
```python
    minValue = minMaxTemp(
        round(
            random.uniform(
                oldValue - random.uniform(1.0, 5.0), 
                oldValue + random.uniform(1.0, 5.0)
            ), 
            2
        )
    )
    maxValue = minMaxTemp(
        round(
            minValue + random.uniform(1.0, 5.0), 
            2
        )
    )
```

Die generierten Werte werden in die Tabelle `temp` der Datenbank eingefügt:
```python
    cursor.execute("INSERT INTO temp (timestamp, minValue, maxValue) VALUES (?, ?, ?)", (timestamp, minValue, maxValue))
```

### 6. Speichern und Schließen der Datenbankverbindung
Nach der Schleife werden die Daten gespeichert und die Verbindung zur Datenbank geschlossen:
```python
connection.commit()
connection.close()
```

## Fazit
Dieses Skript simuliert Temperaturdaten für einen Zeitraum von 30 Tagen mit jeweils stündlichen Minimal- und Maximalwerten. Die Werte werden zufällig erzeugt, aber innerhalb eines sinnvollen Bereichs gehalten, bevor sie in eine SQLite-Datenbank gespeichert werden. Es eignet sich für Tests oder zur Generierung von Beispieldaten für Analysen.

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

Die Antwort auf diese Anfrage ist ein JSON-Objekt, welches den eingetragenen Wert enthält.

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
* minValue (number) - Der minimale Wert des Datenpunktes.
* maxValue (number) - Der maximale Wert des Datenpunktes.



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
            "minValue": {
                "type": "number"
            },
            "maxValue": {
                "type": "number"
            }
        },
        "required": ["timestamp", "minValue", "maxValue"]
    }
}
```