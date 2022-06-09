from mysql.connector import MySQLConnection
import pandas as pd

from read_config import read_db_config
from hash_func import hash_func
import cryption

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn



def delete_book(ISBN):
    cursor, conn = re_connect()
    cursor.execute("DELETE FROM buecher WHERE ISBN='%s'" % (ISBN))
    conn.commit()


def insert_book(ISBN, Titel, Verlag, preis=0):
    cursor, conn = re_connect()
    values=[ISBN, Titel, Verlag, preis]
    cursor.execute("INSERT INTO buecher (ISBN, Titel, Verlag, preis) VALUES (%s, %s, %s, %s)", values)
    conn.commit()


def update_book(ISBN, Titel, Verlag, preis):
    cursor, conn = re_connect()
    cursor.execute(""""UPTATE buecher SET Titel='%s', Verlag='%s', preis=%s WHERE ISBN=%s""" % (Titel, Verlag, preis, ISBN))
    conn.commit()


def search_book(search_term):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis FROM buecher WHERE Titel LIKE '%"+search_term+"%' OR ISBN LIKE '%"+search_term+"%'")
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["ISBN", "Titel", "Verlag", "preis"])
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))
    return data


def print_books():
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis FROM buecher")
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["ISBN", "Titel", "Verlag", "Preis"])
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))
    return data


def book_by_ISBN(ISBN):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis FROM buecher WHERE ISBN='%s'" % (ISBN))


def insert_taken_book_add(Sch_ID, ISBN, Anzahl=1):
    cryption.decrypt(Sch_ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID='%s' AND ISBN=%s""" % (Sch_ID, ISBN))
    result=cursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        cursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID='%s' AND ISBN=%s""" % (books+Anzahl, Sch_ID, ISBN))
        conn.commit()
    else:
        cursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES ('%s', %s, %s)""" % (Sch_ID, ISBN, Anzahl))
        conn.commit()


def insert_taken_book_absolute(Sch_ID, ISBN, Anzahl=1):
    Sch_ID=cryption.decrypt(Sch_ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID='%s' AND ISBN=%s""" % (Sch_ID, ISBN))
    result=cursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        cursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID='%s' AND ISBN=%s""" % (Anzahl, Sch_ID, ISBN))
        conn.commit()
    else:
        cursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES ('%s', %s, %s)""" % (Sch_ID, ISBN, Anzahl))
        conn.commit()


def delete_zero_taken_books():
    cursor, conn = re_connect()
    cursor.execute("""DELETE FROM ausgeliehen WHERE Anzahl=0""")
    conn.commit()


def book_by_user(ID):
    ID=cryption.decrypt(ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT schueler.Stufe, schueler.Klasse, schueler.Vorname, schueler.Nachname, schueler.Religion, schueler.Fremdsp1, schueler.Fremdsp2, schueler.Fremdsp3 FROM schueler WHERE schueler.ID = '%s'""" % (ID))
    data = cursor.fetchall()
    schueler=pd.DataFrame(data, columns=["Stufe", "Klasse", "Vorname", "Nachname", "Religion", "Fremdsp1", "Fremdsp2", "Fremdsp3"])

    cursor.execute("""SELECT ISBN, Anzahl FROM ausgeliehen WHERE ID = '%s'""" % (ID))
    data=cursor.fetchall()

    buecher=pd.DataFrame(data, columns=["ISBN", "Anzahl"])

    for index in buecher.iterrows():#get Titel from ISBN
        num=index[0]
        ISBN=buecher.iloc[num]["ISBN"]
        cursor.execute("""SELECT Titel FROM buecher WHERE ISBN = %s""" % (ISBN))
        data=cursor.fetchall()
        if len(data)>0:
            buecher.at[num, "ISBN"]=data[0][0]

    return (schueler, buecher)


def next_schueler(ID):
    ID=cryption.decrypt(ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT Stufe, Klasse FROM schueler WHERE ID = '%s'""" % (ID))
    data=cursor.fetchall()[0]
    Stufe=data[0]
    Klasse=data[1]

    cursor.execute("""SELECT Nachname, Vorname, ID FROM schueler WHERE Stufe = '%s' AND Klasse = '%s'""" % (Stufe, Klasse))
    data=cursor.fetchall()
    data.sort()
    
    i=0
    while i<len(data):
        if data[i][2]==ID:
            next_i=(i+1)%len(data)
            next_ID=data[next_i][2]

            prev_i=i-1
            if i<0:
                prev_i=len(data)-1
                
            prev_ID=data[prev_i][2]
        i+=1
    next_ID=cryption.encrypt(next_ID)
    prev_ID=cryption.encrypt(prev_ID)
    return (next_ID, prev_ID)


def search_schueler(name):
    schueler=[]
    cursor, conn = re_connect()
    cursor.execute("SELECT Vorname, Nachname, ID FROM schueler WHERE Nachname LIKE '%"+name+"%'")
    data=cursor.fetchall()

    for list_l in data:
        list_l=list(list_l)
        list_l[2]=cryption.encrypt(list_l[2])
        list_l[0]+=" "+list_l[1]
        list_l.pop(1)
        schueler.append(list_l)



    data=pd.DataFrame(schueler, columns=["Name", "Seite"])
    data["Seite"]=data["Seite"].apply(lambda x:'<form action="/" methond="get"><input type="hidden" name="user" value={0}><input type="submit" value="Seite"></form>')
    return data


def login(username, password):
    cursor, conn = re_connect()
    try:
        cursor.execute("SELECT hash FROM user WHERE username = '%s'" % (username))
        hash_d=cursor.fetchall()
        hash_d=hash_d[0][0]
        hash_input=hash_func(password)

        if str(hash_d)==str(hash_input):
            return True
        else:
            return False
    
    except:
        return False

search_schueler("Eckenfels")