import sqlite3

connection = sqlite3.connect("../database.db")
print(connection.total_changes)

cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS temp (id INTEGER PRIMARY KEY NOT NULL, timestamp INTEGER, value REAL)")
connection.close()