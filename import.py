import csv
import mysql.connector


state="INSERT INTO schueler (ID, Stufe, Klasse, Vorname, Nachname, Religion, Fremdsp1, Fremdsp2, Fremdsp3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"


mydb = mysql.connector.connect(
  host="localhost",
  user="user",
  password="test",
  database="create_test"
)

mycursor = mydb.cursor()


with open("./export.csv", "r") as file:
    csvFile=csv.reader(file)
    next(csvFile)
    

#['Klasse', 'Vornamen', 'Nachname', 'ID', 'Fremdsprache 1.', 'Fremdsprache 2.', 'Fremdsprache 3.', 'Religion', 'Alle besuchten Pflichtfächer']
#   0           1           2         3             4               5                   6               7                   8
    for lines in csvFile:
        values=[]


        klasse=lines[0]
        vorname=lines[1]
        nachname=lines[2]
        Sch_ID=lines[3]
        frem1=lines[4]
        frem2=lines[5]
        frem3=lines[6]
        religion=lines[7]





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

        print(values)

        mycursor.execute(state, values)
        mydb.commit()
