from mysql.connector import MySQLConnection
import pandas


from read_config import read_db_config


state="INSERT INTO schueler (ID, Stufe, Klasse, Vorname, Nachname, Religion, Fremdsp1, Fremdsp2, Fremdsp3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

def re_conn():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn

def delete():
    cursor, conn = re_conn()
    cursor.execute("DELETE FROM schueler")
    conn.commit()
    
def exe(data):
    cursor, conn = re_conn()

#['Klasse', 'Vornamen', 'Nachname', 'ID', 'Fremdsprache 1.', 'Fremdsprache 2.', 'Fremdsprache 3.', 'Religion', 'Alle besuchten Pflichtfächer']
#   0           1           2         3             4               5                   6               7                   8
    values=[]


    klasse=data[0]
    vorname=data[1]
    nachname=data[2]
    Sch_ID=data[3]
    frem1=data[4]
    frem2=data[5]
    frem3=data[6]
    religion=data[7]





    if klasse[0:2] != "J1" and klasse[0:2] != "J2":
        stufe=klasse[0:-1]
        klasse=klasse[-1:]
    else:
        stufe=klasse[0:2]
        klasse=""


    values.append(Sch_ID)
    values.append(stufe)
    values.append(klasse)
    values.append(vorname)
    values.append(nachname)
    values.append(religion)
    values.append(frem1)
    values.append(frem2)
    values.append(frem3)

    #print(values)

    cursor.execute(state, values)
    conn.commit()



def filename(name):
    try:
        delete()

        end=name[-6:]
        end=end.split(".")[1]

        if end=="xls" or end=="xlsx":
            df=pandas.read_excel(name, sheet_name=0)
        elif end=="csv":
            df=pandas.read_csv(name)

        df=df.fillna("")

        for index, rows in df.iterrows():
            data=[]
            for i in rows:
                data.append(i)

            exe(data)
    
    except Exception as e:
        return ("Problem, bitte melden: "+str(e), 1)

    else:
        return ("Schülerliste wurde aktualisiert.", 0)