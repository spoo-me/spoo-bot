from flask import Flask, jsonify
from threading import Thread
import subprocess

app = Flask("")


@app.route("/")
def home():
    return "Hello, I am alive"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "I am alive"}), 200


def run():
    try:
        server = subprocess.Popen(["gunicorn", "-w", "4", "api:app"])
        return server
    except:
        app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
