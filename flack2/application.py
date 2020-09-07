import os
import requests

from flask import Flask, jsonify, render_template, request, abort, redirect, url_for, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwertyuiop"
socketio = SocketIO(app)

channel_names = []
channel_messages = {}
user_names = []

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")

@app.route("/home", methods=["POST", "GET"])
def home():
    if ("username" not in session):
        session["username"] = request.form.get("username")
    return render_template("index.html", channels=channel_names)

@app.route("/channel/<string:channel>")
def view_channel(channel: str):
    if not channel:
        abort(404)
    messages = channel_messages[channel]
    return render_template("index.html", channels=channel_names, messages=messages)

@app.route("/user/<string:user>", methods=["POST"])
def add_user(user: str):
    user_names.append(user)
    print(user_names)
    return ('', 200)

@app.route("/addchannel", methods=["POST", "GET"])
def add_channel():
    new_channel = request.form.get("new_channel")
    if not new_channel:
        abort(404)
    if new_channel not in channel_names:
        channel_names.append(new_channel)
        channel_messages[new_channel]  = []

        return redirect(url_for('home'))
        #return render_template("index.html", channels=channel_names)
    else:
        # channel name already exists
        abort(404)

@app.route("/chat", methods=["POST", "GET"])
def chat():
    print(user_names)
    return render_template("chat.html", users=user_names)

@socketio.on("new message")
def add_message(data):
    new_message = data["message"]
    user = data["user"]
    timestamp = data["timestamp"]
    channel_name = data["channel"]
    delete_message = False
    if channel_name in channel_messages:
        if len(channel_messages[channel_name]) >= 100:
            channel_messages[channel_name].pop(0)
            delete_message = True
        message = user + ": " + new_message + "\n" + timestamp
        # print("Message: "+ message)
        channel_messages[channel_name].append(message)
        message_dic = {}
        message_dic["user"] = user
        message_dic["message"] = new_message
        message_dic["channel"] = channel_name
        message_dic["timestamp"] = timestamp
        message_dic["delete_message"] = delete_message
        emit("announce_message", message_dic, broadcast=True)
    else:
        # channel does not exist
        return

@socketio.on("new user message")
def add_user_message(data):
    new_message = data["message"]
    from_user = data["from_user"]
    to_user = data["to_user"]
    timestamp = data["timestamp"]
    message_dic = {}
    message_dic["from_user"] = from_user
    message_dic["to_user"] = to_user
    message_dic["message"] = new_message
    message_dic["timestamp"] = timestamp
    emit("announce_user_message", message_dic, broadcast=True)