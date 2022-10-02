from PIL import Image, ImageDraw, ImageFont

import Assets
from LoLAPI import LoLData
from LoLMatch import Match


def AMH_picture(match: Match, lolData: LoLData):
    res = Assets.assets()

    FONT = res + 'fonts/Friz Quadrata Std Medium.otf'

    WIDTH = 1920
    HEIGHT = 1080

    ICON_SIZE = 240

    MARGIN = 5

    with Image.open(res + 'images/lol/base.png') as img:
        draw = ImageDraw.Draw(img, 'RGBA')

        # win
        font = ImageFont.truetype(FONT, 50)
        win = 'Victory' if match.win() else 'Defeat'
        x = MARGIN
        y = MARGIN
        draw.text((x, y), win, fill=(10, 210, 5, 255),
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
        with Image.open(res + f'images/lol/Champions_icons/{lolData.current_ddragon_version}/{match.champion()}.png', 'r') as icon:
            icon = icon.resize((240, 240))
            img.paste(icon, (x, y))
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
        draw.text((x_ally, y), ally, fill=(255, 5, 5, 255), font=font)
        draw.text((x_enemy, y), enemy, fill=(160, 5, 255, 255), font=font)
        ally_box = draw.textbbox((x_ally, y), ally, font)
        enemy_box = draw.textbbox((x_enemy, y), enemy, font)
        teams_score_box = [ally_box[0], min(ally_box[1], enemy_box[1]), enemy_box[2], max(ally_box[3], enemy_box[3])]

        # towers destroyed

        return img
