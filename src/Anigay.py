import os, discord, discord.ext, logging
from discord import *
from discord.ext import commands
from dotenv import load_dotenv
from MainCog import *
import asyncio, asqlite
from datetime import datetime, timedelta
import re

from User import User
from Card import Card
from Currency import Currency
from Dev import Dev
from Game import Game
from Start import ProfileStart
from Shop import Shop

# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("../logs/bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger()


# Privileged Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents, case_insensitive=True, status="Self Creating")
bot.help_command = MyHelp()



# On_Ready runs the bot when the code is ran. Add's the cogs (commands)
@bot.event
async def on_ready():
	logger.info(f"Logged in as {bot.user}")
	await bot.add_cog(Debug(bot))
	await bot.add_cog(Dev(bot))
	await bot.add_cog(ProfileStart(bot))
	await bot.add_cog(User(bot))
	await bot.add_cog(Currency(bot))
	await bot.add_cog(Card(bot))
	await bot.add_cog(Game(bot))
	await bot.add_cog(Shop(Shop))

# Load Env file and load it then set the token var
load_dotenv("env")
TOKEN = os.getenv("Token")
bot.run(TOKEN, reconnect=True)
