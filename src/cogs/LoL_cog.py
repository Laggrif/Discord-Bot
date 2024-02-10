import io
import json
import os.path

import discord
from discord import Interaction, Embed, option
from discord.ext import commands, tasks
from discord.ui import Button, View

from Assets import res_folder
from cogs.Checks import Checks
from LoL import LoLAPI, AdvancedHistory
from LoL.LoLMatch import *
from LoL.LoLChamp import Champ
from LoL.ChampInfos import ChI_image

res = res_folder() + 'League of Legends/'

if not os.path.isfile(res + 'Registered_users.json'):
    open(res + 'Registered_users.json', 'w').write('{}')

regions = ['euw', 'br', 'eun', 'jp', 'kr', 'la', 'na', 'oc', 'tr', 'ru']
languages = LoLAPI.LoLData().languages


class LimitedList:
    def __init__(self, max_length: int):
        self.list = {}
        self.maxLength = max_length

    async def add(self, ele, key):
        self.list[key] = ele
        if len(self.list) > self.maxLength:
            k = next(iter(self.list))
            View = discord.ui.View.from_message(k)
            View.clear_items()
            await k.edit(view=View)
            self.list.pop(k)

        return len(self.list) - 1

    def get(self, key):
        return self.list.get(key)


matches = LimitedList(500)


class LoL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LoLData = LoLAPI.LoLData()
        self.default_region = 'euw'

    @tasks.loop(hours=12)
    async def actualise_data(self):
        self.LoLData.actualise()

    @Checks.is_owner()
    @commands.slash_command(description='Recharge la clé d\'API Riot', aliases=['api'])
    async def reload_api_key(self, ctx: discord.ApplicationContext):
        self.LoLData.reload_api_key()
        await ctx.respond('Reloaded Riot API key')

    @commands.slash_command(description='Montre l\'historique des X dernières parties de l\'invocateur donné. (par '
                                        'défaut 5 parties)')
    @option('summoner',
            type=str,
            description="Enter a summoner name",
            required=False,
            default=None,
            )
    @option('games_count',
            type=int,
            description='Enter the number of games you want',
            required=False,
            min_value=1,
            max_value=100,
            defaul=5,
            )
    @option('region',
            descrition='Enter a region',
            required=False,
            default=None,
            choices=regions)
    async def history(self, ctx: discord.ApplicationContext, summoner=None, games_count=None, region=None):
        if summoner is None:
            with open(res + 'Registered_users.json', 'r') as fb:
                registered_users = json.load(fb)
            author_id = str(ctx.author.id)
            if author_id in registered_users:
                summoner_uuid = registered_users[author_id]
            else:
                await ctx.respond('Please give a summoner name or link your summoner name with `link_account`')
                return
        else:
            summoner_uuid = self.LoLData.get_player_uuid(summoner, region)

        await ctx.defer(invisible=True)

        async with ctx.typing():
            history = self.LoLData.get_match_history(summoner_uuid, games_count)
            if history[1] is None:
                if history[0] == 400:
                    await ctx.respond('Error 400, make sure you gave correct arguments.')
                    return
                await ctx.respond(f'Error {history[0]} happened during connection to Riot servers')
                return
            history = history[1]
            for data in history:
                match = Match(data, summoner_uuid, self.LoLData.queues)

                win = match.win()
                title = 'Victory' if win else 'Defeat'
                embed = Embed(title=title + '     ' + match.game_mode().lstrip('5v5 ').rstrip(' games'),
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
                KDA = '%.2f' % match.kda() if match.kda() is not None else "∞"
                embed.add_field(name='KDA', value=KDA, inline=True)

                # Show champion's icon
                self.LoLData.get_champ_icon(champ_name)
                champ_icon = discord.File(
                    res_folder() + 'images/lol/Champions_icons/{}/{}.png'.format(self.LoLData.current_ddragon_version,
                                                                                 champ_name),
                    filename='champ_icon.png')
                embed.set_thumbnail(url='attachment://champ_icon.png')

                # Adds a button to show advanced stats
                async def advanced_stats_callback(interaction: Interaction):
                    message = interaction.message
                    image = AdvancedHistory.AMH_picture(matches.get(message), self.LoLData)
                    with io.BytesIO() as bites:
                        image.save(bites, format='PNG')
                        bites.seek(0)
                        file = discord.File(fp=bites, filename='champ_icon.png')
                        await message.edit(content=None, embed=None, view=None, file=file)

                button = Button(label='Advanced stats')
                button.callback = advanced_stats_callback

                view = View(button, timeout=None)

                # Send embed
                msg = await ctx.send(embed=embed, file=champ_icon, view=view)

                await matches.add(match, msg)

    @commands.slash_command(
        description='Lie votre nom d\'invocateur LoL. L\'historique sera disponible sans spécifier d\'invocateur',
        aliases=['link'])
    @option('summoner',
            type=str,
            description='Enter your summoner name',
            required=True)
    async def link_account(self, ctx: discord.ApplicationContext, summoner):
        player_uuid = self.LoLData.get_player_uuid(summoner)
        if player_uuid == 400:
            await ctx.respond('Make sure summoner name is valid (do not use spaces)')
            return

        if not os.path.isfile(res + 'Registered_users.json'):
            with open(res + 'Registered_users.json', 'a') as fp:
                json.dump({}, fp)
        with open(res + 'Registered_users.json', 'r+') as fb:
            registered_users = json.load(fb)
            registered_users[str(ctx.author.id)] = player_uuid
            fb.seek(0)
            json.dump(registered_users, fb, indent=4, separators=(',', ': '))
        await ctx.respond('Successfully linked discord account **{}** to summoner name **{}**'
                          .format(ctx.author.name + '#' + ctx.author.discriminator, summoner))

    @commands.slash_command(
        description='Affiche les statistiques détaillées d\'un champion',
        aliases=['champ', 'champ info', 'champion info', 'champion information'])
    @option('champion name', type=str, description='Give the name of a champion', required=True)
    @option('version', type=str, description='Desired version (patch note)', required=False, default=None)
    @option('language', description='Desired language', required=False, default=None)
    async def champ_info(self, ctx: discord.ApplicationContext, champion, version=None, language=None):
        await ctx.defer(invisible=True)
        wrong_champ = False
        wrong_lang = False
        view = None
        if champion not in self.LoLData.champ_list:
            wrong_champ = True

            async def champ_list_callback(interaction: Interaction):
                embed = Embed(title='')
                champs = ''
                for i, champ in enumerate(self.LoLData.champ_list):
                    champs += f'{champ}\n'
                    if (i + 1) % 10 == 0:
                        embed.add_field(name='', value=champs, inline=True)
                        champs = ''
                if len(champs) != 0:
                    embed.add_field(name='', value=champs, inline=True)
                if len(embed.fields) % 3 != 0:
                    [embed.add_field(name='', value='', inline=True) for _ in range(1 + (len(embed.fields) % 2))]
                await interaction.message.edit(content=None, embed=embed)

            button = Button(label='Show champions list')
            button.callback = champ_list_callback

            view = View(button, timeout=None)

        if language not in languages and language is not None:
            wrong_lang = True

            async def lang_list_callback(interaction: Interaction):
                embed = Embed(title='')
                langs = ''
                for i, lang in enumerate(languages):
                    langs += f'{lang}\n'
                    if (i + 1) % 10 == 0:
                        embed.add_field(name='', value=langs, inline=True)
                        langs = ''
                if len(langs) != 0:
                    embed.add_field(name='', value=langs, inline=True)
                if len(embed.fields) % 3 != 0:
                    [embed.add_field(name='', value='', inline=True) for _ in range(1 + (len(embed.fields) % 2))]
                await interaction.message.edit(content=None, embed=embed)

            button = Button(label='Show languages list')
            button.callback = lang_list_callback

            if view is not None:
                view.add_item(button)
            else:
                view = View(button, timeout=None)

        if wrong_champ and wrong_lang:
            await ctx.respond('Language and champion are not valid. Make sure they are valid', view=view)
        elif wrong_champ:
            await ctx.respond('Champion is not valid. Make sure it is written correctly', view=view)
        elif wrong_lang:
            await ctx.respond('Language is not valid. Make sure it is available', view=view)

        else:
            async with ctx.typing():
                img = ChI_image(self.LoLData, Champ(self.LoLData, champion, version, language))
                with io.BytesIO() as bites:
                    img.save(bites, format='PNG')
                    bites.seek(0)
                    file = discord.File(fp=bites, filename=f'{champion}.png')
                    await ctx.respond(content=None, file=file)


def setup(bot: discord.Bot):
    bot.add_cog(LoL(bot))
    print('LoL loaded')
