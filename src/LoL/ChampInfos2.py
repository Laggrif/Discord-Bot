from PIL import Image, ImageDraw, ImageFont

from Assets import res_folder
from ColorAverage import *
from LoL.LoLAPI import LoLData
from LoL.LoLChamp import Champ

data = res_folder() + 'League of Legends/Data/'
images = res_folder() + 'images/lol/'

FONT60 = ImageFont.truetype(res_folder() + 'fonts/Friz Quadrata Std Medium.otf', 60)
FONT40 = FONT60.font_variant(size=40)
FONT50 = FONT60.font_variant(size=50)
FONT80 = FONT60.font_variant(size=80)
FONT100 = FONT60.font_variant(size=100)

WIDTH = 2120

SPACING = 15
XS_MARGIN = 10
S_MARGIN = 20
M_MARGIN = 40
L_MARGIN = 60
XL_MARGIN = 80
XXL_MARGIN = 160

SPELL_IMG_SIZE = 150
STATS_IMG_SIZE = 30
CHAMP_ICON_SIZE = 300


def paste_image(path, coords, size, img, mask=True):
    with Image.open(path, 'r') as icon:
        icon = icon.resize(size)
        img.paste(icon, coords, mask=icon if mask else None)


def break_text(txt: str, font, draw: ImageDraw.ImageDraw, max_width):
    words = txt.split(' ')
    new_text = ''
    tmp = ''
    for word in words:
        if word == '\n':
            tmp += word
            new_text += tmp
            tmp = ''
        else:
            word = word + ' '
            tmp += word
            if draw.textlength(tmp, font) > max_width:
                tmp = tmp.removesuffix(word)
                new_text += tmp
                new_text += '\n'
                tmp = word.removeprefix(' ')
    new_text += tmp
    return new_text


def f_txt(txt: str):
    return txt.replace('<br>', ' \n ')


def text(draw, x, y, txt, maxWidth=None, font=FONT60, spacing=SPACING, format=False):
    if format:
        txt = f_txt(txt)

    if maxWidth is not None and draw.textbbox((0, 0), txt, font=font)[2] > maxWidth:
        txt = break_text(txt, font, draw, maxWidth)
        box = draw.multiline_textbbox((x, y), txt, font=font, spacing=spacing)
    else:
        box = draw.textbbox((x, y), txt, font=font)

    box += (box[2] - box[0], box[3] - box[1])
    return txt, box


def image(x, y, w, h):
    return x, y, x + w, y + h, w, h


def r_image(x, y, w, h):
    return x - w, y, x, y + h, w, h


def Champ_Infos_Image(lolData: LoLData, champ: Champ):
    version = champ.version
    language = champ.language
    champion = champ.champ_id()

    name_title = f'{champ.champ_name()} {champ.champ_title()}'

    with Image.open(images + 'base_champ.png') as img:
        draw = ImageDraw.Draw(img, 'RGBA')
        champ_icon = r_image(WIDTH - M_MARGIN, M_MARGIN, CHAMP_ICON_SIZE, CHAMP_ICON_SIZE)
        champ_name = text(draw, L_MARGIN, champ_icon[1] + champ_icon[5], name_title, font=FONT80)

        stats =
