from logging import Logger

from nextcord.ext import commands

from tools.database import Database
from tools.env import Env


class SireniaBot(commands.Bot):

    def __init__(
        self,
        env: Env,
        database: Database,
        logger: Logger,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.env = env
        self.database = database
        self.logger = logger
