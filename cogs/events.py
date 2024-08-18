import nextcord

from nextcord import Message
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
from settings import DISCORD_EMBED_COLORS


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        try:
            for guild in self.bot.guilds:
                await self.bot.sync_application_commands(guild_id=guild.id)
        except nextcord.Forbidden:
            pass

        await self.bot.change_presence(
            status=nextcord.Status.dnd,
            activity=nextcord.Activity(
                type=nextcord.ActivityType.listening,
                name='hzswdef'
            )
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> [Message, None]:
        if isinstance(error, CommandNotFound):
            return await ctx.send(embed=nextcord.Embed(
                color=DISCORD_EMBED_COLORS['DEFAULT'],
                title='404 Not Found',
                description=f'The command doesn\'t exist.'
            ))

        raise error


async def setup(bot):
    bot.add_cog(Events(bot))
