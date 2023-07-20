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


talents = {"Active": ["Amplifier", "Balancing Strike", "Blaze", "Breaker", "Celestial Blessing", "Devour", "Dexterity Drive", "Double-edged Strike", "Elemental Strike", "Endurance", "Evasion", "Freeze", "Lucky Coin", "Mana Reaver", "Offensive Stance", "Pain For Power", "Paralysis", "Poison", "Precision", "Regeneration", "Rejuvenation", "Restricted Instinct", "Smokescreen", "Time Attack", "Time Bomb", "Trick Room", "Ultimate Combo", "Unlucky Coin", "Vengeance" ],
           "PSV": ["Berserker", "Blood Surge", "Bloodthirster", "Celestial Influence", "Divine Blessing", "Dominance", "Grevious Limiter", "Life Sap", "Miracle Injection", "Overload", "Recoil", "Reflector", "Soul Stealer", "Transformation", "Underdog", "Executioner", "Protector", "Reversion", "Temporal Rewind"]}

def calcEffect( markiplier ):
    if markiplier == 1:
        return ""
    elif markiplier == 1.5:
        return "It was **Super Strong**!!"
    elif markiplier == .5:
        return "It was **Very Weak**..."
    elif markiplier == .75:
        return "It was **Not Very Effective**."


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


def applyTalent(fighter1, fighter2, battle_round):
    if fighter1.talent in talents["Active"]:
        ## Apply Active Talent
        if fighter1.mana == 100:
            if fighter1.talent == "Amplifier":
                if fighter1.rarity_s == "SR":
                    boost = 0.46
                elif fighter1.rarity_s == "UR":
                    boost = 0.52
                else:
                    boost = 0.40

                if fighter1.name in "Inosuke Hashibira,".split(","):
                    def_increase = fighter1.df * boost
                    #print("Defense Stat:", fighter1.df)
                    fighter1.df += def_increase

                fighter1.mana = 0

                message = f"**{fighter1.name}** uses Amplifier increasing DEF by __{round(def_increase)} [{round(boost*100)}%]__"
                return message

            if fighter1.talent == "Double-edged Strike":
                if fighter1.rarity_s == "SR":
                    damage = 0.27
                elif fighter1.rarity_s == "UR":
                    damage = 0.30
                else:
                    damage = 0.24

                if fighter1.name in "Giyu Tomioka,".split(","):
                    damage = damage * fighter1.spd

                ele_mult = calcEleAdvantage(fighter1.element, fighter2.element)

                damage = round(damage*ele_mult)
                backlash = round(damage*0.25)
                effect = calcEffect(ele_mult)

                fighter1.hp -= backlash
                fighter2.hp -= damage

                fighter1.mana = 0

                message = f"**{fighter1.name}** uses Double-edged Strike inflicting __{damage}__ damage to **{fighter2.name}**,\n and receives __{backlash}__ damage from the backlash. " + effect
                return message

            if fighter1.talent == "Pain For Power":
                if fighter1.rarity_s == "SR":
                    sacrifice = 0.12
                    increase = 0.54
                elif fighter1.rarity == "UR":
                    sacrifice = 0.14
                    increase = 0.60
                else:
                    sacrifice = 0.10
                    increase = 0.48

                fighter1.hp -= round(fighter1.hp*sacrifice)
                fighter1.current_atk += round(fighter1.current_atk*increase)
                fighter1.spd += fighter1.spd*increase

                fighter1.mana = 0

                message = f"**{fighter1.name}** uses Pain For Power, sacrifince __{round(fighter1.hp*sacrifice)}__ HP\n to increase ATK by __{round(fighter1.current_atk*increase)} [{round(increase*100)}%]__ \nand SPD by __{round(fighter1.spd*increase)} [{round(increase*100)}%]__"
                return message

            if fighter1.talent == "Paralysis":
                if fighter1.rarity_s == "SR":
                    defense_drop = 0.18
                    if random.randint(1, 100) in range(1, 73):
                        # Paralysis succeeded
                        fighter2.stunned = True
                elif fighter1.rarity_s == "UR":
                    defense_drop = 0.20
                    if random.randint(1, 100) in range(1, 81):
                        # Paralysis succeeded
                        fighter2.stunned = True
                else:
                    defense_drop = 0.16
                    if random.randint(1, 100) in range(1, 64):
                        # Paralysis succeeded
                        fighter2.stunned = True

                fighter2.df = fighter2.df - int(fighter2.df*defense_drop)
                fighter1.mana = 0

                if fighter2.stunned:
                    message = f"**{fighter1.name}** uses Paralysis, stunning {fighter2.name} for 1 turn and \nlowering their DEFENSE by __{int(defense_drop*100)}__%"
                else:
                    message = f"**{fighter1.name}** uses Paralysis but fails to stun!! **{fighter2.name}**'s \ndefense is lowered by __{int(defense_drop*100)}__%"
                return message


    elif fighter1.talent in talents["PSV"]:
        if fighter1.talent == "Bloodthirster":
            if fighter1.rarity_s == "SR":
                fighter1.lifesteal = 0.32
                fighter1.healing_bonus += 0.41
            if fighter1.rarity_s == "UR":
                fighter1.lifesteal = 0.36
                fighter1.healing_bonus += 0.46
            else:
                fighter1.lifesteal = 0.28
                fighter1.healing_bonus += 0.36

            if fighter1.healing_bonus > 0.5:
                fighter1.healing_bonus = 0.5

            message = f"**{fighter1.name}** uses Bloodthirster, Granting __{int(fighter1.lifesteal*100)}__% LIFESTEAL\n and __{int(fighter1.healing_bonus*100)}__% bonus healing"
            return message

        if fighter1.talent == "Executioner":
            if fighter1.rarity_s == "SR":
                if fighter2.hp < fighter2.max_hp*0.48:
                    if fighter1.talent_proc:
                        # Talent Already proc'd
                        pass
                    else:
                        fighter1.talent_proc = True
                        fighter1.atk *= 1.9
                        increase = 90

            elif fighter1.rarity_s == "UR":
                if fighter2.hp < fighter2.max_hp*0.54:
                    if fighter1.talent_proc:
                        # Talent Already proc'd
                        pass
                    else:
                        fighter1.talent_proc = True
                        fighter1.atk *= 2.0
                        increase = 100

            else:
                if fighter2.hp < fighter2.max_hp*0.43:
                    if fighter1.talent_proc:
                        # Talent Already proc'd
                        pass
                    else:
                        fighter1.talent_proc = True
                        fighter1.atk *= 1.8
                        increase = 80

            message = f"**{fighter1.name}** uses Executioner, increasing their attack for __{increase}__%!!"
            return message

        if fighter1.talent == "Life Sap":
            if fighter1.rarity_s == "SR":
                damage_dealt = round(fighter2.max_hp*0.03)
                healing = round(damage_dealt*1.75)

            elif fighter1.rarity_s == "UR":
                damage_dealt = round(fighter2.max_hp*0.04)
                healing = round(damage_dealt*1.75)

            else:
                damage_dealt = round(fighter2.max_hp*0.03)
                healing = round(damage_dealt*1.75)              

            fighter1.hp += healing
            if fighter1.hp > fighter1.max_hp:
                fighter1.hp = fighter1.max_hp

            fighter2.hp -= damage_dealt

            message = f"**{fighter1.name}** uses Life Sap, inflicting __{damage_dealt}__ damage to \n**{fighter2.name}** and heals for __{healing}__ HP"
            return message

        if fighter1.talent == "Miracle Injection":
            if battle_round == 1:
                if fighter1.rarity_s == "SR":
                    bonus = round(fighter1.max_hp *.18)

                elif fighter1.rarity_s == "UR":
                    bonus = round(fighter1.max_hp *.2)

                else:
                    bonus = round(fighter1.max_hp *.16)

                fighter1.max_hp -= bonus
                fighter1.hp -= bonus

                fighter1.atk += bonus*2
                fighter1.df += bonus*2
                fighter1.spd += bonus*2

                message = f"**{fighter1.name}** uses Miracle Injection, sacrificing HP to imbue themself with power\n and increasing all stats by __{bonus*6}__!!"
                return message

        if fighter1.talent == "Temporal Rewind":
            if battle_round == 4:
                damage = round((fighter1.max_hp - fighter1.hp)/2)
                healing = round(damage * (1 + fighter1.healing_bonus))

                fighter1.hp += healing
                if fighter1.hp > fighter1.max_hp:
                    fighter1.hp = fighter1.max_hp

                fighter2.hp -= damage

                message = f"**{fighter1.name}** reverts back in time and restores __{healing}__ HP due to Temporal Rewind\n and simultaneously deals __{damage}__ true damage to **{fighter2.name}**!!"
                return message





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
        def displayHP(player, enemy, battle_round):
            player_hp_percentage = player.hp / (player.max_hp) * 100
            player_hp_filled = round(player_hp_percentage / 100 * hp_bar_length)
            player_hp_empty = hp_bar_length - player_hp_filled

            enemy_hp_percentage = enemy.hp / (enemy.max_hp) * 100
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

            ## Display Mana
            if player.max_mana == 0:
                player_mp_percentage = 0
            else:
                player_mp_percentage = player.mana / player.max_mana*100
            player_mp_filled = round(player_mp_percentage / 100 * mp_bar_length)
            player_mp_empty = mp_bar_length - player_mp_filled

            if enemy.max_mana == 0:
                enemy_mp_percentage = 0
            else:
                enemy_mp_percentage = enemy.mana / enemy.max_mana*100
            enemy_mp_filled = round(enemy_mp_percentage / 100 * mp_bar_length)
            enemy_mp_empty = mp_bar_length - enemy_mp_filled

            if player.mana >= 100 or player_mp_filled > 20:
                player.mana = 100
                player_mp_filled = 20
                player_mp_empty = 0

            if enemy.mana >= 100 or enemy_mp_filled > 20:
                enemy.mana = 100
                enemy_mp_filled = 20
                enemy_mp_empty = 0

            player_mp_bar = "●" * player_mp_filled + "◌" * player_mp_empty
            enemy_mp_bar = "●" * enemy_mp_filled + "◌" * enemy_mp_empty

            embed = discord.Embed(title=f"{ctx.author} is challenging Floor {loc}-{floor}", color=0xF76103)
            embed.add_field(name=f"", value=f"**{player.name}** __{player.rarity}__ **Lvl {player.level} [Evo {player.evo}]**", inline=False)
            embed.add_field(name="", value=f"Element: {player.element} [{player.ele_mult}]", inline=False)
            embed.add_field(name=f"**{player.hp} / {player.max_hp}** ♥", value=f"`[{player_hp_bar}]`", inline=False)
            embed.add_field(name=f"**{player.mana} / {player.max_mana}** Ψ", value=f"`<{player_mp_bar}>`", inline=False)
            embed.add_field(name=f"", value=f"**{enemy.name}** __{enemy.rarity}__ **Lvl {enemy.level} [Evo {enemy.evo}]**", inline=False)
            embed.add_field(name="", value=f"Element: {enemy.element} [{enemy.ele_mult}]", inline=False)
            embed.add_field(name=f"**{enemy.hp} / {enemy.max_hp}** ♥", value=f"`[{enemy_hp_bar}]`", inline=False)
            embed.add_field(name=f"**{enemy.mana} / {enemy.max_mana} Ψ**", value=f"`<{enemy_mp_bar}>`", inline=False)

            if battle_round >= 1:
                embed.add_field(name=f"**[Round {battle_round}]**", value="", inline=False)

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
                user_card.battlePrep()
                
                oppo = FloorCard(loc, floor)
                oppo.battlePrep()

                user_card.ele_mult = calcEleAdvantage(user_card.element, oppo.element)
                oppo.ele_mult = calcEleAdvantage(oppo.element, user_card.element)

                hp_bar_length = 20
                mp_bar_length = 20
                battle_round = 0


                #CRITICAL_MULTIPLIER = 1


                embed = displayHP(user_card, oppo, battle_round)

                bt = await ctx.send(embed=embed)
                await asyncio.sleep(1.5)
                battle_round += 1


                async def battleRound( fighter1, fighter2 ):
                    if fighter1.stunned:
                        if fighter1.talent == "Recoil":
                            pass
                        elif random.randint(1, 20) == 1:
                            embed.add_field(name="", value=f"**{fighter1.name}** is stunned but resists and continues to fight!!", inline=False)

                            await bt.edit(embed=embed)
                            await asyncio.sleep(2.5)
                        else:
                            embed = displayHP(user_card, oppo, battle_round)

                            embed.add_field(name="", value=f"**{fighter1.name}** is stunned and is unable to attack!!", inline=False)
                            fighter1.stunned = False

                            await bt.edit(embed=embed)
                            await asyncio.sleep(2.5)
                            return

                    talent_message = applyTalent( fighter1, fighter2, battle_round )
                    fighter1.critical_mult = 1

                    miss = False
                    # Evasion / Critical rates
                    evasion = random.randint(1, 100)
                    if evasion in range(1, fighter1.evasion+1):
                        #print("Evasion Roll: ", evasion)
                        miss = True

                    crit = random.randint(1, 100)
                    if crit in range(1, fighter1.critical_rate+1):
                        #print("Crit Roll: ", crit, "Range: ", range(1, fighter1.critical_rate+1))
                        #print(crit in range(1, fighter1.critical_rate+1))
                        fighter1.critical_mult = 1.75



                    if fighter1.max_mana > 0:
                        speed_multiplier = fighter1.spd/fighter2.spd
                        if speed_multiplier >= 1.4:
                            speed_multiplier = 1.4
                        else:
                            speed_multiplier = 1

                        mana_gained = int((15*(2-(fighter1.hp/fighter1.max_hp)))+(2*15/battle_round)*speed_multiplier)
                        fighter1.mana += mana_gained

                    if fighter2.max_mana > 0:
                        speed_multiplier = fighter2.spd/fighter1.spd
                        if speed_multiplier >= 1.4:
                            speed_multiplier = 1.4
                        else:
                            speed_multiplier = 1

                        mana_gained = int((15*(2-(fighter2.hp/fighter2.max_hp)))+(2*15/battle_round)*speed_multiplier)
                        fighter2.mana += mana_gained

                    #print(fighter1.talent)

                    embed = displayHP(user_card, oppo, battle_round)

                    if talent_message != None:
                        embed.add_field(name="", value=talent_message, inline=False)
                        await bt.edit(embed=embed)
                        await asyncio.sleep(2.5)

                    if not miss:
                        dmg = int((((fighter1.current_atk*fighter1.atk)+638000)/(8.7 * fighter2.df)) * fighter1.ele_mult * fighter1.critical_mult)
                        fighter2.hp -= dmg
                        fighter1.hp += int(dmg*fighter1.lifesteal*(1+fighter1.healing_bonus))
                        if fighter1.hp > fighter1.max_hp:
                            fighter1.hp = fighter1.max_hp

                        embed = displayHP(user_card, oppo, battle_round)
                        if talent_message != None:
                            embed.add_field(name="", value=talent_message, inline=False)


                    if miss:
                        embed.add_field(name="", value=f"**{fighter2.name}** manages to evade **{fighter1.name}!!**", inline=False)
                    elif fighter1.critical_mult > 1:
                        embed.add_field(name="", value=f"**{fighter1.name}** deals **{dmg}** to **{fighter2.name}**. **CRITICAL HIT!!**\n {calcEffect( fighter1.ele_mult )}", inline=False)
                    else:
                        embed.add_field(name="", value=f"**{fighter1.name}** deals **{dmg}** to **{fighter2.name}.**\n {calcEffect( fighter1.ele_mult )}", inline=False)

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

                    elif oppo.spd > user_card.spd:
                        await battleRound(oppo, user_card)
                        if user_card.hp > 0 and oppo.hp > 0:
                            await battleRound( user_card, oppo )
                        else:
                            break

                    else:
                        await battleRound(user_card, oppo) ## Handle same speed later
                        if user_card.hp > 0 and oppo.hp > 0:
                            await battleRound( oppo, user_card )
                        else:
                            break

                    
                    battle_round += 1

                if user_card.hp > 0:
                    # Player Wins
                    #rint("player wins")
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