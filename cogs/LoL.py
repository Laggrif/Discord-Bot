import io
import json
import discord
import os.path

import AdvancedHistory
import LoLAPI

from PIL import ImageDraw, Image
from pathlib import Path
from discord import Interaction, Embed
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, View
from Assets import assets
from LoLMatch import Match

res = assets() + 'League of Legends/'


class LimitedList:
    def __init__(self, max_length: int):
        self.list = []
        self.maxLength = max_length

    def add(self, ele):
        self.list.append(ele)
        if len(self.list) > self.maxLength:
            self.list.pop(0)
        return len(self.list) - 1

    def get(self, index):
        return self.list[index]


matchs = LimitedList(500)


class LoL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LoLData = LoLAPI.LoLData()
        self.default_region = 'euw'

    @tasks.loop(hours=12)
    async def actualise_data(self):
        self.LoLData.actualise()

    @commands.command(help='Recharge la clé d\'API Riot', aliases=['api'])
    async def reload_api_key(self, ctx: Context):
        self.LoLData.reload_api_key()
        await ctx.send('Reloaded Riot API key')

    @commands.command(help='Montre l\'historique des X dernières parties de l\'invocateur donné. (par '
                           'défaut 5 parties en normal)')
    async def history(self, ctx: Context, summoner=None, games_count=None, region=None):
        if summoner is None:
            try:
                with open(res + 'Registered_users.json', 'r') as fb:
                    registered_users = json.load(fb)
                author_id = str(ctx.message.author.id)
                if author_id in registered_users:
                    summoner_uuid = registered_users[author_id]
                else:
                    await ctx.send('Please give a summoner name or link your summoner name with `link_account`')
                    return
            except:
                await ctx.send('Please give a summoner name or link your summoner name with `link_account`')
                return
        else:
            summoner_uuid = self.LoLData.get_player_uuid(summoner, region)

        async with ctx.typing():
            history = self.LoLData.get_match_history(summoner_uuid, games_count)
            if history[1] is None:
                if history[0] == 400:
                    await ctx.send('Error 400, make sure you gave correct arguments.')
                    return
                await ctx.send(f'Error {history[0]} happened during connection to Riot servers')
                return
            history = history[1]
            for data in history:
                match = Match(data, summoner_uuid, self.LoLData.queues)

                index = matchs.add(match)

                win = match.win()
                embed = Embed(title='Victory' if win else 'Defeat',
                              color=discord.Color.green() if win else discord.Color.red())

                # For kayn, gets the transformation
                transform = match.transform()

                # Show champion played
                champ_name = match.champion()
                embed.add_field(name='Champion played', value=champ_name + transform, inline=True)

                # Show score
                embed.add_field(name='Score',
                                value='/'.join(str(x) for x in [match.kills(), match.deaths(), match.assists()]),
                                inline=True)

                # Show KDA
                KDA = match.kda()
                embed.add_field(name='KDA', value=str(round(KDA, 2)), inline=True)

                # Show champion's icon
                self.LoLData.get_champ_icon(champ_name)
                champ_icon = discord.File(
                    assets() + 'images/lol/Champions_icons/{}/{}.png'.format(self.LoLData.current_ddragon_version,
                                                                             champ_name),
                    filename='champ_icon.png')
                embed.set_thumbnail(url='attachment://champ_icon.png')

                # Adds a button to show advanced stats
                async def advanced_stats_callback(interaction: Interaction, index):
                    image = AdvancedHistory.AMH_picture(matchs.get(index), self.LoLData)
                    with io.BytesIO() as bites:
                        image.save(bites, format='PNG')
                        bites.seek(0)
                        file = discord.File(fp=bites, filename='champ_icon.png')
                        await interaction.message.edit(content=None, embed=None, view=None, file=file)

                button = Button(label='Advanced stats')
                button.callback = advanced_stats_callback

                view = View(button, timeout=None)

                # Send embed
                await ctx.send(embed=embed, file=champ_icon, view=view)

    @commands.command(help='Lie votre nom d\'invocateur LoL. Permet de rechercher votre historique de parties sans '
                           'spécifier d\'invocateur', aliases=['link'])
    async def link_account(self, ctx: Context, summoner):
        player_uuid = self.LoLData.get_player_uuid(summoner)
        if player_uuid == 400:
            await ctx.send('Make sure summoner name is valid (do not use spaces)')
            return

        if not os.path.isfile(res + 'Registered_users.json'):
            with open(res + 'Registered_users.json', 'a') as fp:
                json.dump({}, fp)
        with open(res + 'Registered_users.json', 'r+') as fb:
            registered_users = json.load(fb)
            registered_users[ctx.message.author.id] = player_uuid
            fb.seek(0)
            json.dump(registered_users, fb, indent=4, separators=(',', ': '))
        await ctx.send('Successfully linked discord account **{}** to summoner name **{}**'
                       .format(ctx.message.author.name + '#' + ctx.message.author.discriminator, summoner))


def setup(bot: discord.Bot):
    bot.add_cog(LoL(bot))
    print('LoL loaded')
