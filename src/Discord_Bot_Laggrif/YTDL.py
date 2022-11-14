import asyncio
import audioop

import discord
import youtube_dl
from discord import ClientException, AudioSource

from Discord_Bot_Laggrif.Assets import res_folder

res = res_folder()

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': res + '/downloads/%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.formated_filename = ytdl.prepare_filename(data).replace(res + '/downloads/', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class PCMVolumeTransformer(discord.PCMVolumeTransformer):
    def __init__(self, original, title, volume=1.0):
        if not isinstance(original, AudioSource):
            raise TypeError('expected AudioSource not {0.__class__.__name__}.'.format(original))

        if original.is_opus():
            raise ClientException('AudioSource must not be Opus encoded.')

        self.original = original
        self.volume = volume
        self.title = title

    @property
    def volume(self):
        """Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
        return self._volume

    @property
    def title(self):
        return self._title

    @volume.setter
    def volume(self, value):
        self._volume = max(value, 0.0)

    @title.setter
    def title(self, value):
        self._title = value

    def cleanup(self):
        self.original.cleanup()

    def read(self):
        ret = self.original.read()
        return audioop.mul(ret, 2, min(self._volume, 2.0))
