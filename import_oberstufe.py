from mysql.connector import MySQLConnection
import camelot
import difflib
import pandas


from read_config import read_db_config


def re_conn():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn



def insert_student(schueler_ID, Vorname, Nachname, leistungsfach, basisfach, jahr):
    cursor, conn = re_conn()

    leistungsfachs=""
    for i in leistungsfach:
        leistungsfachs+=i+", "


    basisfachs=""
    for i in basisfach:
        basisfachs+=i+", "

    cursor.execute("INSERT INTO oberstufe (vorname, nachname, l, m, studentid, abiturjahr) VALUES ('%s', '%s', '%s', '%s', '%s', %s)" % (Vorname, Nachname, leistungsfachs, basisfachs,schueler_ID, jahr))
    conn.commit()


def find_student(stufe, vorname, nachname, leistungsfach, basisfach, jahr):
    cursor, conn = re_conn()

    name=vorname+" "+nachname

    cursor.execute("SELECT ID, Vorname, Nachname FROM schueler WHERE Stufe='%s' " % (stufe))
    data=cursor.fetchall()
    i=0

    test_namen={}
    while i<len(data):
        student_test=data[i]
        test_name=student_test[1]+" "+student_test[2]
        test_namen[test_name]=student_test[0]
        i+=1

    closest=difflib.get_close_matches(name, test_namen, n=1, cutoff=0.1)[0]
    id=test_namen[closest]

    cursor.execute("SELECT Nachname, Vorname FROM schueler WHERE ID='%s' " % (id))
    data=cursor.fetchall()[0]
    vorname=data[1]
    nachname=data[0]

    insert_student(id, vorname, nachname, leistungsfach, basisfach, jahr)

def Oberstufe(path, stufe, abschlussjahr):
    pdf=camelot.read_pdf(path)
    dataframe=pdf[0].df


    try:
        i=2
        max_column=len(list(dataframe.columns))
        Faecher=[]
        while i<max_column:
            Faecher.append(dataframe.loc[0, i])
            i+=1

        i=1
        while True:
            name=dataframe.loc[i, 0][4:]
            name=name.split(",")
            vorname=name[1][1:]
            nachname=name[0]

            j=3

            liste_Faecher=[]
            while j<max_column:
                if dataframe.loc[i+1, j]=="?":
                    liste_Faecher.append(j)

                j+=1

            leistun_Fach=[]
            basis_Fach=[]
            for k in liste_Faecher:
                art_fach=dataframe.loc[i, k]
                if art_fach!="":
                    if art_fach[0]=="L":
                        leistun_Fach.append(Faecher[k-3])
                    else:
                        basis_Fach.append(Faecher[k-3])
                else:
                    basis_Fach.append(Faecher[k-3])

            i+=2

            
            find_student(stufe, vorname, nachname, leistun_Fach, basis_Fach, abschlussjahr)

    except Exception as e:
        print("Fehler:",e)


Oberstufe("../J1.pdf", "J1", 2024)