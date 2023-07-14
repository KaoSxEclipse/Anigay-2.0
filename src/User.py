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

devids = [533672241448091660, 301494278901989378, 318306707493093376, 552151385127256064]
# Privileged Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='a!', intents=intents)


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
# View's profile of others, if no user specified returns your profile
    @commands.hybrid_command(name="profile", description="Get an overview of your profile.", aliases=["p"])
    @bot.listen('on_message')
    async def profile(self, ctx, message="<", user: discord.Member = None):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                #print("message:", message)

                if message == "<":
                    user = ctx.author
                elif not "<"  in str(message):
                    return
                else:

                    user_id = int(message[2:-1])

                    user = await ctx.bot.fetch_user( user_id )


                if user == None or user == ctx.author:
                    user_id = str(ctx.author.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  # User is found
                    user_data = user_data[0]

                    if user_data["card"] != 0:
                        card = CardClass( uid=user_data['card'] )

                        await card.Query()
                    else:
                        card = None

                    embed = discord.Embed(title=f"__{user.name}'s__ Profile",
                                          description="",
                                          color=0x75FFEE)
                    #embed.add_field(name="**Level**", value=f'{user_data["level"]}', inline=True)
                    embed.add_field(name="**Experience**", value=f'{user_data["exp"]}/{user_data["exp"]}', inline=True)
                    embed.add_field(name=f" {Wuns} **Balance**", value=f'{user_data["wuns"]} wuns', inline=True)
                    embed.add_field(name="**Stamina**", value=f'{user_data["stamina"]}/{user_data["stamina"]}',
                                    inline=True)
                    if card == None:
                        embed.add_field(name="**Card Selected:**", value=f"{card}", inline=False)
                    else:
                        embed.add_field(name="**Card Selected:**", value=f"{card.stats['name']}", inline=False)
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found", description=f"{user} has no profile",
                                          color=0xA80108)
                    await ctx.send(embed=embed)

    # Return the Player inventory by cycling through card database
    @commands.hybrid_command(aliases=["inv"])
    async def inventory(self, ctx):
        async with asqlite.connect(path_to_db+"card_data.db") as connection:
            async with connection.cursor() as cursor:
                user = ctx.author.id
                await cursor.execute( "SELECT * FROM Upper WHERE owner=?", (user,) )
                player_inventory = await cursor.fetchall()

                embed = discord.Embed(title=f"{ctx.author}'s Inventory:", color=0x03F76A)

                for i in range( 0, len(player_inventory) ):
                    card = CardClass( player_inventory[i]['uid'], player_inventory[i]['rarity'] )

                    await card.Query()

                    #print("card id: ", card.uid)
                    #print("card stats: ", card.stats)
                    #print("card data: ", card.data)

                    embed.add_field(name=f"#{str(i+1)} | {card.stats['name']}  [Evo {card.data['evo']}]", value=f"{card.data['rarity'].upper()} | Exp: {card.data['exp']} | ID: {card.uid}", inline=False)


                await cursor.execute( "SELECT * FROM Lower WHERE owner=?", (user,) )
                player_inventory = await cursor.fetchall()

                await cursor.execute("SELECT * FROM Dex")
                cards = await cursor.fetchall()

                for ii in range( i, i+len(player_inventory) ):
                    #print("SQL", player_inventory[ii-i])
                    card_dex = player_inventory[ii-i]["dex"]
                    card_uid = player_inventory[ii-i]["uid"]

                    for card in cards:
                        if card_dex == card["dex"]:
                            card_name = card["name"]
                            break

                    embed.add_field(name=f"#{str(ii+1)} | {card_name}", value=f"Rare | Exp: -- | ID: {card_uid}", inline=False)               

                await ctx.send(embed=embed)

                await connection.commit()

    # Select a card and assign it to the user for battling
    @commands.hybrid_command()
    async def select(self, ctx, message=0):
        async with asqlite.connect(path_to_db+"card_data.db") as connection:
            async with connection.cursor() as cursor:
                user = ctx.author.id
                await cursor.execute( "SELECT * FROM Upper WHERE owner=?", (user,) )
                player_inventory = await cursor.fetchall()

                if 0 < int(message) <= len(player_inventory):
                    # Proper card is in inventory
                    card_index = int(message)-1
                    card_id = player_inventory[card_index]["uid"]
                    async with asqlite.connect(path_to_db+"player_data.db") as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute( """UPDATE Users set card=? WHERE id=?""", ( card_id, user ) )

                    card = CardClass( player_inventory[card_index]['uid'], player_inventory[card_index]['rarity'] )
                    await card.Query()

                    embed = discord.Embed(title=f"Card Selected!", description=f"{card.stats['name']} was selected for battle!", color=0x03F76A)

                    await ctx.send(embed=embed)

                    await connection.commit()

    # Shows the full stats of a card
    @commands.hybrid_command()
    async def info(self, ctx, message = None):
        async with asqlite.connect(path_to_db+"card_data.db") as connection:
            async with connection.cursor() as cursor:
                user = ctx.author.id
                await cursor.execute( "SELECT * FROM Upper WHERE owner=?", (user,) )
                player_inventory = await cursor.fetchall()

                try:
                    message = int(message) - 1
                except:
                    embed = discord.Embed(title=f"Card not found",
                                          description=f"Please specify a legitamate card name!",
                                          color=0xF76103)
                    await ctx.send(embed=embed)
                    return

                card = player_inventory[message]
                card_dex = player_inventory[message]["dex"]

                await cursor.execute( "SELECT * FROM Dex WHERE dex=?", (card_dex,) )
                data = await cursor.fetchall()
                data = data[0]

                await connection.commit()


        user_card = UserCard(card, data)

        embed = discord.Embed(title=f"{user_card.name} | Level {user_card.level}", color=0x03F76A)
        embed.add_field(name="", value=f"**Evo:** {user_card.evo}", inline=False)
        embed.add_field(name="", value=f"**Rarity:** {user_card.rarity}", inline=False)
        embed.add_field(name="", value=f"**HP:** {user_card.hp}", inline=False)
        embed.add_field(name="", value=f"**ATK:** {user_card.atk}", inline=False)
        embed.add_field(name="", value=f"**DEF:** {user_card.df}", inline=False)
        embed.add_field(name="", value=f"**SPD:** {user_card.spd}", inline=False)
        embed.add_field(name="", value=f"**Talent:** {user_card.talent}", inline=False)
        embed.set_footer(text="Card ID: " + str(user_card.id))

        await ctx.send(embed=embed)