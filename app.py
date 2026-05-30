from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

DATA_FILE = "analytics.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510203543783473214/VeZPvBnybCrTk4IYmOW78hSfQ5IF9jOXWvY_W23hJXKnlqfTbU-OH4xi7WURayszkmhw"

def load_sessions():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sessions(sessions):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=4)

def calculate_stats(sessions):

    total = len(sessions)
    if total == 0:
        return None

    avg_time = sum(s["sessionTime"] for s in sessions) / total
    died = sum(1 for s in sessions if s.get("leftWhenDied"))

    stage_counts = {}

    for s in sessions:
        for stage in s.get("stages", {}):
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

    stage_percent = {
        k: round((v / total) * 100, 1)
        for k, v in stage_counts.items()
    }

    return {
        "total": total,
        "avg_time": round(avg_time, 1),
        "died_percent": round((died / total) * 100, 1),
        "stage_percent": stage_percent
    }

def send_discord(stats):

    desc = f"""
    📊 **Analytics Summary**

    👥 Sessions: {stats['total']}
    ⏱ Avg time: {stats['avg_time']} sec
    💀 Death rate: {stats['died_percent']}%

    📍 Stage completion:
    """


    for stage, pct in sorted(stats["stage_percent"].items(), key=lambda x: x[0]):
        desc += f"- {stage}: {pct}%\n"

    payload = {
        "content": "",
        "embeds": [
            {
                "title": "📈 Game Analytics Report (Batch Update)",
                "description": desc,
                "color": 3447003
            }
        ]
    }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print("Discord send error:", e)


@app.route("/session", methods=["POST"])
def session():

    data = request.json

    sessions = load_sessions()
    sessions.append(data)
    save_sessions(sessions)

    print("Received session")

    if len(sessions) % 10 == 0:
        stats = calculate_stats(sessions)
        send_discord(stats)

    return jsonify({"success": True})


@app.route("/")
def home():
    return "Analytics server online"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)