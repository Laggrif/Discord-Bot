import time
from datetime import datetime

import adafruit_ssd1306
import board
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from src.Discord_Bot_Laggrif.Assets import res_folder

res = res_folder()

disp = adafruit_ssd1306.SSD1306_I2C(width=128, height=64, i2c=board.I2C())

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 64
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

fontsize = 1

hour = '00 : 00'

font_t = ImageFont.truetype(res + '/fonts/arial_bold.ttf', fontsize)
while font_t.getsize(hour)[0] < image.size[0]:
    # iterate until the text size is just larger than the criteria
    fontsize += 1
    font_t = ImageFont.truetype(res + '/fonts/arial_bold.ttf', fontsize)

date = '00.00.0000'
fontsize = 1

font_d = ImageFont.truetype(res + '/fonts/arial_bold.ttf', fontsize)
while font_d.getsize(date)[0] < image.size[0]:
    # iterate until the text size is just larger than the criteria
    fontsize += 1
    font_d = ImageFont.truetype(res + '/fonts/arial_bold.ttf', fontsize)

font_d = ImageFont.truetype(res + '/fonts/arial_bold.ttf', fontsize - 1)

height_d = draw.textsize(date, font=font_d)[1]

positions = [(0, 0, 10, 10), (width - 10, 0, width, 10), (width - 10, height - 10, width, height), (0, height - 10, 10, height)]


def clock(display, cnt):

    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if cnt % 150 in [0, 1, 2, 3]:
        draw.rectangle(positions[cnt % 10], outline=1, fill=1)

    else:
        if cnt % 2 == 0:
            draw.text((0, 0), '{:02d} : {:02d}'.format(datetime.now().hour, datetime.now().minute), font=font_t, fill=255,
                      align='center')
        else:
            draw.text((0, 0), '{:02d}   {:02d}'.format(datetime.now().hour, datetime.now().minute), font=font_t, fill=255,
                      align='center')
        draw.text((0, 63 - height_d),
                  '{:02d}.{:02d}.{:04d}'.format(datetime.now().day, datetime.now().month, datetime.now().year),
                  font=font_d, fill=1, align='center')

    display.image(image)
    display.show()


async def main():
    while True:
        clock(disp)
        time.sleep(0.9)
