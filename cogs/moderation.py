import nextcord

from nextcord.ext import commands
from settings import DISCORD_GUILD_ID


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name='clear',
        description='Purge specified count of messages.',
        guild_ids=[DISCORD_GUILD_ID],
        default_member_permissions=8192,
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
        if count > 100:
            count = 100

        try:
            await interaction.channel.purge(limit=count)
            await interaction.response.send_message(f'Deleted {count} messages.')
        except nextcord.errors.Forbidden:
            await interaction.response.send_message('Missing permissions to delete messages.', delete_after=5)

    @clear.error
    async def clear_error(self, error, ctx):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You don\'t have permission to do that!')


async def setup(bot):
    bot.add_cog(Moderation(bot))
