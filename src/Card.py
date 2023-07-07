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

    @commands.hybrid_command(name="summon", description="Summon a card. Param: target, card name, rarity")
    async def summon(self, ctx, name=None, rarity="sr" ):
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
                    await ctx.send(embed=embed)
                    return

                rarity = rarity.lower()


                if name == None or rarity == None: #Verify arguments
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
                            await cursor.execute( "SELECT * FROM Dex WHERE name=?", (name,))

                            card_index = await cursor.fetchall()

                    if len(card_index) != 0:  # card is found
                        card_data = card_index[0]

                    card_index = card_data["dex"]


                    await Database.generateCard( card_index, user_id, rarity, 1 )

                    embed = discord.Embed(title=f"Card Summoned!", description=f"A {rarity.upper()} {name} was summoned", color=0x03F76A)

                    await ctx.send(embed=embed)