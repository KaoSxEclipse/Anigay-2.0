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

path_to_db = ""

# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
# Dev ID's
devids = [533672241448091660, 301494278901989378, 318306707493093376, 552151385127256064]
# Privileged Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='a!', intents=intents)
# Create variables for emojis in json dict
with open("CustomEmojis", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")


class MyHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping, filter_commands=True):
        embed = discord.Embed(title='Need a hand?', color=discord.Color.teal())
        embed.set_footer(text="Use Help [command] for help. | <> is required, [] is optional.")
        for cog, commands in mapping.items():
            if cog:
                cog_name = cog.qualified_name.replace('_', ' ')
                if True:
                    emoji = ''
                    if cog_name == 'Currency':
                        emoji = "<:scales:1072373342281142412>"
                    if cog_name == 'Start':
                        emoji = "<:star2:1072373582165975050>"
                    if cog_name == 'User':
                        emoji = "<:bust_in_silhouette:1072373688885854272>"
                    if cog_name == 'Card':
                        emoji = "<:diamonds:1072645673582858250>"

                # Adding embed fields for each command category.
                # Not displaying hidden categories.
                if cog_name not in ['Dev', 'Help']:
                    command_list = []
                    for command in commands:
                        command_list.append(command.name)
                    if cog_name in ['General']:
                        command_list.append('help')
                    command_list.sort()
                    command_list = '`, `'.join(command_list)
                    embed.add_field(name=f'{emoji} __{cog_name}__', value=f'`{command_list}`', inline=False)

        await self.context.reply(embed=embed)

    """!help <command>"""

    async def send_command_help(self, command):
        cog_name = command.cog_name
        if cog_name in ['Dev'] and self.context.author.id not in devids:
            return

        if command.cog:
            cog_name = cog_name.replace('_', ' ')

        embed = discord.Embed(title=f'{cog_name} › {command.name}', description=command.description,
                              color=0x00f780)
        if True:
            required = ''
            optional = ''
            foobar = ''
            if '<' in command.signature:
                required = '`<> - required`\n'
            if '[' in command.signature:
                optional = '`[] - optional`\n'
            if '|' in command.signature:
                foobar = '`item1/item2 - choose either item1 or item2`\n'

        if required != '' or optional != '':
            embed.add_field(name='Syntax:', value=required + optional + foobar, inline=False)

        signature = command.signature.replace("=", "").replace("None", "").replace("...", "").replace("|", "/").replace(
            '"', "").replace("_", " ")
        embed.add_field(name='Usage:',
                        value=f"```{bot.command_prefix if 'Slash command only.' not in command.description else '/'}{command.name} {signature}```",
                        inline=False)

        if command.aliases:
            embed.add_field(name='Aliases:', value='`' + '`, `'.join(command.aliases) + f'`, `{command.name}`',
                            inline=False)

        embed.set_footer(text=f'Use {bot.command_prefix}help [command] for more info on a specific command.')

        await self.context.reply(embed=embed)

    """!help <cog>"""

    async def send_cog_help(self, cog):
        return
        await self.context.reply("This is help cog")

# test command can be removed / ignored
class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


# Profile Start commands, prints User's ID and name, returns an embed for now
class ProfileStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="start", description="Start your journey!",
                             usage="type a!start or /start to begin playin!")
    async def start(self, ctx):
        async with asqlite.connect("player_data.db") as connection:
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

                    async with asqlite.connect("card_data.db") as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute("SELECT * FROM Dex")

                            card_list = await cursor.fetchall()
                            cards = len(card_list)

                    rand_card = random.randint(0, cards-1)
                    card_name = card_list[rand_card]["name"]

                    if rand_card in range(2, 5):
                        rand_card = random.randint(0, cards-1)

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

               #await connection.commit()


# Currency Based Commands go in this Cog
# Allows Devs (Anyone atm) to give others currency + view the Balance of yourself and others.
class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Gives a user money from own balance
    @commands.hybrid_command(name="give", aliases=['g'])
    async def give(self, ctx, user: discord.User, amount: int):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_giver = int(ctx.author.id)

                user_target = int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_giver,))
                user_giver_data = await cursor.fetchall()

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_target,))
                user_target_data = await cursor.fetchall()

                if len(user_giver_data) != 0 and len(user_target_data) != 0:  ## User is found
                    user_data_giver = user_giver_data[0]
                    user_data_target = user_target_data[0]

                    if user_data_giver["wuns"] >= amount:

                        new_balance_target = user_data_target["wuns"] + amount
                        new_balance_giver = user_data_giver["wuns"] - amount
                        amount_readable = "{:,}".format(amount)
                        await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance_giver, user_giver))
                        await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance_target, user_target))
                        embed = discord.Embed(title=f"{ctx.author} has blessed you",
                                              description=f"{ctx.author} has given {user_target} {Wuns}{amount_readable} wuns",
                                              color=0x04980f)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"Not Enough Money!!",
                                              description=f"You poor fool. Learn to count before giving money away, eh?",
                                              color=0xA80108)
                        await ctx.send(embed=embed)

                else:  # User not found
                    if len(user_giver_data) == 0:
                        embed = discord.Embed(title=f"Unregistered User",
                                              description=f"Looks like you haven't started yet!! Type a!start!",
                                              color=0xA80108)
                        await ctx.send(embed=embed)

                    elif len(user_target_data) == 0:  # Target not found
                        embed = discord.Embed(title=f"{user.name} not found",
                                              description=f"Have {user.name} type a!start!",
                                              color=0xA80108)
                        await ctx.send(embed=embed)

    # Views a user balance if "None" returns Command Authors balance
    @commands.hybrid_command(aliases=['bal'])
    async def balance(self, ctx, user: discord.User = None):
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:

                if not user:
                    user = ctx.author

                user_id = int(ctx.author.id) if user is None else int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  # User is found
                    user_data = user_data[0]
                    balance = user_data["wuns"]
                    balance_readable = "{:,}".format(balance)

                    embed = discord.Embed(title=f"{user}'s Balance", color=0x03F76A)
                    embed.add_field(name="", value=f"{user} has {Wuns}{balance_readable} wuns")
                    embed.set_thumbnail(url=user.avatar)
                    embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found",
                                          description=f"ask {user.mention} to type a!start",
                                          color=0xF76103)
                    await ctx.send(embed=embed)

        # Random Claim command, need to add a cooldown. possible feature early on to earn Currency?

    @commands.hybrid_command(name="claim", description="get a random amount of gold added to your balance")
    @commands.cooldown(1, 28800, type=BucketType.user)
    @commands.has_permissions(view_channel=True, read_messages=True, send_messages=True)
    async def claim(self, ctx):
        """Claim Gold"""
        async with asqlite.connect(path_to_db+"player_data.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM Users WHERE id=?", (ctx.author.id,))
                user_data = await cursor.fetchall()
                claim_value = random.randint(10, 50)

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    new_balance = user_data["wuns"] + claim_value
                    await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance, ctx.author.id))
                    embed = discord.Embed(title="**Claim Complete**", color=discord.Color.purple())
                    embed.add_field(name=f"Amount Claimed {Wuns}{claim_value} wuns",
                                    value=f"Your new balance is {Wuns}{new_balance}")
                await ctx.send(embed=embed)

        @self.claim.error
        async def claim(self, ctx, error):
            if isinstance(error, CommandOnCooldown):
                retry_after_seconds = error.retry_after
                time_remaining = datetime.datetime.now() + timedelta(seconds=retry_after_seconds)
                timestamp = int(time_remaining.timestamp())
                time_remaining = f"<t:{timestamp}:R>"
                await ctx.send(f"{ctx.author.mention}, you can claim again in {time_remaining}.")

            else:
                raise error


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

                    print("card id: ", card.uid)
                    print("card stats: ", card.stats)
                    print("card data: ", card.data)

                    embed.add_field(name=f"#{str(i+1)} | {card.stats['name']}  [Evo {card.data['evo']}]", value=f"{card.data['rarity'].upper()} | Exp: {card.data['exp']} | ID: {card.uid}", inline=False)

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
        embed.add_field(name="", value=f"**Hp:** {user_card.hp}", inline=False)
        embed.add_field(name="", value=f"**ATK:** {user_card.atk}", inline=False)
        embed.add_field(name="", value=f"**DEF:** {user_card.df}", inline=False)
        embed.add_field(name="", value=f"**SPD:** {user_card.spd}", inline=False)
        embed.add_field(name="", value=f"**Talent:** {user_card.talent}", inline=False)
        embed.set_footer(text="Card ID: " + str(user_card.id))

        await ctx.send(embed=embed)



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





class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="summon", description="Summon a card. Param: target, card name, rarity")
    async def summon(self, ctx, name=None, rarity="sr"):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                user_id = ctx.author.id

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user = await cursor.fetchall()

                await connection.commit()
                if ctx.author.id not in devids:
                    return

                if user == []: # User not found in database
                    embed = discord.Embed(title=f"Unregistered User",
                                          description=f"Looks like you haven't started yet!! Type a!start!",
                                          color=0xA80108)
                    await ctx.send(embed=embed)
                    return

                if name == None or rarity == None:  # Verify arguments
                    rarity = rarity.lower()
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

                    async with asqlite.connect("card_data.db") as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute("SELECT * FROM Dex WHERE name=?", (name,))

                            card_index = await cursor.fetchall()

                    if len(card_index) != 0:  # card is found
                        card_data = card_index[0]

                    card_index = card_data["dex"]

                    await Database.generateCard( card_index, user_id, rarity, 1 )

                    embed = discord.Embed(title=f"Card Summoned!", description=f"A {rarity.upper()} {name} was summoned", color=0x03F76A)

                    await ctx.send(embed=embed)


    @commands.command(description='Syncs all commands globally. Only accessible to developers.')
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if ctx.author.id not in devids:
            return

        embed = discord.Embed(description="Syncing...", color=discord.Color.red())
        await ctx.send(embed=embed)
        print("Syncing...")
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(embed=discord.Embed(
                description=f"Synced `{len(synced)}` commands {'globally' if spec is None else 'to the current guild.'}.",
                color=discord.Color.green()))
            print("Synced.")
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(embed=discord.Embed(description=f"Synced the tree to {ret}/{len(guilds)}.", color=discord.Color.green()))
        print("Synced.")

    @commands.hybrid_command()
    async def reset(self, ctx, user: discord.User):

        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                if ctx.author.id not in devids:
                    return
                user_id = str(user.id)
                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()


                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    balance = user_data["wuns"]
                    new_balance = user_data["wuns"] * 0
                    balance_readable = "{:,}".format(balance)
                    await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance, user_id))
                    embed = discord.Embed(title=f"a Dev has cursed you",
                                          description=f"{ctx.author} has taken away {Wuns}{balance_readable} wuns from your account",
                                          color=0xA80108)
                    await ctx.send(embed=embed)
                else:  ## User not found
                    embed = discord.Embed(title=f"{user.display_name} not found",
                                          description=f"Have {user.mention} type a!start!",
                                          color=0xA80108)
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name="devgive", aliases=['grant'])
    async def devgive(self, ctx, user: discord.User, amount: int):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                if ctx.author.id not in devids:
                    await ctx.send(f"{ctx.author.mention} You've found a Dev command, unfortunately you can't use it.")
                    return

                user_id = str(user.id)
                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    new_balance = user_data["wuns"] + amount
                    amount_readable = "{:,}".format(amount)
                    await cursor.execute("""UPDATE Users set wuns=? WHERE id=?""", (new_balance, user_id))
                    embed = discord.Embed(title=f"a Dev has blessed you",
                                          description=f"{ctx.author} has given {user} {Wuns}{amount_readable} wuns",
                                          color=0x04980f)
                    embed.set_thumbnail(url=ctx.author.avatar)
                    await ctx.send(embed=embed)
                else:  ## User not found
                    embed = discord.Embed(title=f"{user} not found",
                                          description=f"Have {user} type a!start!",
                                          color=0xA80108)
                    embed.set_thumbnail(url=user.avatar)
                    await ctx.send(embed=embed)


# Adds Cogs
async def setup(bot):
    await bot.add_cog((bot))
    await bot.add_cog(User(bot))
    await bot.add_cog(Currency(bot))
    await bot.add_cog(Card(bot))
    await bot.add_cog(Game(bot))
    await bot.add_cog(Dev(bot))
