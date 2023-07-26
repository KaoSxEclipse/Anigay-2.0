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
from genutil import *

path_to_db = "../db/"


with open("CustomEmojis", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")

packs = {
    "rare": [80, 19.5, 0.5],
    "epic": [65, 33, 2],
    "legendary": [50, 47, 3]
}


price = {
    "rare": 35000,
    "epic": 70000,
    "legendary": 120000
}

packtypes = list(packs.keys())


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def shop(self, ctx):

        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                user_id = ctx.author.id

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user = await cursor.fetchall()

                await connection.commit()

                if user == []: # User not found in database
                    embed = discord.Embed(title=f"Unregistered User",
                                          description=f"Looks like you haven't started yet!! Type a!start!",
                                          color=0xA80108)
                    return await ctx.send(embed=embed)

        title = "Summoning Sanctuary"
        desc = ""
        embed = discord.Embed(title=title, description=desc)

        for i in range(len(packs)):
            embed.add_field(name=f"#{i+1} | {packtypes[i].capitalize()} Pack | {price[packtypes[i]]:,} Wuns",
                            value=f"Contains | 5x Cards\n**["
                                  f"{packs[packtypes[i]][0]}% R / "
                                  f"{packs[packtypes[i]][1]}% SR / "
                                  f"{packs[packtypes[i]][2]}% UR]**",
                            inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def buy(self, ctx, itemtype, itemname):

        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                user_id = ctx.author.id

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user = await cursor.fetchall()

                await connection.commit()
                if user == []: # User not found in database
                    embed = discord.Embed(title=f"Unregistered User",
                                          description=f"Looks like you haven't started yet!! Type a!start!",
                                          color=0xA80108)
                    return await ctx.send(embed=embed)

                if itemname in "pack":
                    if itemtype in packtypes:
                        cost = price[itemtype]

                        async with asqlite.connect(path_to_db + "player_data.db") as connection:
                            async with connection.cursor() as cursor:
                                await cursor.execute("SELECT * FROM Users WHERE id=?", (ctx.author.id,))

                                user_data = user[0]
                                if user_data["wuns"] >= cost:
                                    left = user_data["wuns"] - cost
                                else:
                                    left = cost - user_data["wuns"]
                                    return await ctx.send(f"Summoner {ctx.author}, you are short of {Wuns}**{left:,}** wuns for this item")

                                await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (left, user_id))
                                await connection.commit()

                        await ctx.send(f"Summoner, you have spent {cost:,} Wuns and received...")

                        async with ctx.typing():

                            rarities = ['r', 'sr', 'ur']
                            rng = packs[itemtype].copy()

                            await packrng(rng)

                            card_list = await Database.generateCardList()

                            async with asqlite.connect(path_to_db + "card_data.db") as connection:
                                async with connection.cursor() as cursor:

                                    desc = ""
                                    for x in range(5):  # 5 cards per pack
                                        name = random.choice(card_list)

                                        await cursor.execute("SELECT * FROM Dex WHERE name=?", (name,))
                                        card_index = await cursor.fetchall()

                                        card_data = card_index[0]

                                        card_index = card_data["dex"]

                                        card_list.remove(name)

                                        rarity = random.choices(rarities, rng, k=1)[0]

                                        await Database.generateCard(index=card_index, owner=user_id, rarity=rarity, evo=1)

                                        desc += f"{await fullname(rarity)} **{name}**\n\n"

                                    await connection.commit()

                            embed = discord.Embed(title=f"Pack opened!", description=desc, color=0x03F76A)
                            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)

                            await asyncio.sleep(2)
                            return await ctx.send(embed=embed)
