from read_config import read_db_config
from mysql.connector import MySQLConnection
import csv

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn

cursor, conn = re_connect()
with open("../buchstufe.csv", mode="r") as file:
    csvFile=csv.reader(file)
    for lines in csvFile:
        cursor.execute("INSERT INTO buchstufe (stufe, ISBN, abgeben) VALUES (%s, %s, %s)", (lines[0], lines[1], lines[3]))

conn.commit()