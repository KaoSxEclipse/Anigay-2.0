import random

talents = {"Active": ["Amplifier", "Balancing Strike", "Blaze", "Breaker", "Celestial Blessing", "Devour", "Dexterity Drive", "Double-edged Strike", "Elemental Strike", "Endurance", "Evasion", "Freeze", "Lucky Coin", "Mana Reaver", "Offensive Stance", "Pain For Power", "Paralysis", "Poison", "Precision", "Regeneration", "Rejuvenation", "Restricted Instinct", "Smokescreen", "Time Attack", "Time Bomb", "Trick Room", "Ultimate Combo", "Unlucky Coin", "Vengeance" ],

           "PSV": ["Berserker", "Blood Surge", "Bloodthirster", "Celestial Influence", "Divine Blessing", "Dominance", "Grevious Limiter", "Life Sap", "Miracle Injection", "Overload", "Recoil", "Reflector", "Soul Stealer", "Transformation", "Underdog", "Executioner", "Protector", "Reversion", "Self Destruct", "Temporal Rewind"]}

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

            if fighter1.talent == "Devour":
                if fighter1.rarity_s == "SR":
                    dmg = 0.09
                    increase = 0.14
                elif fighter1.rarity_s == "UR":
                    dmg = 0.10
                    increase = 0.16
                else:
                    dmg = 0.08
                    increase = 0.12

                if fighter1.hp > fighter2.hp:
                    bonus = 0.60
                else:
                    bonus = 0.15

                devour = round(fighter1.max_hp * 0.09)
                devour += round(bonus*abs(fighter1.max_hp - fighter2.max_hp))
                hp_increase = round(fighter1.max_hp * increase)
                fighter1.max_hp += hp_increase
                fighter2.hp -= devour
                fighter1.mana = 0

                message = f"**{fighter1.name}** devours **{fighter2.name}**'s HP for __{devour}__ damage\n and increasing MAX HP by __[{hp_increase}]{round(increase*100)}%__"
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

            if fighter1.talent == "Endurance":
                fighter1.endurance = battle_round + 3
                fighter1.mana = 0

                message = f"**{fighter1.name}** summons a defensive shield, buffing themselves with Endurance for 3 turns!!"
                return message

            if fighter1.talent == "Evasion":
                if fighter1.rarity_s == "SR":
                    bonus = 28
                elif fighter1.rarity_s == "UR":
                    bonus = 32
                else:
                    bonus = 24

                fighter1.evasion += bonus
                if fighter1.evasion > 65:
                    fighter1.evasion = 65

                fighter1.mana = 0

                message = f"**{fighter1.name}** uses evasive maneuvers, increasing\n Evasion by __{bonus}__% to __{fighter1.evasion}__%!!"
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

            if fighter1.talent == "Regeneration":
                fighter1.regen_stacks += 1
                fighter1.regen_lose.append(battle_round+4) ## When hero will lose next stack
                fighter1.mana = 0

                message = f"**{fighter1.name}** uses Regeneration, granting themselves a stack of Regneration!!"
                return message

            if fighter1.talent == "Time Bomb":
                fighter2.tbomb = battle_round+1
                fighter1.mana = 0

                message = f"**{fighter1.name}** snaps, inflicting a stack of Time Bomb on **{fighter2.name}**!!"
                return message

            if fighter1.talent == "Unlucky Coin":
                if fighter1.rarity_s == "SR":
                    max_range = 36
                elif fighter1.rarity_s == "UR":
                    max_range = 40
                else:
                    max_range = 32

                # Lower amount
                roll = random.randint(1, max_range)
                decrease = roll*2

                # Which stat to lower
                stat = random.randint(1, 4)
                if stat == 1:
                    amount = round(fighter2.hp*(decrease/100))
                    stat = "HP"
                    fighter2.hp -= amount
                elif stat == 2:
                    amount = round(fighter2.current_atk*(decrease/100))
                    stat = "ATK"
                    fighter2.current_atk -= amount
                elif stat == 3:
                    amount = round(fighter2.df*(decrease/100))
                    stat = "DEF"
                    fighter2.df -= amount
                else:
                    amount = round(fighter2.spd*(decrease/100))
                    stat = "SPD"
                    fighter2.spd -= amount

                fighter1.mana = 0

                message = f"**{fighter1.name}** flips the Unlucky Coin and rolls a **{roll}**!\n **{fighter2.name}** has its {stat} decreased by __{decrease}%__"
                return message


    elif fighter1.talent in talents["PSV"]:
        if fighter1.talent == "Berserker":
            if fighter1.rarity_s == "SR":
                boost = 54
            elif fighter1.rarity_s == "UR":
                boost = 60
            else:
                boost = 48

            if fighter1.hp < round(fighter1.max_hp*0.4): # At 40%
                if fighter1.berserker == 1:
                    fighter1.berserker += boost/100
                else:
                    fighter1.berserker = ((boost)/(fighter1.berserker) + fighter1.berserker*100)
                    fighter1.berserker = fighter1.berserker/100
                    print(boost, ":", fighter1.berserker, ":", fighter1.berserker)

                if fighter1.name in "Satoru Gojo,Kanao Tsuyuri,Kyojiro Rengoku,".split(","):
                    fighter1.current_atk = (fighter1.atk*fighter1.berserker)
                    message = f"**{fighter1.name}** uses Berserker, standing their ground and \nincreasing ATK by __{round(fighter1.current_atk*boost/100)}[{int(boost)}]%__"

                else:
                    fighter1.df = (fighter1.df*fighter1.berserker)
                    message = f"**{fighter1.name}** uses Berserker, standing their ground and \nincreasing DEF by __{round(fighter1.current_atk*boost/100)}[{int(boost)}]%__"

                return message


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

        if fighter1.talent == "Self Destruct":
            if battle_round == 1:
                fighter1.hp -= round(fighter1.hp*0.8)
                fighter1.current_atk -= fighter1.current_atk*0.8
                fighter1.df -= fighter1.df*0.8
                fighter1.spd -= fighter1.spd*0.8

                message = f"**{fighter1.name}** decreases all stats by __80%__, causing himself to **SELF DESTRUCT**!!"
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