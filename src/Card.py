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


class Card(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # Show the Information on a single card in the index
    @commands.hybrid_command(aliases=['ci'])
    async def cinfo(self, ctx, message = None, message2 = None):
        async with asqlite.connect(path_to_db+"card_data.db") as connection:
            async with connection.cursor() as cursor:

                if message2 != None:
                    message = message.capitalize() + " " + message2.capitalize()
                else:
                    message = message.capitalize()

                cards = await Database.generateCardList()

                for i in cards:
                    if message in i:
                        message = i

                if message == None:
                    embed = discord.Embed(title=f"Card not found",
                                          description=f"Please specify a legitamate card name!",
                                          color=0xF76103)
                    await ctx.send(embed=embed)
                    return

                else:

                    await cursor.execute( "SELECT * FROM Dex WHERE name=?", (message,))

                    card_index = await cursor.fetchall()

                    if len(card_index) != 0:  # User is found
                        card_data = card_index[0]

                        embed = discord.Embed(title=f"{card_data['name']}", color=0x03F76A)
                        embed.add_field(name=f"HP: {card_data['hp']}", value="", inline=False)
                        embed.add_field(name=f"Attack: {card_data['atk']}", value="", inline=False)
                        embed.add_field(name=f"Defense: {card_data['def']}", value="", inline=False)
                        embed.add_field(name=f"Speed: {card_data['spd']}", value="", inline=False)
                        embed.add_field(name=f"Talent: {card_data['talent']}", value="", inline=False)
                        embed.set_thumbnail(url=ctx.author.avatar)
                        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"Card not found",
                                          description=f"Please specify a legitamate card name!",
                                          color=0xF76103)
                        await ctx.send(embed=embed)