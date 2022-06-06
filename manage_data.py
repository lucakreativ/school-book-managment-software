import mysql.connector

from read_config import read_db_config

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


def update_book(ISBN, Titel, Verlag, preis):
    mycursor.execute(""""UPTATE buecher SET Titel='%s', Verlag='%s', preis=%s WHERE ISBN=%s""" % (Titel, Verlag, preis, ISBN))
    mydb.commit()


def insert_taken_book_add(Sch_ID, ISBN, Anzahl=1):
    mycursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID='%s' AND ISBN=%s""" % (Sch_ID, ISBN))
    result=mycursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        mycursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID='%s' AND ISBN=%s""" % (books+Anzahl, Sch_ID, ISBN))
        mydb.commit()
    else:
        mycursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES ('%s', %s, %s)""" % (Sch_ID, ISBN, Anzahl))
        mydb.commit()


def insert_taken_book_absolute(Sch_ID, ISBN, Anzahl=1):
    mycursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID='%s' AND ISBN=%s""" % (Sch_ID, ISBN))
    result=mycursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        mycursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID='%s' AND ISBN=%s""" % (Anzahl, Sch_ID, ISBN))
        mydb.commit()
    else:
        mycursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES ('%s', %s, %s)""" % (Sch_ID, ISBN, Anzahl))
        mydb.commit()