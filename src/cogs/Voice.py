import json
import os
import random

from discord import ApplicationContext, option
from discord.ext import commands
from discord.ext.commands import Bot, Cog, slash_command

from YTDL import *
from Assets import *

res = res_folder()


class VoiceClients:
    def __init__(self, voice, guild_id):
        self.guild_id = guild_id
        self.source_queue = []
        self.player_queue = []
        self.voice = voice
        self.is_playing = False
        self.loop = False
        self.volume = 0.6

        if not os.path.isfile(res + 'settings/Voice.json'):
            with open(res + 'settings/Voice.json', 'w') as fp:
                json.dump({}, fp, indent=4, separators=(',', ': '))
        with open(res + 'settings/Voice.json', 'r') as fp:
            settings = json.load(fp)
        if str(guild_id) not in settings.keys():
            settings[guild_id] = {'volume': self.volume, 'loop': self.loop}
            with open(res + 'settings/Voice.json', 'w') as fp:
                json.dump(settings, fp, indent=4, separators=(',', ': '))
        else:
            self.volume = settings[str(guild_id)]['volume']

    def add_song(self, player, source):
        self.player_queue.append(player)
        self.source_queue.append(source)
        return self

    def add_song_now(self, player, source):
        self.player_queue.insert(1, player)
        self.source_queue.insert(1, source)
        return self

    def set_volume(self, volume):
        if self.voice and self.voice.source:
            self.voice.source.volume = volume

        self.volume = volume
        with open(res + 'settings/Voice.json', 'r+') as fp:
            settings = json.load(fp)
        settings[str(self.guild_id)]['volume'] = volume
        with open(res + 'settings/Voice.json', 'w') as fp:
            json.dump(settings, fp, indent=4, separators=(',', ': '))
        return self

    def toggle_loop(self):
        self.loop = not self.loop
        with open(res + 'settings/Voice.json', 'r+') as fp:
            settings = json.load(fp)
        settings[str(self.guild_id)]['loop'] = self.loop
        with open(res + 'settings/Voice.json', 'w') as fp:
            json.dump(settings, fp, indent=4, separators=(',', ': '))
        return self

    def move_to(self, voice):
        self.voice = voice
        return self

    def play(self):
        self.voice.source.volume = self.volume
        self.is_playing = True
        return self

    def pause(self):
        self.is_playing = False
        return self

    def purge(self):
        self.player_queue = []
        self.source_queue = []
        return self

    def head(self):
        return self.player_queue[0], self.source_queue[0]

    def pop2(self):
        self.player_queue.pop(0)
        self.source_queue.pop(0)
        if not self.is_empty():
            return self.player_queue[0], self.source_queue[0]

    def has_next(self):
        return len(self.player_queue) > 1

    def is_empty(self):
        return len(self.player_queue) <= 0

    def remove(self):
        with open(res + 'settings/Voice.json', 'r+') as fp:
            settings = json.load(fp)
        del settings[str(self.guild_id)]
        with open(res + 'settings/Voice.json', 'w') as fp:
            json.dump(settings, fp, indent=4, separators=(',', ': '))


class Voice(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.voice_clients = dict()

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.voice_clients[guild.id] = VoiceClients(guild.voice_client, guild.id)

    @Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return

        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect(force=True)
            self.voice_clients[member.guild.id].\
                pause().\
                purge().\
                voice = None

    @Cog.listener()
    async def on_guild_join(self, guild):
        self.voice_clients[guild.id] = VoiceClients(guild.voice_client, guild.id)

    @Cog.listener()
    async def on_guild_remove(self, guild):
        id = guild.id
        self.voice_clients[id].remove()
        del self.voice_clients[id]

    @slash_command(ignore_extra=False, description='Joins the channel you are in', aliases=['Join'])
    @option('channel',
            default=None,
            description='Enter a voice channel',
            input_type=str,
            required=False)
    @option('message',
            default=True,
            description='DO NOT USE! Whether bot should respond to you.',
            input_type=bool,
            required=False)
    async def join(self, ctx: ApplicationContext, channel, message):
        await ctx.response.defer()
        if channel is None:
            try:
                channel = ctx.author.voice.channel
            except:
                await ctx.respond('Please join a channel or give a channel to join')
                return None

        else:
            if channel not in [x.name for x in ctx.guild.voice_channels]:
                await ctx.followup.send('Please enter a valid voice channel')
                return None
            else:
                for ch in ctx.guild.voice_channels:
                    if channel == ch.name:
                        channel = ch
                        break
            if len(channel.members) == 0:
                await ctx.followup.send('Channel is empty, I don\'t want to be alone...')
                return

        guild_id = ctx.guild.id
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        self.voice_clients[guild_id].move_to(ctx.voice_client)

        if message:
            await ctx.followup.send('Joined voice channel')
            return None
        return ctx

    @slash_command(help='Leaves all channels')
    async def leave(self, ctx: ApplicationContext):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect(force=True)
            self.voice_clients.pop(ctx.guild.id)
        await ctx.respond('Left voice channel')

    @slash_command()
    async def volume(self, ctx, volume):
        vol = float(volume) / 100.0
        self.voice_clients[ctx.guild.id].set_volume(vol)
        await ctx.respond(f'Changed volume to {volume}')

    @slash_command(help='farts in the current channel or join the channel you are in to fart')
    async def fart(self, ctx):
        if not self.bot.voice_clients:
            ctx = await self.join(ctx, None, False)
        if ctx is None:
            return

        voice_client = self.voice_clients[ctx.guild.id]
        if not voice_client.is_playing:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'fart/fart{random.randrange(9)}.mp3'))
            voice_client.voice.play(source, after=lambda e: (print(f'Player error: {e}'), voice_client.pause()) if e
                                    else voice_client.pause())
            voice_client.play()
            await ctx.delete(delay=0)

    @slash_command()
    async def info(self, ctx, url, message=True):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
            name = player.formated_filename
            available = 'not in the database. Use `download` to add it'
            bool = False
            if os.path.isfile(res + f'downloads/{name}'):
                available = 'in the database'
                bool = True
        if message:
            await ctx.respond(f'***{name}*** is {available}')
        return [player, name, bool]

    @slash_command(help='plays the song or adds it to the queue if already playing')
    async def play(self, ctx, url):
        def play_next(error):
            voice_client = self.voice_clients[ctx.guild.id]
            voice_client.pause()
            if voice_client.is_empty():
                return
            if voice_client.loop:
                player, source = voice_client.head()
            elif voice_client.has_next():
                player, source = voice_client.pop2()
            else:
                voice_client.pop2()
                return

            async def play(ctx, player):
                if os.path.isfile(res + f'downloads/{player}'):
                    player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{player}'))
                else:
                    infos = await Voice.info(ctx, player, False)
                    if infos[2]:
                        player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{infos[0]}'))
                    else:
                        player = infos[0]

                voice_client.voice.play(player, after=play_next)
                voice_client.play()
                await ctx.send(f'Now playing: ***{player.title}***\nFrom {source}')
            l = asyncio.run_coroutine_threadsafe(play(ctx, player), self.bot.loop)

        if not self.bot.voice_clients:
            ctx = await self.join(ctx, None, message=False)
        else:
            await ctx.response.defer()
        if ctx is None:
            return

        async with ctx.typing():
            if os.path.isfile(res + f'downloads/{url}'):
                player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{url}'))
                source = 'Database'
                player.title = url
            else:
                infos = await Voice.info(ctx, url=url, message=False)
                if infos[2]:
                    player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{infos[1]}'))
                    source = 'Database'
                    player.title = infos[1]
                else:
                    player = infos[0]
                    source = 'Youtube'

            voice_client = self.voice_clients[ctx.guild.id]
            voice_client.add_song(player.title, source)
            if voice_client.is_playing:
                await ctx.followup.send(f'Added ***{player.title}*** to the queue')
                return
            else:
                voice_client.voice.play(player, after=play_next)
                voice_client.play()
                await ctx.followup.send(f'Now playing: ***{player.title}***\nFrom {source}')
                return

    @slash_command(help='Plays the song right after')
    async def playnext(self, ctx, url):
        voice_client = self.voice_clients[ctx.guild.id]

        if voice_client.is_playing:
            await ctx.response.defer()
            infos = await self.info(ctx, url, False)
            if infos[2]:
                title, source = infos[1], 'Database'
                voice_client.add_song_now(title, source)
            else:
                title, source = infos[0].title, 'Youtube'
                voice_client.add_song_now(title, source)
            await ctx.followup.send(f'Added ***{title}*** to be played next')
        else:
            await self.play(ctx, url)

    @slash_command(help='stops the music playing')
    async def stop(self, ctx):
        ctx.voice_client.stop()
        self.voice_clients[ctx.guild.id].pause().purge()
        await ctx.respond('Stopped voice and purged queue')

    @slash_command()
    async def pause(self, ctx):
        self.voice_clients[ctx.guild.id].pause().\
            voice.pause()
        await ctx.respond('Paused voice')

    @slash_command()
    async def resume(self, ctx):
        self.voice_clients[ctx.guild.id].play().\
            voice.resume()
        await ctx.respond('Resuming')

    @slash_command()
    async def loop(self, ctx):
        voice_client = self.voice_clients[ctx.guild.id].toggle_loop()
        await ctx.respond('Loop is on' if voice_client.loop else 'Loop is off')

    @slash_command()
    async def skip(self, ctx):
        await ctx.response.defer()
        voice_client = self.voice_clients[ctx.guild.id]
        change = False
        if voice_client.loop:
            voice_client.toggle_loop()
            change = True
        voice_client.voice.stop()
        if change:
            voice_client.toggle_loop()

    @slash_command()
    async def queue(self, ctx):
        voice_client = self.voice_clients[ctx.guild.id]
        if voice_client.is_empty():
            await ctx.respond('Queue is empty')
        else:
            embed = discord.Embed(title='Queue')
            for i in range(len(voice_client.player_queue)):
                embed.add_field(name=f'{i} (currently playing)' if i == 0 else str(i),
                                value=voice_client.player_queue[i],
                                inline=False)
            await ctx.respond(embed=embed)

    @slash_command()
    async def download(self, ctx, *, url):
        async with ctx.typing():
            await ctx.respond('Downloading...')
            player = await YTDLSource.from_url(url, loop=False, stream=False)
            await ctx.send('Download finished')
        return player

    @slash_command(aliases=['dataBase', 'data', 'Data'])
    async def database(self, ctx):
        dir = res + 'downloads/'
        if not os.path.exists(dir):
            await ctx.respond('Database is Empty')
            return
        await ctx.respond('Fetching database')
        async with ctx.typing():
            embed = discord.Embed(title='Database content')
            for f in os.listdir(dir):
                file_size = f'{round(os.stat(dir + f).st_size / 1000000.0, 2)} Mo'
                embed.add_field(name=f, value=file_size, inline=False)
        await ctx.channel.send(embed=embed)

    @slash_command()
    async def sendfile(self, ctx, *, file):
        async with ctx.typing():
            if not os.path.isfile(res + f'downloads/{file}'):
                await ctx.respond(
                    'Sorry, the file you selected is not available. Download it using `download`')
        try:
            await ctx.respond(file=discord.File(res + f'downloads/{file}'))
        except:
            await ctx.respond('Sorry, the selected file is too big')

    @Cog.listener()
    async def on_cog_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(Voice(bot))
    print('Voice loaded')
