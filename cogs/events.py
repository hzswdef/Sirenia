from asyncio import sleep

import nextcord
from nextcord.ext import commands

from cord.bot import SireniaBot
from settings import DISCORD_GUILD_ID


class Events(commands.Cog):
    """ Events. """

    def __init__(self, bot: SireniaBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Change bot status. """

        await self.bot.change_presence(
            status=nextcord.Status.dnd,
            activity=nextcord.Activity(
                type=nextcord.ActivityType.listening,
                name='hzswdef'
            )
        )

        await sleep(5)

        try:
            self.bot.add_all_application_commands()
            await self.bot.sync_application_commands(guild_id=DISCORD_GUILD_ID)
        except nextcord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        """ Ignore errors. """

        pass


def setup(bot: SireniaBot):
    bot.add_cog(Events(bot))
