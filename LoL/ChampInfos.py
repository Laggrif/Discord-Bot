from PIL import Image, ImageDraw

import Assets
from LoLAPI import LoLData

data = Assets.assets() + 'League of Legends/Data/'
images = Assets.assets() + 'images/lol/'

FONT = Assets.assets() + 'fonts/Friz Quadrata Std Medium.otf'

WIDTH = 1080
HEIGHT = 1920


def ChI(lolData: LoLData):
    with Image.open(images) as img:
        draw = ImageDraw.Draw(img, 'RGBA')

        draw.text(lolData)
