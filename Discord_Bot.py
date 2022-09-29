import json
import tracemalloc

from discord.ext import commands

from Assets import assets
from MyError import NoError
from cogs.Voice import *
from cogs.Checks import *


# folder to search for res
res = assets()


# Search the token for the right bot to launch
with open(res + 'settings/Tokens.json', 'r') as fp:
    bots = json.load(fp)["Bot"]
    # Change "Esclave" for the name of your default bot
    token = bots["Esclave"][0]
    welcome_channel = bots['Esclave'][1]
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in bots:
            token = bots[arg][0]
            welcome_channel = bots[arg][1]


# initialise bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)


tracemalloc.start()


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


@bot.event
async def on_voice_state_updated(ctx, before, after):
    pass


@bot.command()
@Checks.is_owner()
async def reload(ctx, extension):
    if f'{extension}' == 'help':
        bot.unload_extension('MyHelp')
        bot.load_extension('MyHelp')
    elif extension in bot.cogs:
        bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'Reloaded Cog {extension}')
    else:
        await ctx.send('Assure cog is valid')


@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument)\
            or isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        bot.unload_extension('cogs.MyHelp')
        bot.load_extension('cogs.MyHelp')
        # Display.show_stats.stop()
        # Display.show_clock.stop()
        tmp = bot.cogs.copy()
        tmp.pop('Help')
        for ext in tmp.keys():
            bot.unload_extension(f'cogs.{ext}')
            bot.load_extension(f'cogs.{ext}')
        await ctx.send('Reloaded all cogs')
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


"""async def start_bot():
    await bot.load_extension('Talking')
    await bot.load_extension('Voice')
    await bot.load_extension('MyHelp')
    # bot.load_extension('Display')
    await bot.load_extension('Checks')
    await bot.load_extension('GUI')"""

bot.load_extension('cogs.Talking')
bot.load_extension('cogs.Voice')
bot.load_extension('cogs.MyHelp')
bot.load_extension('cogs.Display')
bot.load_extension('cogs.Checks')
bot.load_extension('cogs.GUI')
bot.load_extension('cogs.ChatBot')
bot.load_extension('cogs.LoL')


bot.run(token)
