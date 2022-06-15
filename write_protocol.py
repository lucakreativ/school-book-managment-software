from mysql.connector import MySQLConnection
from read_config import read_db_config
import time

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn


def write_protocol(type, ID, ISBN, Anzahl, user):
    cursor, conn = re_connect()
    zeit=round(time.time())
    cursor.execute("INSERT INTO protocolaus (type, schuelerID, ISBN, Anzahl, unix, user) VALUES (%s, '%s', %s, %s, %s, '%s')" % (type, ID, ISBN, Anzahl, zeit, user))
    conn.commit()

def write_login(user, erfolgreich):
    cursor, conn = re_connect()
    zeit=round(time.time())
    cursor.execute("INSERT INTO protocollogin (user, unix, erfolgreich) VALUES ('%s', %s, %s)" % (user, zeit, erfolgreich))
    conn.commit()