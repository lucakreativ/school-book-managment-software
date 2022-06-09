from configparser import ConfigParser


def read_db_config(filename='config.ini', section='mysql'):
    """ Liest die Konfigurationsdatei und gibt ein Dictionary Objekt zurück
    filename = Dateiname der Konfigurationsdatei
    section = Teil von der Konfigurationsdatei, der gelesen Werden soll
    """

    #erstellt den Parser und liest ini Konfigurationsdatei
    parser = ConfigParser()
    parser.read(filename)

    #bekommt Sektion, liest mysql-Teil
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db       #gibt Dictionary mit den Einträgen zurück


def read_aes_config(filename='config.ini', section='aes'):
    """ Liest die Konfigurationsdatei und gibt ein Dictionary Objekt zurück
    filename = Dateiname der Konfigurationsdatei
    section = Teil von der Konfigurationsdatei, der gelesen Werden soll
    """

    #erstellt den Parser und liest ini Konfigurationsdatei
    parser = ConfigParser()
    parser.read(filename)

    #bekommt Sektion, liest mysql-Teil
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db       #gibt Dictionary mit den Einträgen zurück