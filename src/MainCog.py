import discord, json, random, asyncio, asqlite, datetime, logging
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from typing import Optional, Literal
from discord.ext.commands.cooldowns import BucketType
from datetime import timedelta
from discord.utils import get
import Database
from CardClass import *
import random

from Start import ProfileStart
from User import User
from Currency import Currency
from Card import Card
from Game import Game

# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("../logs/bot.log"), logging.StreamHandler()]
)
# Privileged Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
# Create variables for emojis in json dict
# Emojis
with open("../CustomEmojis", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")


# test command can be removed / ignored
class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test", description="Test Command")
    async def test(self, ctx):
        """Test Command"""
        embed = discord.Embed(title="Test Embed", description="App Command Invoked")
        await ctx.send(embed=embed, ephemeral=True)


# SYNCS Commands to all GUILDS DO NOT TOUCH / ALTER
class Sync(commands.Cog):
    @commands.command(description='Syncs all commands globally. Only accessible to developers.')
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if ctx.author.id != 301494278901989378 or 533672241448091660:
            return

        embed = discord.Embed(description="Syncing...", color=discord.Color.red())
        await ctx.send(embed=embed)
        print("Syncing...")
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(embed=discord.Embed(
                description=f"Synced `{len(synced)}` commands {'globally' if spec is None else 'to the current guild.'}.",
                color=discord.Color.green()))
            print("Synced.")
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(embed=discord.Embed(description=f"Synced the tree to {ret}/{len(guilds)}.", color=discord.Color.green()))
        print("Synced.")


# Adds Cogs
async def setup(bot):
    await bot.add_cog(Debug(bot))
    await bot.add_cog(Sync(bot))
    await bot.add_cog(User(bot))
    await bot.add_cog(Currency(bot))
    await bot.add_cog(Card(bot))
    await bot.add_cog(Game(bot))

