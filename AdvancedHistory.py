from PIL import Image, ImageDraw, ImageFont

import Assets
from LoLAPI import LoLData
from LoLMatch import Match

res = Assets.assets()

FONT = res + 'fonts/Friz Quadrata Std Medium.otf'

WIDTH = 1920
HEIGHT = 1080

ICON_SIZE = 240

MARGIN = 5


def AMH_picture(match: Match, lolData: LoLData):

    with Image.open(res + 'images/lol/base.png') as img:
        draw = ImageDraw.Draw(img, 'RGBA')

        # win
        font = ImageFont.truetype(FONT, 50)
        win = 'Victory' if match.win() else 'Defeat'
        color = (10, 210, 5, 255) if match.win() else (255, 70, 0, 220)
        x = MARGIN
        y = MARGIN
        draw.text((x, y), win, fill=color,
                  font=font)
        win_box = draw.textbbox((x, y), win, font)

        # game mode + map
        font = ImageFont.truetype(FONT, 30)
        game_mode = match.game_mode()
        map = match.map()
        x = MARGIN
        y = win_box[3] + 40
        draw.text((x, y), map + ' ' + game_mode, fill=(200, 200, 200, 255), font=font)
        game_mode_box = draw.textbbox((x, y), map + game_mode, font)

        # time spent
        font = ImageFont.truetype(FONT, 30)
        time = match.game_duration_string()
        x = MARGIN
        y = game_mode_box[3] + 10
        draw.text((x, y), time, fill=(200, 200, 200, 255), font=font)
        time_spent_box = draw.textbbox((x, y), time, font)

        # date
        font = ImageFont.truetype(FONT, 30)
        date = match.date()
        x = WIDTH / 2 - draw.textlength(date, font) / 2
        y = MARGIN + draw.textbbox((0, 0), time, font)[3]
        draw.text((x, y), date, fill=(200, 200, 200, 255), font=font)
        date_spent_box = draw.textbbox((x, y), time, font)

        # champ icon
        x = WIDTH - MARGIN - ICON_SIZE
        y = MARGIN
        draw.rectangle((x - 1, y - 1, x + ICON_SIZE, y + ICON_SIZE))
        paste_image(res + f'images/lol/Champions_icons/{lolData.current_ddragon_version}/{match.champion()}.png',
                    (x, y), (240, 240), img, mask=False)
        champ_icon_box = (x, y, x + ICON_SIZE, y + ICON_SIZE)

        # champion
        font = ImageFont.truetype(FONT, 40)
        champion = match.champion()
        transform = match.transform()
        text = champion + transform
        x = (champ_icon_box[0] + champ_icon_box[2]) / 2 - draw.textlength(text, font) / 2
        y = champ_icon_box[3] + MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        champion_box = draw.textbbox((x, y), text, font)

        # Teams score
        font = ImageFont.truetype(FONT, 40)
        kills_ally = match.team_kills()
        deaths_ally = match.team_deaths()
        assists_ally = match.team_assists()
        kills_enemy = match.enemy_kills()
        deaths_enemy = match.enemy_deaths()
        assists_enemy = match.enemy_assists()
        ally = '/'.join(str(x) for x in [kills_ally, deaths_ally, assists_ally])
        enemy = '/'.join(str(x) for x in [kills_enemy, deaths_enemy, assists_enemy])
        x_ally = WIDTH / 2 - draw.textlength(ally, font) - 30
        x_enemy = WIDTH / 2 + 30
        y = game_mode_box[1]
        draw.text((x_ally, y), ally, fill=(160, 5, 255, 255), font=font)
        draw.text((x_enemy, y), enemy, fill=(255, 5, 5, 255), font=font)
        ally_box = draw.textbbox((x_ally, y), ally, font)
        enemy_box = draw.textbbox((x_enemy, y), enemy, font)
        teams_score_box = [ally_box[0], min(ally_box[1], enemy_box[1]), enemy_box[2], max(ally_box[3], enemy_box[3])]

        # size of box containing scores and objectives
        teams_box = [0, 0, 0, 0]

        # ally towers destroyed
        size = 40
        font = ImageFont.truetype(FONT, 40)
        tower_num_ally = str(match.team_turret_kills())
        size_text_ally = draw.textbbox((0, 0), tower_num_ally, font=font)
        x_icon_ally = int(teams_score_box[0] - 2 * size)
        y_icon_ally = int((teams_score_box[1] + teams_score_box[3]) / 2 - size - MARGIN)
        x_text_ally = x_icon_ally - size_text_ally[2] - 10
        y_text_ally = y_icon_ally + (size - size_text_ally[3]) / 2
        paste_image(res + 'images/lol/icon-tower.png', (x_icon_ally, y_icon_ally), (size, size), img)
        draw.text((x_text_ally, y_text_ally), tower_num_ally, fill=(160, 5, 255, 255), font=font)
        teams_box[0] = x_text_ally
        teams_box[1] = y_icon_ally

        # ally barons killed
        size = 40
        font = ImageFont.truetype(FONT, 40)
        tower_num_ally = str(match.team_baron_kills())
        size_text_ally = draw.textbbox((0, 0), tower_num_ally, font=font)
        x_icon_ally = int(teams_score_box[0] - 2 * size)
        y_icon_ally = int((teams_score_box[1] + teams_score_box[3]) / 2 + MARGIN)
        x_text_ally = x_icon_ally - size_text_ally[2] - 10
        y_text_ally = y_icon_ally + (size - size_text_ally[3]) / 2
        paste_image(res + 'images/lol/icon-baron.png', (x_icon_ally, y_icon_ally), (size, size), img)
        draw.text((x_text_ally, y_text_ally), tower_num_ally, fill=(160, 5, 255, 255), font=font)

        # enemy towers destroyed
        size = 40
        font = ImageFont.truetype(FONT, 40)
        tower_num_enemy = str(match.enemy_turret_kills())
        size_text_enemy = draw.textbbox((0, 0), tower_num_enemy, font=font)
        x_icon_enemy = int(teams_score_box[2] + size)
        y_icon_enemy = int((teams_score_box[1] + teams_score_box[3]) / 2 - size - MARGIN)
        x_text_enemy = x_icon_enemy + size + 10
        y_text_enemy = y_icon_enemy + (size - size_text_enemy[3]) / 2
        paste_image(res + 'images/lol/icon-tower-r.png', (x_icon_enemy, y_icon_enemy), (size, size), img)
        draw.text((x_text_enemy, y_text_enemy), tower_num_enemy, fill=(255, 5, 5, 255), font=font)

        # enemy barons killed
        size = 40
        font = ImageFont.truetype(FONT, 40)
        tower_num_enemy = str(match.enemy_baron_kills())
        size_text_enemy = draw.textbbox((0, 0), tower_num_enemy, font=font)
        x_icon_enemy = int(teams_score_box[2] + size)
        y_icon_enemy = int((teams_score_box[1] + teams_score_box[3]) / 2 + MARGIN)
        x_text_enemy = x_icon_enemy + size + 10
        y_text_enemy = y_icon_enemy + (size - size_text_enemy[3]) / 2
        paste_image(res + 'images/lol/icon-baron-r.png', (x_icon_enemy, y_icon_enemy), (size, size), img)
        draw.text((x_text_enemy, y_text_enemy), tower_num_enemy, fill=(255, 5, 5, 255), font=font)
        teams_box[2] = x_text_enemy + size_text_enemy[3]
        teams_box[3] = y_icon_enemy + size

        return img


def paste_image(path, coords, size, img, mask=True):
    with Image.open(path, 'r') as icon:
        icon = icon.resize(size)
        img.paste(icon, coords, mask=icon if mask else None)


"""
        # towers destroyed
        font = ImageFont.truetype(FONT, 40)
        tower_num_ally = int(match.team_turret_kills())
        ally_tower_path = res + 'images/lol/icon-tower.png'
        tower_num_enemy = int(match.enemy_turret_kills())
        enemy_tower_path = res + 'images/lol/icon-tower-r.png'
        show_icon_objectives(ally_tower_path, tower_num_ally, teams_score_box, (-1, -1), img)
        show_icon_objectives(enemy_tower_path, tower_num_enemy, teams_score_box, (1, -1), img)
"""

"""
def show_icon_objectives(path, num, box, pos, img):
    for i in range(num):
        anchor_x = box[0 if pos[0] == -1 else 2]
        coord = (int(anchor_x + pos[0] * 45 * (i + 1)), int((box[1] + box[3]) / 2 + pos[1] * 45))
        with Image.open(path, 'r') as icon:
            icon = icon.resize((40, 40))
            img.paste(icon, coord, mask=icon)
"""
