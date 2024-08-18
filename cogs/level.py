import nextcord

from nextcord.ext import commands
from datetime import datetime
from tools.level import Level as LevelHandler


class Level(commands.Cog):

    sessions = {}

    def __init__(self, bot):
        self.bot = bot
        self.level_handler = LevelHandler(bot.database)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ) -> None:
        current_time = round(datetime.now().timestamp())

        # Create session.
        if after.channel is not None and before.channel is None:
            self.sessions[member.id] = current_time

        # Close session and write the voice activity to database.
        if before.channel is not None and after.channel is None:
            self.level_handler.on_voice_activity(
                member,
                self.sessions[member.id],
                current_time,
            )

            del self.sessions[member.id]

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message) -> None:
        self.level_handler.on_message(message.author)


async def setup(bot):
    bot.add_cog(Level(bot))
