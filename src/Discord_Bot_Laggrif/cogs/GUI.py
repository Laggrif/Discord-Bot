from discord.ui import Button, View

from Discord_Bot_Laggrif.Assets import res_folder
from Discord_Bot_Laggrif.cogs.MyHelp import *

res = res_folder()


class GUI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx = None

    @commands.slash_command()
    async def command_panel(self, ctx):
        button = Button(label='Help')
        self.ctx = ctx

        async def help_callback(interaction):
            # await interaction.response.send_message('Salut')
            await self.ctx.send_help()
        button.callback = help_callback

        view = View(button, timeout=None)
        await ctx.send('Salu', view=view)

    @commands.Cog.listener()
    async def on_cog_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(GUI(bot))
    print('GUI loaded')