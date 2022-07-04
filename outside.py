import os
import socket
import struct
from mysql.connector import MySQLConnection
from read_config import read_db_config

def re_connect():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    return cursor, conn

def check_data(user):
    cursor, conn = re_connect()
    try:
        cursor.execute("SELECT outside FROM user WHERE username='%s'" % (user))
        data=cursor.fetchall()[0][0]
        if data==1:
            return True
        else:
            return False
    
    except:
        return False

def check_ip(check_ip):

    sysip = os.popen("ip -o -f inet addr show | awk '/scope global/ {print $4}'").read()

    ip, net_bits = sysip.split('/')
    host_bits = 32 - int(net_bits)
    mask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))


    check_ip=''.join([bin(int(x)+256)[3:] for x in check_ip.split('.')])
    ip=''.join([bin(int(x)+256)[3:] for x in ip.split('.')])
    mask=''.join([bin(int(x)+256)[3:] for x in mask.split('.')])


    con=True
    i=0
    while con==True and i<len(ip):
        if check_ip[i]!=ip[i]:
            if mask[i]=="1":
                con=False

        i+=1

    return con