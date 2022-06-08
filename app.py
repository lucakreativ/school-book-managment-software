from flask import Flask, render_template, request, redirect, session
import random
import time
import os

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
        pass





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