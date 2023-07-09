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

path_to_db = "../db/"


with open("CustomEmojis", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")


# Currency Based Commands go in this Cog
# Allows Devs (Anyone atm) to give others currency + view the Balance of yourself and others.
class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Gives a user money from own balance
    @commands.hybrid_command(name="give", aliases=['g'])
    async def give(self, ctx, user: discord.User, amount: int):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_giver = int(ctx.author.id)

                user_target = int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_giver,))
                user_giver_data = await cursor.fetchall()

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_target,))
                user_target_data = await cursor.fetchall()

                if len(user_giver_data) != 0 and len(user_target_data) != 0:  ## User is found
                    user_data_giver = user_giver_data[0]
                    user_data_target = user_target_data[0]

                    if user_data_giver["wuns"] >= amount:

                        new_balance_target = user_data_target["wuns"] + amount
                        new_balance_giver = user_data_giver["wuns"] - amount
                        amount_readable = "{:,}".format(amount)
                        await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance_giver, user_giver))
                        await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance_target, user_target))
                        embed = discord.Embed(title=f"{ctx.author} has blessed you",
                                              description=f"{ctx.author} has given {user_target} {Wuns}{amount_readable} wuns",
                                              color=0x04980f)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"Not Enough Money!!",
                                              description=f"You poor fool. Learn to count before giving money away, eh?",
                                              color=0xA80108)
                        await ctx.send(embed=embed)

                else:  # User not found
                    if len(user_giver_data) == 0:
                        embed = discord.Embed(title=f"Unregistered User",
                                              description=f"Looks like you haven't started yet!! Type a!start!",
                                              color=0xA80108)
                        await ctx.send(embed=embed)

                    elif len(user_target_data) == 0:  # Target not found
                        embed = discord.Embed(title=f"{user.name} not found",
                                              description=f"Have {user.name} type a!start!",
                                              color=0xA80108)
                        await ctx.send(embed=embed)

    # Views a user balance if "None" returns Command Authors balance
    @commands.hybrid_command(aliases=['bal'])
    async def balance(self, ctx, user: discord.User = None):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:

                if not user:
                    user = ctx.author

                user_id = int(ctx.author.id) if user is None else int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  # User is found
                    user_data = user_data[0]
                    balance = user_data["wuns"]
                    balance_readable = "{:,}".format(balance)

                    embed = discord.Embed(title=f"{user}'s Balance", color=0x03F76A)
                    embed.add_field(name="", value=f"{user} has {Wuns}{balance_readable} wuns")
                    embed.set_thumbnail(url=user.avatar)
                    embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found",
                                          description=f"ask {user.mention} to type a!start",
                                          color=0xF76103)
                    await ctx.send(embed=embed)

        # Random Claim command, need to add a cooldown. possible feature early on to earn Currency?

    @commands.hybrid_command(name="claim", description="get a random amount of gold added to your balance")
    @commands.cooldown(1, 28800, type=BucketType.user)
    @commands.has_permissions(view_channel=True, read_messages=True, send_messages=True)
    async def claim(self, ctx):
        """Claim Gold"""
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM Users WHERE id=?", (ctx.author.id,))
                user_data = await cursor.fetchall()
                claim_value = random.randint(10, 50)

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    new_balance = user_data["wuns"] + claim_value
                    await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance, ctx.author.id))
                    embed = discord.Embed(title="**Claim Complete**", color=discord.Color.purple())
                    embed.add_field(name=f"Amount Claimed {Wuns}{claim_value} wuns",
                                    value=f"Your new balance is {Wuns}{new_balance}")
                await ctx.send(embed=embed)

        @self.claim.error
        async def claim(self, ctx, error):
            if isinstance(error, CommandOnCooldown):
                retry_after_seconds = error.retry_after
                time_remaining = datetime.datetime.now() + timedelta(seconds=retry_after_seconds)
                timestamp = int(time_remaining.timestamp())
                time_remaining = f"<t:{timestamp}:R>"
                await ctx.send(f"{ctx.author.mention}, you can claim again in {time_remaining}.")

            else:
                raise error