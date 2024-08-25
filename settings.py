from os import getcwd, getenv

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = getcwd()

DISCORD_GUILD_ID = int(getenv('DISCORD_GUILD_ID'))

DISCORD_EMBED_COLORS = {
    'DEFAULT': 0x000000,
}
