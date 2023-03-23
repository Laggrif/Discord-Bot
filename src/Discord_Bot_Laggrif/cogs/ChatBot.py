import json
import os.path
from pathlib import Path

import discord
import requests
from discord import ButtonStyle, option
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.ui import Button, View

from Assets import res_folder

res = res_folder()

API_URL = 'https://api-inference.huggingface.co/models/Laggrif/'
MODEL_NAME = 'DialoGPT-medium-Luke'
huggingface_token = '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'

Path(res + 'settings').mkdir(parents=True, exist_ok=True)

path = res + 'settings/Active_Chatbot_Channels.json'


def fetch_channel_ids():
    if not os.path.isfile(path):
        with open(path, 'w') as f:
            f.write('{}')
    with open(path, 'r') as fp:
        ids = json.load(fp)
    return ids


class ChatBot(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.api_endpoint = API_URL + MODEL_NAME
        # retrieve the secret API token from the system environment
        # format the header in our request to Hugging Face
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }
        self.chat_channels = fetch_channel_ids()

    def query(self, payload):
        """
        make request to the Hugging Face model API
        """
        data = json.dumps(payload)
        response = requests.request('POST',
                                    self.api_endpoint,
                                    headers=self.request_headers,
                                    data=data)
        ret = json.loads(response.content.decode('utf-8'))
        return ret

    @tasks.loop(minutes=5)
    async def stay_awake(self):
        self.query({'inputs': {'text': 'Hello'}})

    @commands.Cog.listener()
    async def on_ready(self):
        # send a request to the model without caring about the response
        # just so that the model wakes up and starts loading
        self.query({'inputs': {'text': 'Hello!'}})
        # keeps the model awake
        self.stay_awake.start()

    @commands.Cog.listener()
    async def on_message(self, msg):
        """
        this function is called whenever the bot sees a message in a channel
        """
        # ignore the message if it comes from the bot itself
        channel_id = str(msg.channel.id)
        content = msg.content
        if channel_id in self.chat_channels and msg.author.id != 915542873309597727:
            prefix = self.chat_channels[channel_id]
            if content.startswith(prefix):

                # form query payload with the content of the message
                payload = {'inputs': {'text': content[len(prefix):]}}

                # while the bot is waiting on a response from the model
                # set the its status as typing for user-friendliness
                async with msg.channel.typing():
                    response = self.query(payload)
                bot_response = response.get('generated_text', None)

                # we may get ill-formed response if the model hasn't fully loaded
                # or has timed out
                if not bot_response:
                    if 'error' in response:
                        bot_response = '`Error: {}`'.format(response['error'])
                    else:
                        bot_response = 'Hmm... something is not right.'

                # send the model's response to the Discord channel
                await msg.channel.send(bot_response)

    @commands.slash_command(description='Enables the chatBot in the specified channel or the current channel')
    @option('channel',
            default=None,
            description='Enter name of channel',
            type=str,
            required=False)
    async def add_chat_channel(self, ctx, channel):

        if channel is None:
            await self.add_chat_channel(ctx, ctx.channel.name)
            return

        await ctx.response.defer()

        chan = discord.utils.get(ctx.guild.channels, name=channel)
        if chan is None:
            await ctx.followup.send('Please enter a valid channel name')
            return

        channel_id = str(chan.id)
        data = fetch_channel_ids()
        if channel_id in data:
            await ctx.followup.send(f'Channel `{chan}` has already been added. You can change its '
                           'prefix with `chat_prefix`')
            return

        async def add_channel(prefix=""):
            with open(res + 'settings/Active_Chatbot_Channels.json', 'w+') as fp:
                data[channel_id] = prefix
                json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ': '))
            return True

        async def yes_callback(interaction: discord.Interaction):
            async with ctx.typing():
                await interaction.response.defer()
                if await add_channel(prefix="chat "):
                    await interaction.message.edit(content=f'Enabled ChatBot in `{chan}` with default prefix `chat `. '
                                                           f'To change or remove it use `chat_prefix`',
                                                   embed=None,
                                                   view=None)

        async def no_callback(interaction):
            async with ctx.typing():
                await interaction.response.defer()
                if await add_channel():
                    await interaction.message.edit(content=f'Enabled ChatBot in `{chan}` without prefix. To add one use '
                                                           f'`chat_prefix`',
                                                   embed=None,
                                                   view=None)

        async def cancel_callback(interaction):
            await interaction.response.defer()
            await interaction.message.edit(content='ChatBot haven\'t been enabled due to cancellation',
                                           embed=None,
                                           view=None)

        yes = Button(label='Yes', style=ButtonStyle.green)
        no = Button(label='No', style=ButtonStyle.red)
        cancel = Button(label='Cancel', style=ButtonStyle.gray)

        yes.callback = yes_callback
        no.callback = no_callback
        cancel.callback = cancel_callback

        view = View(yes, no, cancel)

        embed = discord.Embed(title='Enabling ChatBot')
        embed.add_field(name='Do you want to add a prefix to the Chatbot?', value='the prefix will only be applied to '
                                                                                  f'`{chan}`')

        await ctx.followup.send(embed=embed, view=view,)

    @commands.slash_command(description='Disables the chatBot in the specified channel or the current channel')
    @option('channel',
            default=None,
            description='Enter name of channel',
            type=str,
            required=False)
    async def remove_chat_channel(self, ctx, channel):
        data = fetch_channel_ids()

        if channel is None:
            await self.remove_chat_channel(ctx, ctx.channel.name)
            return

        chan = discord.utils.get(ctx.guild.channels, name=channel)
        if chan is None:
            await ctx.respond('Please enter a valid channel name')
            return

        channel_id = str(chan.id)
        if channel_id in data:
            del data[channel_id]
            with open(path, 'w')as fp:
                json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ': '))
        await ctx.respond(f'Disabled ChatBot in `{chan}`. To re-enable it use `add_chat_channel`')

    @commands.slash_command(description='Changes prefix of ChatBot in current channel. Leave blank to remove prefix')
    @option('prefix',
            autocomplete=['!', '$', '!c', '^', '?', '/', '&'],
            default=None,
            description='Enter a prefix',
            input_type=str,
            required=False)
    async def chat_prefix(self, ctx: Context, prefix):
        channel_id = str(ctx.channel.id)
        data = fetch_channel_ids()

        if channel_id in data:
            if prefix is None:
                await ctx.respond(f'Removed prefix of ChatBot in `{ctx.channel}`')
                data[channel_id] = ""
            else:
                await ctx.respond(f'Changed prefix of ChatBot in `{ctx.channel.name}` to `{prefix}`')
                data[channel_id] = prefix
            with open(res + 'settings/Active_Chatbot_Channels.json', 'w+') as fp:
                json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ': '))

        else:
            await ctx.respond(f'ChatBot is not enabled in `{ctx.channel}`. You can add it with `add_chat_channel`')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        if isinstance(error, (commands.CommandNotFound, commands.MissingRequiredArgument)):
            pass
        else:
            raise error


def setup(bot):
    bot.add_cog(ChatBot(bot))
    print('ChatBot loaded')
