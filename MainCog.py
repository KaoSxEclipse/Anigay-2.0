import discord, logging,json, random, asyncio, asqlite
from discord.ext import *
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from typing import Optional, Literal


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
        "Test Command"
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

    @commands.hybrid_command(name="devgive")
    async def give(self, ctx, user: discord.Member, amount: int):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                user_id = int(ctx.author.id)
                if user_id == 533672241448091660 or user_id == 301494278901989378:

                    user_id = str(user.id)
                    await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                    user_data = await cursor.fetchall()

                    if len(user_data) != 0:  ## User is found
                        user_data = user_data[0]
                        new_balance = user_data["wun"] + amount
                        await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance, user_id))
                        embed = discord.Embed(title=f"a Dev has blessed you",
                                              description=f"{ctx.author} has given you {Wuns}{amount} wuns", color=0x04980f)
                        await ctx.send(embed=embed)
                    else:  ## User not found
                        embed = discord.Embed(title=f"{user.name} not found",
                                              description=f"Have {user.name} type a!start!",
                                              color=0xA80108)
                        await ctx.send(embed=embed)
# Views a user balance if "None" returns Command Authors balance
    @commands.hybrid_command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member = None):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                if not user:
                    user = ctx.author

                user_id = int(ctx.author.id) if user is None else int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]
                    balance = user_data["wun"]

                    embed = discord.Embed(title=f"{user} Balance", color=0x03F76A)
                    embed.add_field(name="", value=f"{user} has {Wuns}{user_data['wun']} wun's")
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.display_name} not found", description=f"ask {user.display_name} to type a!start",
                                          color=0xF76103)
                    await ctx.send(embed=embed)

        # Random Claim command, need to add a cooldown. possible feature early on to earn Currency?
    @commands.hybrid_command(name="claim", description="get a random amount of gold added to your balance")
    async def claim(self, ctx, ):
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
                    embed.add_field(name=f"Amount Claimed {Wuns}{claim_value} wun's", value=f"Your new balance is {Wuns}{new_balance}")
                await ctx.send(embed=embed)
    @commands.hybrid_command()
    async def reset(self, ctx, user: discord.Member):
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
                        await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance, user_id))
                        embed = discord.Embed(title=f"a Dev has cursed you",
                                              description=f"{ctx.author} has taken away {Wuns}{balance} wun's from your account", color=0xA80108)
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
    async def profile(self, ctx, user: discord.Member = None):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                if not user:
                    user = ctx.author

                user_id = str(ctx.author.id) if user is None else str(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0:  ## User is found
                    user_data = user_data[0]

                    embed = discord.Embed(title=f"__{user.name}'s__ Profile",
                                          description="",
                                          color=0x75FFEE)
                    embed.add_field(name="**Level**", value=f'{user_data["level"]}', inline=True)
                    embed.add_field(name="**Experience**", value=f'{user_data["exp"]}/{user_data["mexp"]}', inline=True)
                    embed.add_field(name=f" {Wuns} **Balance**", value=f'{user_data["wun"]} wuns', inline=True)
                    embed.add_field(name="**Stamina**", value=f'{user_data["stamina"]}/{user_data["mstamina"]}', inline=True)
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)


                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found", description=f"{user.name} has no profile",
                                          color=0xA80108)
                    await ctx.send(embed=embed)


# SYNCS Commands to all GUILDS DO NOT TOUCH / ALTER
class sync(commands.Cog):
    @commands.command(description='Syncs all commands globally. Only accessible to developers.')
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if ctx.author.id != 301494278901989378:
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

        await ctx.send(embed=discord.Embed(description=f"Synced the tree to {ret}/{len(guilds)}.", color=self.color))
        print("Synced.")


# Adds Cogs
async def setup(bot):
    await bot.add_cog(Debug(bot))
    await bot.add_cog(sync(bot))
    await bot.add_cog(User(bot))
    await bot.add_cog(currency(bot))
