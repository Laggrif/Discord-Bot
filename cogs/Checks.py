import asyncio
import discord
from discord.ext import commands

owners = [347809940611661825]


class Checks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        async def predicate(ctx):
            return ctx.author.id in owners
        return commands.check(predicate)


def setup(bot):
    bot.add_cog(Checks(bot))
    print('Checks loaded')
