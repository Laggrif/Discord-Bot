#!/usr/bin/env python3
import sys

from discord.ext import commands

from Discord_Bot_Laggrif.MyError import NoError
from Discord_Bot_Laggrif.cogs.Checks import *
from Discord_Bot_Laggrif.cogs.Display import Display
from Discord_Bot_Laggrif.cogs.Voice import *

# folder to search for res
res = res_folder()


# initialise bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents) #, debug_guilds=[944230321572962314, 501076532975108098])


@bot.event
async def on_ready():
    channel = bot.get_channel(welcome_channel)
    mention = '<@347809940611661825>'
    await channel.send(f'Paré à me faire exploiter {mention}')
    await bot.change_presence(activity=discord.Game(name="Slave simulator"))
    print("Paré bande de petits pd albinos!")


@bot.event
async def on_message(msg):
    if 'salut' in msg.content.lower():
        await msg.add_reaction('a:Salut:915623038140158063')
    await bot.process_commands(msg)


@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        if 'salut' in after.content.lower():
            await after.add_reaction('a:Salut:915623038140158063')
        await bot.process_commands(after)


@bot.slash_command(name='reload', description='Reloads specified cog or all cogs if `All`')
@option('cog',
        autocomplete=lambda ctx: [cog for cog in list(bot.cogs.keys()) + ['All'] if
                                  cog.lower().startswith(ctx.value.lower())],
        description="Enter a cog name",
        input_type=str,
        choices=list(bot.cogs.keys())
        )
@Checks.is_owner()
async def reload(ctx: discord.ApplicationContext, cog):
    if cog == 'All':
        bot.unload_extension('cogs.MyHelp')
        bot.load_extension('cogs.MyHelp')
        Display.show_stats.stop()
        Display.show_clock.stop()
        tmp = bot.cogs.copy()
        tmp.pop('Help')
        for ext in tmp.keys():
            bot.unload_extension(f'cogs.{ext}')
            bot.load_extension(f'cogs.{ext}')
        await ctx.respond('Reloaded all cogs')
        return

    if f'{cog}' == 'help':
        bot.unload_extension('MyHelp')
        bot.load_extension('MyHelp')
    elif cog in bot.cogs:
        bot.reload_extension(f'cogs.{cog}')
        await ctx.respond(f'Reloaded Cog {cog}')
    else:
        await ctx.respond('Assure cog is valid')


@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) \
            or isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        pass
    elif isinstance(error, commands.CheckFailure):
        return
    else:
        return


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure, NoError)):
        print('err1')
        del error
        return

    else:
        await ctx.send('Something went wrong...')
        raise error


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, NoError):
        print('err2')
        return
    else:
        await on_application_command_error(ctx, error)


def get_bot():
    return bot


def run(which):
    bot.load_extension('cogs', package='.')

    # Search the token for the right bot to launch
    with open(res + 'settings/Tokens.json', 'r') as fp:
        bots = json.load(fp)["Bot"]
        token = bots[which][0]
        global welcome_channel
        welcome_channel = bots[which][1]

    bot.run(token)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        # Change `Esclave` for the name of your default bot
        run('Esclave')
