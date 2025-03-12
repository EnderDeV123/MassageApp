from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Create tables
with app.app_context():
    db.create_all()


# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('chat'))
    return render_template('login.html')


# Chat Page
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')


# Provide username to JavaScript
@app.route('/get_username')
def get_username():
    if 'username' in session:
        return jsonify({'username': session['username']})
    return jsonify({'username': 'Anonymous'})


# Handle user messages
@socketio.on('message')
def handle_message(data):
    sender = session.get('username', 'Anonymous')
    content = data['message']

    # Save message to the database
    new_message = Message(sender=sender, content=content)
    db.session.add(new_message)
    db.session.commit()

    # Broadcast message to all clients
    send({'username': sender, 'message': content, 'timestamp': new_message.timestamp.strftime('%H:%M')}, broadcast=True)


# Load old messages when a user connects
@socketio.on('connect')
def handle_connect():
    messages = Message.query.order_by(Message.timestamp).all()
    for msg in messages:
        send({'username': msg.sender, 'message': msg.content, 'timestamp': msg.timestamp.strftime('%H:%M')})


# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    socketio.run(app, debug=True)
