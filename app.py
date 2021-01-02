import random
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
app = Flask(__name__)

with open("config.json") as f:
    params = json.load(f)["params"]

if params["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_server_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["pd_uri"]


db = SQLAlchemy(app)
app.config["SECRET_KEY"] = "secret_key"
show = False
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["GMAIL_USER"],
    MAIL_PASSWORD=params["GMAIL_PASSWORD"]
)
mail = Mail(app)
# contact: Random User ID Generator


def generateID(idlen):
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_&"
    ID = ""
    for i in range(idlen):
        ID += charset[random.randint(0, len(charset)-1)]
    return ID

# contact: A Counter class to add a counter to the contacts template


class _Counter(object):
    def __init__(self, start_value=1):
        self.value = start_value

    def current(self):
        return self.value

    def next(self):
        v = self.value
        self.value += 1
        return v


class Book1(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.Text, unique=True, nullable=False)
    tel = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=True)
    address = db.Column(db.Text, unique=False, nullable=True)
    color = db.Column(db.String(30), unique=False, nullable=False)
    date = db.Column(db.String(20), unique=True, nullable=True)


class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), unique=False, nullable=False)
    firstname = db.Column(db.String(30), unique=True, nullable=False)
    lastname = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(30), unique=True, nullable=False)
    date = db.Column(db.Date, unique=True, nullable=True)

# Create the tables
db.create_all()
db.session.commit()


@app.route("/")
def home():
    view = request.args.get("view")
    if view != None:
        session["view"] = view
    elif "view" not in session:
        session["view"] = "table"

    if "email" in session and "password" in session:
        user = User.query.filter_by(email=session["email"]).first()
        contacts = Book1.query.filter_by(userid=user.userid).all()
        if session["email"] == user.email and session["password"] == user.password:
            return render_template("index.html", params=params, contacts=contacts, show=show, view=session["view"], counter=_Counter(1), isLogin=True, user=user)
    return render_template("index.html", params=params, contacts=[], show=show, view=session["view"], isLogin=False, counter=_Counter(1), noaccesstype="disabled")


@app.route("/code-of-table")
def code():
    global show
    q = request.args.get("q")
    if q == "0":
        show = False
    else:
        show = True
    return redirect("/")


@app.route("/delete/<string:sno>", methods=["GET", "POST"])
def delete(sno):
    if "email" in session and "password" in session:
        user = User.query.filter_by(email=session["email"]).first()
        if session["password"] == user.password and session["userid"] == user.userid:
            if sno == "all":
                if request.method == "POST":
                    confirmation = request.form.get("confirmation")
                    confirmation = confirmation.lower()
                    if confirmation == "delete-all-contacts" or confirmation == "delete all contacts":
                        contacts = Book1.query.filter_by(
                            userid=user.userid).all()
                        for contact in contacts:
                            db.session.delete(contact)
                            db.session.commit()
                        return redirect("/")
                return render_template("delete-all.html", params=params)
            else:
                contactInfo = Book1.query.filter_by(sno=sno).first()
                if contactInfo.userid == user.userid:
                    db.session.delete(contactInfo)
                    db.session.commit()
                return redirect("/")
    else:
        return redirect("/login")


@app.route("/edit/<string:sno>", methods=["GET", "POST"])
def edit(sno):
    if "email" in session and "password" in session:
        user = User.query.filter_by(email=session["email"]).first()
        if session["email"] == user.email and session["password"] == user.password:
            contact = Book1.query.filter_by(sno=sno).first()
            if request.method == "POST":
                info = request.form
                name = info["name"]
                tel = info["tel"]
                email = info["email"]
                address = info["address"]
                color = info["color"]

                if sno == "0":
                    entry = Book1(userid=user.userid, name=name, tel=tel, date=datetime.now(),
                                  email=email, address=address, color=color)
                    db.session.add(entry)
                    db.session.commit()
                    return redirect("/")
                else:
                    contact = Book1.query.filter_by(sno=sno).first()
                    contact.name = name
                    contact.tel = tel
                    contact.email = email
                    contact.address = address
                    contact.color = color
                    db.session.commit()
                    return redirect("/")
            if sno != "0":
                if contact.userid == user.userid:
                    return render_template("edit.html", params=params, contact=contact, sno=sno)
                else:
                    return redirect("/edit/0")
            return render_template("edit.html", params=params, contact=contact, sno=sno)

    else:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user != None:
            if user.email == email and user.password == password:
                session["email"] = email
                session["password"] = password
                session["userid"] = user.userid
                name = f"{user.firstname} {user.lastname}"
                return redirect("/")
            else:
                return redirect("/login")
        else:
            return redirect("/login")
    return render_template("login.html", params=params)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    users = User.query.filter_by().all()
    if request.method == "POST":
        signupInfo = request.form
        firstname = signupInfo["firstname"]
        lastname = signupInfo["lastname"]
        email = signupInfo["email"]
        password = signupInfo["password"]
        repassword = signupInfo["repassword"]
        isExistUser = User.query.filter_by(email=email).first()
        name = f"{firstname} {lastname}"
        if isExistUser == None:
            if password == repassword:
                id_ = generateID(20)
                # mail.send_message("Your OTP to SignUp to ContactBook", sender=params["GMAIL_USER"],
                #                   recipients=[email], body=f"HELLO {name}! WELCOME TO Contact Book Site\nHere is your signup information => \nFirstname : {firstname}\nLastname : {lastname}\nEmail : {email}\nUserID / OTP : {id_}\nPlease Enter the OTP => {id_} to signup")
                # return redirect(f"/validation?fname={firstname}&lname={lastname}&email={email}&ps={password}&id_={id_}")
                newUserAccount = User(userid=id_,
                                      firstname=firstname, lastname=lastname, email=email, password=password, date=datetime.now())
                db.session.add(newUserAccount)
                db.session.commit()
                return redirect("/login")
            else:
                return render_template("signup.html", params=params, success=False, errorField=email, error="Password Doesn't match", tip="Please check your password.")
        else:
            return render_template("signup.html", params=params, success=False, errorField=email, errorFieldName="Email", error=" Account or Email Already exists!", tip="Please enter an another email to login!")
    return render_template("signup.html", users=users, params=params)

@app.route("/validation", methods=["GET", "POST"])
def validate():
    signupInfo = request.form
    firstname = request.args.get("fname")
    lastname = request.args.get("lname")
    email = request.args.get("email")
    password = request.args.get("ps")
    id_ = request.args.get("id_")
    name = f"{firstname} {lastname}"
    if request.method == "POST":
        userid2 = request.form.get('userid2')
        if id_ == userid2:
                newUserAccount = User(userid=id_,
                                      firstname=firstname, lastname=lastname, email=email, password=password, date=datetime.now())
                db.session.add(newUserAccount)
                db.session.commit()
                return redirect("/login")
        else:
            return redirect("/signup")
    return render_template("validation.html", params=params, email=email, name=name)
        
@app.route("/profile/<string:userid>", methods=["GET", "POST"])
def profile(userid):
    user = User.query.filter_by(userid=userid).first()
    if user.email == session["email"] and user.password == session["password"]:
        name = f"{user.firstname} {user.lastname}"
        if request.method == "POST":
            profileInfo = request.form
            firstname = profileInfo["firstname"]
            lastname = profileInfo["lastname"]
            password = profileInfo["password"]
            repassword = profileInfo["repassword"]
            user = User.query.filter_by(email=session["email"]).first()
            user.firstname = firstname
            user.lastname = lastname
            if password != "" and repassword != "":
                user.password = password
                session["password"] = password
            name = f"{user.firstname} {user.lastname}"
            db.session.commit()
            return render_template("profile.html", params=params, user=user, name=name)
        return render_template("profile.html", params=params, user=user, name=name)

@app.route("/logout")
def logout():
    session.pop("email")
    session.pop("password")
    session.pop("userid")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
