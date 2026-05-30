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

    stage_text = "\n".join(
        [f"**{k}**: {v}%" for k, v in sorted(stats["stage_percent"].items())]
    )

    payload = {
        "embeds": [
            {
                "title": "📊 Game Analytics Dashboard",
                "color": 3447003,

                "fields": [
                    {
                        "name": "👥 Total Sessions",
                        "value": str(stats["total"]),
                        "inline": True
                    },
                    {
                        "name": "⏱ Avg Session Time",
                        "value": f"{stats['avg_time']} sec",
                        "inline": True
                    },
                    {
                        "name": "💀 Death Rate",
                        "value": f"{stats['died_percent']}%",
                        "inline": True
                    },
                    {
                        "name": "📍 Stage Completion",
                        "value": stage_text or "No data",
                        "inline": False
                    }
                ],

                "footer": {
                    "text": "Updated every 10 sessions"
                }
            }
        ]
    }

    requests.post(DISCORD_WEBHOOK_URL, json=payload)


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