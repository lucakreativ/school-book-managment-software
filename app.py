from flask import Flask, render_template, request, redirect, session
import random
import time
import os


import cryption
import manage_data



max_time_in_m=10
max_time_in_s=max_time_in_m*60



random_string=""
for i in range(16):
    secret_integer=random.randint(0, 255)
    random_string+=(chr(secret_integer))

app = Flask(__name__)
app.secret_key=random_string



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
                schueler, buecher = manage_data.book_by_user(ID)
                next_ID, prev_ID = manage_data.next_schueler(ID)
                return render_template("schueler.html", tables=[schueler.to_html(escape=False), buecher.to_html(escape=False)], titles=["Test"], ID_next=next_ID, ID_prev=prev_ID, ID=ID)
        
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
            if klasse==None:
                data=manage_data.get_klassen()
                return render_template("klassen.html", tables=[data.to_html(escape=False)], titles=["Klassen"])
            else:
                data=manage_data.schueler_by_class(klasse)
                return render_template("student_class.html", tables=[data.to_html(escape=False)], titles=["Schueler"])


        elif site=="insert_book":
            verlag=request.args.get("verlag")
            ISBN=request.args.get("ISBN")
            titel=request.args.get("titel")
            preis=float(request.args.get("preis"))

            manage_data.insert_book(ISBN, titel, verlag, preis)
            return redirect("/?site=book_by_ISBN&ISBN=%s" % (ISBN))

        elif site=="insert":
            return render_template("insert.html")

        elif site=="book_by_ISBN":
            save=request.args.get("save")
            ISBN=request.args.get("ISBN")
            Titel=request.args.get("Titel")
            Verlag=request.args.get("verlag")
            preis=request.args.get("preis")

            if save=="1":
                manage_data.update_book(ISBN, Titel, Verlag, preis)

            data=manage_data.book_by_ISBN(ISBN)
            print(data)
            return render_template("book_by_ISBN.html", ISBN=data[0], Titel=data[1], Verlag=data[2], Preis=data[3])

        elif site=="save":
            ID_e=request.args.get("ID")
            ID=cryption.decrypt(ID_e)

            
            con=False
            i=0
            while con==False:
                ISBN=request.args.get("b"+str(i))
                Anzahl=request.args.get("a"+str(i))
                if ISBN!=None and Anzahl!=None:
                    manage_data.insert_taken_book_absolute(ID, ISBN, Anzahl)
                else:
                    con=True
                i+=1

            ISBN_zu=request.args.get("zu")
            ISBN_ei=request.args.get("ei")
            if ISBN_zu!="":
                manage_data.insert_taken_book_add(ID, ISBN_zu, str(-1))
            if ISBN_ei!="":
                manage_data.insert_taken_book_add(ID, ISBN_ei, str(1))
            return redirect("/?site=schueler&ID=%s" % (ID_e))


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
    if manage_data.login(username, password)==True:
        session["login"]=2
        session["login_time"]=time.time()
        session["user"]=username

        return(redirect("/"))

    else:
        return(redirect("/loginf"))



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


port=int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)