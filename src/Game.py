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

from Talents import *

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

                    if current_floor+1 > highest_floor:
                        embed = discord.Embed(title=f"Invalid Floor!!",
                                              description=f"You have cleared this Realm. Please travel to the next Realm to proceed",
                                              color=0xF76103)
                        await ctx.send(embed=embed)

                    elif current_floor+1 > max_floor: # Player has not cleared the previous floor yet
                        embed = discord.Embed(title=f"You have not unlocked this floor!!",
                                      description=f"Please clear the current floor before progressing your journey.",
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
        def displayBar( fighter ):
            hp_percentage = fighter.hp / (fighter.max_hp) * 100
            hp_filled = round(hp_percentage / 100 * hp_bar_length)
            hp_empty = hp_bar_length - hp_filled

            if fighter.hp <= 0:
                fighter.hp = 0
                filled = 0
                hp_empty = 20

            hp_bar = "█" * hp_filled + "░" * hp_empty

            ## Display Mana
            if fighter.max_mana == 0:
                mp_percentage = 0
            else:
                mp_percentage = fighter.mana / fighter.max_mana*100

            mp_filled = round(mp_percentage / 100 * mp_bar_length)
            mp_empty = mp_bar_length - mp_filled


            if fighter.mana >= 100 or mp_filled > 20:
                fighter.mana = 100
                mp_filled = 20
                mp_empty = 0

            mp_bar = "■" * mp_filled + "□" * mp_empty

            return hp_bar, mp_bar

        def displayHP(player, enemy, battle_round):
            player_hp_bar, player_mp_bar = displayBar(player)
            enemy_hp_bar, enemy_mp_bar = displayBar(enemy)

            embed = discord.Embed(title=f"{ctx.author} is challenging Floor {loc}-{floor}", color=0xF76103)
            embed.add_field(name=f"", value=f"**{player.name}** __{player.rarity}__ **Lvl {player.level} [Evo {player.evo}]**", inline=False)
            embed.add_field(name="", value=f"Element: {player.element} [{player.ele_mult}]", inline=False)
            embed.add_field(name=f"**{player.hp} / {player.max_hp}** ♥", value=f"`[{player_hp_bar}]`", inline=False)
            embed.add_field(name=f"**{player.mana} / {player.max_mana}** Ψ", value=f"`[{player_mp_bar}]`", inline=False)
            embed.add_field(name=f"", value=f"**{enemy.name}** __{enemy.rarity}__ **Lvl {enemy.level} [Evo {enemy.evo}]**", inline=False)
            embed.add_field(name="", value=f"Element: {enemy.element} [{enemy.ele_mult}]", inline=False)
            embed.add_field(name=f"**{enemy.hp} / {enemy.max_hp}** ♥", value=f"`[{enemy_hp_bar}]`", inline=False)
            embed.add_field(name=f"**{enemy.mana} / {enemy.max_mana} Ψ**", value=f"`[{enemy_mp_bar}]`", inline=False)

            if battle_round >= 1:
                embed.add_field(name=f"**[Round {battle_round}]**", value="", inline=False)

            return embed

        def updateEmbed(player, enemy, embed):
            player_hp_bar, player_mp_bar = displayBar(player)
            enemy_hp_bar, enemy_mp_bar = displayBar(enemy)

            embed.set_field_at(0, name=f"", value=f"**{player.name}** __{player.rarity}__ **Lvl {player.level} [Evo {player.evo}]**", inline=False)
            embed.set_field_at(1, name="", value=f"Element: {player.element} [{player.ele_mult}]", inline=False)
            embed.set_field_at(2, name=f"**{player.hp} / {player.max_hp}** ♥", value=f"`[{player_hp_bar}]`", inline=False)
            embed.set_field_at(3, name=f"**{player.mana} / {player.max_mana}** Ψ", value=f"`[{player_mp_bar}]`", inline=False)
            embed.set_field_at(4, name=f"", value=f"**{enemy.name}** __{enemy.rarity}__ **Lvl {enemy.level} [Evo {enemy.evo}]**", inline=False)
            embed.set_field_at(5, name="", value=f"Element: {enemy.element} [{enemy.ele_mult}]", inline=False)
            embed.set_field_at(6, name=f"**{enemy.hp} / {enemy.max_hp}** ♥", value=f"`[{enemy_hp_bar}]`", inline=False)
            embed.set_field_at(7, name=f"**{enemy.mana} / {enemy.max_mana} Ψ**", value=f"`[{enemy_mp_bar}]`", inline=False)

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
                            embed = displayHP(user_card, oppo, battle_round)

                            embed.add_field(name="", value=f"**{fighter1.name}** is immune to status effects due to Recoil", inline=False)
                            fighter1.stunned = False
                            fighter2.stunned = False

                            await bt.edit(embed=embed)
                            await asyncio.sleep(2.5)
                        elif random.randint(1, 20) == 1:
                            embed = displayHP(user_card, oppo, battle_round)

                            embed.add_field(name="", value=f"**{fighter1.name}** is stunned but resists and continues to fight!!", inline=False)
                            fighter1.stunned = False

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
                    embed = displayHP(user_card, oppo, battle_round)

                    if talent_message != None:
                        embed = updateEmbed(user_card, oppo, embed)
                        embed.add_field(name="", value=talent_message, inline=False)
                        await bt.edit(embed=embed)
                        await asyncio.sleep(2.5)

                    fighter1.critical_mult = 1

                    miss = False
                    # Evasion / Critical rates
                    evasion = random.randint(1, 100)
                    #print("Evasion Roll: ", evasion)
                    #print(fighter1.evasion)
                    if evasion in range(1, fighter2.evasion+1):
                        miss = True

                    crit = random.randint(1, 100)
                    if crit in range(1, fighter1.critical_rate+1):
                        #print("Crit Roll: ", crit, "Range: ", range(1, fighter1.critical_rate+1))
                        #print(crit in range(1, fighter1.critical_rate+1))
                        fighter1.critical_mult = 1.75+fighter1.critical_bonus_dmg

                    if fighter1.max_mana > 0:
                        speed_multiplier = fighter1.spd/fighter2.spd
                        if speed_multiplier > 1.4:
                            speed_multiplier = 1.4
                        elif speed_multiplier < 1:
                            speed_multiplier = 1

                        mana_gained = int((fighter1.mana_regen*(fighter1.mana_regen_bonus)*(2-(fighter1.hp/fighter1.max_hp)))+(2*fighter1.mana_regen*(fighter1.mana_regen_bonus)/battle_round)*speed_multiplier)
                        fighter1.mana += mana_gained

                    if fighter2.max_mana > 0:
                        speed_multiplier = fighter2.spd/fighter1.spd
                        if speed_multiplier >= 1.4:
                            speed_multiplier = 1.4
                        elif speed_multiplier < 1:
                            speed_multiplier = 1

                        mana_gained = int((fighter2.mana_regen*(fighter2.mana_regen_bonus)*(2-(fighter2.hp/fighter2.max_hp)))+(2*(fighter2.mana_regen*(fighter2.mana_regen_bonus)/battle_round)*speed_multiplier))
                        fighter2.mana += mana_gained

                    #print(fighter1.talent)


                    if fighter1.regen_stacks > 0:
                        if battle_round in fighter1.regen_lose:
                            fighter1.regen_lose.remove(battle_round)
                            fighter1.regen_stacks -= 1

                        healing = int(fighter1.max_hp * (0.075 * fighter1.regen_stacks)) # Healing * stacks
                        fighter1.hp += healing
                        if fighter1.hp > fighter1.max_hp:
                            fighter1.hp = fighter1.max_hp

                        embed = updateEmbed(user_card, oppo, embed)
                        message = f"**{fighter1.name}** restores __{healing}__ HP due to Regneration!!"
                        embed.add_field(name="", value=message, inline=False)
                        await bt.edit(embed=embed)
                        await asyncio.sleep(2.5)


                    if not miss:
                        if fighter2.endurance > battle_round:
                            dmg = int(((((fighter1.current_atk*fighter1.atk)+638000)/(8.7 * fighter2.df)) * fighter1.ele_mult * fighter1.critical_mult) *0.35)
                        else:
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

                    embed = updateEmbed(user_card, oppo, embed)
                    await bt.edit(embed=embed)
                    await asyncio.sleep(2.5)

                    ## TIME BOMBs
                    if fighter1.recoil and fighter2.recoil:
                        damage = round(fighter1.max_hp*0.03)
                        fighter1.hp -= damage
                        message = f"**{fighter1.name}** is affected by Recoil, taking __{damage}__ damage!!"
                        embed = updateEmbed(user_card, oppo, embed)
                        embed.add_field(name="", value=message, inline=False)
                        await bt.edit(embed=embed)
                        await asyncio.sleep(2.5)

                        damage = round(fighter2.max_hp*0.03)
                        fighter2.hp -= damage
                        message = f"**{fighter2.name}** is affected by Recoil, taking __{damage}__ damage!!"
                        embed = updateEmbed(user_card, oppo, embed)
                        embed.add_field(name="", value=message, inline=False)
                        await bt.edit(embed=embed)
                        await asyncio.sleep(2.5)
                    else:
                        if fighter2.tbomb > 0 and battle_round == fighter2.tbomb:
                            fighter2.tbomb = False

                            if random.randint(1, 10) == 1:
                                message = f"**{fighter1.name}**'s Time Bomb misfired causing 0 damage to **{fighter2.name}** D:"
                            else:
                                damage = round(fighter1.current_atk*0.3)
                                fighter2.hp -= damage

                                message = f"**{fighter1.name}**'s Time Bomb exploded, dealing __{damage}__ true damage\n to **{fighter2.name}**!!"


                            embed = updateEmbed(user_card, oppo, embed)
                            embed.add_field(name="", value=message, inline=False)
                            await bt.edit(embed=embed)
                            await asyncio.sleep(2.5)

                        elif fighter2.poison > 0: ## Fighter 2 is poisoned
                            if random.randint(1, 10) == 1:
                                fighter2.poison = 0 ## RESISTS
                                message = f"**{fighter2.name}** was affected by Poison, but they **resisted**!! D:"
                            else:
                                fighter2.hp -= round(fighter2.max_hp * fighter2.poison * 0.05)
                                message = f"**{fighter2.name}** was affected by Poison, and suffers __{round(fighter2.poison*0.05*100)}%__ of their MAX HP D:"
                                fighter2.poison += 1

                            embed = updateEmbed(user_card, oppo, embed)
                            embed.add_field(name="", value=message, inline=False)
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
                    max_loc = int(user["maxloc"])
                    highest_floor = len(series[realms[loc-1]])
                    if loc == max_loc:
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