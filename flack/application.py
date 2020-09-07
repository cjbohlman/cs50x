import os
import requests

from flask import Flask, request, jsonify, render_template, session
from flask_socketio import SocketIO, emit
from collections import deque 
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwertyuiop"
socketio = SocketIO(app)

username_error_length_short = "Username must be longer than 3 characters."
username_error_length_long = "Username must be shorter than 21 characters."
min_length = 3
max_length = 20

channels = {}

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home", methods=["POST"])
def home():
    session["username"] = request.form.get("username")
    return render_template("home.html")

@app.route("/channel/<string:channel_name>", methods=["POST"])
def get_channel(channel_name):
    return jsonify({"success": True, "messages": channels['channel_name']})

# @socketio.on("new message")
# def add_message(data):
#     # Add message (should automatically pop if size = 100 messages)
#     channels[data["channel_name"]].append(data.message)
#     emit("announce message", {"data": data}, broadcast=True)

# @socketio.on("new channel")
# def add_channel(data):
#     # Add new channel if it doesn't exist
#     channel = data["channel_name"]
#     if channel not in channels:
#         channels[channel] = deque(maxlen=100)
#         emit("announce channel", {"data": channel}, broadcast=True)
