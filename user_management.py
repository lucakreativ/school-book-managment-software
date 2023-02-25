from mysql.connector import MySQLConnection
from read_config import read_db_config
from hash_func import hash_func

import cryption

import pandas as pd

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn

def show_one_user(username):
    cursor, conn = re_connect()
    cursor.execute("SELECT username, privileges, outside FROM user WHERE username='%s'" % (username))
    data=cursor.fetchall()[0]

    if data[2]==0:
        zero="selected"
        one=""
    else:
        zero=""
        one="selected"

    pandas_temp=[]
    pandas_temp.append("""<input type="hidden" name="username" value="%s">%s""" % (data[0], data[0]))
    pandas_temp.append("""<input type="number" name="privileges" value="%s">""" % (data[1]))
    pandas_temp.append("""<select name="outside">
                            <option value="0" %s>Nein</option>
                            <option value="1" %s>Ja</option>
                            </select>""" % (zero, one))
    pandas_temp.append("""<input type="submit" value="Speichern" id="usersp"><br><input type="reset" value="Zurücksetzen"></form>""")
    pandas_temp.append("""<form action="/admin" method="post"><input type="hidden" name="site" value="deleteuser"><input type="hidden" name="username" value="%s"><input type="submit" value="Benutzer löschen"></form>""" % (username))
    df=pd.DataFrame([pandas_temp], columns=["Benutzername", "Rechte", "Außen", "", ""])

    return df

def edit_user_data(username, privileges, outside):
    cursor, conn = re_connect()
    cursor.execute("UPDATE user SET privileges=%s, outside=%s WHERE username='%s'" % (privileges, outside, username))
    conn.commit()


def show_user_data():
    cursor, conn = re_connect()

    cursor.execute("SELECT username, privileges, outside FROM user WHERE username!='admin'")
    data=cursor.fetchall()
    data=sorted(data)
    df=pd.DataFrame(data, columns=["Benutzername", "Rechte", "Außen*"])
    
    for index in df.iterrows():
        num=index[0]
        number_outside=df.iloc[num]["Außen*"]
        if number_outside==0:
            df.at[num, "Außen*"]='<input type="checkbox" onclick="return false;">'
        else:
            df.at[num, "Außen*"]='<input type="checkbox" onclick="return false;" checked>'

        
        benutzername=df.iloc[num]["Benutzername"]
        df.at[num, "PW zurücksetzen"]="""<input type="submit" value="Passwort zurücksetzen" id="admin_reset_password" onclick="confirmf('%s')">""" % (benutzername)
        df.at[num, "Bearbeiten/Löschen"]="""<form action="/admin" method="post"><input type="hidden" name="site" value="bea"><input type="hidden" name="username" value="%s"><input type="submit" value="Bearbeiten/Löschen" id="admin_bea_losch"></form>""" % (benutzername)
    
    return df


def create_user(username, privileges, outside):
    cursor, conn = re_connect()

    password=cryption.generate_password(8)

    hash=hash_func(password)

    cursor.execute("INSERT INTO user VALUES ('%s', '%s', %s, %s)" % (username, hash, privileges, outside))
    conn.commit()

    return password


def delete_user(username):
    cursor, conn = re_connect()
    cursor.execute("DELETE FROM user WHERE username='%s'" % (username))
    conn.commit()


def update_user(oldusername, username, privileges, outside):
    cursor, conn = re_connect()

    cursor.execute("UPDATE user SET username='%s', privileges=%s, outside=%s WHERE username='%s'" % (username, privileges, outside, oldusername))
    conn.commit()


def reset_password(username):
    cursor, conn = re_connect()
    
    password=cryption.generate_password(8)
    hash=hash_func(password)

    cursor.execute("UPDATE user SET hash='%s' WHERE username='%s'" % (hash, username))
    conn.commit()

    return password
