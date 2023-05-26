import textwrap

import adafruit_ssd1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from discord.ext import tasks

from Assets import res_folder
from cogs.Checks import *

# For OLED display support
try:
    from Stats import stats
    from Clock import clock

    import board
except Exception as e:
    print("Board is not recognised or display is not connected")


res = res_folder()
timer = 0

stats_cnt = 0
clock_cnt = 0


def init_display():
    try:
        global draw
        global font
        global bold
        global width
        global height
        global image
        global disp
        disp = adafruit_ssd1306.SSD1306_I2C(width=128, height=64, i2c=board.I2C())
        disp.fill(0)
        disp.show()
        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(res + '/fonts/arial_bold.ttf')
        bold = ImageFont.load_default()
        return disp, 'Display successfully enabled'
    except Exception as e:
        print(e)
        return None, 'Unable to enable display'


async def display_logo(display):
    image = Image.open(res + '/images/discord_logo.png')
    image = image.convert('1')
    display.clear()
    display.image(image)
    display.display()
    asyncio.create_task(display_reset_timer(display))


async def display_reset_timer(display):
    global timer
    timer += 1
    await asyncio.sleep(10)
    timer -= 1
    if timer == 0:
        display.clear()
        display.display()


class Display(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.disp = None
        self.modes = ["Statistics", "Notifications", "Clock"]
        self.mode = 2

    @commands.Cog.listener()
    async def on_ready(self):
        self.disp, msg = init_display()
        print(msg)
        if self.disp is not None:
            await display_logo(self.disp)
            # await asyncio.sleep(10)
            self.show_clock.start()

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id != 915542873309597727 and self.mode == 1 and self.disp is not None:
            image = Image.new('1', (width, height))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((0, -1), msg.author.name, fill=1, font=bold)
            offset = 6
            for line in textwrap.wrap(msg.content, int(128 / bold.getsize("w")[0])):
                draw.text((0, 4 + offset), line, font=font, fill=1)
                offset += font.getsize(line)[1]
            disp.fill(0)
            disp.image(image)
            disp.show()
            asyncio.create_task(display_reset_timer(self.disp))

    @tasks.loop(seconds=0.5)
    async def show_stats(self):
        global stats_cnt
        global timer
        timer = 0
        if self.disp is not None:
            stats(self.disp, stats_cnt)
            stats_cnt += 1

    @tasks.loop(seconds=1)
    async def show_clock(self):
        global clock_cnt
        global timer
        timer = 0
        if self.disp is not None:
            clock(self.disp, clock_cnt)
            clock_cnt += 1

    @commands.command(help='Active ou désactive l\'affichage', aliases=['display'])
    @Checks.is_owner()
    async def toggle_display(self, ctx):
        if self.disp is not None:
            self.disp.clear()
            self.disp.display()
            self.show_stats.stop()
            self.show_clock.stop()
            self.disp = None
            await ctx.send('Display disabled')
            return
        self.disp, msg = init_display()
        if self.disp is not None:
            try:
                if self.mode == 0:
                    self.show_stats.start()
                if self.mode == 2:
                    self.show_clock.start()
            except:
                pass
        await ctx.send(msg)

    @commands.command(help='Passe du mode statistiques au mode notifications et inversement', aliases=['switch'])
    @Checks.is_owner()
    async def switch_mode(self, ctx):
        self.mode = (self.mode + 1) % len(self.modes)
        if self.mode == 0:
            self.show_clock.stop()
            self.show_stats.stop()
            if self.disp is not None:
                self.disp.clear()
                self.disp.display()
            self.show_stats.start()

        elif self.mode == 1:
            self.show_clock.stop()
            self.show_stats.stop()
            if self.disp is not None:
                self.disp.clear()
                self.disp.display()

        elif self.mode == 2:
            self.show_stats.stop()
            self.show_clock.stop()
            if self.disp is not None:
                self.disp.clear()
                self.disp.display()
            self.show_clock.start()

        else:
            await ctx.send('An error occurred while changing mode')
            return
        await ctx.send('{0} mode'.format(self.modes[self.mode]))

    @commands.Cog.listener()
    async def on_cog_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(Display(bot))
    print('Display loaded')
