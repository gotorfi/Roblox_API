import requests
import os

FIREBASE_URL = os.getenv("FIREBASE_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

STAGES = [
    "Intro",
    "KeyCard",
    "Healed",
    "ForWaugh Appearance",
    "Mall Trigger",
    "PowerDoor",
    "Smilay Scene",
    "Smilay Death",
    "C.E.D. Appearance",
    "Theater",
    "AfterChase",
    "Levers",
    "Greta Puzzle",
    "Second Chase Intro",
    "Ending"
]

EMOJIS = {
    "Intro": "🎁",
    "KeyCard": "💳",
    "Healed": "🩹",
    "ForWaugh Appearance": "🤖",
    "Mall Trigger": "🏬",
    "PowerDoor": "🚧",
    "Smilay Scene": "🧿",
    "Smilay Death": "🩻",
    "C.E.D. Appearance": "💡",
    "Theater": "🧸",
    "AfterChase": "🔦",
    "Levers": "🎛️",
    "Greta Puzzle": "🧰",
    "Second Chase Intro": "🔪",
    "Ending": "🎉"
}

data = requests.get(FIREBASE_URL, timeout=30).json()

if not data:
    quit()

sessions = list(data.values())

total = len(sessions)

deaths = 0
completed = 0
total_time = 0

stage_counts = {
    stage: 0
    for stage in STAGES
}

all_stages = set()

for session in sessions:
    all_stages.update(
        session.get("stages", {}).keys()
    )

print("ALL STAGES FOUND:")
print(sorted(all_stages))
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

avg_time = int(total_time / total)

minutes = avg_time // 60
seconds = avg_time % 60

summary_text = (
    f"🪬 **Started Story**\n"
    f"└ {total} players\n\n"

    f"💀 **Died**\n"
    f"└ {deaths} players\n\n"

    f"⚠️ **Gave Up**\n"
    f"└ {gave_up} players\n\n"

    f"❇️ **Average Playtime**\n"
    f"└ {minutes}m {seconds}s\n\n"

    f"🏆 **Completed Story**\n"
    f"└ {completed} players"
)

stage_text = ""

for stage in STAGES:

    count = stage_counts[stage]
    percent = round(count / total * 100, 1)

    stage_text += (
        f"{EMOJIS[stage]} **{stage}**\n"
        f"└ {count} players • {percent}%\n\n"
    )

payload = {
    "embeds": [
        {
            "title": "📊 Ruined Analytics Summary",
            "description": summary_text,
            "color": 3447003,
            "footer": {
                "text": f"{total} sessions analyzed"
            }
        },
        {
            "title": "📜 Story Progression",
            "description": stage_text,
            "color": 5763719
        }
    ]
}

response = requests.post(
    DISCORD_WEBHOOK_URL,
    json=payload,
    timeout=30
)

print("Discord Status:", response.status_code)
print("Summary sent.")