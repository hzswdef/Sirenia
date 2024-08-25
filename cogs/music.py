from asyncio import sleep
from enum import Enum
from glob import glob
from os import remove
from os.path import isfile
from re import match

import nextcord
from nextcord import PartialInteractionMessage
from nextcord.ext import commands
from yt_dlp import YoutubeDL

from cord.bot import SireniaBot
from cord.player import FFmpegPCMAudioCustom
from settings import PROJECT_ROOT, DISCORD_EMBED_COLORS


class MusicSource(Enum):
    YOUTUBE = 0
    PLAYLIST = 1


class MusicPlayer(object):
    """ Music player. """

    CACHE_DIR = PROJECT_ROOT + '/.cache'

    YTDL = YoutubeDL({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'outtmpl': PROJECT_ROOT + '/.cache/' + '%(id)s.%(ext)s',
    })

    CURRENT = 0
    QUEUE = []

    def __init__(self, bot: SireniaBot) -> None:
        self.bot = bot

    def reset(self) -> None:
        """ Reset state. """

        self.CURRENT = 0
        self.QUEUE.clear()

        cached_files = glob(self.CACHE_DIR + '/*')

        for cached_file in cached_files:
            if isfile(cached_file):
                remove(cached_file)

    def youtube_extract(self, url: str) -> dict:
        """ Download audio from YouTube video and return video data. """

        self.YTDL.download([url])

        return self.YTDL.extract_info(url, download=False)

    async def play_next(self) -> None:
        """ Do actions after the song was finished. """

        queue_items = len(self.QUEUE)

        # Increase current song index value or reset to 0 to play next song.
        if queue_items != 1:
            if (self.CURRENT + 1) == queue_items:
                self.CURRENT = 0
            else:
                self.CURRENT += 1

        await self.play()

        # Cache next audio.
        next_audio = self.QUEUE[self.CURRENT]
        if not isfile(self.CACHE_DIR + '/' + next_audio['id'] + '.mp3'):
            if next_audio['length'] <= 15:
                self.youtube_extract(next_audio['source'])
            else:
                await sleep(next_audio['length'] - 15)
                self.youtube_extract(next_audio['source'])

    async def play(self) -> None:
        voice_client = self.bot.voice_client

        if not voice_client:
            return

        if voice_client.is_playing():
            voice_client.stop()

        audio = self.QUEUE[self.CURRENT]
        audio_path = self.CACHE_DIR + '/' + audio['id'] + '.mp3'

        while not isfile(audio_path):
            await sleep(1)

        voice_client.play(
            source=FFmpegPCMAudioCustom(
                source=self.CACHE_DIR + '/' + audio['id'] + '.mp3',
            ),
            after=lambda e: self.play_next(),
        )

    def add(self, source: MusicSource, item: str) -> dict:
        """ Add item to the queue. """

        data = None

        if source is MusicSource.YOUTUBE:
            data = self.youtube_extract(item)

            self.QUEUE.append({
                'source': item,
                'url': data['url'],
                'id': data['id'],
                'title': data['title'],
                'length': data['duration'],
            })

        if source is MusicSource.PLAYLIST:
            pass

        return data


class Music(commands.Cog):
    """ Music commands. """

    YOUTUBE_REGEX = \
        '^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))' \
        '(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$'

    def __init__(self, bot: SireniaBot):
        self.bot = bot
        self.player = MusicPlayer(bot)

    @commands.Cog.listener()
    async def on_voice_state_update(
            self,
            member: nextcord.Member,
            before: nextcord.VoiceState,
            after: nextcord.VoiceState,
    ) -> None:
        """ Clear cached files if channel is empty. """

        voice_client = self.bot.voice_client

        if voice_client \
                and before.channel \
                and len(before.channel.members) == 1 \
                and voice_client.channel.id == before.channel.id:
            self.player.reset()

        elif voice_client \
                and before.channel \
                and not after.channel \
                and member.id == self.bot.user.id:
            self.player.reset()

    @nextcord.slash_command(dm_permission=False)
    async def music(self, interaction: nextcord.Interaction):
        pass

    async def _play_autocomplete(self, interaction: nextcord.Interaction, item: str) -> [str]:
        """ Playlist search autocomplete. """

        if item.startswith('https://') or item.startswith('http://'):
            return []

        items = []

        return items

    @music.subcommand(
        name='play',
        description='Play music!',
    )
    async def play(
            self,
            interaction: nextcord.Interaction,
            item: str = nextcord.SlashOption(
                name='item',
                description='URL or Playlist name.',
                autocomplete=True,
                autocomplete_callback=_play_autocomplete,
                required=True,
            )
    ) -> [nextcord.PartialInteractionMessage, None]:
        """ Play YouTube video or own playlist. """

        if not interaction.user.voice:
            return await interaction.response.send_message(
                'You must join a voice channel first.',
                ephemeral=True,
            )

        url = None
        playlist = None

        if match(self.YOUTUBE_REGEX, item):
            url = item

        if not url:
            playlist_item = self.bot.database.query(
                "SELECT * FROM `music_playlist`"
                f" WHERE `name` = '{item}'",
                return_output=True,
            )

            if not playlist_item:
                return await interaction.response.send_message(
                    f'Playlist `{item}` not found.',
                    ephemeral=True,
                )

            playlist = playlist_item

        if not url and not playlist:
            return await interaction.response.send_message(
                f'Video not found.',
                ephemeral=True,
            )

        voice_client = self.bot.voice_client

        if not voice_client:
            await interaction.user.voice.channel.connect()
        else:
            if voice_client.channel.id != interaction.user.voice.channel.id:
                return await interaction.response.send_message(
                    'I\'m on another voice channel.',
                    ephemeral=True,
                )

            if voice_client.is_playing() and len(self.player.QUEUE) == 0:
                return await interaction.response.send_message(
                    'I\'m busy.',
                    ephemeral=True,
                )

        message: PartialInteractionMessage = await interaction.response.send_message('Downloading...')

        if url:
            # If that's initial song.
            if len(self.player.QUEUE) == 0:
                data = self.player.add(MusicSource.YOUTUBE, url)
                await self.player.play()

                return await message.edit(content=f'Playing **{data["title"]}**!')

            # Otherwise, add song to the queue.
            data = self.player.add(MusicSource.YOUTUBE, url)
            await message.edit(content=f'Added **{data["title"]}** to the queue!')
        # Playlist.
        else:
            pass

    @music.subcommand(
        name='pause',
        description='Pause on un-pause song.',
    )
    async def pause(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Pause on unpause song. """

        if not interaction.user.voice:
            return await interaction.response.send_message(
                'You must join a voice channel first.',
                ephemeral=True,
            )

        voice_client = self.bot.voice_client

        if not voice_client:
            return await interaction.response.send_message(
                'I\'m not playing music right now.',
                ephemeral=True,
            )

        if interaction.user.voice.channel.id != voice_client.channel.id:
            return await interaction.response.send_message(
                'You can\'t interact with music player while you in another voice channel.',
                ephemeral=True,
            )

        if not self.player.QUEUE:
            return await interaction.response.send_message(
                'I\'m not playing music right now.',
                ephemeral=True,
            )

        if voice_client.is_playing():
            voice_client.pause()

            await interaction.response.send_message('Music paused.')
        else:
            voice_client.resume()

            await interaction.response.send_message('Music un-paused.')

    @music.subcommand(
        name='queue',
        description='Music queue.',
    )
    async def queue(self, interaction: nextcord.Interaction) -> [nextcord.PartialInteractionMessage, None]:
        """ Music queue. """

        # Number suffix for: 1"st", 2"nd", etc.
        number_suffix = {
            1: 'st',
            2: 'nd',
            3: 'rd',
        }

        if not self.bot.voice_client:
            return await interaction.response.send_message(
                'I\'m not playing music right now.',
                ephemeral=True,
            )

        if not self.player.QUEUE:
            return await interaction.response.send_message(
                'Queue is empty.',
                ephemeral=True,
            )

        message = ''
        for i, song in enumerate(self.player.QUEUE):
            message += f'**{i + 1}**. [{song["title"]}]({song["source"]})\n'

        current_song_index = self.player.CURRENT + 1
        if current_song_index in number_suffix.keys():
            current_song_suffix = number_suffix[current_song_index]
        else:
            current_song_suffix = str(current_song_index) + 'th'

        embed = nextcord.Embed(
            color=DISCORD_EMBED_COLORS['DEFAULT'],
            title='Queue',
            description=message,
        )
        embed.set_footer(
            text='Currently playing: {index}{suffix}'.format(
                index=current_song_index,
                suffix=current_song_suffix,
            )
        )

        await interaction.response.send_message(embed=embed)


def setup(bot: SireniaBot):
    bot.add_cog(Music(bot))
