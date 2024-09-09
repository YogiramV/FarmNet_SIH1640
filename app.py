from flask import Flask
from flask import render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://yogi:passwd@localhost/todo"

db = SQLAlchemy(app)

class Credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String, nullable=False)
    def __repr__(self):
        return f'<data {self.name}>'

# Create the database and tables
with app.app_context():
    db.create_all()


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/save", methods=['POST'])
def save():
    username = request.form['username']
    password = request.form['password']

    data = Credentials(
        name=username,
        password=password
    )

    db.session.add(data)
    db.session.commit()

    return render_template("login.html")

@app.route("/check", methods=['POST'])
def check_credentials():
    username = request.form['username']
    password = request.form['password']

    user = Credentials.query.filter_by(name=username).first()
    if user and user.password == password:
        return render_template("success.html")
    else:
        return render_template("failure.html")




