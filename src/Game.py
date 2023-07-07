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


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Manage Locations
    @commands.hybrid_command(aliases=["loc"])
    async def location(self, ctx, loc=None, floor=None):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                user_id = str(ctx.author.id)
                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user = await cursor.fetchall()
                user = user[0]

                with open(path_to_db+"cards.json", "r") as file:
                    series = json.load(file)
                    realms = []

                    for i in series:
                        realms.append(i)

                max_loc = int(str(user["maxloc"]).split(".")[0])
                max_floor = int(str(user["maxloc"]).split(".")[1])
                
                if loc != None:
                    loc = int(loc) - 1

                if loc == None:
                    embed = discord.Embed(title=f"Realms",
                                          description=f"You are at realm {user['location']}",
                                          color=0xF76103)

                    index = 1
                    for i in realms:
                        embed.add_field(name=f"Realm {index}", value=f"{i}", inline=False)
                        index += 1

                    await ctx.send(embed=embed)

                elif 0 <= int(loc) < len(realms): ## Existing Realms
                    if int(loc) > max_loc: # Player has not cleared the previous location yet
                        embed = discord.Embed(title=f"You have not unlocked this Realm!!",
                                          description=f"Please clear the previous Realms and floors before ascending to this realm.",
                                          color=0xF76103)
                        await ctx.send(embed=embed)
                    else:
                        if int(floor) > max_floor: # Player has not cleared the previous floor yet
                            embed = discord.Embed(title=f"You have not unlocked this area!!",
                                          description=f"Please clear the previous areas before progressing your journey.",
                                          color=0xF76103)
                            await ctx.send(embed=embed)
                        else:
                            location = float(str(loc)+".00"+str(floor))
                            #print(location)
                            await cursor.execute( """UPDATE Users set location=? WHERE id=?""", ( location, user_id ) )

                            card = series[realms[int(loc)]][int(floor)]

                            #print(card)

                            embed = discord.Embed(title=f"Realm {loc+1}, Floor {floor}",
                                          description=f"{card[1]} stands before you.",
                                          color=0xF76103)
                            await ctx.send(embed=embed)



                else:
                    embed = discord.Embed(title=f"Realm not found!!",
                                          description=f"Please specify a legitamate realm number!!",
                                          color=0xF76103)
                    await ctx.send(embed=embed)

    # Battle function TESTING!!
    @commands.hybrid_command(aliases=["bt"])
    async def battle(self, ctx, amount=1):
        def displayHP(player_hp, enemy_hp, battle_round):
            player_hp_percentage = player_hp / (user_card.hp*10) * 100
            player_hp_filled = round(player_hp_percentage / 100 * hp_bar_length)
            player_hp_empty = hp_bar_length - player_hp_filled

            enemy_hp_percentage = enemy_hp / (oppo.hp*10) * 100
            enemy_hp_filled = round(enemy_hp_percentage / 100 * hp_bar_length)
            enemy_hp_empty = hp_bar_length - enemy_hp_filled

            if player_hp <= 0:
                player_hp = 0
                player_filled = 0
                player_hp_empty = 20

            if enemy_hp <= 0:
                enemy_hp = 0
                enemy_filled = 0
                enemy_hp_empty = 20

            player_hp_bar = "█" * player_hp_filled + "░" * player_hp_empty
            enemy_hp_bar = "█" * enemy_hp_filled + "░" * enemy_hp_empty

            embed = discord.Embed(title=f"{ctx.author} is challenging Floor {loc}-{floor}", color=0x00FF00)
            embed.add_field(name=f"**{user_card.name}**", value="", inline=False)
            embed.add_field(name="", value="Element: ", inline=False)
            embed.add_field(name=f"**{player_hp} / {user_card.hp*10}** ♥", value=f"`[{player_hp_bar}]`", inline=False)
            embed.add_field(name=f"**{oppo.name}**", value="", inline=False)
            embed.add_field(name="", value="Element: ", inline=False)
            embed.add_field(name=f"**{enemy_hp} / {oppo.hp*10} ♥**", value=f"`[{enemy_hp_bar}]`", inline=False)

            if battle_round >= 1:
                embed.add_field(name=f"**[Round {battle_round}]**", value="", inline=False)
                embed.add_field(name=f"{user_card.name} deals {player_dmg} to {oppo.name}", value="", inline=False)
                embed.add_field(name=f"{oppo.name} deals {enemy_dmg} to {user_card.name}", value="", inline=False)

            return embed

        user_id = ctx.author.id
        user = await Database.verifyUser(user_id)

        if user == []:
            embed = discord.Embed(
                title="Unregistered User",
                description="Looks like you haven't started yet! Type a!start!",
                color=0xA80108
            )
            await ctx.send(embed=embed)
        else:
            user = user[0]

            if user["card"] != 0:
                card = CardClass(user["card"])

                with open(path_to_db+"cards.json", "r") as file:
                    series = json.load(file)
                    realms = [i for i in series]

                async with asqlite.connect(path_to_db+"player_data.db") as connection: # Get Player data
                    async with connection.cursor() as cursor:
                        user_id = str(ctx.author.id)
                        await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                        user = await cursor.fetchall()
                        user = user[0]

                        loc = int(str(user["location"]).split(".")[0])
                        floor = int(str(user["location"]).split(".")[1])

                        await connection.commit()

                async with asqlite.connect(path_to_db+"card_data.db") as connection: # Get User card data
                    async with connection.cursor() as cursor:
                        user_id = ctx.author.id
                        await cursor.execute( "SELECT * FROM Upper WHERE owner=?", (user_id,) )
                        player_inventory = await cursor.fetchall()

                        for c in player_inventory:
                            if c["uid"] == user["card"]:
                                card_dex = c["dex"]

                        await cursor.execute( "SELECT * FROM Dex WHERE dex=?", (card_dex,) )
                        user_card = await cursor.fetchall()
                        user_card = user_card[0]

                        await connection.commit()


                #print(user_card["name"]) ## Raw Dex card. Will calculate the stats later.


                # user card = dictionary
                # Enemy Floor card is a Class

                card = series[realms[loc]][floor]

                user_card = UserCard(c, user_card)

                #print(user_card.name)

                oppo = FloorCard(loc, floor)

                player_hp = user_card.hp*10
                enemy_hp = oppo.hp*10

                hp_bar_length = 20

                battle_round = 0

                embed = displayHP(player_hp, enemy_hp, battle_round)
                bt = await ctx.send(embed=embed)
                await asyncio.sleep(1.5)

                ELEMENT_MULTIPLIER = 1
                CRITICAL_MULTIPLIER = 1

                while player_hp > 0 and enemy_hp > 0:
                    player_dmg = int(round((((user_card.atk / oppo.df) * (user_card.atk / 2.9) + 220000 / oppo.df) / 3 * ELEMENT_MULTIPLIER * CRITICAL_MULTIPLIER)))
                    enemy_dmg = int(round((((oppo.atk / user_card.df) * (oppo.atk / 2.9) + 220000 / user_card.df) / 3 * ELEMENT_MULTIPLIER * CRITICAL_MULTIPLIER)))

                    player_hp -= enemy_dmg
                    enemy_hp -= player_dmg

                    battle_round += 1
                    embed = displayHP(player_hp, enemy_hp, battle_round)

                    await bt.edit(embed=embed)
                    await asyncio.sleep(2.5)

            else:
                embed = discord.Embed(
                    title="No Card Equipped",
                    description="Please equip a card before battling!",
                    color=0xA80108
                )
                await ctx.send(embed=embed)