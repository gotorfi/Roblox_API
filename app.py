from flask import Flask, request, jsonify
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "analytics.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510203543783473214/VeZPvBnybCrTk4IYmOW78hSfQ5IF9jOXWvY_W23hJXKnlqfTbU-OH4xi7WURayszkmhw"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)
def send_discord_message(message):

    try:
        requests.post(
            DISCORD_WEBHOOK_URL,
            json={
                "content": message
            },
            timeout=10
        )

    except Exception as e:
        print(f"Discord error: {e}")


@app.route("/session", methods=["POST"])
def session():

    data = request.json

    print(json.dumps(data, indent=4))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sessions = json.load(f)

    sessions.append(data)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=4)

    print("Received session")

    return jsonify({
        "success": True
    })

@app.route("/")
def home():
    return "Analytics server online"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



