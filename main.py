import asyncio
import logging
from glob import glob
from os import listdir, remove, mkdir
from os.path import basename, isdir

import nextcord

from cord.bot import SireniaBot
from settings import PROJECT_ROOT
from tools.database import Database
from tools.env import Env


async def main() -> None:
    # Cleanup cached files.
    if isdir(PROJECT_ROOT + '/.cache'):
        cached_files = glob(PROJECT_ROOT + '/.cache/*')
        for cached_file in cached_files:
            remove(cached_file)
    else:
        mkdir(PROJECT_ROOT + '/.cache')

    logging.basicConfig(
        format="[{asctime} / {levelname}]: {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )
    logger = logging.getLogger('sirenia')

    env = Env()
    database = Database(
        host=env.DATABASE_HOST,
        user=env.DATABASE_USER,
        password=env.DATABASE_PASS,
        database=env.DATABASE_NAME,
    )

    bot = SireniaBot(
        logger=logger,
        env=env,
        database=database,
        command_prefix=env.DISCORD_BOT_PREFIX,
        intents=nextcord.Intents.all(),
        help_command=None,
    )

    for module in listdir(PROJECT_ROOT + '/cogs'):
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
