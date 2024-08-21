import nextcord

from nextcord.ext import commands

from cord.bot import SireniaBot


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

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        """ Ignore errors. """

        pass


def setup(bot: SireniaBot):
    bot.add_cog(Events(bot))
