import asyncio
import random
import time

import discord
import youtube_dl
import os
import sys
from discord.ext import commands
from YTDL import *
from Assets import assets

res = assets()


class Voice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.volume = 1
        self.source_queue = []
        self.player_queue = []

    @commands.command(ignore_extra=False, help='Joins the channel you are in', aliases=['Join'])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        if channel is None:
            try:
                channel = ctx.author.voice.channel
            except:
                await ctx.send('Please join a channel or give a channel to join')
                return

        if channel in ctx.guild.voice_channels:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
        else:
            await ctx.send('Please enter a valid voice channel')

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send('Please enter a valid channel')
        else:
            raise error

    @commands.command(help='Leaves all channels')
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(help='stops the music playing')
    async def stop(self, ctx):
        ctx.voice_client.stop()

    @stop.error
    async def stop_error(self, ctx, error):
        return

    @commands.command()
    async def pause(self, ctx):
        ctx.message.guild.voice_client.pause()
        await ctx.send('Paused song')

    @commands.command()
    async def resume(self, ctx):
        ctx.message.guild.voice_client.resume()
        await ctx.send('Resuming')

    @commands.command()
    async def volume(self, ctx, volume):
        volume = int(volume)
        self.volume = volume / 100
        if ctx.voice_client is not None:
            ctx.voice_client.source.volume = volume / 100
        await ctx.send(f'Changed volume to {volume}')

    """
    @commands.command()
    async def loop(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.loop = not ctx.voice_client.loop
    """

    @commands.command(help='farts in your current channel after joining it')
    async def fart(self, ctx):
        if not self.bot.voice_clients:
            await Voice.join(ctx)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'fart/fart{random.randrange(9)}.mp3'))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

    @commands.command()
    async def info(self, ctx, *, url, message=True):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            name = player.formated_filename
            available = 'not in the database. Use `download` to add it'
            bool = False
            if os.path.isfile(res + f'downloads/{name}'):
                available = 'in the database'
                bool = True
            print(res + f'downloads/{name}')
        if message:
            await ctx.send(f'***{name}*** is {available}')
        return [player, name, bool]

    @commands.command()
    async def play(self, ctx, *, url):
        if not self.bot.voice_clients:
            await Voice.join(ctx)

        async with ctx.typing():
            if os.path.isfile(res + f'downloads/{url}'):
                player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{url}'))
                source = 'Database'
                player.title = url
                print(1)
            else:
                infos = await Voice.info(ctx, url=url, message=False)
                if infos[2]:
                    player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(res + f'downloads/{infos[1]}'))
                    source = 'Database'
                    player.title = infos[1]
                    print(2)
                else:
                    player = infos[0]
                    source = 'Youtube'
                    print(3)
            if ctx.voice_client.is_playing():
                self.player_queue.append(player)
                self.source_queue.append(source)
                await ctx.send(f'Added ***{player.title}*** to the queue')
                return
            else:
                await ctx.send(f'Now playing: ***{player.title}***\nFrom {source}')
                ctx.voice_client.play(player, after=await Voice.play_next(ctx))
                return

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please give a name or url')
        else:
            raise error

    @commands.command()
    async def play_next(self, ctx):
        if len(self.player_queue) > 0:
            while ctx.voice_client.is_playing():
                print(ctx.voice_client.is_playing())
            player = self.player_queue.pop(0)
            source = self.source_queue.pop(0)
            await ctx.send(f'Now playing next: ***{player.title}***\nFrom {source}')
            ctx.voice_client.play(player, after=await Voice.play_next(ctx))

    @commands.command()
    async def next(self, ctx):
        if len(self.player_queue) > 0:
            player = self.player_queue.pop(0)
            source = self.source_queue.pop(0)
            ctx.voice_client.stop()
            await ctx.send(f'Now playing: ***{player.title}***\nFrom {source}')
            ctx.voice_client.play(player, after=await Voice.play_next(ctx))
        else:
            await ctx.send('Queue is empty')

    @commands.command()
    async def queue(self, ctx):
        queue_len = len(self.player_queue)
        if queue_len == 0:
            await ctx.send('Queue is empty')
        else:
            embed = discord.Embed(title='Queue')
            for i in range(queue_len):
                embed.add_field(name=str(i), value=self.player_queue[i].title, inline=False)
            await ctx.channel.send(embed=embed)

    @commands.command()
    async def download(self, ctx, *, url):
        async with ctx.typing():
            await ctx.send('Downloading...')
            player = await YTDLSource.from_url(url, loop=False, stream=False)
            await ctx.send('Download finished')
        return player

    @commands.command(aliases=['dataBase', 'data', 'Data'])
    async def database(self, ctx):
        dir = res + 'downloads/'
        await ctx.send('Fetching database')
        async with ctx.typing():
            embed = discord.Embed(title='Database content')
            for f in os.listdir(dir):
                file_size = f'{round(os.stat(dir + f).st_size / 1000000.0, 2)} Mo'
                embed.add_field(name=f, value=file_size, inline=False)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def sendfile(self, ctx, *, file):
        async with ctx.typing():
            if not os.path.isfile(res + f'downloads/{file}'):
                await ctx.send(
                    'Sorry, the file you selected is not available. Download it using `download`')
        try:
            await ctx.send(file=discord.File(res + f'downloads/{file}'))
        except:
            await ctx.send('Sorry, the selected file is too big')

    @play.before_invoke
    @fart.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            await Voice.join(ctx)
        try:
            ctx.voice_client.source.volume = self.volume
        finally:
            return

    @stop.after_invoke
    @leave.after_invoke
    async def purge(self, ctx):
        self.player_queue = []
        self.source_queue = []

    @staticmethod
    async def on_cog_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(Voice(bot))
    print('Voice loaded')
