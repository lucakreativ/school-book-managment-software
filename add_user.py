from mysql.connector import MySQLConnection
from read_config import read_db_config
from hash_func import hash_func

dbconfig =  read_db_config()
conn = MySQLConnection(**dbconfig)
cursor = conn.cursor()

username=input("Benutzername: ")
passwort=input("Passwort: ")
priv=int(input("Rechte (niedriger = mehr Rechte): "))
outside=int(input("ausen zugreifen? (1=Ja, 0=nein): "))

print("Benutzername: '"+username+"'")
print("Passwort: '"+passwort+"'")
print("Rechte: "+ str(priv))
print("Außen: "+str(outside))

hash_i=hash_func(passwort)
print("Hash: '"+ hash_i+"'")

cursor.execute("""INSERT INTO user (username, hash, privileges, outside) VALUES (%s, %s, %s, %s)""", (username, hash_i, priv, outside))
conn.commit()

print("Success") 