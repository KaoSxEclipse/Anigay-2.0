import discord, json, random, asyncio, asqlite, datetime, logging
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from typing import Optional, Literal
from discord.ext.commands.cooldowns import BucketType
from datetime import timedelta
from discord.utils import get

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


# test command can be removed / ignored
class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test", description="Test Command")
    async def test(self, ctx):
        """Test Command"""
        embed = discord.Embed(title="Test Embed", description="App Command Invoked")
        await ctx.send(embed=embed, ephemeral=True)


# Profile Start commands, prints User's ID and name, returns an embed for now
class ProfileStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="start", description="Start your journey!")
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
class currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="devgive", aliases=['grant'])
    async def devgive(self, ctx, user: discord.User, amount: int):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = int(ctx.author.id)
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

    # Gives a user money from own balance
    @commands.hybrid_command(name="give", aliases=['g'])
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
    @commands.hybrid_command(aliases=['bal'])
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

    @commands.hybrid_command(name="claim", description="get a random amount of gold added to your balance")
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

    @commands.hybrid_command()
    async def reset(self, ctx, user: discord.User):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = int(ctx.author.id)
                if user_id == 533672241448091660 or user_id == 301494278901989378 or user_id == 755186746966147082:

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
                        embed = discord.Embed(title=f"{user.name} not found",
                                              description=f"Have {user.name} type a!start!",
                                              color=0xA80108)
                        await ctx.send(embed=embed)


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
# View's profile of others, if no user specified returns your profile
    @commands.hybrid_command(name="profile", description="Get an overview of your profile.")
    @bot.listen('on_message')
    async def profile(self, ctx, message="<", user: discord.Member = None):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                print("message:", message)

                if message == "<":
                    user = ctx.author
                elif not "<"  in str(message):
                    return
                else:

                    user_id = int(message[2:-1])

                    user = await ctx.bot.fetch_user( user_id )

                    print("member:", member)
                    #user = member



                #user = bot.get_user(user)

                print("user", user)

                if user == None or user == ctx.author:
                    user_id = str(ctx.author.id)
                #else:
                #    user = member

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  # User is found
                    user_data = user_data[0]

                    embed = discord.Embed(title=f"__{user.name}'s__ Profile",
                                          description="",
                                          color=0x75FFEE)
                    embed.add_field(name="**Level**", value=f'{user_data["level"]}', inline=True)
                    embed.add_field(name="**Experience**", value=f'{user_data["exp"]}/{user_data["mexp"]}', inline=True)
                    embed.add_field(name=f" {Wuns} **Balance**", value=f'{user_data["wun"]} wuns', inline=True)
                    embed.add_field(name="**Stamina**", value=f'{user_data["stamina"]}/{user_data["mstamina"]}',
                                    inline=True)
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)

                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found", description=f"{user} has no profile",
                                          color=0xA80108)
                    await ctx.send(embed=embed)


# SYNCS Commands to all GUILDS DO NOT TOUCH / ALTER
class sync(commands.Cog):
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

        await ctx.send(embed=discord.Embed(description=f"Synced the tree to {ret}/{len(guilds)}.", color=discord.Color.green()))
        print("Synced.")


# Adds Cogs
async def setup(bot):
    await bot.add_cog(Debug(bot))
    await bot.add_cog(sync(bot))
    await bot.add_cog(User(bot))
    await bot.add_cog(currency(bot))
