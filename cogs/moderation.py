import nextcord
from nextcord.ext import commands

from cord.bot import SireniaBot


class Moderation(commands.Cog):
    """ Moderation commands. """

    def __init__(self, bot: SireniaBot):
        self.bot = bot

    @nextcord.slash_command(
        name='clear',
        description='Purge specified count of messages.',
        default_member_permissions=8192,
        dm_permission=False,
    )
    async def clear(
            self,
            interaction: nextcord.Interaction,
            count: int = nextcord.SlashOption(
                name='count',
                description='Count of messages to delete.',
                required=False,
                default=1,
            ),
    ):
        """ Clear specified count of messages on the channel where the command is invoked. """

        if count > 100:
            count = 100

        try:
            await interaction.channel.purge(limit=count)
            await interaction.response.send_message(
                f'Deleted {count} messages.',
                ephemeral=True,
                delete_after=5,
            )
        except nextcord.errors.Forbidden:
            await interaction.response.send_message(
                'Missing permissions to delete messages.',
                ephemeral=True,
                delete_after=5,
            )


def setup(bot: SireniaBot):
    bot.add_cog(Moderation(bot))
