from mysql.connector import MySQLConnection
import pandas as pd
import os.path
import random

from read_config import read_db_config
from hash_func import hash_func
from write_protocol import write_protocol
import cryption

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn


def get_unused_ID():
    cursor, conn = re_connect()
    ID=random.randint(10**6, 9*10**6)
    cursor.exectue("SELECT * FROM addedstudent WHERE ID='%s'" % (ID))
    schueler=cursor.fetchall()
    if len(schueler)!=0:
        ID=get_unused_ID()
    
    return ID

def add_student(Stufe, Klasse, Vorname, Nachname, Religion="", Fremdsp1="", Fremdsp2="", Fremdsp3=""):
    cursor, conn = re_connect()
    ID=get_unused_ID()
    cursor.execute("INSERT INTO schueler (ID, Stufe, Klasse, Vorname, Nachname, Religion, Fremdsp1, Fremdsp2, Fremdsp3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (ID, Stufe, Klasse, Vorname, Nachname, Religion, Fremdsp1, Fremdsp2, Fremdsp3))
    conn.commit()
    cursor.execute("INSERT INTO addedstudent (ID, Stufe, Klasse, Vorname, Nachname, Religion, Fremdsp1, Fremdsp2, Fremdsp3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (ID, Stufe, Klasse, Vorname, Nachname, Religion, Fremdsp1, Fremdsp2, Fremdsp3))
    conn.commit()

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
    cursor.execute("""UPDATE buecher SET Titel='%s', Verlag='%s', preis=%s WHERE ISBN=%s""" % (Titel, Verlag, preis, ISBN))
    conn.commit()


def search_book(search_term):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis FROM buecher WHERE Titel LIKE '%"+search_term+"%' OR ISBN LIKE '%"+search_term+"%'")
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["ISBN", "Titel", "Verlag", "Preis"])
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))
    data["Preis"]=data["Preis"].apply(lambda x:'{0} €'.format(x))
    return data


def print_books():
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis FROM buecher")
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["ISBN", "Titel", "Verlag", "Preis"])
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))
    data["Preis"]=data["Preis"].apply(lambda x:'{0} €'.format(x))
    return data


def book_by_ISBN(ISBN):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis FROM buecher WHERE ISBN='%s'" % (ISBN))
    data=cursor.fetchall()[0]
    return data


def insert_taken_book_add(Sch_ID, ISBN, user, Anzahl=1, ):
    if Anzahl!=0:
        write_protocol(0, Sch_ID, ISBN, Anzahl, user)
    cursor, conn = re_connect()
    cursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID='%s' AND ISBN=%s""" % (Sch_ID, ISBN))
    result=cursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        cursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID='%s' AND ISBN=%s""" % (str(int(Anzahl)+int(books)), Sch_ID, ISBN))
        conn.commit()
    else:
        cursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES ('%s', %s, %s)""" % (Sch_ID, ISBN, Anzahl))
        conn.commit()


def insert_taken_book_absolute(Sch_ID, ISBN, user, Anzahl=1):
    write_protocol(1, Sch_ID, ISBN, Anzahl, user)
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

def execute_stufe(user):
    stufen=[]
    schueler={}
    delete_zero_taken_books()
    cursor, conn = re_connect()
    cursor.execute("SELECT * FROM buchstufe")
    data=cursor.fetchall()
    
    for i in data:
        stufe=i[0]
        stufen.append(stufe)

    stufen=list(dict.fromkeys(stufen))
    for stufe in stufen:
        schule=[]
        cursor.execute("SELECT ID FROM schueler WHERE Stufe='%s'" % (stufe))
        schul=cursor.fetchall()
        for sch in schul:
            schule.append(sch[0])
        
        schueler[stufe]=schule

    for i in data:
        stufe=i[0]
        ISBN=i[1]
        IDs=schueler[stufe]
        for ID in IDs:
            insert_taken_book_add(ID, ISBN, user, 0)

def book_by_user(ID):
    ID=cryption.decrypt(ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT schueler.Stufe, schueler.Klasse, schueler.Vorname, schueler.Nachname, schueler.Religion, schueler.Fremdsp1, schueler.Fremdsp2, schueler.Fremdsp3 FROM schueler WHERE schueler.ID = '%s'""" % (ID))
    data = cursor.fetchall()
    schueler=pd.DataFrame(data, columns=["Stufe", "Klasse", "Vorname", "Nachname", "Religion", "Fremdsp1", "Fremdsp2", "Fremdsp3"])
    schueler["Klasse"]=schueler["Stufe"].astype(str)+schueler["Klasse"].astype(str)
    schueler.drop(schueler.columns[[0]], axis=1, inplace=True)

    cursor.execute("""SELECT ISBN, Anzahl FROM ausgeliehen WHERE ID = '%s'""" % (ID))
    data=cursor.fetchall()

    buecher=pd.DataFrame(data, columns=["ISBN", "Anzahl"])

    for index in buecher.iterrows():
        num=index[0]
        anzahl=buecher.iloc[num]["Anzahl"]
        temp='<input type="number" name="a%s" value="%s" onchange="submitform()">' % (num, anzahl)
        buecher.at[num, "Anzahl"]=temp

    for index in buecher.iterrows():#get Titel from ISBN
        num=index[0]
        ISBN=buecher.iloc[num]["ISBN"]
        temp='<input type="hidden" name="b%s" value="%s">' % (num, ISBN)
        buecher.at[num, "ISBN"]=temp
        cursor.execute("""SELECT Titel FROM buecher WHERE ISBN = %s""" % (ISBN))
        data=cursor.fetchall()
        if len(data)>0:
            ISBN=data[0][0]

        buecher.at[num, "ISBN"]+=ISBN

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


def get_klassen():
    cursor, conn = re_connect()
    cursor.execute("SELECT Stufe FROM schueler t WHERE t.ID = (SELECT min(t1.ID) FROM schueler t1 WHERE t1.Stufe=t.Stufe)")
    data=cursor.fetchall()

    Klassen={}
    data=sorted(data)
    for i in data:
        Stufe=i[0]
        cursor.execute("SELECT Klasse FROM schueler t WHERE t.ID = (SELECT min(t1.ID) FROM schueler t1 WHERE t1.Klasse=t.Klasse AND Stufe='%s')" % (Stufe))
        data2=cursor.fetchall()
        data2=sorted(data2)
        Klassen_a=[]
        for j in data2:
            
            Klasse=j[0]
            if Klasse==" ":
                Klasse=""
            comp=Stufe+Klasse
            Klassen_a.append('<form action="/" method="get"><input type="hidden" name="site" value="klassen"><input type="hidden" name="k" value="%s"><input type="submit" value="%s"></form>' % (comp, comp))

        Klassen[Stufe]=Klassen_a

    
    data=pd.DataFrame.from_dict(Klassen, orient='index')
    data=data.transpose()
    data=data.fillna("")
    data.to_pickle("data/klassen.pkl")


def print_klassen():
    if os.path.exists("data/klassen.pkl")==False:
        get_klassen()
    
    data=pd.read_pickle("data/klassen.pkl")
    return data


def schueler_by_class(klasse):
    schueler=[]
    cursor, conn = re_connect()

    if klasse[0:2]!="J1" and klasse[0:2]!="J2":
        stufe=klasse[0:-1]
        klasse=klasse[-1:]
    else:
        stufe=klasse[0:2]
        klasse=""

    cursor.execute("SELECT Vorname, Nachname, ID FROM schueler WHERE Stufe='%s' AND Klasse='%s'" % (stufe, klasse))
    data=cursor.fetchall()
    data.sort(key=lambda x:x[1])

    for list_l in data:
        list_l=list(list_l)
        list_l[2]=cryption.encrypt(list_l[2])
        list_l[0]=list_l[1]+" "+list_l[0]
        list_l.pop(1)
        schueler.append(list_l)

    #sortieren
    data=pd.DataFrame(schueler, columns=["Name", "Seite"])
    data["Seite"]=data["Seite"].apply(lambda x:'<form action="/" method="get"><input type="hidden" name="site" value="schueler"><input type="hidden" name="ID" value={0}><input type="submit" value="Seite"></form>'.format(x))
    return data


def search_schueler(name):
    schueler=[]
    cursor, conn = re_connect()
    cursor.execute("SELECT Vorname, Nachname, ID FROM schueler WHERE Nachname LIKE '%"+name+"%'")
    data=cursor.fetchall()

    for list_l in data:
        list_l=list(list_l)
        list_l[2]=cryption.encrypt(list_l[2])
        list_l[0]=list_l[1]+" "+list_l[0]
        list_l.pop(1)
        schueler.append(list_l)



    data=pd.DataFrame(schueler, columns=["Name", "Seite"])
    data["Seite"]=data["Seite"].apply(lambda x:'<form action="/" method="get"><input type="hidden" name="site" value="schueler"><input type="hidden" name="ID" value={0}><input type="submit" value="Seite"></form>'.format(x))
    return data


def add_book_stufe(Stufe, ISBN, abgeben=0):
    cursor, conn = re_connect()
    cursor.execute("INSERT INTO buchstufe (stufe, ISBN, abgeben) VALUES ('%s', %s, %s)" % (Stufe, ISBN, abgeben))
    conn.commit()

def remove_book_stufe(Stufe, ISBN, abgeben=0):
    cursor, conn = re_connect()
    cursor.execute("DELETE FROM buchstufe WHERE Stufe='%s' AND ISBN=%s AND abgeben=%s" % (Stufe, ISBN, abgeben))
    conn.commit()

def select_book_stufe(Stufe):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN FROM buchstufe WHERE Stufe='%s' AND abgeben=0" % (Stufe))
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["Buch"])
    data["ent"]=data["Buch"]

    for index in data.iterrows():
        num=index[0]
        ISBN=data.iloc[num]["ent"]

        temp='<form action="/" method="get"><input type="hidden" name="ab" value="0"><input type="hidden" name="site" value="remove_stufe"><input type="hidden" name="stufe" value="%s"><input type="hidden" name="ISBN" value="%s"><input type="submit" value="X" id="remove_stufe"></form>' % (Stufe, ISBN)

        data.at[num, "ent"]=temp

        cursor.execute("SELECT Titel FROM buecher WHERE ISBN=%s" % (ISBN))
        title=cursor.fetchall()
        if len(title)!=0:
            data.at[num, "Buch"]=title[0][0]
    bekommen=data

    cursor.execute("SELECT ISBN FROM buchstufe WHERE Stufe='%s' AND abgeben=1" % (Stufe))
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["Buch"])
    data["ent"]=data["Buch"]

    for index in data.iterrows():
        num=index[0]
        ISBN=data.iloc[num]["ent"]

        temp='<form action="/" method="get"><input type="hidden" name="ab" value="1"><input type="hidden" name="site" value="remove_stufe"><input type="hidden" name="stufe" value="%s"><input type="hidden" name="ISBN" value="%s"><input type="submit" value="X" id="remove_stufe"></form>' % (Stufe, ISBN)

        data.at[num, "ent"]=temp

        cursor.execute("SELECT Titel FROM buecher WHERE ISBN=%s" % (ISBN))
        title=cursor.fetchall()
        if len(title)!=0:
            data.at[num, "Buch"]=title[0][0]
    abgeben=data

    return (bekommen, abgeben)


def get_stufe():
    stufen=[]
    cursor, conn = re_connect()
    cursor.execute("SELECT Stufe FROM schueler t WHERE t.ID = (SELECT min(t1.ID) FROM schueler t1 WHERE t1.Stufe=t.Stufe)")
    data=cursor.fetchall()
    for i in data:
        stufen.append(i[0])
        
    stufen=sorted(stufen)
    return stufen

def bemgeld(id):
    id=cryption.decrypt(id)
    cursor, conn = re_connect()
    cursor.execute("SELECT bemerkung, schaden FROM bemgeld WHERE ID='%s'" % (id))
    data=cursor.fetchall()

    if len(data)==0:
        bemerkung=""
        geld=0.00
    else:
        data=data[0]
        bemerkung=data[0]
        geld=data[1]

    return (bemerkung, geld)

def bemgeld_up(id, bemerkung="", geld=0):
    id=cryption.decrypt(id)
    cursor, conn = re_connect()
    cursor.execute("SELECT ID FROM bemgeld WHERE ID='%s'" % (id))
    data=cursor.fetchall()
    if len(data)!=0:
        cursor.execute("UPDATE bemgeld SET bemerkung='%s', schaden=%s WHERE ID='%s'" % (bemerkung, geld, id))
        conn.commit()
    else:  
        cursor.execute("INSERT INTO bemgeld (ID, bemerkung, schaden) VALUES ('%s', '%s', %s)" % (id, bemerkung, geld))
        conn.commit()


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


def change_password(username, old_pass, new1_pass, new2_pass):
    cursor, conn = re_connect()
    cursor.execute("""SELECT hash FROM user WHERE username = '%s'""" % (username))
    database_pass=cursor.fetchall()[0][0]

    old_hash=hash_func(old_pass)
    if old_hash==database_pass:
        if new1_pass==new2_pass:
            new_pass_hash=hash_func(new1_pass)
            cursor.execute("""UPDATE user SET hash = '%s' WHERE username = '%s'""" % (new_pass_hash, username))
            conn.commit()
            
            return 0
        else:
            return 2
    else:
        return 1

def check_rechte(username):
    cursor, conn = re_connect()
    cursor.execute("SELECT privileges FROM user WHERE username='%s'" % (username))
    data=int(cursor.fetchall()[0][0])
    return data