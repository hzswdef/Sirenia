from logging import Logger

from nextcord.ext import commands

from tools.database import Database
from tools.env import Env


class SireniaBot(commands.Bot):
    """ Extended nextcord.ext.commands.Bot with a few useful objects. """

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
