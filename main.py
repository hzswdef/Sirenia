import nextcord
import asyncio
import logging

from os import listdir, getcwd
from os.path import basename
from nextcord.ext import commands
from tools.env import Env
from tools.database import Database


async def main() -> None:
    logging.basicConfig(
        format="[{asctime} / {levelname}]: {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    env = Env()
    database = Database(
        host=env.DATABASE_HOST,
        user=env.DATABASE_USER,
        password=env.DATABASE_PASS,
        database=env.DATABASE_NAME,
    )

    bot = commands.Bot(
        command_prefix=env.DISCORD_BOT_PREFIX,
        intents=nextcord.Intents.all(),
        help_command=None,
    )
    setattr(bot, 'env', env)
    setattr(bot, 'database', database)
    setattr(bot, 'logger', logger)

    for module in listdir(getcwd() + '/cogs'):
        if not module.endswith('.py'):
            continue

        module = basename(module)
        module = module.replace('.py', '')

        bot.load_extension('cogs.' + module)

        logger.info(f'Loaded cogs.{module} module.')

    logger.info('Bot has been started!')

    await bot.start(env.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
