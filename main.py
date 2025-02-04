from flask import Flask, jsonify, request, g
from flask_cors import CORS, cross_origin
import time
from datetime import datetime
import random
import sqlite3

app = Flask(__name__)
CORS(app, support_credentials=True)

database = "database.db"
currentTemp = None # Init

def minMaxTemp(temp: float) -> float:
    return max(10.0, min(30.0, temp))

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

@app.route("/api/temp/get")
@cross_origin(supports_credentials=True)
def api_get_current_temp():
    #cursor = get_db().cursor()
    #currentTemp = cursor.execute("SELECT timestamp, value FROM temp ORDER BY timestamp DESC LIMIT 1").fetchone()
    #if currentTemp == None:
        #return jsonify({ 'status': False, 'error': 'Aktuell gibt es keine Werte in der Datenbank.' }), 400
    #return jsonify({ 'timestamp': currentTemp[0], 'value': currentTemp[1] })

    if currentTemp is None:
        return jsonify({ 'status': False, 'error': 'Aktuell gibt es keine Werte in der Datenbank.' }), 400

    return jsonify(currentTemp)

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
        return jsonify({ 'status': False, 'error': 'Im Request muss { \'value\': \'19.9\' } entahlten sein.' }), 400

    db = get_db()

    lastTemp = db.cursor().execute("SELECT id, timestamp, minValue, maxValue FROM temp ORDER BY timestamp DESC LIMIT 1").fetchone()

    # Für diese Stunde gab es noch keine Datensätze oder es gibt überhaupt noch keine Datensätze, also wird ein neuer erstellt.
    if lastTemp is None or datetime.fromtimestamp(lastTemp[1]).strftime("%d.%m.%y %H") != datetime.fromtimestamp(timestamp).strftime("%d.%m.%y %H"):
        newDate = datetime.fromtimestamp(timestamp)
        newTimestamp = int(datetime(newDate.year, newDate.month, newDate.day, newDate.hour).timestamp())
        db.cursor().execute("INSERT INTO temp (timestamp, minValue, maxValue) VALUES (?, ?, ?)", (newTimestamp, temp, temp))
    elif min(lastTemp[2], temp) != temp or max(lastTemp[2], temp) != temp:
        db.cursor().execute("UPDATE temp SET minValue = ?, maxValue = ? WHERE id = ?", (min(lastTemp[2], temp), max(lastTemp[3], temp), lastTemp[0]))

    # REM: WIRD NICHT MEHR BENÖTIGT, DA DER PI NICHT GENÜGEND LEISTUNG HAT!!!
    #db.cursor().execute("INSERT INTO temp (timestamp, value) VALUES (?, ?)", (timestamp, temp))
    # REM

    currentTemp = { 'timestamp': timestamp, 'value': temp }
    db.commit()

    return jsonify({ 'result': temp })

@app.route("/api/chart/get", methods=['GET'])
@cross_origin(supports_credentials=True)
def api_get_chart_data():
    days = request.args.get('days', default=1, type=int)
    currentDate = datetime.fromtimestamp(time.time())
    currentTimestamp = int(
        datetime(
            currentDate.year, 
            currentDate.month, 
            currentDate.day, 
            currentDate.hour
        ).timestamp()
    )
    minTimestamp = int(currentTimestamp - (days * 24 * 60 * 60))

    # Es werden keine Werte aus der Datenbank gelesen, sondern zufällig generiert
    simulate = request.args.get("simulate", default=None, type=bool)
    if simulate == True:
        simValues = []
        for i in range(days * 24):
            timestamp = currentTimestamp - (i * 60 * 60)
            minValue = 0
            maxValue = 0

            if i == 0:
                minValue = round(random.uniform(15.0, 30.0), 2)
            else:
                minValue = minMaxTemp(
                    round(
                        random.uniform(
                            simValues[i - 1]['minValue'] - 5.0, 
                            simValues[i - 1]['minValue'] + 5.0
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

            simValues.insert(0, { 'timestamp': timestamp, 'minValue': minValue, 'maxValue': maxValue })
        return jsonify(simValues)

    db = get_db()
    db.row_factory = sqlite3.Row
    #rows = db.cursor().execute(f"SELECT timestamp, value FROM temp WHERE timestamp >= { minTimestamp }").fetchall()

    rows = db.cursor().execute(f"SELECT timestamp, minValue, maxValue FROM temp WHERE timestamp >= { minTimestamp }").fetchall()

    return jsonify([dict(ix) for ix in rows])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)