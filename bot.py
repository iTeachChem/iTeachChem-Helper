import discord
from discord.ext import commands
import time
import aiosqlite
import os
from dotenv import load_dotenv
import subprocess

intents = discord.Intents.all()

async def setup_database():
    async with aiosqlite.connect("questions.db") as db:
        with open('schemas.sql', 'r') as f:
            schema_sql = f.read()
        await db.executescript(schema_sql)
        await db.commit()

class iTeachChem(commands.Bot):
    async def setup_hook(self):
        await setup_database()
        print("Database loaded")
        await self.load_extension("admin.admin")
        await self.load_extension("admin.error")
        await self.load_extension("commands.checker")
        await self.load_extension("commands.forum")
        await self.load_extension("commands.lb")
        await self.load_extension("commands.quiz")
        await self.load_extension("commands.questions")
        await self.load_extension("commands.sheets")
        await self.load_extension("admin.help")
        print("All cogs loaded")

    async def on_ready(self):
        custom_activity = discord.CustomActivity(name="Waking up ⛔") 
        await self.change_presence(status=discord.Status.do_not_disturb, activity=custom_activity)
        print('Bot is Ready.')
        await self.change_presence(activity=discord.Game(name="in iTeachChem server", status=discord.Status.online))
        print("Bot is Online")

def install_dependencies():
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

install_dependencies()

bot = iTeachChem(command_prefix=['+'], intents=intents, help_command=None, strip_after_prefix=True)

@bot.command()
async def ping(ctx):
    start_time = time.time()
    message = await ctx.send("Pinging...")
    end_time = time.time()

    latency = round((end_time - start_time) * 1000)
    api_latency = round(bot.latency * 1000)

    await message.edit(content=f"Pong! Latency: **{latency}ms** | API Latency: **{api_latency}ms**")

load_dotenv()
bot.run(os.getenv("BOT_TOKEN"))