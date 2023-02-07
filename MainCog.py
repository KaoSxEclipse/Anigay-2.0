import discord, json, random, asyncio, asqlite, datetime, logging
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from typing import Optional, Literal
from discord.ext.commands.cooldowns import BucketType
from datetime import timedelta

# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
# Privileged Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='a!', intents=intents)
# Create variables for emojis in json dict
# Emojis
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

        if command.cog:
            cog_name = cog_name.replace('_', ' ')

        embed = discord.Embed(title=f'{cog_name} › {command.name}', description=command.description,
                              color=discord.Color.purple())
        embed.add_field(name='Usage:', value=command.signature, inline=False)
        embed.set_footer(text="<> is required, [] is optional.")

        if command.aliases:
            embed.add_field(name='Aliases:', value=command.aliases, inline=False)

        await self.context.reply(embed=embed)

    """!help <cog>"""

    async def send_cog_help(self, cog):
        return
        await self.context.reply("This is help cog")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


# Profile Start commands, prints User's ID and name, returns an embed for now
class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="start", description="Start your journey!",
                             usage="'ype a!start or /start to begin playin!")
    async def start(self, ctx):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = int(ctx.author.id)
                username = str(ctx.author.display_name)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) == 0:
                    ## User doesn't exist
                    await cursor.execute("INSERT OR IGNORE INTO Users VALUES (?, 1, 0, 500, 0, 10, 10)", (user_id))

                    embed = discord.Embed(title=f"Welcome to Anigame 2.0 {ctx.author}",
                                          description="You've been given *Super Rare* __card__ to start your Journey!",
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

                await connection.commit()


# Allows Devs (Anyone atm) to give others currency + view the Balance of yourself and others.
class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Gives a user money from own balance
    @commands.hybrid_command(name="give", aliases=['g'], usage="a!give <@user> <amount> , /give @user <amount>")
    async def give(self, ctx, user: discord.User, amount: int):
        async with asqlite.connect("player_data.db") as connection:
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

                    if user_data_giver["wun"] >= amount:

                        new_balance_target = user_data_target["wun"] + amount
                        new_balance_giver = user_data_giver["wun"] - amount
                        amount_readable = "{:,}".format(amount)
                        await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance_giver, user_giver))
                        await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance_target, user_target))
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
    @commands.hybrid_command(aliases=['bal'], description=" View the Balance of yourself or others.",
                             usage="a!bal [@user], /bal [@user]")
    async def balance(self, ctx, user: discord.User = None):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                if not user:
                    user = ctx.author

                user_id = int(ctx.author.id) if user is None else int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  # User is found
                    user_data = user_data[0]
                    balance = user_data["wun"]
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

    @commands.hybrid_command(name="claim",
                             description="get a random amount of gold added to your balance every 8 hours.",
                             usage="a!claim or /claim")
    @commands.cooldown(1, 28800, type=BucketType.user)
    @commands.has_permissions(view_channel=True, read_messages=True, send_messages=True)
    async def claim(self, ctx):
        """Claim Gold"""
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM Users WHERE id=?", (ctx.author.id,))
                user_data = await cursor.fetchall()
                claim_value = random.randint(10, 50)

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    new_balance = user_data["wun"] + claim_value
                    await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance, ctx.author.id))
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
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                # print("message:", message)

                if message == "<":
                    user = ctx.author
                elif not "<" in str(message):
                    return
                else:

                    user_id = int(message[2:-1])

                    user = await ctx.bot.fetch_user(user_id)

                if user == None or user == ctx.author:
                    user_id = str(ctx.author.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  # User is found
                    user_data = user_data[0]

                    if user_data["card"] != 0:
                        card = CardClass(uid=user_data['card'])

                        await card.Query()
                    else:
                        card = None

                    embed = discord.Embed(title=f"__{user.name}'s__ Profile",
                                          description="",
                                          color=0x75FFEE)
                    # embed.add_field(name="**Level**", value=f'{user_data["level"]}', inline=True)
                    embed.add_field(name="**Experience**", value=f'{user_data["exp"]}/{user_data["exp"]}', inline=True)
                    embed.add_field(name=f" {Wuns} **Balance**", value=f'{user_data["wuns"]} wuns', inline=True)
                    embed.add_field(name="**Stamina**", value=f'{user_data["stamina"]}/{user_data["stamina"]}',
                                    inline=True)
                    if card == None:
                        embed.add_field(name="**Card Selected:**", value=f"{card}", inline=False)
                    else:
                        embed.add_field(name="**Card Selected:**", value=f"{card.card_stats['name']}", inline=False)
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found", description=f"{user} has no profile",
                                          color=0xA80108)
                    await ctx.send(embed=embed)

    # Returns User's Inventory
    @commands.hybrid_command(aliases=["inv", "i"], usage="a!inv,/inv")
    async def inventory(self, ctx):
        async with asqlite.connect("card_data.db") as connection:
            async with connection.cursor() as cursor:
                user = ctx.author.id
                await cursor.execute("SELECT * FROM Upper WHERE owner=?", (user,))
                player_inventory = await cursor.fetchall()

                embed = discord.Embed(title=f"{ctx.author}'s Inventory:", color=0x03F76A)

                for i in range(0, len(player_inventory)):
                    card = CardClass(player_inventory[i]['rarity'], player_inventory[i]['uid'])

                    await card.Query()
                    embed.add_field(name=f"#{str(i + 1)} | {card.card_stats['name']}  [Evo {card.card_data['evo']}]",
                                    value=f"{card.card_data['rarity'].upper()} | Exp: {card.card_data['exp']} | ID: {card.uid}",
                                    inline=False)

                await ctx.send(embed=embed)

                await connection.commit()
            # Select a card and assign it to the user for battling

    @commands.hybrid_command(usage="a!select <Inventory ID> , /select <Inventory ID> ")
    async def select(self, ctx, message=0):
        async with asqlite.connect("card_data.db") as connection:
            async with connection.cursor() as cursor:
                user = ctx.author.id
                await cursor.execute("SELECT * FROM Upper WHERE owner=?", (user,))
                player_inventory = await cursor.fetchall()

                if 0 < int(message) <= len(player_inventory):
                    # Proper card is in inventory
                    card_index = int(message) - 1
                    card_id = player_inventory[card_index]["uid"]
                    async with asqlite.connect("player_data.db") as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute("""UPDATE Users set card=? WHERE id=?""", (card_id, user))

                    card = CardClass(player_inventory[card_index]['rarity'], player_inventory[card_index]['uid'])
                    await card.Query()

                    embed = discord.Embed(title=f"Card Selected!",
                                          description=f"{card.card_stats['name']} was selected for battle!",
                                          color=0x03F76A)

                    await ctx.send(embed=embed)

                    await connection.commit()
    # Select a card and assign it to the user for battling


@commands.hybrid_command()
async def select(self, ctx, message=0):
    async with asqlite.connect("card_data.db") as connection:
        async with connection.cursor() as cursor:
            user = ctx.author.id
            await cursor.execute("SELECT * FROM Upper WHERE owner=?", (user,))
            player_inventory = await cursor.fetchall()

            if 0 < int(message) <= len(player_inventory):
                # Proper card is in inventory
                card_index = int(message) - 1
                card_id = player_inventory[card_index]["uid"]
                async with asqlite.connect("player_data.db") as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute("""UPDATE Users set card=? WHERE id=?""", (card_id, user))

                card = CardClass(player_inventory[card_index]['rarity'], player_inventory[card_index]['uid'])
                await card.Query()

                embed = discord.Embed(title=f"Card Selected!",
                                      description=f"{card.card_stats['name']} was selected for battle!",
                                      color=0x03F76A)

                await ctx.send(embed=embed)

                await connection.commit()


class Card(commands.Cog):
    class CardClass:
        def __init__(self, rarity="sr", uid='0'):
            self.rarity = rarity
            self.uid = uid
            self.card_data = None
            self.card_stats = None
            self.bot = bot

            if rarity in "uc c r".split(" "):
                self.table = "Lower"
            else:
                self.table = "Upper"

        async def Query(self):
            # Obtain the card information from the Index database and the global card database
            async with asqlite.connect("card_data.db") as connection:
                async with connection.cursor() as cursor:
                    # Get unique card id from Global Upper Card Table
                    await cursor.execute("SELECT * FROM {} WHERE uid={}".format(self.table, self.uid, ))

                    self.card_data = await cursor.fetchall()
                    print(self.card_data)
                    self.card_data = self.card_data[0]
                    index = self.card_data["dex"]

                    print("index:", index)

                    # Get Card stats using corresponding index from table
                    await cursor.execute("SELECT * FROM Dex WHERE dex=?", (index,))
                    self.card_stats = await cursor.fetchall()

                    print("Card Stats:", self.card_stats)

                    if self.card_stats == []:
                        return
                    else:
                        self.card_stats = self.card_stats[0]

                    await connection.commit()

        def checkRarity(self):
            return

        def CalcLevel(self):
            pass

        def CalcStats(self):
            pass

        def ReturnCard(self):
            self.Query()
            self.CalcLevel()
            self.CalcStats()

    # Show the Information on a single card in the index
    @commands.hybrid_command(aliases=['ci'])
    async def cinfo(self, ctx, message=None, message2=None):
        async with asqlite.connect("card_data.db") as connection:
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

                    await cursor.execute("SELECT * FROM Dex WHERE name=?", (message,))

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

                if user == []:  # User not found in database
                    embed = discord.Embed(title=f"Unregistered User",
                                          description=f"Looks like you haven't started yet!! Type a!start!",
                                          color=0xA80108)
                    await ctx.send(embed=embed)
                    return

                if name == None or rarity == None:  # Verify arguments
                    embed = discord.Embed(title=f"Error!",
                                          description=f"One or more arguments invalid",
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

                    await Database.generateCard(card_index, user_id, rarity, 1)

                    embed = discord.Embed(title=f"Card Summoned!",
                                          description=f"A {rarity.upper()} {name} was summoned", color=0x03F76A)

                    await ctx.send(embed=embed)

    @commands.command(description='Syncs all commands globally. Only accessible to developers.')
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if ctx.author.id != 301494278901989378 or 533672241448091660:
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

        await ctx.send(embed=discord.Embed(description=f"Synced the tree to {ret}/{len(guilds)}.",
                                           color=discord.Color.green()))
        print("Synced.")

    @commands.hybrid_command()
    async def reset(self, ctx, user: discord.User):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = int(ctx.author.id)
                if user_id == 533672241448091660 or user_id == 301494278901989378:
                    user_id = str(user.id)
                    await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                    user_data = await cursor.fetchall()

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    balance = user_data["wun"]
                    new_balance = user_data["wun"] * 0
                    balance_readable = "{:,}".format(balance)
                    await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance, user_id))
                    embed = discord.Embed(title=f"a Dev has cursed you",
                                          description=f"{ctx.author} has taken away {Wuns}{balance_readable} wuns from your account",
                                          color=0xA80108)
                    await ctx.send(embed=embed)
                else:  ## User not found
                    embed = discord.Embed(title=f"{user.display_name} not found",
                                          description=f"Have {user.mention} type a!start!",
                                          color=0xA80108)
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name="devgive", aliases=['grant'], hidden=True)
    async def devgive(self, ctx, user: discord.User, amount: int, hidden=True):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = str(user.id)
                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    new_balance = user_data["wun"] + amount
                    amount_readable = "{:,}".format(amount)
                    await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance, user_id))
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
