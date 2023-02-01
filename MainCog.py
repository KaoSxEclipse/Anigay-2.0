import discord, logging
from discord.ext import *
from discord import *
from discord.ext.commands import *
from typing import Optional, Literal
import json, getpass
import asyncio, asqlite

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

                    if len(user_data) != 0: ## User is found
                        user_data = user_data[0]
                        new_balance = user_data["wun"] + amount
                        await cursor.execute("""UPDATE Users set wun=? WHERE id=?""", (new_balance, user_id))
                        embed = discord.Embed(title=f"{ctx.author} has given {user.name} {amount} currency",
                                          description=f"Transfer Complete", color=0x04980f)
                        await ctx.send(embed=embed)
                    else: ## User not found
                        embed = discord.Embed(title=f"{user.name} not found", description=f"Have {user.name} type a!start!",
                                          color=0xA80108)
                        await ctx.send(embed=embed)
                    
                

    @commands.hybrid_command()
    async def balance(self, ctx, user: discord.Member = None):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:

                if not user:
                    user = ctx.author

                user_id = int(ctx.author.id) if user is None else int(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0: ## User is found
                    user_data = user_data[0]
                    balance = user_data["wun"]

                    embed = discord.Embed(title=f"{user.name} has {balance} currency", color=0x04980f)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{user.name} not found", description=f"{user.name} has no currency",
                                      color=0xA80108)
                    await ctx.send(embed=embed)

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_command(name="profile", description="Get an overview of your profile.")
    async def profile(self, ctx, user: discord.Member = None):
        async with asqlite.connect("player_data.db") as connection:
            async with connection.cursor() as cursor:
                if not user:
                    user = ctx.author

                user_id = str(ctx.author.id) if user is None else str(user.id)

                await cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
                user_data = await cursor.fetchall()

                if len(user_data) != 0: ## User is found
                    user_data = user_data[0]

                    embed = discord.Embed(title=f"{user.name}'s Profile", description=f'Level: {user_data["level"]}\nExperience: {user_data["exp"]}/{user_data["mexp"]}\nBalance: {user_data["wun"]} wuns\nStamina: {user_data["stamina"]}/{user_data["mstamina"]}', color=0x04980f)
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
