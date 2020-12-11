from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/contacts-book'
db = SQLAlchemy(app)

class Book1(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), unique=True, nullable=False)
    tel = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=True)
    address = db.Column(db.Text, unique=True, nullable=True)
    date = db.Column(db.String(20), unique=True, nullable=True)
    
show = False
@app.route("/")
def contacts():
    contacts = Book1.query.filter_by().all()
    return render_template("index.html", contacts=contacts, show=show)

@app.route("/edit/<string:sno>", methods=["GET", "POST"])
def add(sno):
    contact = Book1.query.filter_by(sno=sno).first()
    if request.method == "POST":
        info = request.form
        name = info["name"]
        tel = info["tel"]
        email = info["email"]
        address = info["address"]
        
        if sno == "0":
            entry = Book1(name=name, tel=tel, date=datetime.now(), email=email, address=address)
            db.session.add(entry)
            db.session.commit()
            return redirect("/")
        else:
            contact = Book1.query.filter_by(sno=sno).first()
            contact.name = name
            contact.tel = tel
            contact.email = email
            contact.address = address
            db.session.commit()
            return redirect("/")
    return render_template("edit.html", sno=sno, contact=contact)

@app.route("/code-of-table")
def code():
    global show
    show = True
    return redirect("/")

@app.route("/delete/<string:sno>")
def delete(sno):
    contactInfo = Book1.query.filter_by(sno=sno).first()
    db.session.delete(contactInfo)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)