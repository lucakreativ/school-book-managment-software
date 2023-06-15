import xmltodict
import requests
import time
import os

from read_config import read_db_config, read_nextcloud_config


headers = {
    "Content-Type": "application/octet-stream",
    "Depth": "0"
}

PROPFIND_REQUEST='''<?xml version="1.0" encoding="UTF-8"?>
    <d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
      <d:prop>
        <nc:upload_time />
      </d:prop>
    </d:propfind>'''



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


def get_files(nextcloud_config):
    s=requests.Session()
    s.auth=(nextcloud_config["username"], nextcloud_config["password"])
    url=nextcloud_config["adress"]+"/remote.php/dav/files/"+nextcloud_config["username"]+"/"+nextcloud_config["folder"]+"/"
    r=s.request(method="PROPFIND", url=url, data=PROPFIND_REQUEST, headers={'Depth': '1'})
    if r.status_code == 207:
        data=r.text
        my_dict=xmltodict.parse(data)
        responses=my_dict["d:multistatus"]["d:response"]
        counter=0
        files=[]
        for i in responses:
            if counter>0:
                files.append([i["d:propstat"]["d:prop"]["nc:upload_time"], i["d:href"]])
            counter+=1

        files.sort(reverse=True)
        return files
    else:
        raise Exception("Das älteste Backup konnte nicht gelöscht werden.")
    

def delete_files(nextcloud_config):
    files=get_files(nextcloud_config)
    to_delete_files=files[int(nextcloud_config["delete_if_more"]):]
    for i in to_delete_files:
        url=nextcloud_config["adress"]+i[1]
        response=requests.delete(url=url, auth=(nextcloud_config["username"], nextcloud_config["password"]))
        if response.status_code!=204:
            raise Exception("Problem beim Löschen der Dateien")


def make_backup():
    nextcloud_config = read_nextcloud_config()

    if int(nextcloud_config["backup"])==1:
        file, file_path=export_database()
        
        upload(file, file_path, nextcloud_config)

        delete_files(nextcloud_config)
