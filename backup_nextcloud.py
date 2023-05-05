import owncloud
import time
import os

from read_config import read_db_config, read_nextcloud_config


def export_database():
    dbconfig=read_db_config()
    file=str(round(time.time(), 2))+"-backup.sql"
    file_path="files/"+file
    os.system("mysqldump -u %s -p%s %s > %s" % (dbconfig["user"], dbconfig["password"], dbconfig["database"], file_path))
    return file, file_path


def upload(file, file_path, nextcloud_config, oc):
    oc.put_file(nextcloud_config["folder"]+file, file_path)

def delte_oldest(nextcloud_config, oc):
    files=oc.list(nextcloud_config["folder"])
    data=[]
    if len(files)>int(nextcloud_config["delete_if_more"]):
        for f in files:
            data.append(str(f))

        data.sort(reverse=True)

        to_delete=data[int(nextcloud_config["delete_if_more"]):]
        for i in to_delete:
            lower=i.find("path=")+5
            upper=i.find(",")
            path=i[lower:upper]
            oc.delete(path)

def make_backup():
    
    file, file_path=export_database()

    nextcloud_config = read_nextcloud_config()
    oc = owncloud.Client(nextcloud_config["adress"])
    oc.login(nextcloud_config["username"], nextcloud_config["password"])
    upload(file, file_path, nextcloud_config, oc)
    delte_oldest(nextcloud_config, oc)