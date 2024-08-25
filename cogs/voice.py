import nextcord
from nextcord.ext import commands

from cord.bot import SireniaBot


class Voice(commands.Cog):
    """ Voice commands. """

    def __init__(self, bot: SireniaBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
            self,
            member: nextcord.Member,
            before: nextcord.VoiceState,
            after: nextcord.VoiceState,
    ) -> None:
        """ Disconnect bot from empty voice channel. """

        voice_client = self.bot.voice_client

        if voice_client \
                and before.channel \
                and len(before.channel.members) == 1 \
                and voice_client.channel.id == before.channel.id:
            if voice_client.is_playing():
                voice_client.stop()

            await self.bot.voice_client.disconnect(force=True)

    @nextcord.slash_command(
        name='summon',
        description='Summon me!',
        dm_permission=False,
    )
    async def summon(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Summon bot to the user's voice channel. """

        voice_client = self.bot.voice_client

        if voice_client:
            return await interaction.response.send_message(
                'Sorry, I\'m is busy.',
                ephemeral=True,
            )

        if not interaction.user.voice:
            return await interaction.response.send_message(
                'You must join a voice channel first.',
                ephemeral=True,
            )

        await interaction.user.voice.channel.connect()

        await self.bot.default_response(interaction)

    @nextcord.slash_command(
        name='leave',
        description='Leave the channel.',
        dm_permission=False,
    )
    async def leave(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Summon bot to the user's voice channel. """

        voice_client = self.bot.voice_client

        if not voice_client:
            return await interaction.response.send_message(
                'I\'m not connected to any voice channel.',
                ephemeral=True,
            )

        try:
            await voice_client.disconnect(force=True)
        except nextcord.ClientException:
            return await interaction.response.send_message(
                'Failed...',
                ephemeral=True,
            )

        await self.bot.default_response(interaction)


def setup(bot: SireniaBot):
    bot.add_cog(Voice(bot))
