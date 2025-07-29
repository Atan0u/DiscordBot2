import discord
from discord.ext import commands , tasks
import logging
from dotenv import  load_dotenv
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

RIFT_TIMES = [14, 17, 20, 23]
REMINDER_MINUTES = 5
CHANNEL_ID = 1287398159152189450
TIMEZONE = ZoneInfo("Europe/Paris")

@bot.event
async def on_ready():
    print('We are ready to go.')
    if not rift_reminder.is_running():
        rift_reminder.start()

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


@bot.command()
async def rift(ctx):
    next_rift, time_remaining = get_next_rift()
    total_seconds = int(time_remaining.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    await ctx.send(f"🌌 La prochaine rift est à **{next_rift.strftime('%H:%M')}** (dans {hours}h {minutes}m).")

def get_next_rift():
    now = datetime.now(TIMEZONE)  # ✅ l’heure actuelle sera en Europe/Paris
    today = now.date()
    rift_datetimes = [
        datetime.combine(today, datetime.min.time(), tzinfo=TIMEZONE) + timedelta(hours=h)
        for h in RIFT_TIMES
    ]

    for rift_time in rift_datetimes:
        if now < rift_time:
            return rift_time, (rift_time - now)

    next_rift = rift_datetimes[0] + timedelta(days=1)
    return next_rift, (next_rift - now)

@tasks.loop(seconds=30)
async def rift_reminder():
    next_rift, time_remaining = get_next_rift()
    minutes_left = time_remaining.total_seconds() / 60

    if abs(minutes_left - REMINDER_MINUTES) < 0.5:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"⚠️ **Rift dans {REMINDER_MINUTES} minutes !")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)