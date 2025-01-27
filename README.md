# bsefi2326_klima_projekt_api
## GET /temp/get

Dieser Endpunkt wird zum Abrufen von Temperaturdaten verwendet.
### Request
Für diesen Endpunkt ist kein Request Body erforderlich.

### Response

Status: 200

Content-Type: application/json
```json
{
    "result": 0
}
```

Die Antwort enthält die Temperaturdaten in dem Feld „Ergebnis“.


## POST /temp/insert

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


## GET /chart/get

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