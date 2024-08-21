from os import getenv

from dotenv import load_dotenv


class MissingEnvironmentVariableException(Exception):
    pass


class Env(object):
    """ Load environment variables. """

    DISCORD_BOT_TOKEN = None
    DISCORD_BOT_PREFIX = None

    DATABASE_HOST = None
    DATABASE_USER = None
    DATABASE_PASS = None
    DATABASE_NAME = None

    AVAILABLE_VARIABLES = (
        'DISCORD_BOT_TOKEN',
        'DISCORD_BOT_PREFIX',
        'DISCORD_GUILD_ID',
        'DATABASE_HOST',
        'DATABASE_USER',
        'DATABASE_PASS',
        'DATABASE_NAME',
    )

    def __init__(self) -> None:
        self.load_env()

    def load_env(self) -> None:
        """ Load environment variables. """

        load_dotenv()

        for env in self.AVAILABLE_VARIABLES:
            environment_variable = getenv(env)

            if not environment_variable:
                raise MissingEnvironmentVariableException()

            setattr(self, env, getenv(env))
