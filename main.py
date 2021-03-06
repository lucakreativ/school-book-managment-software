from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import random
import time
import os


import login_v
import cryption
import constants
import import_data
import manage_data

from write_protocol import write_login



max_time_in_m=10
max_time_in_s=max_time_in_m*60



random_string=""
for i in range(16):
    secret_integer=random.randint(0, 255)
    random_string+=(chr(secret_integer))

app = Flask(__name__)
app.secret_key=random_string

app.config["UPLOAD_FOLDER"] = "files/"


@app.route("/")
def home():
    if not check_login():
        return (redirect("/login"))
    else:
        site=request.args.get("site")
        if site==None:
            return render_template("main.html")

        elif site=="schueler":
            ID=request.args.get("ID")
            if ID==None:
                return "Schueler auswählen"
            else:
                if check_rechte(0):
                    dis=""
                else:
                    dis="disabled"

                bemerkung, geld = manage_data.bemgeld(ID)
                schueler, buecher = manage_data.book_by_user(ID)
                next_ID, next_name, prev_ID, prev_name = manage_data.next_schueler(ID)
                return render_template("schueler.html", tables=[schueler.to_html(escape=False), buecher.to_html(escape=False)], titles=["Test"], ID_next=next_ID, ne_name=next_name, ID_prev=prev_ID, vor_name=prev_name, ID=ID, dis=dis, bemerkung=bemerkung, geld=geld)
        
        elif site=="search":
            name=request.args.get("term")
            if name==None:
                return render_template("search_student.html")
            else:
                schueler=manage_data.search_schueler(name)
                return render_template("search_student.html", tables=[schueler.to_html(escape=False)], titles=["Schueler"], term=name)

        elif site=="books":
            search=request.args.get("search")
            
            if search==None:
                data=manage_data.print_books()
                return render_template("book.html", search="", tables=[data.to_html(escape=False)], titles=["Bücher"])

            else:
                data=manage_data.search_book(search)
                return render_template("book.html", search=search, tables=[data.to_html(escape=False)], titles=["Bücher"])

        elif site=="klassen":
            klasse=request.args.get("k")
            b=request.args.get("b")
            if b=="1":
                manage_data.get_klassen()
                
            if klasse==None:
                data=manage_data.print_klassen()
                return render_template("klassen.html", tables=[data.to_html(escape=False)], titles=["Klassen"])
            else:
                data=manage_data.schueler_by_class(klasse)
                return render_template("student_class.html", tables=[data.to_html(escape=False)], titles=["Schueler"])

        elif site=="fbuch":
            if check_rechte(0):
                stufe=request.args.get("stufe")
                if stufe==None:
                    data=manage_data.get_stufe()
                    return render_template("stufen.html", klassen=data, site="fbuch", titel="Fehlende Bücher")
                else:
                    data=manage_data.schueler_by_class(stufe+"a", 1, 1)
                    return render_template("student_class.html", tables=[data.to_html(escape=False)], titles=["Schueler"])
            else:
                return render_template("rechte_un.html")


        elif site=="insert_book":
            verlag=request.args.get("verlag")
            ISBN=request.args.get("ISBN")
            titel=request.args.get("titel")
            preis=request.args.get("preis")
            Fach=request.args.get("Fach")
            if preis=="":
                preis=0

            msg="Buch wurde hinzugefügt"
            try:
                manage_data.insert_book(ISBN, titel, verlag, Fach, preis)
            except:
                msg="ISBN wurde schon vergeben"
            return redirect("/?site=book_by_ISBN&ISBN=%s&msg=%s" % (ISBN, msg))

        elif site=="insert":
            return render_template("insert.html", religion=constants.faecher)

        elif site=="book_by_ISBN":
            save=request.args.get("save")
            ISBN=request.args.get("ISBN")
            Titel=request.args.get("Titel")
            Verlag=request.args.get("verlag")
            preis=request.args.get("preis")
            Fach=request.args.get("Fach")
            msg=request.args.get("msg")
            if msg==None:
                msg=""

            if save=="1":
                if Fach==None:
                    Fach=""
                manage_data.update_book(ISBN, Titel, Verlag, preis, Fach)

            data=manage_data.book_by_ISBN(ISBN)
            if data[4]=="":
                fachn="Kein Religionsbuch"
            else:
                fachn=data[4]

            return render_template("book_by_ISBN.html", ISBN=data[0], Titel=data[1], Verlag=data[2], Preis=data[3], msg=msg, Fach=data[4], Fachn=fachn, faecher=constants.faecher)

        elif site=="stufe":
            if check_rechte(0):
                stufe=request.args.get("stufe")
                if stufe==None:
                    data=manage_data.get_stufe()
                    return render_template("stufen.html", klassen=data, site="stufe", titel="Stufenverwaltung")
                else:
                    bekommen, abgeben=manage_data.select_book_stufe(stufe)
                    return render_template("stufe_exakt.html", Stufe=stufe, tables=[bekommen.to_html(escape=False), abgeben.to_html(escape=False)], titles=["Bücher", "Bekommen", "Abgeben"])
            else:
                return render_template("rechte_un.html")

        elif site=="remove_stufe":
            if check_rechte(0):
                stufe=request.args.get("stufe")
                ISBN=request.args.get("ISBN")
                ab=request.args.get("ab")
                manage_data.remove_book_stufe(stufe, ISBN, ab)
                return redirect("/?site=stufe&stufe="+stufe)
            else:
                return redirect("/?site=stufe")
        
        elif site=="add_stufe":
            if check_rechte(0):
                stufe=request.args.get("stufe")
                ISBN=request.args.get("ISBN")
                manage_data.add_book_stufe(stufe, ISBN)
                return redirect("/?site=stufe&stufe="+stufe)
            else:
                return redirect("/?site=stufe")

        elif site=="re_stufe":
            if check_rechte(0):
                stufe=request.args.get("stufe")
                ISBN=request.args.get("ISBN")
                manage_data.add_book_stufe(stufe, ISBN, 1)
                return redirect("/?site=stufe&stufe="+stufe)
            else:
                return redirect("/?site=stufe")

        elif site=="execute_stufe":
            user=user_get()
            if check_rechte(0):
                stufe=request.args.get("stufe")
                manage_data.execute_stufe(user)
                return redirect("/?site=stufe&stufe="+stufe)
            else:
                return redirect("/?site=stufe")

        elif site=="save":
            ID_e=request.args.get("ID")
            ID=cryption.decrypt(ID_e)
            user=user_get()
            
            con=False
            i=0
            while con==False:
                ISBN=request.args.get("b"+str(i))
                Anzahl=request.args.get("a"+str(i))
                if ISBN!=None and Anzahl!=None:
                    manage_data.insert_taken_book_absolute(ID, ISBN, user, Anzahl)
                else:
                    con=True
                i+=1

            ISBN_zu=request.args.get("zu")
            ISBN_ei=request.args.get("ei")
            if ISBN_zu!="" and ISBN_zu!=None:
                manage_data.insert_taken_book_add(ID, ISBN_zu, user, str(-1))
            if ISBN_ei!="" and ISBN_ei!=None:
                manage_data.insert_taken_book_add(ID, ISBN_ei, user, str(1))

            if check_rechte(0):
                geld=request.args.get("geld")
                bemerkung=request.args.get("bemerkung")
                if geld!=None and bemerkung!=None:
                    manage_data.bemgeld_up(ID_e, bemerkung, geld)

            return redirect("/?site=schueler&ID=%s" % (ID_e))


        elif site=="admin":
            if check_rechte(0):
                msg=session.get("msg")
                farbe=session.get("farbe")
                

                if farbe==0:
                    farbe="green"
                elif farbe==1:
                    farbe="red"

                if msg==None:
                    msg=""
                    
                session["msg"]=None
                session["farbe"]=None

                return render_template("admin.html", msg=msg, farbe=farbe)
            else:
                return render_template("rechte_un.html")

        elif site=="settings":                      #Einstllungen werden aufgerufen
            message=request.args.get("message")     #Nachricht die angezeigt werden soll wird geholt
            if message!=None:                       #Wenn es eine gibt
                if message=="0":                    #0=Erfolgreich
                    me="Passwort wurde erfolgreich geändert"
                elif message=="1":                  #1=Fehler
                    me="Altes Passwort stimmt nicht überein"
                elif message=="2":                  #2=Fehler
                    me="Die neuen Passwörter stimmen nicht überein"

                return render_template("settings.html", Message=me)     #laden der HTML-Seite mit der Nachricht

            else:                                                       #wenn keine mitgegeben wird
                return render_template("settings.html")                 #laden der HTML-Seite ohne Nachricht


        elif site=="logout":                #ausloggen wird aufgerufe
            session.clear()                 #alle Daten werden gelöscht
            return(redirect("/login"))      #wird zur Login-Seite weitergeleitet

        else:                               #keine gültige Seite wurde aufgerufen
            return("Seite nicht gefunden")  #404-Page wird angezeigt


@app.route("/save_file", methods=["POST"])
def save_file():
    if check_login:
        if check_rechte(0):
            username=session.get("user")

            f=request.files["file"]
            filename=secure_filename(f.filename)
            filename=str(round(time.time(), 2))+"-"+username+"-"+filename
            path=app.config["UPLOAD_FOLDER"]+filename
            f.save(path)

            msg, farbe=import_data.filename(path)
            session["msg"]=msg
            session["farbe"]=farbe
            manage_data.get_klassen()
            return redirect("/?site=admin")

        else:
            return redirect("/?site=admin")
    else:
        return redirect("/login")

@app.route("/save_setting", methods=["POST"])       #Änderungen werden gepseichert und mit der Methode Post übergeben
def save_settting():                                #wird ausgeführt, wenn @app.route richtig ist
    if check_login():                               #überprüft, ob der Nutzer eingeloggt ist
        username=session["user"]                    #bekommt den angemeldeten Benutzer
        olrder=request.form.get("order")            #was geändert werden soll
        old_pass=request.form.get("old_pass")       #altes Passwort zu verifizierung
        new1_pass=request.form.get("new1_pass")     #neues Passwort
        new2_pass=request.form.get("new2_pass")     #neues Passwort wiederholung

        re=manage_data.change_password(username, old_pass, new1_pass, new2_pass)   #Übergibt die Werte und bekommt message zurück

        return redirect("/?site=settings&message=%s" % (re))                    #wird zu Eintellungen weitergeleitet und message wird übergeben
    
    else:                                   #wenn man nicht eingeloggt ist
        return redirect("/login")           #wird man zur Login-Seite weitergeleitet


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loginf")
def loginf():
    return render_template("loginf.html")



@app.route("/validate", methods=["POST"])
def validate():
    username=request.form.get("username")
    password=request.form.get("password")
    ip_addr = request.remote_addr
    if login_v.abfragen(ip_addr):
        if manage_data.login(username, password)==True:
            if (login_v.check_ip(ip_addr)==False and login_v.check_data(username)==True) or login_v.check_ip(ip_addr)==True:

                write_login(username, 1, ip_addr)
                session["login"]=2
                session["login_time"]=time.time()
                session["user"]=username

                return(redirect("/"))
            else:
                write_login(username, 0, ip_addr)
                return(redirect("/loginf"))

        else:
            write_login(username, 0, ip_addr)
            return(redirect("/loginf"))
    else:
        return("Zu viele Versuche: Bitte warten Sie ca. 10 Minuten")



def check_login():
    if session.get("login")==2:
        if check_inactivity()==True:
            return True
        else:
            return False

    else:
        return False

def check_inactivity():
    delta=time.time()-float(session.get("login_time"))
    if delta<max_time_in_s:
        session["login_time"]=time.time()
        return True
    else:
        return False

def check_rechte(erford):
    username=session.get("user")
    if erford>=manage_data.check_rechte(username):
        return True
    else:
        return False

def user_get():
    username=session.get("user")
    return username

port=int(os.environ.get("PORT", 5100))
app.run(host="0.0.0.0", port=port)