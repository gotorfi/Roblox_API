from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

FIREBASE_URL = "https://ruined-analytics-roblox-default-rtdb.europe-west1.firebasedatabase.app/sessions.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510203543783473214/VeZPvBnybCrTk4IYmOW78hSfQ5IF9jOXWvY_W23hJXKnlqfTbU-OH4xi7WURayszkmhw"
session_count = 0

def save_session_to_firebase(session):
    requests.post(FIREBASE_URL, json=session)

def load_sessions():
    r = requests.get(FIREBASE_URL)
    print("FIREBASE RAW:", r.text)
    if r.status_code != 200:
        return []
    
    data = r.json()
    if not data:
        return []
    return list(data.values())

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
                    {"name": "👥 Sessions", "value": str(stats["total"]), "inline": True},
                    {"name": "⏱ Avg Time", "value": f"{stats['avg_time']} sec", "inline": True},
                    {"name": "💀 Death Rate", "value": f"{stats['died_percent']}%", "inline": True},
                    {"name": "📍 Stages", "value": stage_text or "No data"}
                ]
            }
        ]
    }

    requests.post(DISCORD_WEBHOOK_URL, json=payload)

@app.route("/session", methods=["POST"])
def session():

    global session_count

    data = request.json

    # save to firebase
    save_session_to_firebase(data)

    sessions = load_sessions()
    session_count = len(sessions)

    print("SESSION RECEIVED:", session_count)

    # every 10 sessions → analytics
    if session_count % 10 == 0:
        sessions = load_sessions()
        stats = calculate_stats(sessions)

        if stats:
            send_discord(stats)

    return jsonify({"success": True})