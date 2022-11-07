import io
import json
import os.path

import discord
from discord import Interaction, Embed, option
from discord.ext import commands, tasks
from discord.ui import Button, View

from Discord_Bot_Laggrif.Assets import assets
from Discord_Bot_Laggrif.LoL.LoLMatch import Match
from Discord_Bot_Laggrif.cogs.Checks import Checks
from LoL import AdvancedHistory, LoLAPI

res = assets() + 'League of Legends/'

if not os.path.isfile(res + 'Registered_users.json'):
    open(res + 'Registered_users.json', 'w').write('{}')

regions = ['euw', 'br', 'eun', 'jp', 'kr', 'la', 'na', 'oc', 'tr', 'ru']


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
                                 'défaut 5 parties en normal)')
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


def setup(bot: discord.Bot):
    bot.add_cog(LoL(bot))
    print('LoL loaded')
