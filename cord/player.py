import io
from typing import Union, Optional, IO

from nextcord import FFmpegPCMAudio

from settings import PROJECT_ROOT


class FFmpegPCMAudioCustom(FFmpegPCMAudio):
    """ The nextcord.FFmpegPCMAudio with a few predefined options. """

    def __init__(
            self,
            source: Union[str, io.BufferedIOBase],
            executable: str = "ffmpeg",
            pipe: bool = False,
            stderr: Optional[IO[str]] = None,
            before_options: Optional[str] = None,
            options: Optional[str] = None,
    ):
        if executable == "ffmpeg":
            executable = PROJECT_ROOT + '/ffmpeg'

        if options is None:
            options = '-filter:a "volume=0.10"'

        super().__init__(
            source,
            executable=executable,
            pipe=pipe,
            stderr=stderr,
            before_options=before_options,
            options=options,
        )
