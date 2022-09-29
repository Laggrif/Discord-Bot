# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import division
import time
import psutil
import socket

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from subprocess import PIPE, Popen

# Raspberry Pi pin configuration:
RST = None  # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

try:
    # Initialize library.
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height - padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0

    # Load default font.
    font = ImageFont.load_default()
except:
    print('error loading display or something')


# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index(bytes('=', 'utf-8')) + 1:output.rindex(bytes("'", 'utf-8'))])


def screensaver(display, choice):
    if choice in [0, 2, 4]:
        for i in range(0, 128, 16):
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.line((i, 0, i, height), fill=255)
            display.image(image)
            display.display()
    if choice in [1, 3, 5]:
        for i in range(127, 0, -16):
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.line((i, 0, i, height), fill=255)
            display.image(image)
            display.display()
    display.clear()
    display.display()


def stats(display, cnt):

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    delay = 300
    if cnt % delay in [0, 1, 2, 3]:
        screensaver(display, cnt % delay)
        return

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    BRIGHTNESS = 1
    draw.text((x, top), 'CPU Load: ' + str(psutil.cpu_percent()) + ' %', font=font, fill=BRIGHTNESS)
    draw.text((x, top + 11), 'CPU Usage: ' + str(psutil.cpu_freq().current / 1000), font=font, fill=BRIGHTNESS)
    draw.text((x, top + 22), 'CPU Temp: ' + str(get_cpu_temperature()) + '°', font=font, fill=BRIGHTNESS)
    draw.text((x, top + 33), "Mem: {:0.0f}/{:0.0f} Mb".format(ram.used / 2 ** 20, ram.total / 2 ** 20),
              font=font,
              fill=BRIGHTNESS)
    draw.text((x, top + 42), "({:0.0f} %)".format(ram.percent), font=font, fill=BRIGHTNESS)
    draw.text((x, top + 53),
              "Disk:{:0.0f}/{:0.0f}Go({}%)".format(disk.used / 2 ** 30, disk.total / 2 ** 30, disk.percent),
              font=font, fill=BRIGHTNESS)

    # Display image.
    display.image(image)
    display.display()


async def main():
    cnt = 0
    while True:
        stats(cnt)
