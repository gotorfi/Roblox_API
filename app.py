from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "analytics.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.route("/session", methods=["POST"])
def session():

    data = request.json

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
    app.run(host="0.0.0.0", port=5000)