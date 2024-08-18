from asyncio import sleep
from hashlib import file_digest
from io import BytesIO
from os.path import basename, splitext

import nextcord

from datetime import datetime
from os import getcwd, rename, remove
from nextcord.ext import commands
from settings import DISCORD_GUILD_ID


class Soundboard(commands.Cog):

    SOUNDBOARD_DIR = getcwd() + '/assets/soundboard/'

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name='soundboard_add',
        description='Upload own soundboard!',
        guild_ids=[DISCORD_GUILD_ID],
    )
    async def soundboard_add(
        self,
        interaction: nextcord.Interaction,
        sound_name: str = nextcord.SlashOption(
            name='name',
            description='Name for sound.',
            required=True,
        ),
        file: nextcord.Attachment = nextcord.SlashOption(
            name='sound',
            description='Please attach a sound file.',
            required=True,
        ),
    ):
        if file.size > 8_000_000:
            return await interaction.response.send_message('Sorry, max allowed filesize is 8 MB.')

        existing_sound_name = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'",
            return_output=True,
        )
        if existing_sound_name:
            return await interaction.response.send_message('Sound with that name already exists.')

        tempfile_name = getcwd() + '/' + str(datetime.now().timestamp())
        await file.save(fp=tempfile_name)

        with open(tempfile_name, "rb", buffering=0) as sound_file:
            sha256 = file_digest(BytesIO(sound_file.read()), "sha256").hexdigest()

        file_extension = splitext(basename(file.filename))[1]
        existing_sha256 = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `sha256` = '{sha256}'",
            return_output=True,
        )
        if existing_sha256:
            return await interaction.response.send_message('That sound already exists.')

        self.bot.database.query(
            "INSERT INTO `soundboard`"
            f" (`author`, `name`, `file_extension`, `sha256`)"
            " VALUES ({}, '{}', '{}', '{}')".format(
                interaction.user.id,
                sound_name,
                file_extension,
                sha256,
            )
        )
        new_sound = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `sha256` = '{sha256}'",
            return_output=True,
        )
        rename(
            tempfile_name,
            self.SOUNDBOARD_DIR + str(new_sound[0]['id']) + file_extension,
        )

        await interaction.response.send_message(f'Added **{sound_name}** sound!')

    async def _delete_sound_autocomplete_callback(
        self,
        interaction: nextcord.Interaction,
        sound_name: str,
    ):
        items = []

        data = self.bot.database.query(
            "SELECT `name` FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` LIKE '%{sound_name}%'"
            " LIMIT 5",
            return_output=True,
        )

        for item in data:
            items.append(item['name'])

        return items

    @nextcord.slash_command(
        name='soundboard_remove',
        description='Remove uploaded sound.',
        guild_ids=[DISCORD_GUILD_ID],
    )
    async def soundboard_remove(
        self,
        interaction: nextcord.Interaction,
        sound_name: str = nextcord.SlashOption(
            name='name',
            description='Name for sound.',
            autocomplete=True,
            autocomplete_callback=_delete_sound_autocomplete_callback,
            required=True,
        ),
    ):
        sound = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'",
            return_output=True,
        )

        if not sound:
            return await interaction.response.send_message(f'{sound_name} sound not found.')

        remove(self.SOUNDBOARD_DIR + str(sound[0]['id']) + sound[0]['file_extension'])

        self.bot.database.query(
            "DELETE FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'"
        )

        await interaction.response.send_message(f'Deleted **{sound_name}** sound.')

    async def _play_sound_autocomplete_callback(
        self,
        interaction: nextcord.Interaction,
        sound_name: str,
    ):
        items = []

        data = self.bot.database.query(
            "SELECT `name` FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` LIKE '%{sound_name}%'"
            " LIMIT 5",
            return_output=True,
        )

        additional_items = []
        if len(data) < 5:
            additional_items = self.bot.database.query(
                "SELECT `name` FROM `soundboard`"
                f" WHERE `author` = {interaction.user.id}"
                " ORDER BY `id` DESC"
                f" LIMIT {5 + len(data)}",
                return_output=True,
            )

        for item in data:
            items.append(item['name'])

        if additional_items:
            for item in additional_items:
                if item['name'] not in items:
                    items.append(item['name'])

        return items

    @nextcord.slash_command(
        name='sb',
        description='Play the soundboard!',
        guild_ids=[DISCORD_GUILD_ID],
    )
    async def play_sound(
        self,
        interaction: nextcord.Interaction,
        sound_name: str = nextcord.SlashOption(
            name='name',
            description='Name of your own sound.',
            autocomplete=True,
            autocomplete_callback=_play_sound_autocomplete_callback,
            required=True,
        ),
    ):
        voice_channel = interaction.user.voice.channel

        if voice_channel is None:
            return await interaction.response.send_message('You must join a voice channel first.')

        sound = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} and `name` = '{sound_name}'",
            return_output=True,
        )

        if not sound:
            return await interaction.response.send_message('Please add sound first. Use `/soundboard_add`.')

        sound = sound[0]

        # if self.bot.user.id not in [member.id for member in voice_channel.members]:
        #     pass

        await interaction.response.send_message(':3')

        voice_channel = await voice_channel.connect()
        voice_channel.play(nextcord.FFmpegPCMAudio(
            source=getcwd() + '/assets/soundboard/' + str(sound['id']) + sound['file_extension'],
            options='-filter:a "volume=0.10"',
        ))

        while voice_channel.is_playing():
            await sleep(.1)

        await voice_channel.disconnect()


async def setup(bot):
    bot.add_cog(Soundboard(bot))
