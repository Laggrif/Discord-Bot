import json
import discord
import PIL

import LoLAPI

from PIL import ImageDraw, Image
from discord import Interaction, Embed
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, View
from Assets import assets

res = assets() + 'League of Legends/'


async def advanced_stats(interaction: Interaction, match, summoner_stats):
    embed = Embed(title='Advanced Stats', description='une description')
    embed.add_field(name='Score', value='0/100/0')

    win = match

    im = Image.open(res + 'base.png')
    image = ImageDraw.Draw(im)
    await interaction.message.edit(content=None, embed=embed, view=None)


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

    @commands.command(help='Montre l\'historique des X dernières parties du type et de l\'invocateur donné. (par '
                           'défaut 5 parties en normal)')
    async def history(self, ctx: Context, summoner=None, games_count=None, type=None, region=None):
        if (games_count is None and type is not None) or (games_count is not None and type is None):
            await ctx.send('If you want custom type/number of games you must indicate both')
            return
        if summoner is None:
            with open(res + '/Registered_users.json', 'r') as fb:
                registered_users = json.load(fb)
            author_id = str(ctx.message.author.id)
            if author_id in registered_users:
                summoner_uuid = registered_users[author_id]
            else:
                await ctx.send('Please give a summoner name or link your summoner name with `link_account`')
                return
        else:
            summoner_uuid = self.LoLData.get_player_uuid(summoner, region)

        async with ctx.typing():
            history = self.LoLData.get_match_history(summoner_uuid, games_count, type)
            if history[1] is None:
                await ctx.send(f'Error {history[0]} happened during connection to Riot servers')
                return
            history = history[1]
            for match in history:
                # Gets the position of summoner in match
                player_order = 0
                for player in match['metadata']['participants']:
                    if player == summoner_uuid:
                        break
                    else:
                        player_order += 1

                summoner_stats = match['info']['participants'][player_order]

                win = summoner_stats['win']
                embed = Embed(title='Victory' if win else 'Defeat',
                              color=discord.Color.green() if win else discord.Color.red())

                # For kayn, gets the transformation
                transform = summoner_stats['championTransform']
                kayn = None
                if transform == 0:
                    kayn = ''
                elif transform == 1:
                    kayn = ' Slayer'
                elif transform == 2:
                    kayn = ' Assassin'

                # Show champion played
                champ_name = summoner_stats['championName']
                embed.add_field(name='Champion played', value=champ_name + kayn, inline=True)

                # Show score
                embed.add_field(name='Score', value=f"{summoner_stats['kills']}/" + f"{summoner_stats['deaths']}" +
                                                    f"/{summoner_stats['assists']}", inline=True)

                # Show KDA
                KDA = (summoner_stats['kills'] + summoner_stats['assists']) / max(1, summoner_stats['deaths'])
                embed.add_field(name='KDA', value=str(round(KDA, 2)), inline=True)

                # Show champion's icon
                self.LoLData.get_champ_icon(champ_name)
                champ_icon = discord.File(
                    res + 'Data/Champions_icons/{}/{}.png'.format(self.LoLData.current_ddragon_version, champ_name),
                    filename='champ_icon.png')
                embed.set_thumbnail(url='attachment://champ_icon.png')

                # Adds a button to show advanced stats
                async def advanced_stats_callback(interaction: Interaction):
                    await advanced_stats(interaction, match, summoner_stats)

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

        with open(res + '/Registered_users.json', 'r+') as fb:
            registered_users = json.load(fb)
            registered_users[ctx.message.author.id] = player_uuid
            fb.seek(0)
            json.dump(registered_users, fb, indent=4, separators=(',', ': '))
        await ctx.send('Successfully linked discord account **{}** to summoner name **{}**'
                       .format(ctx.message.author.name + '#' + ctx.message.author.discriminator, summoner))


def setup(bot: discord.Bot):
    bot.add_cog(LoL(bot))
    print('LoL loaded')
