from os import getenv

from dotenv import load_dotenv

load_dotenv()

DISCORD_GUILD_ID = int(getenv('DISCORD_GUILD_ID'))

DISCORD_EMBED_COLORS = {
    'DEFAULT': 0x000000,
}
