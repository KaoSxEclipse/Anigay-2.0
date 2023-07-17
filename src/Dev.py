"""
Dev commands

"""

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
devids = [533672241448091660, 301494278901989378, 318306707493093376, 552151385127256064]

with open("CustomEmojis", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="summon", description="Summon a card. Param: target, card name, rarity")
    async def summon(self, ctx, name=None, rarity="sr"):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                user_id = ctx.author.id

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user = await cursor.fetchall()

                await connection.commit()
                if ctx.author.id not in devids:
                    return

                if user == []: # User not found in database
                    embed = discord.Embed(title=f"Unregistered User",
                                          description=f"Looks like you haven't started yet!! Type a!start!",
                                          color=0xA80108)
                    await ctx.send(embed=embed)
                    return

                if name == None or rarity == None:  # Verify arguments
                    rarity = rarity.lower()
                    embed = discord.Embed(title=f"Error!",
                                          description=f"One or more arguments invalid",
                                          color=0xF76103)
                    await ctx.send(embed=embed)
                elif not rarity in ("ur", "sr"):
                    embed = discord.Embed(title=f"Error!",
                                          description=f"Invalid Rarity!!",
                                          color=0xF76103)
                    await ctx.send(embed=embed)
                else:
                    card_list = await Database.generateCardList()

                    for i in card_list:
                        if name.lower() in i.lower():
                            name = i

                    async with asqlite.connect(path_to_db+"card_data.db") as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute("SELECT * FROM Dex WHERE name=?", (name,))

                            card_index = await cursor.fetchall()

                    if len(card_index) != 0:  # card is found
                        card_data = card_index[0]

                    card_index = card_data["dex"]

                    await Database.generateCard( card_index, user_id, rarity, 1 )

                    embed = discord.Embed(title=f"Card Summoned!", description=f"A {rarity.upper()} {name} was summoned", color=0x03F76A)

                    await ctx.send(embed=embed)


    @commands.command(description='Syncs all commands globally. Only accessible to developers.')
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if ctx.author.id not in devids:
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

    @commands.hybrid_command()
    async def reset(self, ctx, user: discord.User):

        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                if ctx.author.id not in devids:
                    return
                user_id = str(user.id)
                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()


                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    balance = user_data["wuns"]
                    new_balance = user_data["wuns"] * 0
                    balance_readable = "{:,}".format(balance)
                    await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance, user_id))
                    embed = discord.Embed(title=f"a Dev has cursed you",
                                          description=f"{ctx.author} has taken away {Wuns}{balance_readable} wuns from your account",
                                          color=0xA80108)
                    await ctx.send(embed=embed)
                else:  ## User not found
                    embed = discord.Embed(title=f"{user.display_name} not found",
                                          description=f"Have {user.mention} type a!start!",
                                          color=0xA80108)
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name="devgive", aliases=['grant'])
    async def devgive(self, ctx, user: discord.User, amount: int):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                if ctx.author.id not in devids:
                    await ctx.send(f"{ctx.author.mention} You've found a Dev command, unfortunately you can't use it.")
                    return

                user_id = str(user.id)
                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    new_balance = user_data["wuns"] + amount
                    amount_readable = "{:,}".format(amount)
                    await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance, user_id))
                    embed = discord.Embed(title=f"a Dev has blessed you",
                                          description=f"{ctx.author} has given {user} {Wuns}{amount_readable} wuns",
                                          color=0x04980f)
                    embed.set_thumbnail(url=ctx.author.avatar)
                    await ctx.send(embed=embed)
                else:  ## User not found
                    embed = discord.Embed(title=f"{user} not found",
                                          description=f"Have {user} type a!start!",
                                          color=0xA80108)
                    embed.set_thumbnail(url=user.avatar)
                    await ctx.send(embed=embed)