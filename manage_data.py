from mysql.connector import MySQLConnection
import pandas as pd
import os.path
import random
import time

from read_config import read_db_config
from hash_func import hash_func
from write_protocol import write_protocol
import cryption

import threading

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
    cursor.execute("DELETE FROM buecher WHERE ISBN=%s", (ISBN,))
    conn.commit()


def insert_book(ISBN, Titel, Verlag, Fach, preis=0):
    cursor, conn = re_connect()
    values=[ISBN, Titel, Verlag, preis, Fach]
    cursor.execute("INSERT INTO buecher (ISBN, Titel, Verlag, preis, Fach) VALUES (%s, %s, %s, %s, %s)", values)
    conn.commit()


def update_book(ISBN, Titel, Verlag, preis, Fach):
    cursor, conn = re_connect()
    cursor.execute("""UPDATE buecher SET Titel=%s, Verlag=%s, preis=%s, Fach=%s WHERE ISBN=%s""", (Titel, Verlag, preis, Fach, ISBN))
    conn.commit()


def search_book(search_term):
    cursor, conn = re_connect()
    term="SELECT ISBN, Titel, Fach, Verlag, preis FROM buecher WHERE Titel LIKE CONCAT('%', %s, '%') OR ISBN LIKE CONCAT('%', %s, '%') OR ("

    terms=search_term.split(" ")
    data=[search_term, search_term, terms[0]]
    term+="Titel LIKE CONCAT('%', %s, '%')"
    if len(terms)>1:
        for i in terms[1::]:
            data.append(i)
            term+=" AND Titel LIKE CONCAT('%', %s, '%')"
    
    term+=")"
    
    cursor.execute(term, data)
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["ISBN", "Titel", "Fach", "Verlag", "Preis"])
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))
    data["Preis"]=data["Preis"].apply(lambda x:'{0} €'.format(x))
    data=data.sort_values(by="Titel")
    data.reset_index(drop=True, inplace=True)
    return data


def print_books():
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Fach, Verlag, preis FROM buecher")
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["ISBN", "Titel", "Fach", "Verlag", "Preis"])
    data["ISBN"]=data["ISBN"].apply(lambda x:'<a href="/?site=book_by_ISBN&ISBN={0}">{0}</a>'.format(x))
    data["Preis"]=data["Preis"].apply(lambda x:'{0} €'.format(x))
    data=data.sort_values(by="Titel")
    data.reset_index(drop=True, inplace=True)
    return data


def book_by_ISBN(ISBN):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, Titel, Verlag, preis, Fach FROM buecher WHERE ISBN=%s", [ISBN,])
    data=cursor.fetchall()[0]
    return data


def insert_taken_book_add(Sch_ID, ISBN, user, Anzahl=1, cursor=None, conn=None):
    if Anzahl!=0:
        write_protocol(0, Sch_ID, ISBN, Anzahl, user)
    if cursor==None:
        cursor, conn = re_connect()
    cursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID=%s AND ISBN=%s""", [Sch_ID, ISBN])
    result=cursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        cursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID=%s AND ISBN=%s""", [str(int(Anzahl)+int(books)), Sch_ID, ISBN])
        conn.commit()
    else:
        cursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES (%s, %s, %s)""", [Sch_ID, ISBN, Anzahl])
        conn.commit()


def insert_taken_book_absolute(Sch_ID, ISBN, user, Anzahl=1):
    write_protocol(1, Sch_ID, ISBN, Anzahl, user)
    cursor, conn = re_connect()
    cursor.execute("""SELECT Anzahl FROM ausgeliehen WHERE ID=%s AND ISBN=%s""", [Sch_ID, ISBN])
    result=cursor.fetchall()
    if len(result)!=0:
        books=result[0][0]
        cursor.execute("""UPDATE ausgeliehen SET Anzahl=%s WHERE ID=%s AND ISBN=%s""", [Anzahl, Sch_ID, ISBN])
        conn.commit()
    else:
        cursor.execute("""INSERT INTO ausgeliehen (ID, ISBN, Anzahl) VALUES (%s, %s, %s)""", [Sch_ID, ISBN, Anzahl])
        conn.commit()


def delete_zero_taken_books():
    cursor, conn = re_connect()
    cursor.execute("""DELETE FROM ausgeliehen WHERE Anzahl=0""")
    conn.commit()


def execute_second(i, schueler, user):
    cursor, conn =re_connect()
    stufe=i[0]
    ISBN=i[1]
    Fach=i[2]
    IDs=schueler[stufe]
    for sch in IDs:
        ID=sch[0]
        Fach_s=sch[1:]
        if Fach in Fach_s or Fach=="":
            insert_taken_book_add(ID, ISBN, user, 0, cursor, conn)

def execute_stufe(user):
    cursor, conn =re_connect()

    threads=[]
    books = []
    stufen=[]
    schueler={}
    delete_zero_taken_books()
    cursor, conn = re_connect()
    cursor.execute("SELECT buchstufe.stufe, buchstufe.abgeben, buchstufe.ISBN, buecher.Fach FROM buchstufe, buecher WHERE buchstufe.ISBN=buecher.ISBN")
    data=cursor.fetchall()
    
    for i in data:
        stufe=i[0]
        
        for j in range(i[1]+1):
            books.append([int(stufe)+j, i[2], i[3]])
            stufen.append(int(stufe)+j)


    stufen=list(dict.fromkeys(stufen))

    for stufe in stufen:
        schule=[]
        cursor.execute("SELECT ID, Religion, Fremdsp1, Fremdsp2, Fremdsp3 FROM schueler WHERE Stufe=%s", [stufe])
        schul=cursor.fetchall()
        for sch in schul:
            schule.append(sch)
        
        schueler[stufe]=schule

    for i in books:

        t=threading.Thread(target=execute_second, args=(i, schueler, user))
        threads.append(t)
        t.start()



    for t in threads:
        t.join()


def add_to_complete_class(klasse, ISBN, user, anzahl):
    if klasse[0:2]!="J1" and klasse[0:2]!="J2":
        stufe=klasse[0:-1]
        klasse=klasse[-1:]
    else:
        stufe=klasse[0:2]
        klasse=""
        
    cursor, conn = re_connect()
    cursor.execute("SELECT ID FROM schueler WHERE Stufe=%s AND Klasse=%s", [stufe, klasse])
    IDs=cursor.fetchall()
    for ID in IDs:
        insert_taken_book_add(ID[0], ISBN, user, anzahl, cursor, conn)


def book_by_user(ID, changed=None):
    abgeben=True

    ID=cryption.decrypt(ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT schueler.Stufe, schueler.Klasse, schueler.Vorname, schueler.Nachname, schueler.Religion, schueler.Fremdsp1, schueler.Fremdsp2, schueler.Fremdsp3 FROM schueler WHERE schueler.ID = %s""", [ID,])
    data = cursor.fetchall()
    stufe=data[0][0]
    klasse=data[0][1]

    faecher=[data[0][4], data[0][5], data[0][6], data[0][7], ""]

    if stufe[0]=="J":
        cursor.execute("SELECT schueler.Stufe, oberstufe.vorname, oberstufe.nachname, oberstufe.l, oberstufe.m, oberstufe.abiturjahr FROM oberstufe, schueler WHERE oberstufe.studentid=%s AND schueler.ID=%s", [ID, ID])
        data2=cursor.fetchall()
        if len(data2)!=0:
            schueler=pd.DataFrame(data2, columns=["Stufe", "Vorname", "Nachname", "Leistungsfächer", "Basisfächer", "Abschlussjahr"])
        else:
            data=list(data[0])
            data.insert(0, "Oberstufendaten nicht gefunden")
            data=[data]
            schueler=pd.DataFrame(data, columns=["Fehler","Stufe", "Klasse", "Vorname", "Nachname", "Religion", "Fremdsp1", "Fremdsp2", "Fremdsp3"])
            schueler["Klasse"]=schueler["Stufe"].astype(str)+schueler["Klasse"].astype(str)
            schueler.drop(schueler.columns[[1]], axis=1, inplace=True)


    else:
        schueler=pd.DataFrame(data, columns=["Stufe", "Klasse", "Vorname", "Nachname", "Religion", "Fremdsp1", "Fremdsp2", "Fremdsp3"])
        schueler["Klasse"]=schueler["Stufe"].astype(str)+schueler["Klasse"].astype(str)
        schueler["Klasse"]=schueler["Klasse"].apply(lambda x:'<input type="hidden" name="site" value="klassen"><input type="hidden" name="k" value={0}><input type="submit" value="{0}" id="full_cell">'.format(x))
        schueler.drop(schueler.columns[[0]], axis=1, inplace=True)

    
    

    cursor.execute("""SELECT b.Titel, a.Anzahl, a.ISBN FROM ausgeliehen a, buecher b WHERE ID = %s AND a.ISBN=b.ISBN ORDER BY b.Titel""", (ID,))
    data=cursor.fetchall()
    cursor.execute("""SELECT DISTINCT a.ISBN, a.Anzahl, a.ISBN FROM ausgeliehen a, buecher b WHERE ID = %s AND a.ISBN NOT IN (SELECT ISBN FROM buecher) ORDER BY a.ISBN""", (ID,))
    data+=cursor.fetchall()


    buecher=pd.DataFrame(data, columns=["Titel/ISBN", "Anzahl", "ISBN"])

    for index in buecher.iterrows():
        num=index[0]
        anzahl=buecher.iloc[num]["Anzahl"]
        ISBN=buecher.iloc[num]["ISBN"]

        temp='<input type="number" name="a%s" value="%s" onchange="submitform()">' % (num, anzahl)
        if ISBN==changed:
            temp="""<div id='mark_changed'>"""+temp+"""</div>"""
        buecher.at[num, "Anzahl"]=temp



        
        Titel=buecher.iloc[num]["Titel/ISBN"]
        temp='<input type="hidden" name="b%s" value="%s">' % (num, ISBN)
        cursor.execute("SELECT IF(stufe + abgeben > %s AND stufe<=%s, 1, 0) FROM buchstufe WHERE ISBN = %s", (stufe, stufe, ISBN))
        data=cursor.fetchall()
        if len(data)==0 or data[0]==(0,):
            if abgeben==True and anzahl>0:
                buecher.at[num, "Titel/ISBN"]='<div id="abgabebuch">'
            else:
                buecher.at[num, "Titel/ISBN"]='<div>'
            buecher.at[num, "Titel/ISBN"]+=temp
        else:
            buecher.at[num, "Titel/ISBN"]=temp

        buecher.at[num, "Titel/ISBN"]+=Titel+"</div>"

    buecher.pop("ISBN")

    return_mess=[]

    cursor.execute("SELECT COUNT(*) FROM ausgeliehen WHERE ID=%s AND Anzahl>=2", [ID,])
    z=cursor.fetchall()[0][0]

    if z>0:
        return_mess.append(["warning", "Mehrere Bücher mit der gleichen ISBN wurden ausgeliehen."])
    

    if abgeben==False: sqlab=0
    else: sqlab=1


    cursor.execute("SELECT ISBN FROM ausgeliehen WHERE ID=%s AND Anzahl>=1", [ID,])
    buecher_check=cursor.fetchall()
    buecher_check_l=[]
    for buch in buecher_check:
        buecher_check_l.append(buch[0])


    cursor.execute("SELECT buchstufe.ISBN, buecher.Fach FROM buchstufe, buecher WHERE buchstufe.ISBN=buecher.ISBN AND buchstufe.stufe=%s", (stufe,))
    data=cursor.fetchall()


    con=True
    for i in data:
        if i[1] in faecher:
            if i[0] not in buecher_check_l:
                con=False
                break
                
    if con==True:
        return_mess.append(["ok", "Alle Bücher wurden ausgeliehen."])

    if len(return_mess)==0:
        return_mess.append(["", ""])

    return (schueler, buecher, stufe, klasse, return_mess)


def missing_books():
    cursor, conn = re_connect()

    df=pd.DataFrame()
    buch_dic={}
    cursor.execute("SELECT ISBN, Titel FROM buecher")
    buecher=cursor.fetchall()
    for i in buecher:
        buch_dic[i[0]]=i[1]

    
    cursor.execute("SELECT ID, Nachname, Vorname, Stufe, Klasse FROM schueler")
    schueler=cursor.fetchall()


    for student in schueler:
        cursor.execute("SELECT schaden FROM bemgeld WHERE ID=%s", (student[0],))
        bemgeld=cursor.fetchone()
        if bemgeld==None:
            bemgeld="0,00 €"
        else:
            bemgeld="%.2f €" % (bemgeld[0])
            bemgeld=bemgeld.replace(".", ",")

        cursor.execute("SELECT ISBN FROM ausgeliehen WHERE ID=%s AND Anzahl>0", (student[0],))
        buecher=cursor.fetchall()
        cursor.execute("SELECT buchstufe.ISBN FROM buchstufe, ausgeliehen WHERE ausgeliehen.ID=%s AND ausgeliehen.ISBN=buchstufe.ISBN AND (stufe+abgeben>%s AND stufe<=%s)", (student[0], student[3], student[3]))
        dont_abgeben=cursor.fetchall()
        dont_abgeben2=[]#Bücher die nicht abgeben werden müssen
        abgeben=[]
        for i in dont_abgeben:
            dont_abgeben2.append(i[0])

        
        #entfernt alle Bücher, die nicht abgeben werden müssen
        for i in buecher:
            buch=i[0]
            if buch not in dont_abgeben2:
                abgeben.append(buch)

        abgeben=sorted(abgeben)#Bücher die abgeben werden müssen
        if len(abgeben)>0:
            abgeben_s=""
            for i in abgeben:
                if i in buch_dic:
                    abgeben_s+=buch_dic[i]
                else:
                    abgeben_s+=i

                abgeben_s+="; "
        
            dfappend=pd.DataFrame([[student[1], student[2], student[3]+student[4], bemgeld, abgeben_s]])
            #print(abgeben_s)
            df=pd.concat([df, dfappend])


    df=df.sort_values([2, 0])
    df.columns = ["Nachname", "Vorname", "Klasse", "Gebühren","Fehlende Bücher"]
    df.reset_index(drop=True, inplace=True)
    path="files/"+str(round(time.time(), 1))+"-missingbooks.xlsx"
    df.to_excel(path)
    return path


def next_schueler(ID):
    ID=cryption.decrypt(ID)
    cursor, conn = re_connect()
    cursor.execute("""SELECT Stufe, Klasse FROM schueler WHERE ID = %s""", (ID,))
    data=cursor.fetchall()[0]
    Stufe=data[0]
    Klasse=data[1]

    cursor.execute("""SELECT Nachname, Vorname, ID FROM schueler WHERE Stufe = %s AND Klasse = %s""", (Stufe, Klasse))
    data=cursor.fetchall()
    data.sort()
    
    i=0
    while i<len(data):
        if data[i][2]==ID:
            next_i=(i+1)%len(data)
            next_ID=data[next_i][2]
            next_name=data[next_i][0]+", "+data[next_i][1]

            prev_i=i-1
            if i<0:
                prev_i=len(data)-1
                
            prev_ID=data[prev_i][2]
            prev_name=data[prev_i][0]+", "+data[prev_i][1]
        i+=1
    next_ID=cryption.encrypt(next_ID)
    prev_ID=cryption.encrypt(prev_ID)
    return (next_ID, next_name, prev_ID, prev_name)


def get_klassen():
    cursor, conn = re_connect()
    cursor.execute("SELECT Stufe FROM schueler t WHERE t.ID = (SELECT min(t1.ID) FROM schueler t1 WHERE t1.Stufe=t.Stufe)")
    data=cursor.fetchall()

    Klassen={}
    data=sorted(data)
    for i in data:
        Stufe=i[0]
        cursor.execute("SELECT Klasse FROM schueler t WHERE t.ID = (SELECT min(t1.ID) FROM schueler t1 WHERE t1.Klasse=t.Klasse AND Stufe=%s)", (Stufe,))
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


def schueler_by_class(klasse, fehlend=0, stufe_t=0):
    schueler=[]
    cursor, conn = re_connect()

    if klasse[0:2]!="J1" and klasse[0:2]!="J2":
        stufe=klasse[0:-1]
        klasse=klasse[-1:]
    else:
        stufe=klasse[0:2]
        klasse=""

    if fehlend==1:
        if stufe_t==1:
            cursor.execute("SELECT schueler.Vorname, schueler.Nachname, schueler.ID FROM schueler, buchstufe, ausgeliehen WHERE schueler.Stufe=%s AND buchstufe.stufe=schueler.Stufe AND schueler.ID=ausgeliehen.ID AND ausgeliehen.ISBN=buchstufe.ISBN AND buchstufe.abgeben=1 AND ausgeliehen.Anzahl>=1", (stufe,))
            data=cursor.fetchall()
        else:
            cursor.execute("SELECT schueler.Vorname, schueles.Nachname, schuler.ID FROM schueler, buchstufe, ausgeliehen WHERE schueler.Stufe=%s AND schueler.Klasse=%s AND buchstufe.stufe=schueler.Stufe AND schueler.ID=ausgeliehen.ID AND ausgeliehen.ISBN=buchstufe.ISBN AND buchstufe.abgeben=1 AND ausgeliehen.Anzahl>=1", (stufe, klasse))
            data=cursor.fetchall()
    else:
        cursor.execute("SELECT Vorname, Nachname, ID FROM schueler WHERE Stufe=%s AND Klasse=%s", (stufe, klasse))
        data=cursor.fetchall()

    data=list(dict.fromkeys(data))
    data.sort(key=lambda x:x[1])

    for list_l in data:
        list_l=list(list_l)
        list_l[2]=cryption.encrypt(list_l[2])
        list_l[0]=list_l[1]+", "+list_l[0]
        list_l.pop(1)
        schueler.append(list_l)

    #sortieren
    data=pd.DataFrame(schueler, columns=["Name", "Seite"])
    data["Seite"]=data["Seite"].apply(lambda x:'<form action="/" method="get"><input type="hidden" name="site" value="schueler"><input type="hidden" name="ID" value={0}><input type="submit" value="Seite"></form>'.format(x))
    return data


def search_schueler(name):
    schueler=[]
    cursor, conn = re_connect()
    cursor.execute("SELECT Vorname, Nachname, ID, Stufe, Klasse FROM schueler WHERE Nachname LIKE CONCAT('%', %s, '%')", (name,))
    data=cursor.fetchall()

    for list_l in data:
        list_l=list(list_l)
        list_l[2]=cryption.encrypt(list_l[2])
        list_l[0]=list_l[1]+", "+list_l[0]
        list_l[1]=list_l[3]+list_l[4]
        list_l.pop(3)
        list_l.pop(3)
        schueler.append(list_l)

    schueler.sort(key=lambda x:x[0])

    data=pd.DataFrame(schueler, columns=["Name", "Klasse", "Seite"])
    data["Seite"]=data["Seite"].apply(lambda x:'<form action="/" method="get"><input type="hidden" name="site" value="schueler"><input type="hidden" name="ID" value={0}><input type="submit" value="Seite"></form>'.format(x))
    return data

def search_settings(ISBN_Titel="", klasse="", stufe="", need_to_have=True):
    cursor, conn = re_connect()
    
    schueler=[]
    arguments=[]
    needed_and=False
    statement='SELECT schueler.Vorname, schueler.Nachname, schueler.ID, schueler.Stufe, schueler.Klasse, ausgeliehen.Anzahl FROM schueler, ausgeliehen WHERE '
    if stufe!="":
        statement+="schueler.Stufe = %s "
        arguments.append(stufe)
        needed_and=True
    if klasse!="":
        if needed_and==True:
            statement+="AND "
        statement+="schueler.Klasse = %s "
        arguments.append(klasse)
        needed_and=True
    
    if needed_and==True:
        statement+="AND "
    if need_to_have==True:
        statement+="ausgeliehen.ISBN = %s AND ausgeliehen.ID=schueler.ID AND ausgeliehen.Anzahl > 0"
        arguments.append(ISBN_Titel)


    cursor.execute(statement, arguments)
    data=cursor.fetchall()

    for list_l in data:
        list_l=list(list_l)
        list_l[2]=cryption.encrypt(list_l[2])
        list_l[0]=list_l[1]+", "+list_l[0]
        list_l[1]=list_l[3]+list_l[4]
        list_l[3]=list_l[5]
        list_l[4]=list_l[2]
        list_l.pop(5)
        schueler.append(list_l)

    schueler.sort(key=lambda x:x[0])

    data=pd.DataFrame(schueler, columns=["Name", "Klasse", "Seite", "Anzahl", "Zurückgeben"])
    data["Seite"]=data["Seite"].apply(lambda x:'<form action="/" method="get"><input type="hidden" name="site" value="schueler"><input type="hidden" name="ID" value={0}><input type="submit" value="Seite"></form>'.format(x))
    statement='<form action="/" method="get"><input type="hidden" name="site" value="save_specific"><input type="hidden" name="zu" value="%s"><input type="hidden" name="stufe" value="%s"><input type="hidden" name="klasse" value="%s">' % (ISBN_Titel, stufe, klasse)
    data["Zurückgeben"]=data["Zurückgeben"].apply(lambda x:statement+'<input type="hidden" name="ID" value="{0}"><input type="submit" value="Zurückgeben"></form>'.format(x))
    return data


def add_book_stufe(Stufe, ISBN, wielange=0):
    cursor, conn = re_connect()
    cursor.execute("INSERT INTO buchstufe (stufe, ISBN, abgeben) VALUES (%s, %s, %s)", (Stufe, ISBN, wielange))
    conn.commit()

def remove_book_stufe(Stufe, ISBN):
    cursor, conn = re_connect()
    cursor.execute("DELETE FROM buchstufe WHERE Stufe=%s AND ISBN=%s", (Stufe, ISBN))
    conn.commit()

def select_book_stufe(Stufe):
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, abgeben FROM buchstufe WHERE Stufe=%s", (Stufe,))
    data=cursor.fetchall()
    data=pd.DataFrame(data, columns=["Buch", "Wie lange"])
    data["del"]=data["Buch"]

    for index in data.iterrows():
        num=index[0]
        ISBN=data.iloc[num]["del"]

        temp='<form action="/" method="get"><input type="hidden" name="site" value="remove_stufe"><input type="hidden" name="stufe" value="%s"><input type="hidden" name="ISBN" value="%s"><input type="submit" value="X" id="remove_stufe"></form>' % (Stufe, ISBN)

        data.at[num, "del"]=temp

        cursor.execute("SELECT Titel FROM buecher WHERE ISBN=%s", (ISBN,))
        title=cursor.fetchall()
        if len(title)!=0:
            data.at[num, "Buch"]=title[0][0]

    data=data.sort_values(by="Buch")
    data.reset_index(drop=True, inplace=True)
    return data


def get_stufe():
    data=print_klassen()
    stufen=list(data.columns.values)     
    stufen=sorted(stufen)
    return stufen

def bemgeld(id):
    id=cryption.decrypt(id)
    cursor, conn = re_connect()
    cursor.execute("SELECT bemerkung, schaden FROM bemgeld WHERE ID=%s", (id,))
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
    cursor.execute("SELECT ID FROM bemgeld WHERE ID=%s", (id,))
    data=cursor.fetchall()
    if len(data)!=0:
        cursor.execute("UPDATE bemgeld SET bemerkung=%s, schaden=%s WHERE ID=%s", (bemerkung, geld, id))
        conn.commit()
    else:  
        cursor.execute("INSERT INTO bemgeld (ID, bemerkung, schaden) VALUES (%s, %s, %s)", (id, bemerkung, geld))
        conn.commit()


def book_usage():
    cursor, conn = re_connect()
    cursor.execute("SELECT ISBN, SUM(Anzahl) FROM ausgeliehen GROUP BY ISBN ORDER BY SUM(Anzahl) DESC")
    data=cursor.fetchall()
    buecher=pd.DataFrame(data, columns=["ISBN", "Anzahl"])
    for index in buecher.iterrows():#get Titel from ISBN
        num=index[0]
        ISBN=buecher.iloc[num]["ISBN"]

        
        cursor.execute("""SELECT Titel FROM buecher WHERE ISBN = %s""", (ISBN,))
        data=cursor.fetchall()
        if len(data)>0:
            Titel=data[0][0]

            buecher.at[num, "ISBN"]=Titel

    
    return buecher


def login(username, password):
    cursor, conn = re_connect()
    try:
        cursor.execute("SELECT hash FROM user WHERE username = %s", (username,))
        hash_d=cursor.fetchall()
        hash_d=hash_d[0][0]
        hash_input=hash_func(password)

        if str(hash_d)==str(hash_input):
            return True
        else:
            return False
    
    except:
        return False


def check_password_strength(passwd):
    SpecialSym =['$', '@', '#', '%']
    val = True
      
    if len(passwd) < 6:
        #length should be at least 6
        val = False
          
    if not any(char.isdigit() for char in passwd):
        #Password should have at least one numeral
        val = False
          
    if not any(char.isupper() for char in passwd):
        #Password should have at least one uppercase letter
        val = False
          
    if not any(char.islower() for char in passwd):
        #Password should have at least one lowercase letter
        val = False


    return val


def change_password(username, old_pass, new1_pass, new2_pass):
    cursor, conn = re_connect()
    cursor.execute("""SELECT hash FROM user WHERE username = %s""", (username,))
    database_pass=cursor.fetchall()[0][0]

    old_hash=hash_func(old_pass)
    if old_hash==database_pass:
        if new1_pass==new2_pass:
            if check_password_strength(new1_pass):
                new_pass_hash=hash_func(new1_pass)
                cursor.execute("""UPDATE user SET hash = %s WHERE username = %s""", (new_pass_hash, username))
                conn.commit()
            
                return 0
            else:
                return 3
        else:
            return 2
    else:
        return 1

def check_rechte(username):
    cursor, conn = re_connect()
    cursor.execute("SELECT privileges FROM user WHERE username=%s", (username,))
    data=int(cursor.fetchall()[0][0])
    return data