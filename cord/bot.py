from logging import Logger

from nextcord import VoiceClient, Interaction
from nextcord.ext import commands

from tools.database import Database
from tools.env import Env


class SireniaBot(commands.Bot):
    """ Extended nextcord.ext.commands.Bot with a few useful objects, properties, and methods. """

    def __init__(
            self,
            logger: Logger,
            env: Env,
            database: Database,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.logger = logger
        self.env = env
        self.database = database

    @property
    def voice_client(self) -> VoiceClient | None:
        """ Get the voice client if available. """

        if not self.voice_clients:
            return None

        voice_client = self.voice_clients[0]

        if isinstance(voice_client, VoiceClient):
            return voice_client

        return None

    @staticmethod
    async def default_response(interaction: Interaction):
        """ Default success response. """

        await interaction.response.send_message(
            ':3',
            ephemeral=True,
        )
