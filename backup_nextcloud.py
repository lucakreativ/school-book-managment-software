import requests
import time
import os

from read_config import read_db_config, read_nextcloud_config


headers = {
    "Content-Type": "application/octet-stream",
    "Depth": "0"
}



def export_database():
    dbconfig=read_db_config()
    file=str(round(time.time(), 2))+"-backup.sql"
    file_path="files/"+file
    os.system("mysqldump -u %s -p%s %s > %s" % (dbconfig["user"], dbconfig["password"], dbconfig["database"], file_path))
    return file, file_path


def upload(file, file_path, nextcloud_config):
    with open(file_path, "rb") as f:
        response = requests.put(nextcloud_config["adress"]+"/remote.php/dav/files/"+nextcloud_config["username"]+"/"+nextcloud_config["folder"]+file, auth=(nextcloud_config["username"], nextcloud_config["password"]), headers=headers, data=f)
        if response.status_code!=201:
            raise Exception("Es konnte kein Backup hochgeladen werden")




def make_backup():
    
    file, file_path=export_database()

    nextcloud_config = read_nextcloud_config()
    
    upload(file, file_path, nextcloud_config)
