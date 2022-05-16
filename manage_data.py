import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="user",
  password="test",
  database="create_test"
)
mycursor = mydb.cursor()


def insert_book(ISBN, Titel, Verlag, preis=0):
    values=[ISBN, Titel, Verlag, preis]
    mycursor.execute("INSERT INTO buecher (ISBN, Titel, Verlag, preis) VALUES (%s, %s, %s, %s)", values)
    mydb.commit()