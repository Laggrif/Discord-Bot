from PIL import Image, ImageDraw, ImageFont

import Assets
from LoL.LoLAPI import LoLData
from LoL.LoLChamp import Champ

data = Assets.assets() + 'League of Legends/Data/'
images = Assets.assets() + 'images/lol/'

FONT = Assets.assets() + 'fonts/Friz Quadrata Std Medium.otf'

WIDTH = 1080
HEIGHT = 1920


def paste_image(path, coords, size, img, mask=True):
    with Image.open(path, 'r') as icon:
        icon = icon.resize(size)
        img.paste(icon, coords, mask=icon if mask else None)


def ChI(lolData: LoLData, champ: Champ):
    with Image.open(images + 'base_champ.png') as img:
        draw = ImageDraw.Draw(img, 'RGBA')

        draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), fill=(255, 0, 0, 255), outline=(255, 255, 255, 255))

        draw.text((5, 5), champ.champ_title(), font=ImageFont.truetype(FONT, 30))

        lolData.get_champ_icon(champ.champion, champ.version)
        paste_image(images + f'Champions_icons/{champ.version}/{champ.champion}.png', (400, 400), (300, 300), img, mask=False)

        img.show()
