from flask import Flask, jsonify, request, g
import time
import random
import sqlite3
import json

app = Flask(__name__)

database = "database.db"
currentTemp = 19.2 # <- Inhalt ist aktuell nicht relevant

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def page_index():
    return "Hier gibt es nichts zu sehen..."

@app.route("/api/get_current_temp")
def api_get_current_temp():
    return jsonify({ 'result': currentTemp })

# Nur fürs testen der DB...
@app.route("/api/insert_temp", methods=['GET'])
def api_insert_temp():
    temp = request.args.get('temp', default=None, type=float)

    if temp is None:
        return "fehlercode und so"

    db = get_db()
    db.cursor().execute("INSERT INTO temp (timestamp, value) VALUES (?, ?)", (int(time.time()), temp))
    db.commit()
    return jsonify({ 'result': temp })

@app.route("/api/get_chart_data", methods=['GET'])
def api_get_chart_data():
    days = request.args.get('days', default=1, type=int)
    currentTimestamp = int(time.time())
    minTimestamp = int(currentTimestamp - (days * 24 * 60 * 60))

    # Es werden keine Werte aus der Datenbank gelesen, sondern zufällig zurückgegeben
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

    db = get_db()
    db.row_factory = sqlite3.Row
    rows = db.cursor().execute(f"SELECT timestamp, value FROM temp WHERE timestamp >= { minTimestamp }").fetchall()

    return jsonify([dict(ix) for ix in rows])

if __name__ == "__main":
    app.run(debug=True, host="0.0.0.0", port=5000)