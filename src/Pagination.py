import asyncio
import discord
from discord.ext import commands


class BotEmbedPaginator(commands.Paginator):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.current = 0
        self.check = lambda i: i.user.id == self.ctx.author.id
        self.original_embed = None  # store a copy of the original embed

    async def paginate(self, ctx):
        self.ctx = ctx  # save context for check lambda
        if len(self.pages) == 1:
            return await ctx.send(embed=self.pages[0])

        if self.current >= len(self.pages):
            raise IndexError('Page index out of range')

        embed = discord.Embed.from_dict(self.pages[self.current].to_dict())
        embed.set_footer(text=f"Page {self.current + 1}/{len(self.pages)}")
        message = await ctx.send(embed=embed, view=self.get_buttons(self.current))

        while True:
            try:
                interaction = await self.bot.wait_for('interaction', check=self.check, timeout=240)
            except asyncio.TimeoutError:
                try:
                    await message.edit(view=self.get_buttons(disabled=True))
                except:
                    pass
                break

            previous_page = self.current

            if interaction.data['custom_id'] == "prev":
                self.current = max(0, self.current - 1)
            elif interaction.data['custom_id'] == "next":
                self.current = min(len(self.pages) - 1, self.current + 1)
            elif interaction.data['custom_id'] == "stop":
                try:
                    await message.delete()
                except:
                    pass
                break

            if self.current != previous_page:
                previous_embed = discord.Embed.from_dict(self.pages[0].to_dict())
                embed = discord.Embed.from_dict(self.pages[self.current].to_dict())
                embed.title = previous_embed.title
                embed.description = previous_embed.description
                embed.set_thumbnail(url=previous_embed.thumbnail.url)
                embed.set_footer(text=f"Page {self.current + 1}/{len(self.pages)}")
                await message.edit(embed=embed, view=self.get_buttons(self.current))

            await interaction.response.edit_message(embed=embed, view=self.get_buttons(self.current))

    def add_embed(self, embed):
        self.pages.append(embed)

    def get_buttons(self, current_page):
        buttons = discord.ui.View()
        emoji_stop = discord.PartialEmoji(name='RedCross', id=1094318147030491286, animated=False)
        emoji_next = discord.PartialEmoji(name='RightArrow', id=1094320459597762620, animated=False)
        emoji_prev = discord.PartialEmoji(name='LeftArrow', id=1094320556670713997, animated=False)

        buttons.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, emoji=emoji_prev, disabled=current_page == 0, custom_id='prev'))
        buttons.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, emoji=emoji_next, disabled=current_page == len(self.pages) - 1, custom_id='next'))
        buttons.add_item(discord.ui.Button(style=discord.ButtonStyle.red, emoji=emoji_stop, custom_id='stop'))

        return buttons
