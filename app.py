from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///users.db")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Redirect root URL to login page
@app.route("/")
def home():
    return redirect(url_for("login"))  # Redirect to login page

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            return redirect(url_for("chat"))  # Redirect to chat after login
        else:
            return "Invalid credentials! Try again."

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists! Try another."

        # Save to database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/chat")
def chat():
    return "Welcome to the Chat!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
