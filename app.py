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
            return "Startseite"

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



        elif site=="save":
            ID_e=request.args.get("ID")
            ID=cryption.decrypt(ID_e)

            ISBN_zu=request.args.get("zu")
            ISBN_ei=request.args.get("ei")
            print(ISBN_zu)
            print(ISBN_ei)
            if ISBN_zu!="":
                print("1")
                manage_data.insert_taken_book_absolute(ID, ISBN_zu, 0)
            if ISBN_ei!="":
                print("2")
                manage_data.insert_taken_book_absolute(ID, ISBN_ei, 1)

            con=False
            i=0
            while con==False:
                ISBN=request.args.get("b"+str(i))
                Anzahl=request.args.get("a"+str(i))
                if ISBN!=None and Anzahl!=None:
                    manage_data.insert_taken_book_absolute(ID, ISBN, Anzahl)
                else:
                    return redirect("/?site=schueler&ID=%s" % (ID_e))
                i+=1



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
    return True
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