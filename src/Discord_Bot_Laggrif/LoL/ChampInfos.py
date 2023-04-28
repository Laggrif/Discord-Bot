from PIL import Image, ImageDraw, ImageFont

from Assets import res_folder
from ColorAverage import *
from LoL.LoLAPI import LoLData
from LoL.LoLChamp import Champ

data = res_folder() + 'League of Legends/Data/'
images = res_folder() + 'images/lol/'

FONT60 = ImageFont.truetype(res_folder() + 'fonts/Friz Quadrata Std Medium.otf', 60)
FONT40 = FONT60.font_variant(size=40)
FONT100 = FONT60.font_variant(size=100)

WIDTH = 2120
HEIGHT = 3769

XS_MARGIN = 10
S_MARGIN = 20
M_MARGIN = 40
L_MARGIN = 60
XL_MARGIN = 80
XXL_MARGIN = 160


def paste_image(path, coords, size, img, mask=True):
    with Image.open(path, 'r') as icon:
        icon = icon.resize(size)
        img.paste(icon, coords, mask=icon if mask else None)


def break_text(text: str, font, draw: ImageDraw.ImageDraw, max_width):
    words = text.split(' ')
    new_text = ''
    tmp = ''
    for word in words:
        word = ' ' + word
        tmp += word
        if draw.textlength(tmp, font) > max_width:
            tmp = tmp.removesuffix(word)
            new_text += tmp
            new_text += '\n'
            tmp = word.removeprefix(' ')
    new_text += tmp
    return new_text


def ChI_image(lolData: LoLData, champ: Champ):
    global HEIGHT
    version = champ.version
    language = champ.language
    champion = champ.champ_id()

    with Image.open(images + 'base_champ.png') as img:
        draw = ImageDraw.Draw(img, 'RGBA')

        lolData.get_champ_icon(champion, version)
        champ_icon_path = images + f'Champions_icons/{version}/{champion}.png'

        lolData.get_champ_splashart(champion, version)
        champ_splashart_path = images + f'Champions_splasharts/{version}/{champion}/0.png'

        lolData.get_champ_passive_icon(champion, version)
        passive_icon = champ.passive_image()
        champ_passive_path = images + f'Champions_passive/{version}/{champion}/{passive_icon}'

        bg = mix_color(champ_icon_path)
        draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), fill=bg, outline=bg)

        # -------------------- champion square icon ---------------------
        width = 300
        height = 300
        paste_image(champ_icon_path,
                    (WIDTH - XS_MARGIN - width, XS_MARGIN),
                    (width, height),
                    img,
                    mask=False)
        champ_icon_box = [WIDTH - XS_MARGIN - width, XS_MARGIN, WIDTH - XS_MARGIN, XS_MARGIN + height]

        # -------------------- champ name and title ---------------------
        txt = champ.champ_name() + ' ' + champ.champ_title()
        y = (champ_icon_box[3] - champ_icon_box[1]) / 2 + champ_icon_box[1]
        draw.text((S_MARGIN, int(y)), txt, font=FONT60)
        champ_name_box = draw.textbbox((S_MARGIN, S_MARGIN), txt, font=FONT60)

        # -------------------- lore ---------------------
        txt = break_text(champ.champ_lore(), FONT40, draw, WIDTH - 2 * L_MARGIN)
        coords = (L_MARGIN, champ_icon_box[3] + XL_MARGIN)
        lore_text_box = draw.multiline_textbbox(coords, txt, font=FONT40)
        draw.rectangle((lore_text_box[0] - M_MARGIN, lore_text_box[1] - M_MARGIN, lore_text_box[2] + M_MARGIN, lore_text_box[3] + M_MARGIN),
                       fill=(bg[0] - 10, bg[1] - 10, bg[2] - 10),
                       outline=(bg[0] + 20, bg[1] + 20, bg[2] + 20))
        draw.multiline_text(coords, txt, font=FONT40, spacing=XS_MARGIN)

        # -------------------- abilities ---------------------
        # passive
        paste_image(champ_passive_path, (XL_MARGIN, lore_text_box[3] + XXL_MARGIN), (200, 200), img, mask=False)

        # -------------------- base stats ---------------------
        stats_space = 30
        stats_start_y = lore_text_box[3] + M_MARGIN + L_MARGIN
        ad = str(champ.attack_damage())

        draw.text((XXL_MARGIN, stats_start_y), ad, font=FONT40)

        # -------------------- skins ---------------------------------
        ratio = 308.0 / 560.0
        skins = champ.champ_skins()
        ids = list(skins.keys())
        names = list(skins.values())
        num = len(skins)
        max_per_row = 5
        wi = WIDTH / max_per_row
        he = wi / ratio

        new_height = int(HEIGHT + int(num / max_per_row) * (he + 80))
        img = img.crop((0, 0, WIDTH, new_height))
        draw = ImageDraw.Draw(img, 'RGBA')
        draw.rectangle((0, HEIGHT, WIDTH, new_height), fill=bg, outline=bg)
        for i in range(num):
            id = ids[i]
            text = names[i].replace(champ.champ_name(), '')
            draw.text((int(wi * (i % max_per_row) + (wi - draw.textlength(text, FONT40)) / 2.0), int(HEIGHT - 60.0 + 20.0 + (he + 80.0 + M_MARGIN) * int(i / max_per_row))), text, font=FONT40)
            lolData.get_champ_loading(champion, version, id)
            paste_image(images + f'Champions_loading/{version}/{champion}/{id}.png',
                        (int(wi * (i % max_per_row)), int(HEIGHT  + (he + 80.0 + M_MARGIN) * int(i / max_per_row))),
                        (int(wi), int(wi / ratio)),
                        img,
                        False)
        HEIGHT = new_height

        return img
