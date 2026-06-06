import discord
from discord import app_commands
from analytics_core import fetch_sessions, compute_stats, STAGES
import os

TOKEN = os.getenv("TOKEN")

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} commands")

client = Client()

# -------------------------
# /Analytics Summary
# -------------------------
@client.tree.command(name="analytics_summary", description="Show player summary")
async def analytics_summary(interaction: discord.Interaction):
    sessions = fetch_sessions()
    stats = compute_stats(sessions)

    minutes = stats["avg_time"] // 60
    seconds = stats["avg_time"] % 60

    embed = discord.Embed(title="📊 Analytics Summary", color=0x3498db)

    embed.add_field(name="Players", value=str(stats["total"]))
    embed.add_field(name="Deaths", value=str(stats["deaths"]))
    embed.add_field(name="Gave Up", value=str(stats["gave_up"]))
    embed.add_field(name="Completed", value=str(stats["completed"]))
    embed.add_field(name="Avg Time", value=f"{minutes}m {seconds}s")

    await interaction.response.send_message(embed=embed)

# -------------------------
# /Analytics Stages
# -------------------------
@client.tree.command(name="analytics_stages", description="Show stage progression")
async def analytics_stages(interaction: discord.Interaction):
    sessions = fetch_sessions()
    stats = compute_stats(sessions)

    total = stats["total"]

    text = ""
    for stage in STAGES:
        count = stats["stage_counts"][stage]
        percent = round(count / total * 100, 1) if total else 0

        text += f"**{stage}** → {count} ({percent}%)\n"

    embed = discord.Embed(
        title="📜 Stage Progression",
        description=text,
        color=0x9b59b6
    )

    await interaction.response.send_message(embed=embed)

client.run(TOKEN)