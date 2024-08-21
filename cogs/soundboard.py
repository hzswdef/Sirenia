from asyncio import sleep
from datetime import datetime
from enum import Enum
from hashlib import file_digest
from io import BytesIO
from os import getcwd, rename, remove
from os.path import basename, splitext

import nextcord
from nextcord.ext import commands
from soundfile import SoundFile

from cord.bot import SireniaBot
from settings import DISCORD_GUILD_ID, DISCORD_EMBED_COLORS


class SoundboardPlayEnum(Enum):
    OWN = 0
    ANY = 1


class Soundboard(commands.Cog):
    """ Soundboard commands. """

    SOUNDBOARD_DIR = getcwd() + '/assets/soundboard/'

    def __init__(self, bot: SireniaBot):
        self.bot = bot

    def get_voice_client(self) -> nextcord.VoiceClient:
        """ Get the voice client if available. """

        voice_client = self.bot.voice_clients[0] if self.bot.voice_clients else None

        if isinstance(voice_client, nextcord.VoiceClient):
            return voice_client

    @staticmethod
    async def default_response(interaction: nextcord.Interaction):
        """ Default success response. """

        await interaction.response.send_message(
            ':3',
            ephemeral=True,
        )

    @nextcord.slash_command(guild_ids=[DISCORD_GUILD_ID])
    async def soundboard(self, interaction: nextcord.Interaction):
        pass

    @soundboard.subcommand(
        name='add',
        description='Upload own soundboard!',
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
    ) -> [nextcord.PartialInteractionMessage, None]:
        """ Upload a user's sound. """

        if file.size > 8_000_000:
            return await interaction.response.send_message(
                'Sorry, max allowed filesize is 8 MB.',
                ephemeral=True,
            )

        file_extension = splitext(basename(file.filename))[1]
        if file_extension not in ('.mp3', '.wav', '.ogg'):
            return await interaction.response.send_message(
                'Sorry, only `.mp3`, `.wav`, `.ogg` audio file extensions are supported.',
                ephemeral=True,
            )

        existing_sound_name = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'",
            return_output=True,
        )
        if existing_sound_name:
            return await interaction.response.send_message(
                'Sound with that name already exists.',
                ephemeral=True,
            )

        tempfile_name = getcwd() + '/' + str(datetime.now().timestamp())
        await file.save(fp=tempfile_name)

        with open(tempfile_name, "rb", buffering=0) as sound_file:
            sha256 = file_digest(BytesIO(sound_file.read()), "sha256").hexdigest()

        existing_sha256 = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `sha256` = '{sha256}'",
            return_output=True,
        )
        if existing_sha256:
            return await interaction.response.send_message(
                'That sound already exists.',
                ephemeral=True,
            )

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
    ) -> list:
        """ List user's own soundboard to delete one of the sound. """

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

    @soundboard.subcommand(
        name='remove',
        description='Remove uploaded sound.',
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
    ) -> [nextcord.PartialInteractionMessage, None]:
        """ Remove own user's sound from the soundboard. """

        sound = self.bot.database.query(
            "SELECT * FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'",
            return_output=True,
        )

        if not sound:
            return await interaction.response.send_message(
                f'{sound_name} sound not found.',
                ephemeral=True,
            )

        remove(self.SOUNDBOARD_DIR + str(sound[0]['id']) + sound[0]['file_extension'])

        self.bot.database.query(
            "DELETE FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'"
        )

        await interaction.response.send_message(f'Deleted **{sound_name}** sound.')

    async def _play_sound(
            self,
            interaction: nextcord.Interaction,
            action: SoundboardPlayEnum,
            sound_name: str,
    ) -> [nextcord.PartialInteractionMessage, None]:
        """ Play the sound from the soundboard. """

        user_voice_channel = interaction.user.voice.channel

        if user_voice_channel is None:
            return await interaction.response.send_message(
                'You must join a voice channel first.',
                ephemeral=True,
            )

        if action == SoundboardPlayEnum.OWN:
            sound = self.bot.database.query(
                "SELECT * FROM `soundboard`"
                f" WHERE `author` = {interaction.user.id} AND `name` = '{sound_name}'",
                return_output=True,
            )
        elif action == SoundboardPlayEnum.ANY:
            sound = self.bot.database.query(
                "SELECT * FROM `soundboard`"
                f" WHERE `name` = '{sound_name}'",
                return_output=True,
            )
        else:
            return

        if not sound:
            return await interaction.response.send_message(
                'Please add sound first. Use `/soundboard add`.',
                ephemeral=True,
            )
        sound = sound[0]

        voice_client = self.get_voice_client()
        is_connected_before = True

        if not voice_client:
            voice_client = await interaction.user.voice.channel.connect()

            is_connected_before = False

        if voice_client.is_playing():
            return await interaction.response.send_message(
                'Sorry, bot is busy.',
                ephemeral=True,
            )

        await self.default_response(interaction)

        voice_client.play(nextcord.FFmpegPCMAudio(
            source=getcwd() + '/assets/soundboard/' + str(sound['id']) + sound['file_extension'],
            options='-filter:a "volume=0.10"',
        ))

        if not is_connected_before:
            while voice_client.is_playing():
                await sleep(.1)

            await sleep(.5)

            await voice_client.disconnect(force=True)

    async def _play_sound_autocomplete_callback(
            self,
            interaction: nextcord.Interaction,
            sound_name: str,
    ) -> list:
        items = []

        data = self.bot.database.query(
            "SELECT `name` FROM `soundboard`"
            f" WHERE `name` LIKE '%{sound_name}%'"
            " LIMIT 5",
            return_output=True,
        )

        for item in data:
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
                name='sound',
                description='Name of your own sound.',
                autocomplete=True,
                autocomplete_callback=_play_sound_autocomplete_callback,
                required=True,
            ),
    ) -> [nextcord.PartialInteractionMessage, None]:
        """ Play any sound from soundboard. """

        await self._play_sound(interaction, SoundboardPlayEnum.ANY, sound_name)

    async def _play_own_sound_autocomplete_callback(
            self,
            interaction: nextcord.Interaction,
            sound_name: str,
    ) -> list:
        """ Autocomplete callback to search the user's own sound. """

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
        name='osb',
        description='Play the own soundboard!',
        guild_ids=[DISCORD_GUILD_ID],
    )
    async def play_own_sound(
            self,
            interaction: nextcord.Interaction,
            sound_name: str = nextcord.SlashOption(
                name='sound',
                description='Name of your own sound.',
                autocomplete=True,
                autocomplete_callback=_play_own_sound_autocomplete_callback,
                required=True,
            ),
    ) -> [nextcord.PartialInteractionMessage, None]:
        """ Play sound from user's own soundboard. """

        await self._play_sound(interaction, SoundboardPlayEnum.OWN, sound_name)

    @soundboard.subcommand(
        name='stop',
        description='Stop playing soundboard.',
    )
    async def stop_soundboard(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Play sound from user's own soundboard. """

        user_voice_channel = interaction.user.voice.channel

        if not user_voice_channel:
            return await interaction.response.send_message(
                'You have to be in the voice channel.',
                ephemeral=True,
            )

        bot_voice_channel = self.get_voice_client()

        if not bot_voice_channel:
            return await interaction.response.send_message(
                'I\'m not in the voice channel!',
                ephemeral=True,
            )

        if self.bot.user.id not in [member.id for member in user_voice_channel.members]:
            return await interaction.response.send_message(
                'I\'m not in your voice channel!',
                ephemeral=True,
            )

        if not bot_voice_channel.is_playing():
            return await interaction.response.send_message(
                'I\'m not playing any sound!',
                ephemeral=True,
            )

        bot_voice_channel.stop()

        await self.default_response(interaction)

    @soundboard.subcommand(
        name='list',
        description='List of your soundboard.',
    )
    async def soundboard_list(self, interaction: nextcord.Interaction) -> nextcord.PartialInteractionMessage:
        """ List of user's soundboard. """

        sounds = self.bot.database.query(
            "SELECT `id`, `name`, `file_extension` FROM `soundboard`"
            f" WHERE `author` = {interaction.user.id}",
            return_output=True,
        )

        if not sounds:
            return await interaction.response.send_message(
                'Your soundboard is empty.'
                '\n\nUse `/soundboard add` to add your own sounds and to use them later!',
                ephemeral=True,
            )

        sound_pages = int(len(sounds) / 10) if len(sounds) >= 10 else 1
        sounds = sounds[:10]

        message = ''

        for i, sound in enumerate(sounds):
            file = SoundFile(getcwd() + '/assets/soundboard/' + str(sound['id']) + sound['file_extension'])
            duration = round(file.frames / file.samplerate)
            duration = "{minutes:02d}:{seconds:02d}".format(
                minutes=int(duration / 60),
                seconds=duration % 60,
            )

            message += f'**{i + 1}.** {sound["name"]} - {duration} length.\n'

        embed = nextcord.Embed(
            color=DISCORD_EMBED_COLORS['DEFAULT'],
            title='Soundboard',
            description=message,
        )
        if sound_pages != 1:
            embed.set_footer(text=f'Page 1/{sound_pages}')

        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name='summon',
        description='Summon me!',
        guild_ids=[DISCORD_GUILD_ID],
    )
    async def summon(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Summon bot to the user's voice channel. """

        voice_client = self.get_voice_client()

        if voice_client:
            return await interaction.response.send_message(
                'Sorry, I\'m is busy.',
                ephemeral=True,
            )

        if not interaction.user.voice:
            return await interaction.response.send_message(
                'You must join a voice channel first.',
                ephemeral=True,
            )

        await interaction.user.voice.channel.connect()

        await self.default_response(interaction)

    @nextcord.slash_command(
        name='leave',
        description='Leave the channel.',
        guild_ids=[DISCORD_GUILD_ID],
    )
    async def leave(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Summon bot to the user's voice channel. """

        voice_client = self.get_voice_client()

        if not voice_client:
            return await interaction.response.send_message(
                'I\'m not connected to any voice channel.',
                ephemeral=True,
            )

        try:
            await voice_client.disconnect(force=True)
        except nextcord.ClientException:
            return await interaction.response.send_message(
                'Failed...',
                ephemeral=True,
            )

        await self.default_response(interaction)


def setup(bot: SireniaBot):
    bot.add_cog(Soundboard(bot))
