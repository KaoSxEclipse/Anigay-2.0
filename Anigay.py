import os, discord, discord.ext, logging
from discord import *
from discord.ext import commands
from dotenv import load_dotenv
from MainCog import *
import asyncio, asqlite


# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[  logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger()
# Privileged Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='a!', intents=intents)

#On_Ready runs the bot when the code is ran. Add's the cogs (commands)
@bot.event
async def on_ready():
	logger.info(f"Logged in as {bot.user}")
	await bot.add_cog(Debug(bot))
	await bot.add_cog((sync(bot)))
	await bot.add_cog((ProfileStart(bot)))
	await bot.add_cog( User(bot) )
	await bot.add_cog(currency(bot))


# Load Env file and load it then set the token var
load_dotenv()
TOKEN = os.getenv("Token")


bot.run(TOKEN)


