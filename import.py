import csv
import mysql.connector


with open("./export.csv", "r") as file:
    csvFile=csv.reader(file)

    next(csvFile)

#['Klasse', 'Vornamen', 'Nachname', 'ID', 'Fremdsprache 1.', 'Fremdsprache 2.', 'Fremdsprache 3.', 'Religion', 'Alle besuchten Pflichtfächer']
#   0           1           2         3             4               5                   6               7                   8
    for lines in csvFile:
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