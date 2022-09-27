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
    
    return df


def exact_user(username):
    cursor, conn = re_connect()
    cursor.execute("SELECT username, privileges, outside FROM user WHERE username='%s'" % (username))
    df=pd.DataFrame(cursor.fetchall(), columns=["Bentuzername", "Rechte", "Außen*"])
    return df


def create_user(username, privileges, outside):
    cursor, conn = re_connect()

    password=cryption.generate_password(8)

    hash=hash_func(password)

    cursor.execute("INSERT INTO user ('%s', '%s', '%s', '%s')" % (username, password, privileges, outside))
    conn.commit()


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

    cursor.execute("UPDATE user SET password='%s' WHERE username='%s'" % (password, username))
    conn.commit()

    return password
