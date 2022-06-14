from mysql.connector import MySQLConnection
from read_config import read_db_config
import time

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn


def write_protocol(type, ID, ISBN, Anzahl):
    cursor, conn = re_connect()
    zeit=round(time.time())
    cursor.execute("INSERT INTO protocolaus (type, schuelerID, ISBN, Anzahl, unix) VALUES (%s, '%s', %s, %s, %s)" % (type, ID, ISBN, Anzahl, zeit))
    conn.commit()