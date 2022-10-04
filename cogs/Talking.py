import asyncio
import random

import discord
import youtube_dl
import os
import sys

from discord import option
from discord.ext import commands
from Assets import assets

res = assets()


class Talking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(ignore_extra=False, help='Il te saluera en retour', aliases=['Salut'])
    async def salut(self, ctx):
        user = ctx.message.author
        if user.id == 347809940611661825:
            await ctx.send('Bonjour, Maitre. Comment se porte votre Magnificence?')
        else:
            await ctx.send('Hello ' + user.display_name + '. Comment ça va?')
            print(user.id)

    @salut.error
    async def salut_error(self, ctx, error):
        if isinstance(error, commands.TooManyArguments):
            return

    @commands.command(help='Si il te demande comment tu vas, réponds lui "bien et toi"', aliases=['Bien'])
    async def bien(self, ctx, et, toi):
        if et == 'et' and toi == 'toi':
            await ctx.send(
                'Un bot ne ressent pas d\'émotions, mais mon programme fonctionne. J\'en déduis donc que je vais bien.')

    @bien.error
    async def bien_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return

    @commands.slash_command(help='Insulte la personne que tu veux. La confidentialité est garantie', aliases=['Insult'])
    @option('name',
            type=str,
            description='Enter a name/mention/something to insult')
    async def insult(self, ctx: discord.ApplicationContext, name):
        await ctx.delete(delay=0)
        insults = [
            '{} est un fils de pute.',
            "Va te faire foutre {}.",
            "{} aime prendre des bites.",
            "Bouhouhou, {} est un gros caca boutchi.",
            "{} est un sac à merde.",
            "Va te faire retourner par un cheval {}.",
            "{} le suce pute."
        ]
        await ctx.send(insults[random.randrange(len(insults))].format(name))

    @commands.slash_command(help='Envoie un message d\'amour à qui tu veux. La confidentialité est garantie', aliases=['Love'])
    @option('name',
            type=str,
            description='Enter a name/mention/something to love')
    async def love(self, ctx: discord.ApplicationContext, name):
        await ctx.delete(delay=0)
        loves = [
            "Ouah, {0} est si beau!!!",
            "{0} est vraiment la personne la plus incroyable au monde.",
            "{0} est si parfait. A-t-il au moins un défaut!?"
            "C'est un peu embarassant, mais je crois que je t'aime {0}."
        ]
        await ctx.send(loves[random.randrange(len(loves))].format(name))

    @commands.slash_command(help='Insère une suggestion pour m\'améliorer et mon magnifique développeur en tiendra '
                           'peut-etre compte', aliases=['Suggest'])
    @option('suggestion',
            type=str,
            description='Enter a suggestion')
    async def suggest(self, ctx, suggestion):
        async with ctx.typing():
            if
            f = open(res + '/suggestions/sugg.txt', 'a')
            f.write(' '.join(suggestion) + '\n')
            f.close()
        await ctx.respond('Suggestion prise en compte')

    @commands.Cog.listener()
    async def on_cog_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(Talking(bot))
    print('Talking loaded')
