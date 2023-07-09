from mysql.connector import MySQLConnection
from datetime import datetime

import time
import os

from read_config import read_db_config


def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn

cursor, conn = re_connect()

min=120
oldest_min=60*min

how_many=10

def get_data():
    cursor.execute("SELECT * FROM protocolaus WHERE unix>%s ORDER BY unix ASC", (time.time()-oldest_min,))
    data=cursor.fetchall()
    conn.commit()
    return data

def return_data(data):
    users={}
    klassen=[]
    protocoll=[]

    for i in data:
        if i[1]==0:
            user=i[6]
            userID=i[2]
            time=datetime.utcfromtimestamp(i[5]).strftime('%H:%M:%S')
            cursor.execute("SELECT Stufe, Klasse, Nachname, Vorname FROM schueler WHERE ID=%s", (userID,))
            userInfo=cursor.fetchone()



            protocoll.append([str(time), str(userInfo[0]+userInfo[1]),str(userInfo[2]+", "+userInfo[3]),str(user),str(i[3]), str(i[4])])

            if user not in users:
                users[user]=1
            else:
                users[user]+=1

    return users, protocoll[-how_many:]

def make_box(data, title):
    rows=[]
    max_length=[]
    for i in data[0]:
        max_length.append(0)

    for i in data:
        counter=0
        for j in i:
            if len(j)>max_length[counter]:
                max_length[counter]=len(j)

            counter+=1

    rows_char=0
    for i in max_length:
        rows_char+=i
        
    rows_char+=len(max_length)*3-1

    rows.append(title)
    chars_print="+"
    for i in range(rows_char):
        chars_print+="-"
    chars_print+="+ "
    rows.append(chars_print)
    chars_print=""

    for i in data:
        chars_print+="| "
        counter=0
        for j in i:
            padding=max_length[counter]-len(j)
            #print(padding)
            for k in range(padding):
                chars_print+=" "
            chars_print+=j+" | "

            counter+=1
        
        rows.append(chars_print)
        chars_print=""


    chars_print+="+"
    for i in range(rows_char):
        chars_print+="-"
    chars_print+="+ "
    rows.append(chars_print)
    return rows


def users_ani(users):
    users=sorted(users.items(), key=lambda x:x[1], reverse=True)
    users_str=[]
    for i in users:
        data=[]
        for j in i:
            data.append(str(j))

        users_str.append(data)

    title="Bücher pro Benutzer:"
    rows=make_box(users_str, title)
    return rows


def add_rows(rows, rows_sec):
    if len(rows_sec)>len(rows):
        rows, rows_sec = rows_sec, rows

    counter=0
    offset=len(rows)-len(rows_sec)
    padding="   "
    while counter<len(rows_sec):
        rows[counter+offset]+=padding+rows_sec[counter]
        counter+=1

    return rows

while True:
    start=time.time()
    data=get_data()
    #print(data)
    users, protocoll=return_data(data)
    if len(protocoll)>0:
        rows=make_box(protocoll, "Die letzten %s Protokolleinträge:" % (how_many))
        rows_sec=users_ani(users)

        rows=add_rows(rows, rows_sec)



        #Printen
        os.system("clear")
        print("\033[1mDaten für die letzten %s Minuten:\033[0m \n" % (min))
        for i in rows:
            print(i)

    else:
        print("Keine aktuellen Daten gefunden.\n")




    diff=time.time()-start
    to_stop=1-diff
    if to_stop>0:  
        time.sleep(to_stop)