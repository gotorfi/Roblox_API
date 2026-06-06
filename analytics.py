import requests

FIREBASE_URL = "https://ruined-analytics-roblox-default-rtdb.europe-west1.firebasedatabase.app/sessions.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510203543783473214/VeZPvBnybCrTk4IYmOW78hSfQ5IF9jOXWvY_W23hJXKnlqfTbU-OH4xi7WURayszkmhw"

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

message = "# 📊 STAGE COMPLETION SUMMARY\n\n"

message += f"## 🪬 Total amount of players who started the story: {total}\n"
message += f"## 💀 Total amount of players who left because of death: {deaths}\n"
message += f"## ⚠️ Total amount of players who gave up: {gave_up}\n"
message += f"## ❇️ Average playtime: {minutes} min, {seconds} sec\n"
message += f"## 💯 Game Completed: {completed}\n\n"

message += "# 📜 STAGES (Amount and Percentage)\n\n"

for stage in STAGES:

    count = stage_counts[stage]
    percent = round(count / total * 100, 1)

    emoji = EMOJIS[stage]

    message += (
        f"## {emoji} {stage}: "
        f"{count} | {percent}%\n"
    )

requests.post(
    
    DISCORD_WEBHOOK_URL,
    json={"content": message},
    timeout=30
)
print(len(message))
print("Summary sent.")