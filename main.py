from flask import Flask, jsonify, request, g
from flask_cors import CORS, cross_origin
import time
import random
import sqlite3

app = Flask(__name__)
CORS(app, support_credentials=True)

database = "database.db"

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
    cursor = get_db().cursor()
    currentTemp = cursor.execute("SELECT timestamp, value FROM temp ORDER BY timestamp DESC LIMIT 1").fetchone()
    if currentTemp == None:
        return jsonify({ 'status': False, 'error': 'Aktuell gibt es keine Werte in der Datenbank.' }), 400
    return jsonify({ 'timestamp': currentTemp[0], 'value': currentTemp[1] })

@app.route("/api/temp/insert", methods=['POST'])
@cross_origin(supports_credentials=True)
def api_insert_temp():
    temp = None
    try:
        temp = float(request.get_json()['value'])
    except:
        temp = None

    if temp is None:
        return jsonify({ 'status': False, 'error': 'Im Request muss { \'value\': \'19.9\' } entahlten sein.' }), 400

    db = get_db()
    db.cursor().execute("INSERT INTO temp (timestamp, value) VALUES (?, ?)", (int(time.time()), temp))
    db.commit()
    return jsonify({ 'result': temp })

@app.route("/api/chart/get", methods=['GET'])
@cross_origin(supports_credentials=True)
def api_get_chart_data():
    days = request.args.get('days', default=1, type=int)
    currentTimestamp = int(time.time())
    minTimestamp = int(currentTimestamp - (days * 24 * 60 * 60))

    # Es werden keine Werte aus der Datenbank gelesen, sondern zufällig generiert
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
    #db.row_factory = sqlite3.Row
    #rows = db.cursor().execute(f"SELECT timestamp, value FROM temp WHERE timestamp >= { minTimestamp }").fetchall()

    res = []

    for i in range(days * 24):
        min = int(currentTimestamp - (i * 24 * 60 * 60))
        max = int(currentTimestamp - ((i + 1) * 24 * 60 * 60))
        f = db.cursor().execute(f"SELECT MIN(value), MAX(value) FROM temp WHERE timestamp >= { min } AND timestamp < { max }").fetchall()
        print(f)

    return jsonify({ "status": "1" })
    #return jsonify([dict(ix) for ix in rows])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)