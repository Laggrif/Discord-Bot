import json

from discord import ApplicationContext, option
from discord.ext.commands import Bot

import Assets
from YTDL import *

res = Assets.assets()


class VoiceClients:
    def __init__(self, voice, guild_id):
        self.guild_id = guild_id
        self.source_queue = []
        self.player_queue = []
        self.voice = voice
        self.loop = False
        self.is_playing = False
        self.volume = 60

        with open(res + 'settings/Voice.json', 'r') as fp:
            settings = json.load(fp)
        if str(guild_id) not in settings.keys():
            settings[guild_id] = {'volume': self.volume}
            with open(res + 'settings/Voice.json', 'w+') as fp:
                json.dump(settings, fp, indent=4, separators=(',', ': '))
            self.volume = 60
        else:
            self.volume = settings[str(guild_id)]['volume']

    def add_song(self, player, source):
        self.player_queue.append(player)
        self.source_queue.append(source)
        return self

    def set_volume(self, volume):
        self.voice.source.volume = volume
        self.volume = volume
        with open(res + 'settings/Voice.json', 'r+') as fp:
            settings = json.load(fp)
            settings[str(self.guild_id)]['volume'] = volume
            json.dump(settings, fp)
        return self

    def toggle_loop(self):
        self.loop = not self.loop
        with open(res + 'settings/Voice.json', 'r+') as fp:
            settings = json.load(fp)
            settings[str(self.guild_id)]['loop'] = self.loop
            json.dump(settings, fp)
        return self

    def move_to(self, voice):
        self.voice = voice
        return self

    def play(self):
        print('play')
        self.voice.source.volume = self.volume
        self.is_playing = True
        return self

    def pause(self, error=None):
        print('pause', error if error is not None else '')
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
        return self.player_queue[0], self.source_queue[0]

    def has_next(self):
        return True if len(self.player_queue) > 1 else False

    def is_empty(self):
        return True if len(self.player_queue) < 0 else False


class Voice(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.voice_clients = dict()
        for guild in self.bot.guilds:
            self.voice_clients[guild.id] = VoiceClients(guild.voice_client, guild.id)

    @commands.slash_command(ignore_extra=False, help='Joins the channel you are in', aliases=['Join'])
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

        guild_id = ctx.guild.id
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
            self.voice_clients[guild_id].move_to(ctx.voice_client)
        else:
            await channel.connect()
        self.voice_clients[guild_id].move_to(ctx.voice_client)

        if message:
            await ctx.followup.send('Joined voice channel')
            return None
        return ctx

    @commands.slash_command(help='Leaves all channels')
    async def leave(self, ctx: ApplicationContext):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect(force=True)
            self.voice_clients.pop(ctx.guild.id)
        await ctx.respond('Left voice channel')

    @commands.slash_command()
    async def volume(self, ctx, volume):
        guild_id = ctx.guild.id
        vol = float(volume) / 100.0
        with open(res + 'settings/Voice.json', 'r+') as fp:
            settings = json.load(fp)
            settings[guild_id]['volume'] = vol
            json.dump(settings, fp, sort_keys=True, indent=4, separators=(',', ': '))
        if ctx.voice_client is not None:
            self.voice_clients[guild_id].set_volume(vol)
        await ctx.respond(f'Changed volume to {volume}')

    @commands.slash_command(help='farts in the current channel or join the channel you are in')
    async def fart(self, ctx):
        if not self.bot.voice_clients:
            ctx = await self.join(ctx, None, False)
        if ctx is None:
            return

        voice_client = self.voice_clients[ctx.guild.id]
        if not voice_client.is_playing:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'fart/fart{random.randrange(9)}.mp3'))
            voice_client.play()
            voice_client.voice.play(source, after=lambda e: (print(f'Player error: {e}'), voice_client.pause()) if e
                                    else voice_client.pause())
            await ctx.delete(delay=0)

    @commands.slash_command()
    async def info(self, ctx, url, message=True):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            name = player.formated_filename
            available = 'not in the database. Use `download` to add it'
            bool = False
            if os.path.isfile(res + f'downloads/{name}'):
                available = 'in the database'
                bool = True
        if message:
            await ctx.respond(f'***{name}*** is {available}')
        return [player, name, bool]

    @commands.slash_command()
    async def play(self, ctx, url):
        def play_next(error):
            print(error)
            voice_client = self.voice_clients[ctx.guild.id]
            voice_client.pause()
            if voice_client.is_empty():
                print('empty')
                return
            if voice_client.loop:
                print('loop')
                player, source = voice_client.head()
            elif voice_client.has_next():
                print('next')
                player, source = voice_client.pop2()
            else:
                print('else')
                return

            async def play(ctx, player):
                print('t')
                if os.path.isfile(res + f'downloads/{player}'):
                    player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{player}'))
                else:
                    infos = await Voice.info(ctx, player, False)
                    if infos[2]:
                        player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{infos[0]}'))
                    else:
                        player = infos[0]

                voice_client.play()
                voice_client.voice.play(player, after=play_next)
                await ctx.send(f'Now playing: ***{player.title}***\nFrom {source}')
            l = asyncio.run_coroutine_threadsafe(play(ctx, player), self.bot.loop)
            print(l.result(10))

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
                voice_client.play()
                voice_client.voice.play(player, after=play_next)
                await ctx.followup.send(f'Now playing: ***{player.title}***\nFrom {source}')
                return

    @commands.slash_command(help='stops the music playing')
    async def stop(self, ctx):
        ctx.voice_client.stop()
        self.voice_clients[ctx.guild.id].pause().purge()
        await ctx.respond('Stopped voice and purged queue')

    @commands.slash_command()
    async def pause(self, ctx):
        self.voice_clients[ctx.guild.id].pause().\
            voice().pause()
        await ctx.respond('Paused voice')

    @commands.slash_command()
    async def resume(self, ctx):
        self.voice_clients[ctx.guild.id].play().\
            voice().resume()
        await ctx.respond('Resuming')

    @commands.slash_command()
    async def loop(self, ctx):
        if ctx.voice_client is not None:
            voice_client = self.voice_clients[ctx.guild.id]
            voice_client.toggle_loop()
            await ctx.respond('Loop is on' if voice_client.loop else 'Loop is off')
        else:
            # TODO change guild settings in json
            await ctx.respond('Bot must be connected to a voice channel to enable looping')

    @commands.slash_command()
    async def next(self, ctx):
        await ctx.response.defer()
        voice_client = self.voice_clients[ctx.guild.id]
        change = False
        if voice_client.loop:
            voice_client.toggle_loop()
            change = True
        voice_client.voice.stop()
        if change:
            voice_client.toggle_loop()

    @commands.slash_command()
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

    @commands.slash_command()
    async def download(self, ctx, *, url):
        async with ctx.typing():
            await ctx.respond('Downloading...')
            player = await YTDLSource.from_url(url, loop=False, stream=False)
            await ctx.send('Download finished')
        return player

    @commands.slash_command(aliases=['dataBase', 'data', 'Data'])
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

    @commands.slash_command()
    async def sendfile(self, ctx, *, file):
        async with ctx.typing():
            if not os.path.isfile(res + f'downloads/{file}'):
                await ctx.respond(
                    'Sorry, the file you selected is not available. Download it using `download`')
        try:
            await ctx.respond(file=discord.File(res + f'downloads/{file}'))
        except:
            await ctx.respond('Sorry, the selected file is too big')

    @commands.Cog.listener()
    async def on_cog_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(Voice(bot))
    print('Voice loaded')
