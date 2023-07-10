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


# Profile Start commands, prints User's ID and name, returns an embed for now
class ProfileStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="start", description="Start your journey!",
                             usage="type a!start or /start to begin playin!")
    async def start(self, ctx):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = int(ctx.author.id)
                username = str(ctx.author.display_name)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) == 0:
                    ## User doesn't exist
                    ## Insert id, exp, stamina, card, realm and location
                    await cursor.execute("INSERT OR IGNORE INTO Users VALUES (?, 0, 500, 10, 0, 1.001, 1.001)", (user_id))

                    ## Change code later on so it selects randomly from db

                    async with asqlite.connect(path_to_db+"card_data.db") as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute("SELECT * FROM Dex")

                            card_list = await cursor.fetchall()
                            cards = len(card_list)

                    rand_card = random.randint(0, cards-1)

                    if rand_card in range(2, 5):
                        rand_card = random.randint(0, cards-1)
                    
                    for card in card_list:
                        if card["dex"] == rand_card:
                            card_name = card["name"]

                    await Database.generateCard( rand_card, user_id, 'sr', 1 )


                    embed = discord.Embed(title=f"Welcome to Anigame 2.0 {ctx.author}",
                                          description=f"You've been given a *Super Rare* **{card_name}** to start your Journey!",
                                          color=0x4DC5BC)
                    embed.add_field(name="**__Rules__**",
                                    value="No botting, cheating, exploiting bugs and/or spamming commands.")
                    embed.set_thumbnail(url=ctx.author.avatar)
                    await ctx.send(embed=embed)

                else:
                    ## User already exists
                    embed = discord.Embed(title="Uh Oh!", description="Looks like you've already started playing!",

                                          color=0xA80108)
                    embed.add_field(name="What's Next?", value="put something here")
                    await ctx.send(embed=embed)