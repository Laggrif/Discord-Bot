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
FONT100 = FONT60.font_variant(size=100)

WIDTH = 2120
HEIGHT = 3769

SPACING = 15
XS_MARGIN = 10
S_MARGIN = 20
M_MARGIN = 40
L_MARGIN = 60
XL_MARGIN = 80
XXL_MARGIN = 160

SPELL_IMG_SIZE = 150


def paste_image(path, coords, size, img, mask=True):
    with Image.open(path, 'r') as icon:
        icon = icon.resize(size)
        img.paste(icon, coords, mask=icon if mask else None)


def break_text(text: str, font, draw: ImageDraw.ImageDraw, max_width):
    words = text.split(' ')
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


def f_txt(text: str):
    return text.replace('<br>', ' \n ')


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
                    (WIDTH - M_MARGIN - width, M_MARGIN),
                    (width, height),
                    img,
                    mask=False)
        champ_icon_box = [WIDTH - M_MARGIN - width, M_MARGIN, WIDTH - M_MARGIN, M_MARGIN + height]

        # -------------------- champ name and title ---------------------
        txt = champ.champ_name() + ' ' + champ.champ_title()
        y = (champ_icon_box[3] - champ_icon_box[1]) / 2 + champ_icon_box[1]
        draw.text((S_MARGIN, int(y)), txt, font=FONT60.font_variant(size=80))
        champ_name_box = draw.textbbox((S_MARGIN, S_MARGIN), txt, font=FONT60.font_variant(size=80))

        # -------------------- lore ---------------------
        txt = break_text(f_txt(champ.champ_lore()), FONT50, draw, WIDTH - 2 * L_MARGIN)
        lore_text_box = draw.multiline_textbbox((0, 0), txt, font=FONT50, spacing=SPACING)
        lore_box = (M_MARGIN, champ_icon_box[3] + XL_MARGIN, WIDTH - M_MARGIN, champ_icon_box[3] + XL_MARGIN + lore_text_box[3] + 2 * S_MARGIN)
        draw.rectangle(lore_box,
                       fill=(bg[0] - 10, bg[1] - 10, bg[2] - 10),
                       outline=(bg[0] + 20, bg[1] + 20, bg[2] + 20))
        draw.multiline_text((lore_box[0] + S_MARGIN, lore_box[1] + S_MARGIN), txt, font=FONT50, spacing=SPACING)

        # -------------------- base stats ---------------------
        stats_start_y = lore_box[3] + L_MARGIN
        ad = str(champ.attack_damage())

        draw.text((XXL_MARGIN, stats_start_y), ad, font=FONT40)

        # -------------------- abilities ---------------------
        # fetch icons
        lolData.get_champ_passive_icon(champion, version)
        lolData.get_champ_ability_icon(champion, 'q', version)
        lolData.get_champ_ability_icon(champion, 'w', version)
        lolData.get_champ_ability_icon(champion, 'e', version)
        lolData.get_champ_ability_icon(champion, 'r', version)

        # passive
        passive_box = (lore_box[0], lore_box[3] + XXL_MARGIN, lore_box[2])
        passive_box = draw_ability(draw, 'passive', passive_box, champ, (bg[0] - 10, bg[1] - 10, bg[2] - 10), img)

        # q
        q_box = (passive_box[0], passive_box[3] + M_MARGIN, passive_box[2])
        q_box = draw_ability(draw, 'q', q_box, champ, (bg[0] - 10, bg[1] - 10, bg[2] - 10), img)

        # w
        w_box = (q_box[0], q_box[3] + M_MARGIN, q_box[2])
        w_box = draw_ability(draw, 'w', w_box, champ, (bg[0] - 10, bg[1] - 10, bg[2] - 10), img)

        # e
        e_box = (w_box[0], w_box[3] + M_MARGIN, w_box[2])
        e_box = draw_ability(draw, 'e', e_box, champ, (bg[0] - 10, bg[1] - 10, bg[2] - 10), img)

        # r
        r_box = (e_box[0], e_box[3] + M_MARGIN, e_box[2])
        draw_ability(draw, 'r', r_box, champ, (bg[0] - 10, bg[1] - 10, bg[2] - 10), img)

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


def draw_ability(draw: ImageDraw, ability: str, box: tuple[int, int, int], champ: Champ, color: tuple, img):
    """
    :param color: color of the background
    :param draw: the canvas to draw on
    :param ability: one of 'passive', 'q', 'w', 'e', 'r'
    :param box: x, y and width
    :param champ: a Champion object from LoLChamp.py
    draws the ability on the designed area of the canvas
    """

    desc = ''
    title = ''
    cd = ''
    letter = f'[{ability.upper()}]'
    match ability:
        case 'passive':
            letter = '[P]'
            desc = champ.passive_description()
            title = champ.passive_name()
            cd = ''
        case 'q':
            desc = champ.q_description()
            title = champ.q_name()
            cd = champ.q_cd()
        case 'w':
            desc = champ.w_description()
            title = champ.w_name()
            cd = champ.w_cd()
        case 'e':
            desc = champ.e_description()
            title = champ.e_name()
            cd = champ.e_cd()
        case 'r':
            desc = champ.r_description()
            title = champ.r_name()
            cd = champ.r_cd()

    desc = break_text(desc, FONT40, draw, box[2] - box[0] - M_MARGIN - 2 * S_MARGIN - SPELL_IMG_SIZE)

    letter_box = draw.multiline_textbbox((0, 0), letter, font=FONT50)

    cd_box = draw.textbbox((0, 0), cd, font=FONT50)

    title_box = draw.multiline_textbbox((0, 0), title, font=FONT50)

    img_box = (0, 0, SPELL_IMG_SIZE, SPELL_IMG_SIZE)

    desc_box = draw.multiline_textbbox((0, 0), desc, font=FONT40, spacing=SPACING)

    x_letter, y_letter = box[0] + S_MARGIN, box[1] + S_MARGIN

    x_img, y_img = x_letter, y_letter + M_MARGIN + letter_box[3]

    x_title, y_title = x_img + img_box[2] + M_MARGIN, y_letter

    x_desc, y_desc = x_title, y_title + L_MARGIN + title_box[3]

    x_cd, y_cd = box[2] - cd_box[2] - S_MARGIN, box[1] + S_MARGIN

    box = (box[0], box[1], box[2], max(y_desc + desc_box[3], y_img + img_box[3]) + S_MARGIN)

    draw.rectangle((box[0], box[1], box[2], box[3]), fill=color)

    draw.text((x_letter, y_letter), letter, font=FONT50)

    draw.text((x_title, y_title), title, font=FONT50)

    draw.text((x_cd, y_cd), cd, font=FONT50)

    draw.multiline_text((x_desc, y_desc), desc, font=FONT40, spacing=SPACING)

    ability = champ.spell_image(ability)
    paste_image(images + f'Champions_abilities/{champ.version}/{champ.champ_id()}/{ability}', (x_img, y_img), (SPELL_IMG_SIZE, SPELL_IMG_SIZE), img, mask=False)

    return box[0], box[1], box[2], box[3]

