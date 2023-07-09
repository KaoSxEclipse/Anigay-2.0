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

from User import User
from Card import Card
from Currency import Currency
from Dev import Dev
from Game import Game
from Start import ProfileStart

path_to_db = "../db/"

# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("../logs/bot.log"), logging.StreamHandler()]
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



# Adds Cogs
async def setup(bot):
    await bot.add_cog((bot))
    await bot.add_cog(User(bot))
    await bot.add_cog(Currency(bot))
    await bot.add_cog(Card(bot))
    await bot.add_cog(Game(bot))
    await bot.add_cog(Dev(bot))
