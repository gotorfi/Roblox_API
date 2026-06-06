import requests

FIREBASE_URL = "https://ruined-analytics-roblox-default-rtdb.europe-west1.firebasedatabase.app/sessions.json"

STAGES = [
    "Intro", "KeyCard", "Healed", "ForWaugh Appearance",
    "Mall Trigger", "PowerDoor", "Smilay Scene", "Smilay Death",
    "C.E.D. Appearance", "Theater", "AfterChase", "Levers",
    "Greta Puzzle", "Second Chase Intro", "Ending"
]

def fetch_sessions():
    data = requests.get(FIREBASE_URL, timeout=30).json()
    return list(data.values()) if data else []

def compute_stats(sessions):
    total = len(sessions)
    deaths = 0
    completed = 0
    total_time = 0

    stage_counts = {stage: 0 for stage in STAGES}

    for session in sessions:
        total_time += session.get("sessionTime", 0)

        if session.get("leftWhenDied"):
            deaths += 1

        stages = session.get("stages", {})

        if "Ending" in stages:
            completed += 1

        for stage in STAGES:
            if stage in stages:
                stage_counts[stage] += 1

    gave_up = total - deaths - completed

    avg_time = int(total_time / total) if total else 0

    return {
        "total": total,
        "deaths": deaths,
        "completed": completed,
        "gave_up": gave_up,
        "avg_time": avg_time,
        "stage_counts": stage_counts
    }