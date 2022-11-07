import discord
from discord.ext import commands


class MyHelp(commands.HelpCommand):

    def get_command_signature(self, command):
        return '%s %s' % (command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        embed.add_field(name='IMPORTANT INFORMATION',
                        value='Most of the commands moved to slash commands. Simply type ´/´ and discord will show you '
                              'available commands',
                        inline=False)
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title='Help for ' + self.get_command_signature(command))
        embed.add_field(name="What does it do???", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command

        help_command = MyHelp()
        help_command.cog = self
        bot.help_command = help_command

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
    print('Help loaded')
