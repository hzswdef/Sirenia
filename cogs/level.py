import nextcord

from nextcord.ext import commands
from datetime import datetime

from cord.bot import SireniaBot
from settings import DISCORD_GUILD_ID
from tools.level import Level as LevelHandler


class Level(commands.Cog):
    """ Track users activities. """

    sessions = {}

    def __init__(self, bot: SireniaBot):
        self.bot = bot
        self.level_handler = LevelHandler(bot.database)

    @commands.Cog.listener()
    async def on_ready(self):
        """ Start users session if bot is restarted. """

        guild = self.bot.get_guild(DISCORD_GUILD_ID)
        current_time = round(datetime.now().timestamp())

        for voice_channel in guild.voice_channels:
            if voice_channel.members:
                for member in voice_channel.members:
                    self.sessions[member.id] = current_time

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ) -> None:
        """ Track user voice channel activity. """

        current_time = round(datetime.now().timestamp())

        # Create session.
        if after.channel is not None and before.channel is None:
            self.sessions[member.id] = current_time

        # Close session and write the voice activity to database.
        elif before.channel is not None and after.channel is None:
            if member.id not in self.sessions:
                return None

            self.level_handler.on_voice_activity(
                member,
                self.sessions[member.id],
                current_time,
            )

            del self.sessions[member.id]

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message) -> None:
        """ Track user messaging activity. """

        self.level_handler.on_message(message.author)


def setup(bot: SireniaBot):
    bot.add_cog(Level(bot))
