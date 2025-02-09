import sqlite3
import time
import random

connection = sqlite3.connect("../database.db")
print(connection.total_changes)
cursor = connection.cursor()

days = 30
probeIntervall = 30 # <- in Sekunden
amountOfValues = int((days * 24 * 60 * 60) / probeIntervall)

currentTimestamp = int(time.time())
oldValue = round(random.uniform(15.0, 30.0), 2)

print(f"Es werden {amountOfValues} Werte erstellt, mit einem Intervall von {probeIntervall} Sekunden.")

for i in range(amountOfValues):
    timestamp = currentTimestamp - (i * probeIntervall)
    value = 0

    value = round(random.uniform(oldValue - random.uniform(1.0, 2.5), oldValue + random.uniform(1.0, 2.5)), 2)
    if value > 30.0:
        value -= value - 30.0
    elif value < 10.0:
        value += 10.0 - value

    cursor.execute("INSERT INTO temp (timestamp, value) VALUES (?, ?)", (timestamp, value))

connection.commit()
connection.close()