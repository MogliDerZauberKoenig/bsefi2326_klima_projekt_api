import sqlite3
import time
from datetime import datetime
import random

connection = sqlite3.connect("../database.db")
print(connection.total_changes)
cursor = connection.cursor()

days = 30
amountOfValues = days * 24


def minMaxTemp(temp: float) -> float:
    if temp > 30.0:
        temp -= temp - 30.0
    elif temp < 10.0:
        temp += 10.0 - temp
    
    return temp


currentDate = datetime.fromtimestamp(time.time())
currentTimestamp = int(datetime(currentDate.year, currentDate.month, currentDate.day, currentDate.hour).timestamp())
oldValue = round(random.uniform(15.0, 30.0), 2)

print(f"Es werden {amountOfValues} Werte erstellt.")

for i in range(amountOfValues):
    timestamp = currentTimestamp - (i * 60 * 60)
    value = 0

    minValue = round(random.uniform(oldValue - random.uniform(1.0, 5.0), oldValue + random.uniform(1.0, 5.0)), 2)
    maxValue = round(minValue + random.uniform(1.0, 5.0), 2)

    minValue = minMaxTemp(minValue)
    maxValue = minMaxTemp(maxValue)

    cursor.execute("INSERT INTO temp (timestamp, minValue, maxValue) VALUES (?, ?, ?)", (timestamp, minValue, maxValue))

connection.commit()
connection.close()