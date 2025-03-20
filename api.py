from flask import Flask, jsonify
from threading import Thread
import subprocess
from config import config

app = Flask("")


@app.route("/")
def home():
    return "Hello, I am alive"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "I am alive"}), 200


def run():
    """Run the Flask application with configured settings"""
    keep_alive_config = config.server.keep_alive
    try:
        if config.server.is_cloud_hosted:
            server = subprocess.Popen(
                [
                    "gunicorn",
                    "-w",
                    "4",  # 4 worker processes
                    "-b",
                    f"{keep_alive_config.host}:{keep_alive_config.port}",
                    "api:app",
                ]
            )
            return server
    except Exception:
        # Fallback to Flask development server
        app.run(host=keep_alive_config.host, port=int(keep_alive_config.port))


def keep_alive() -> None:
    """Start the keep-alive service if enabled in cloud environment"""
    if (
        config.server.environment != "development"
        and config.server.is_cloud_hosted
        and config.server.keep_alive.enabled
    ):
        t = Thread(target=run)
        t.start()
        print(
            f"Keep-alive service started on {config.server.keep_alive.host}:{config.server.keep_alive.port}"
        )
    else:
        print("Keep-alive service is disabled or not in cloud environment")
