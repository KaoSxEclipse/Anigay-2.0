"""
Class File handles the main game aspects such as Floors, Locations, Raiding, etc.

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


with open("CustomEmojis", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")


def parseFloor( location ):
    floor = str(location).split(".")[1]

    mult = 2
    for digit in floor:
        if int(digit) == 0:
            mult -= 1

    floor = int(floor)*(10**mult)

    return floor


def displayFloor( loc, floor ):
    card = FloorCard(loc, floor)

    embed = discord.Embed(title=f"Traveled to Area [{loc}-{floor}]", description="", color=0x03F76A)
    embed.add_field(name="", value=f"**:crossed_swords: FLOOR GUARDIAN:**", inline=False)
    embed.add_field(name="", value=f"**__{card.rarity}__ Level {card.level} {card.name} [{card.evo}]**", inline=False)
    embed.add_field(name="", value=f"**Element:** {card.element}", inline=False)
    embed.add_field(name="", value=f"**HP:** {card.hp}", inline=False)
    embed.add_field(name="", value=f"**ATK:** {card.atk}", inline=False)
    embed.add_field(name="", value=f"**DEF:** {card.df}", inline=False)
    embed.add_field(name="", value=f"**SPD:** {card.spd}", inline=False)
    embed.add_field(name="Talent:", value=f"{card.talent}", inline=False)
    #embed.set_footer(text=str(card.quote))

    return embed


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Manage Locations
    @commands.hybrid_command(aliases=["loc"])
    async def location(self, ctx, loc=None):
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

                current_loc = int(str(user["location"]).split(".")[0])
                current_floor = parseFloor(user["location"])

                max_loc = int(str(user["maxloc"]).split(".")[0])
                max_floor = parseFloor(user["maxloc"])

                #print("Max Loc: ", max_loc)
                #print("Max Floor: ", max_floor)
                #print("Realms: ", len(realms))

                if loc == None:
                    embed = discord.Embed(title=f"Realms",
                                          description=f"You are at Realm {current_loc} Floor {current_floor}",
                                          color=0xF76103)

                    index = 1
                    for i in realms:
                        if current_loc == index:
                            embed.add_field(name=f"Realm {index}", value=f"**{i}**", inline=False)
                        else:
                            embed.add_field(name=f"Realm {index}", value=f"{i}", inline=False)
                        index += 1

                    await ctx.send(embed=embed)

                elif loc in "n next nxt".split(" "):
                    if current_loc == len(realms):
                        embed = discord.Embed(title=f"End of the Universe!!",
                                          description=f"There are no more Realms after this!!",
                                          color=0xF76103)
                        await ctx.send(embed=embed)

                    elif current_loc == max_loc:
                        embed = discord.Embed(title=f"You have not unlocked this Realm!!",
                                          description=f"Please clear the previous Realms and floors before ascending to this realm.",
                                          color=0xF76103)
                        await ctx.send(embed=embed)

                    else:
                        current_loc += 1
                        new_loc = float(str(current_loc)+".001")
                        #print(location)
                        await cursor.execute( """UPDATE Users set location=? WHERE id=?""", ( new_loc, user_id ) )

                        card = series[realms[int(current_loc)-1]][0]

                        #print(card)

                        embed = discord.Embed(title=f"Realm {current_loc}, Floor 1 | {realms[int(current_loc)-1]}",
                                      description=f"{card[1]} stands before you.",
                                      color=0xF76103)
                        await ctx.send(embed=embed)



                elif 0 < int(loc) <= len(realms): ## Existing Realms
                    if int(loc) > max_loc: # Player has not cleared the previous location yet
                        embed = discord.Embed(title=f"You have not unlocked this Realm!!",
                                          description=f"Please clear the previous Realms and floors before ascending to this realm.",
                                          color=0xF76103)
                        await ctx.send(embed=embed)
                    else:
                        new_loc = float(str(loc)+".001")
                        #print(location)
                        await cursor.execute( """UPDATE Users set location=? WHERE id=?""", ( new_loc, user_id ) )

                        card = series[realms[int(loc)-1]][0]

                        #print(card)

                        embed = discord.Embed(title=f"Realm {loc}, Floor 1 | {realms[int(loc)-1]}",
                                      description=f"{card[1]} stands before you.",
                                      color=0xF76103)
                        await ctx.send(embed=embed)



                else:
                    embed = discord.Embed(title=f"Realm not found!!",
                                          description=f"Please specify a legitamate realm number!!",
                                          color=0xF76103)
                    await ctx.send(embed=embed)


    @commands.hybrid_command(aliases=["fl"])
    async def floor(self, ctx, floor=None):
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

                #max_loc = int(str(user["maxloc"]).split(".")[0])
                max_floor = parseFloor(user["maxloc"])
                current_loc = int(str(user["location"]).split(".")[0])
                current_floor = parseFloor(user["location"])

                highest_floor = len(series[realms[current_loc-1]])

                #print("Max Loc: ", max_loc)
                #print("Max Floor: ", max_floor)
                #print("Realms: ", realms)
                #print("Num of Floors", highest_floor)


                if floor == None:
                    embed = discord.Embed(title=f"Realm {current_loc} | {realms[current_loc-1]}",
                                          description=f"You are at Floor **{current_floor}**",
                                          color=0xF76103)

                    index = 1
                    for i in range(highest_floor):
                        ## print(series[realms[index-1]][i][1]) --> Prints name of each card
                        if current_floor == index:
                            embed.add_field(name="", value=f"**Floor {index} |** **{series[realms[current_loc-1]][i][1]}**", inline=False)
                        else:
                            embed.add_field(name="", value=f"**Floor {index} |** {series[realms[current_loc-1]][i][1]}", inline=False)
                        index += 1

                    await ctx.send(embed=embed)

                elif floor in "next n nxt".split(" "):

                    if current_floor+1 > max_floor: # Player has not cleared the previous floor yet
                        embed = discord.Embed(title=f"You have not unlocked this floor!!",
                                      description=f"Please clear the current floor before progressing your journey.",
                                      color=0xF76103)
                        await ctx.send(embed=embed)

                    elif current_floor+1 > highest_floor:
                        embed = discord.Embed(title=f"Invalid Floor!!",
                                              description=f"You have cleared this Realm. Please travel to the next Realm to proceed",
                                              color=0xF76103)
                        await ctx.send(embed=embed)

                    else:
                        current_floor += 1
                        if current_floor > 9:
                            location = float(str(current_loc)+".0"+str(current_floor))
                        else:
                            location = float(str(current_loc)+".00"+str(current_floor))
                        #print(location)
                        await cursor.execute( """UPDATE Users set location=? WHERE id=?""", ( location, user_id ) )

                        card = series[realms[int(current_loc)-1]][int(current_floor)-1]

                        #embed = discord.Embed(title=f"Realm {current_loc}, Floor {current_floor} | {realms[int(current_loc)-1]}",
                        #                          description=f"You travel to the next floor where {card[1]} stands before you.",
                        #                          color=0x072A6C)
                        embed = displayFloor(current_loc, current_floor)
                        await ctx.send(embed=embed)

                elif isinstance(int(floor), int):
                    floor = int(floor)

                    if floor > max_floor:
                        embed = discord.Embed(title=f"You have not unlocked this floor!!",
                                      description=f"Please clear the current floor before progressing your journey.",
                                      color=0xF76103)
                        await ctx.send(embed=embed)

                    elif floor<= 0 or floor > highest_floor:
                        embed = discord.Embed(title=f"Invalid Floor!!",
                                              description=f"Please specify a legitamate Floor number!!",
                                              color=0xF76103)
                        await ctx.send(embed=embed)

                    else:
                        if floor > 9:
                            location = float(str(current_loc)+".0"+str(floor))
                        else:
                            location = float(str(current_loc)+".00"+str(floor))

                        #print(location)
                        await cursor.execute( """UPDATE Users set location=? WHERE id=?""", ( location, user_id ) )

                        card = series[realms[int(current_loc)-1]][int(floor)-1]


                        #embed = discord.Embed(title=f"Realm {current_loc}, Floor {floor} | {realms[int(current_loc)-1]}",
                        #                      description=f"You travel to Floor {floor}, where {card[1]} stands before you.",
                        #                      color=0x072A6C)
                        embed = displayFloor(current_loc, floor)

                        await ctx.send(embed=embed)



    # Battle function TESTING!!
    @commands.hybrid_command(aliases=["bt"])
    async def battle(self, ctx, amount=1):
        def displayHP(player, player_hp, enemy, enemy_hp, battle_round):
            player_hp_percentage = player.hp / (player_hp) * 100
            player_hp_filled = round(player_hp_percentage / 100 * hp_bar_length)
            player_hp_empty = hp_bar_length - player_hp_filled

            enemy_hp_percentage = enemy.hp / (enemy_hp) * 100
            enemy_hp_filled = round(enemy_hp_percentage / 100 * hp_bar_length)
            enemy_hp_empty = hp_bar_length - enemy_hp_filled

            if player.hp <= 0:
                player.hp = 0
                player_filled = 0
                player_hp_empty = 20

            if enemy.hp <= 0:
                enemy.hp = 0
                enemy_filled = 0
                enemy_hp_empty = 20

            player_hp_bar = "█" * player_hp_filled + "░" * player_hp_empty
            enemy_hp_bar = "█" * enemy_hp_filled + "░" * enemy_hp_empty

            embed = discord.Embed(title=f"{ctx.author} is challenging Floor {loc}-{floor}", color=0xF76103)
            embed.add_field(name=f"", value=f"**{player.name}** __{player.rarity}__ **Lvl {player.level} [Evo {player.evo}]**", inline=False)
            embed.add_field(name="", value=f"Element: {player.element} [{player.ele_mult}]", inline=False)
            embed.add_field(name=f"**{player.hp} / {player_hp}** ♥", value=f"`[{player_hp_bar}]`", inline=False)
            embed.add_field(name=f"", value=f"**{enemy.name}** __{enemy.rarity}__ **Lvl {enemy.level} [Evo {enemy.evo}]**", inline=False)
            embed.add_field(name="", value=f"Element: {enemy.element} [{enemy.ele_mult}]", inline=False)
            embed.add_field(name=f"**{enemy.hp} / {enemy_hp} ♥**", value=f"`[{enemy_hp_bar}]`", inline=False)

            if battle_round >= 1:
                embed.add_field(name=f"**[Round {battle_round}]**", value="", inline=False)

            return embed


        def calcEleAdvantage( element1, element2 ):
            '''Returns the first element advantage compared to the second'''

            elements = {"Light": {"Light": .75, "Dark": 1.5, "Neutral": 1, "Water": 1, "Ground": 1, "Electric": 1, "Fire": 1, "Grass": 1},

                        "Dark": {"Light": 1.5, "Dark": .75, "Neutral": 1, "Water": 1, "Ground": 1, "Electric": 1, "Fire": 1, "Grass": 1},

                        "Neutral": {"Light": 1, "Dark": 1, "Neutral": 1, "Water": 1, "Ground": 1, "Electric": 1, "Fire": 1, "Grass": 1},

                        "Water": {"Light": 1, "Dark": 1, "Neutral": 1, "Water": .75, "Ground": 1, "Electric": .5, "Fire": 1.5, "Grass": 1},

                        "Ground": {"Light": 1, "Dark": 1, "Neutral": 1, "Water": 1, "Ground": .75, "Electric": 1.5, "Fire": 1, "Grass": .5},

                        "Electric": {"Light": 1, "Dark": 1, "Neutral": 1, "Water": 1.5, "Ground": .5, "Electric": .75, "Fire": 1, "Grass": 1},

                        "Fire":  {"Light": 1, "Dark": 1, "Neutral": 1, "Water": .5, "Ground": 1, "Electric": 1, "Fire": .75, "Grass": 1.5},

                        "Grass": {"Light": 1, "Dark": 1, "Neutral": 1, "Water": 1, "Ground": 1.5, "Electric": 1, "Fire": .5, "Grass": .75}}

            return elements[element1][element2]



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
                        floor = parseFloor(user["location"])

                        await connection.commit()

                async with asqlite.connect(path_to_db+"card_data.db") as connection: # Get User card data
                    async with connection.cursor() as cursor:
                        user_id = ctx.author.id
                        await cursor.execute( "SELECT * FROM Upper WHERE owner=?", (user_id,) )
                        player_inventory = await cursor.fetchall()

                        for c in player_inventory:
                            if c["uid"] == user["card"]:
                                card_dex = c["dex"]
                                break

                        await cursor.execute( "SELECT * FROM Dex WHERE dex=?", (card_dex,) )
                        user_card = await cursor.fetchall()
                        user_card = user_card[0]

                        await connection.commit()


                #print(user_card["name"]) ## Raw Dex card. Will calculate the stats later.


                # user card = dictionary
                # Enemy Floor card is a Class

                card = series[realms[loc-1]][floor-1]

                #print("User Card ID:", c["uid"])
                user_card = UserCard(c, user_card)
                user_card.hp *= 10
                player_hp = user_card.hp
                
                oppo = FloorCard(loc, floor)
                oppo.hp *= 10
                enemy_hp = oppo.hp

                user_card.ele_mult = calcEleAdvantage(user_card.element, oppo.element)
                oppo.ele_mult = calcEleAdvantage(oppo.element, user_card.element)

                hp_bar_length = 20
                battle_round = 0


                #CRITICAL_MULTIPLIER = 1


                embed = displayHP(user_card, player_hp, oppo, enemy_hp, battle_round)

                bt = await ctx.send(embed=embed)
                await asyncio.sleep(1.5)


                async def battleRound( fighter1, fighter2 ):
                    def calcEffect( markiplier ):
                        if markiplier == 1:
                            return ""
                        elif markiplier == 1.5:
                            return "It was **Super Strong**!!"
                        elif markiplier == .5:
                            return "It was **Very Weak**..."
                        elif markiplier == .75:
                            return "It was **Not Very Effective**."

                    CRITICAL_MULTIPLIER = 1
                    miss = False
                    # New damage formula
                    if random.randint(1, 100) in range(1, 16):
                        CRITICAL_MULTIPLIER = 1.5

                    elif random.randint(1, 100) == 1:
                        miss = True

                    if not miss:
                        dmg = int((((fighter1.current_atk*fighter1.atk*10)+638000)/(8.7 * fighter2.df*10)) * fighter1.ele_mult * CRITICAL_MULTIPLIER)
                        fighter2.hp -= dmg

                    embed = displayHP(user_card, player_hp, oppo, enemy_hp, battle_round)

                    if miss:
                        embed.add_field(name="", value=f"**{fighter2.name}** manages to evade **{fighter1.name}!!**", inline=False)
                    elif CRITICAL_MULTIPLIER > 1:
                        embed.add_field(name="", value=f"**{fighter1.name}** deals **{dmg}** to **{fighter2.name}**. **CRITICAL HIT!!** {calcEffect( fighter1.ele_mult )}", inline=False)
                    else:
                        embed.add_field(name="", value=f"**{fighter1.name}** deals **{dmg}** to **{fighter2.name}.** {calcEffect( fighter1.ele_mult )}", inline=False)


                    await bt.edit(embed=embed)
                    await asyncio.sleep(2.5)


                while user_card.hp > 0 and oppo.hp > 0:
                    ## Determine who goes first 

                    if user_card.spd > oppo.spd:
                        #Player is faster
                        await battleRound( user_card, oppo )
                        if user_card.hp > 0 and oppo.hp > 0:
                            await battleRound( oppo, user_card )
                        else:
                            break

                    elif user_card.spd < oppo.spd:
                        await battleRound(oppo, user_card)
                        if user_card.hp > 0 and oppo.hp > 0:
                            await battleRound( user_card, oppo )
                        else:
                            break

                    else:
                        await battleRound(user_card, oppo) ## Handle same speed later

                    
                    battle_round += 1

                if user_card.hp > 0:
                    # Player Wins
                    print("player wins")
                    wun_reward = int(loc*1.5*(floor*.8) + 100)
                    exp_reward = random.randint(1, 5)

                    user_exp = user["exp"] + exp_reward
                    user_card.exp += exp_reward
                    user_wuns = user["wuns"] + wun_reward + random.randint(-10, 10)

                    async with asqlite.connect(path_to_db+"player_data.db") as connection: # Get Player data
                        async with connection.cursor() as cursor:
                            await cursor.execute("UPDATE Users set exp=? WHERE id=?", (user_exp, user_id))
                            await cursor.execute("UPDATE Users set wuns=? WHERE id=?", (user_wuns, user_id))
                            await connection.commit()

                    async with asqlite.connect(path_to_db+"card_data.db") as connection: # Get Player data
                        async with connection.cursor() as cursor:
                            #print("card ID:", user_card.id)
                            await cursor.execute("UPDATE Upper set exp=? WHERE uid=?", (user_card.exp, user_card.id))
                            await connection.commit()


                    dex = await oppo.getDex()
                    await Database.generateFodder(user_id, dex)

                    embed = discord.Embed(
                                title="Victory!",
                                description=f"Your **{user_card.name}** has defeated **{oppo.name}** in battle",
                                color=0x00FF00
                            )
                    embed.add_field(name="Rewards :moneybag:", value="", inline=False)
                    embed.add_field(name="", value=f"+ 1 *rare* **{oppo.name}** copy", inline=False)
                    embed.add_field(name="", value=f"+ {wun_reward} **Wuns** {Wuns} ", inline=False)
                    embed.set_footer(text=f"{user_card.name} +{exp_reward} EXP | Player +{exp_reward} EXP")
                    await ctx.send(embed=embed)



                    max_floor = parseFloor(user["maxloc"])
                    highest_floor = len(series[realms[loc-1]])
                    if floor == max_floor: ## Player clears a new floor
                        if max_floor == highest_floor: ## Player completes a realm/location
                            new_loc = str(loc+1) + ".001"

                            embed = discord.Embed(
                                title="Realm Cleared!!",
                                description="Please proceed to the next Realm with `.loc n`!",
                                color=0x00FF00
                            )
                            await ctx.send(embed=embed)

                        else:
                            if floor+1 > 9:
                                new_loc = str(loc) + ".0" + str(floor+1)
                            else:
                                new_loc = str(loc) + ".00" + str(floor+1)

                            embed = discord.Embed(
                                title="Floor Cleared!!",
                                description="Please proceed to the next Floor with `.fl n`!",
                                color=0x00FF00
                            )
                            await ctx.send(embed=embed)


                        async with asqlite.connect(path_to_db+"player_data.db") as connection:
                            async with connection.cursor() as cursor:
                                user_id = str(ctx.author.id)
                                await cursor.execute( """UPDATE Users set maxloc=? WHERE id=?""", ( new_loc, user_id ) )

                                await connection.commit()


                else:
                    # Player Loses
                    pass


            else:
                embed = discord.Embed(
                    title="No Card Equipped",
                    description="Please equip a card before battling!",
                    color=0xA80108
                )
                await ctx.send(embed=embed)