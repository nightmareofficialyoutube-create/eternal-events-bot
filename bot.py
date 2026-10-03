import os
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ONLY THIS USER CAN CREATE EVENTS
# Keep your existing Discord User ID here.
OWNER_ID = 553648435018989588

# Current event
event_queue = set()
event_minimum = 5
event_name = "The Eternal SMP Event"
event_timestamp = None


def get_queue_text():
    if not event_queue:
        return "No players have joined yet."

    return "\n".join(
        f"• <@{user_id}>"
        for user_id in event_queue
    )


def get_event_message():
    return (
        f"🎟️ **{event_name}**\n\n"
        f"🕐 **Event Time:** <t:{event_timestamp}:F>\n\n"
        f"**Confirmed Players: {len(event_queue)}/{event_minimum}**\n\n"
        "👥 **Current Queue**\n"
        f"{get_queue_text()}\n\n"
        "⚠️ **Important:** Joining the queue means you are confirming "
        "that you intend to attend this event. Please only join if you "
        "are sure you can participate."
    )


class EventView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="JOIN QUEUE",
        style=discord.ButtonStyle.green,
        emoji="🎟️"
    )
    async def join_queue(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id in event_queue:
            await interaction.response.send_message(
                "⚠️ You are already in the event queue.",
                ephemeral=True
            )
            return

        event_queue.add(interaction.user.id)

        await interaction.response.edit_message(
            content=get_event_message(),
            view=self
        )

        await interaction.followup.send(
            "✅ You are officially signed up for this event.\n"
            "By joining the queue, you are confirming that you intend to attend.",
            ephemeral=True
        )

    @discord.ui.button(
        label="LEAVE QUEUE",
        style=discord.ButtonStyle.red,
        emoji="🚪"
    )
    async def leave_queue(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id not in event_queue:
            await interaction.response.send_message(
                "⚠️ You are not currently in the event queue.",
                ephemeral=True
            )
            return

        event_queue.remove(interaction.user.id)

        await interaction.response.edit_message(
            content=get_event_message(),
            view=self
        )

        await interaction.followup.send(
            "🚪 You have been removed from the event queue.",
            ephemeral=True
        )


@bot.event
async def on_ready():
    print(f"Bot is online als {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands gesynchroniseerd: {len(synced)}")
    except Exception as error:
        print(f"Sync error: {error}")


@bot.tree.command(
    name="event",
    description="Create an Eternal SMP event"
)
async def event(
    interaction: discord.Interaction,
    minimum_players: int,
    name: str,
    date: str,
    time: str
):
    global event_queue
    global event_minimum
    global event_name
    global event_timestamp

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ You do not have permission to create events.",
            ephemeral=True
        )
        return

    # Convert the entered Dutch time into a Discord timestamp
    try:
        amsterdam_time = datetime.strptime(
            f"{date} {time}",
            "%Y-%m-%d %H:%M"
        ).replace(
            tzinfo=ZoneInfo("Europe/Amsterdam")
        )

        event_timestamp = int(amsterdam_time.timestamp())

    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid date or time.\n\n"
            "Use:\n"
            "`YYYY-MM-DD` for the date\n"
            "`HH:MM` for the time\n\n"
            "Example: `2026-10-10` and `20:00`",
            ephemeral=True
        )
        return

    event_queue = set()
    event_minimum = minimum_players
    event_name = name

    await interaction.response.send_message(
        get_event_message(),
        view=EventView()
    )


bot.run(TOKEN)