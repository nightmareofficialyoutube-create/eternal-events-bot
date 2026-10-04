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

OWNER_ID = 553648435018989588

# =========================================================

# EVENT SYSTEM

# =========================================================

event_queue = set()
event_minimum = 5
event_name = "The Eternal SMP Event"
event_timestamp = None

def get_queue_text():
if not event_queue:
return "No players have joined yet."

```
return "\n".join(
    f"• <@{user_id}>"
    for user_id in event_queue
)
```

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
def **init**(self):
super().**init**(timeout=None)

```
@discord.ui.button(
    label="JOIN QUEUE",
    style=discord.ButtonStyle.green,
    emoji="🎟️"
)
async def join_queue(self, interaction, button):
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
async def leave_queue(self, interaction, button):
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
```

# =========================================================

# CHARACTER SYSTEM

# =========================================================

character_applicants = {}
character_name = ""
character_role = ""
character_minimum = 1
character_panel_message = None

def get_character_message():
if character_applicants:
applicant_list = "\n".join(
f"<@{user_id}> {'🎤' if has_mic else '❌'}"
for user_id, has_mic in character_applicants.items()
)
else:
applicant_list = "No applicants yet."

```
return (
    f"🎭 **{character_name}**\n"
    f"{character_role}\n\n"
    f"**Applicants: {len(character_applicants)}/{character_minimum}**\n"
    f"**Minimum applicants: {character_minimum}**\n\n"
    f"{applicant_list}"
)
```

async def update_character_panel():
global character_panel_message

```
if character_panel_message is not None:
    try:
        await character_panel_message.edit(
            content=get_character_message(),
            view=CharacterView()
        )
    except discord.NotFound:
        character_panel_message = None
```

class MicView(discord.ui.View):
def **init**(self, applicant_id):
super().**init**(timeout=300)
self.applicant_id = applicant_id

```
@discord.ui.button(
    label="Yes",
    style=discord.ButtonStyle.green,
    emoji="🎤"
)
async def mic_yes(self, interaction, button):
    if interaction.user.id != self.applicant_id:
        await interaction.response.send_message(
            "This application belongs to another player.",
            ephemeral=True
        )
        return

    character_applicants[interaction.user.id] = True

    await interaction.response.edit_message(
        content="Application submitted.",
        view=None
    )

    await update_character_panel()

@discord.ui.button(
    label="No",
    style=discord.ButtonStyle.red
)
async def mic_no(self, interaction, button):
    if interaction.user.id != self.applicant_id:
        await interaction.response.send_message(
            "This application belongs to another player.",
            ephemeral=True
        )
        return

    character_applicants[interaction.user.id] = False

    await interaction.response.edit_message(
        content="Application submitted.",
        view=None
    )

    await update_character_panel()
```

class CharacterView(discord.ui.View):
def **init**(self):
super().**init**(timeout=None)

```
@discord.ui.button(
    label="APPLY",
    style=discord.ButtonStyle.green
)
async def apply(self, interaction, button):
    if interaction.user.id in character_applicants:
        await interaction.response.send_message(
            "You have already applied for this character.",
            ephemeral=True
```
