from PIL import Image, ImageDraw, ImageFont

from Discord_Bot_Laggrif.Assets import res_folder
from Discord_Bot_Laggrif.LoL.LoLAPI import LoLData
from Discord_Bot_Laggrif.LoL.LoLMatch import Match

res = res_folder()

FONT = res + 'fonts/Friz Quadrata Std Medium.otf'

WIDTH = 1920
HEIGHT = 1080

ICON_SIZE = 240

MARGIN = 5

STATS_MARGIN = 40


def paste_image(path, coords, size, img, mask=True):
    with Image.open(path, 'r') as icon:
        icon = icon.resize(size)
        img.paste(icon, coords, mask=icon if mask else None)


def AMH_picture(match: Match, lolData: LoLData):

    with Image.open(res + 'images/lol/base_history.png') as img:
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

        # ---------------------------------- Champ ---------------------------------------------------------------------

        # champ icon
        x = WIDTH - MARGIN - ICON_SIZE
        y = MARGIN
        draw.rectangle((x - 1, y - 1, x + ICON_SIZE, y + ICON_SIZE))
        lolData.get_champ_icon(match.champion())
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

        # champion level
        font = ImageFont.truetype(FONT, 40)
        x1 = champ_icon_box[0] + MARGIN
        x2 = x1 + 60
        y2 = champ_icon_box[3] - MARGIN
        y1 = y2 - 60
        level = str(match.level())
        size = draw.textbbox((0, 0), level, font)
        x = x1 + (x2 - x1) / 2 - size[2] / 2
        y = y1 + (y2 - y1) / 2 - size[3] / 2
        draw.ellipse((x1, y1, x2, y2), fill=(10, 10, 10, 255), outline=(255, 220, 0, 255))
        draw.text((x, y), level, fill=(200, 200, 5, 255), font=font)
        champion_level_box = [x1, y1, x2, y2]

        # ------------------------------------------- scores and objectives --------------------------------------------

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

        # ----------------------- Items --------------------------------------------------------------------------------

        # items icons
        items = match.items()
        x = 70
        y = int(champion_box[3] + 30)
        for i in range(7):
            draw.rectangle((i * 97 + 70 - 1, y - 1, (i + 1) * 97 + 70 - 1, y + 96),
                           outline=(200, 200, 200, 255),
                           fill=(0, 0, 0, 90))
            if items[i] != '0':
                lolData.get_item_icon(items[i])
                paste_image(res + f'images/lol/Items_icons/{lolData.current_ddragon_version}/{items[i]}.png',
                            (i * 97 + x, y),
                            (96, 96),
                            img,
                            False)
        items_box = [x, y, x + 7 * 97, y + 97]

        # gold earned
        font = ImageFont.truetype(FONT, 30)
        earned = str(match.gold_earned()) + ' Gold earned'
        gold_earned_size = draw.textbbox((0, 0), earned, font)
        x = items_box[2] + 50
        y = items_box[1] + MARGIN
        draw.text((x, y), earned, fill=(255, 215, 0, 255), font=font)
        gold_earned_box = draw.textbbox((x, y), earned, font)

        # gold spent
        font = ImageFont.truetype(FONT, 30)
        spent = str(match.gold_spent()) + ' Gold spent'
        x = gold_earned_box[0]
        y = items_box[3] - gold_earned_size[3] - MARGIN
        draw.text((x, y), spent, fill=(255, 215, 0, 255), font=font)
        gold_spent_box = draw.textbbox((x, y), spent, font)

        # ----------------------------- summoner spells ----------------------------------------------------------------
        # summoner spells
        sums = match.summoners()
        m = max(gold_spent_box[2], gold_earned_box[2])
        x = int((WIDTH - m) / 2 + m - 97)
        y = items_box[1]
        for i in range(2):
            draw.rectangle((x + 97 * i - 1, y - 1, x + 97 * i + 97 - 1, y + 97),
                           outline=(200, 200, 200, 255),
                           fill=(0, 0, 0, 90))
            lolData.get_sum_icon(sums[i])
            paste_image(res + f'images/lol/Summoner_spells_icons/{lolData.current_ddragon_version}/{sums[i]}.png',
                        (i * 97 + x, y),
                        (96, 96),
                        img,
                        False)
        sums_box = [x, y, x + 2 * 97, y + 97]

        # ------------------------------ damages dealt -----------------------------------------------------------------

        #                           -----static text----

        # total damages (global)
        font = ImageFont.truetype(FONT, 30)
        damages = 'Total damages dealt'
        x = 30
        y = HEIGHT - 100
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        total_damages_text_box = draw.textbbox((x, y), damages, font=font)

        # damages to objectives
        font = ImageFont.truetype(FONT, 30)
        damages = 'Damages to objectives'
        y = total_damages_text_box[1] - STATS_MARGIN
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        objectives_damages_text_box = draw.textbbox((x, y), damages, font=font)

        # damages to towers
        font = ImageFont.truetype(FONT, 30)
        damages = 'Damages to towers'
        y = objectives_damages_text_box[1] - STATS_MARGIN
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        tower_damages_text_box = draw.textbbox((x, y), damages, font=font)

        # true damages dealt
        font = ImageFont.truetype(FONT, 30)
        damages = 'True damages dealt'
        y = tower_damages_text_box[1] - STATS_MARGIN
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        true_damages_champ_text_box = draw.textbbox((x, y), damages, font=font)

        # magic damages dealt
        font = ImageFont.truetype(FONT, 30)
        damages = 'Magic damages dealt'
        y = true_damages_champ_text_box[1] - STATS_MARGIN
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        magic_damages_champ_text_box = draw.textbbox((x, y), damages, font=font)

        # physic damages dealt
        font = ImageFont.truetype(FONT, 30)
        damages = 'Physic damages dealt'
        y = magic_damages_champ_text_box[1] - STATS_MARGIN
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        physic_damages_champ_text_box = draw.textbbox((x, y), damages, font=font)

        # total damages dealt (champ)
        font = ImageFont.truetype(FONT, 30)
        damages = 'Damages to champions'
        y = physic_damages_champ_text_box[1] - STATS_MARGIN
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        damages_champ_text_box = draw.textbbox((x, y), damages, font=font)

        # title
        font = ImageFont.truetype(FONT, 40)
        text = 'Offensive Statistics'
        y = damages_champ_text_box[3] - 80
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        title_offense_box = draw.textbbox((x, y), text, font=font)

        #                       ------statistics text-----

        # total damages dealt (champ)
        font = ImageFont.truetype(FONT, 30)
        text = f'{match.damage_dealt_champ():,d}'.replace(',', ' ')
        x = damages_champ_text_box[2] + 100
        y = damages_champ_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        damages_champ_box = draw.textbbox((x, y), text, font=font)

        # physic damages dealt
        font = ImageFont.truetype(FONT, 30)
        text = f'{match.physic_damages_champ():,d}'.replace(',', ' ')
        y = physic_damages_champ_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        physic_damages_champ_box = draw.textbbox((x, y), text, font=font)

        # magic damages dealt
        font = ImageFont.truetype(FONT, 30)
        damages = f'{match.magic_damages_champ():,d}'.replace(',', ' ')
        y = magic_damages_champ_text_box[1]
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        magic_damages_champ_box = draw.textbbox((x, y), text, font=font)

        # true damages dealt
        font = ImageFont.truetype(FONT, 30)
        damages = f'{match.true_damages_champ():,d}'.replace(',', ' ')
        y = true_damages_champ_text_box[1]
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        true_damages_champ_box = draw.textbbox((x, y), text, font=font)

        # damages to towers
        font = ImageFont.truetype(FONT, 30)
        damages = f'{match.damage_to_buildings():,d}'.replace(',', ' ')
        y = tower_damages_text_box[1]
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        tower_damages_box = draw.textbbox((x, y), text, font=font)

        # damages to objectives
        font = ImageFont.truetype(FONT, 30)
        damages = f'{match.damage_to_objectives():,d}'.replace(',', ' ')
        y = objectives_damages_text_box[1]
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        objectives_damages_box = draw.textbbox((x, y), text, font=font)

        # total damages (global)
        font = ImageFont.truetype(FONT, 30)
        damages = f'{match.total_damages():,d}'.replace(',', ' ')
        y = total_damages_text_box[1]
        draw.text((x, y), damages, fill=(200, 200, 200, 255), font=font)
        total_damages_box = draw.textbbox((x, y), text, font=font)

        # ------------------------------------------ defensive stats ---------------------------------------------------

        # defines size of box containing defensive stats
        width = WIDTH / 2
        defense_box = [width - 225, 0, width + 225, 0]

        #                   -------------static text--------------
        # title
        font = ImageFont.truetype(FONT, 40)
        text = 'Defensive Statistics'
        x = WIDTH / 2 - draw.textlength(text, font) / 2
        y = title_offense_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        title_defense_box = draw.textbbox((x, y), text, font=font)

        # damages taken
        font = ImageFont.truetype(FONT, 30)
        text = 'Damages taken'
        x = defense_box[0]
        y = title_defense_box[1] + 80
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        damages_taken_text_box = draw.textbbox((x, y), text, font=font)

        # physic damages taken
        text = 'Physic damages taken'
        y = damages_taken_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        physic_damages_taken_text_box = draw.textbbox((x, y), text, font=font)

        # magic damages taken
        text = 'Magic damages taken'
        y = physic_damages_taken_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        magic_damages_taken_text_box = draw.textbbox((x, y), text, font=font)


        # true damages taken
        text = 'True damages taken'
        y = magic_damages_taken_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        true_damages_taken_text_box = draw.textbbox((x, y), text, font=font)

        # damages mitigated
        text = 'Damages mitigated'
        y = true_damages_taken_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        damages_mitigated_text_box = draw.textbbox((x, y), text, font=font)

        # self-healing
        text = 'Self healing'
        y = damages_mitigated_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        self_healing_text_box = draw.textbbox((x, y), text, font=font)

        # cc taken
        text = 'CC taken'
        y = self_healing_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        cc_taken_text_box = draw.textbbox((x, y), text, font=font)

        #                    ------------------statistics text---------------
        # damages taken
        font = ImageFont.truetype(FONT, 30)
        text = f'{match.damage_taken():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = damages_taken_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        damages_taken_box = draw.textbbox((x, y), text, font=font)

        # physic damages taken
        text = f'{match.physic_damage_taken():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = physic_damages_taken_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        physic_damages_taken_box = draw.textbbox((x, y), text, font=font)

        # magic damages taken
        text = f'{match.magic_damage_taken():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = magic_damages_taken_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        magic_damages_taken_box = draw.textbbox((x, y), text, font=font)

        # true damages taken
        text = f'{match.true_damage_taken():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = true_damages_taken_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        true_damages_taken_box = draw.textbbox((x, y), text, font=font)

        # damages mitigated
        text = f'{match.damage_mitigated():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = damages_mitigated_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        mitigated_damages_box = draw.textbbox((x, y), text, font=font)

        # self-healing
        text = f'{match.heal_self():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = self_healing_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        self_healing_box = draw.textbbox((x, y), text, font=font)

        # cc taken
        text = f'{match.cc_taken():,d}'.replace(',', ' ')
        x = defense_box[2] - draw.textlength(text, font)
        y = cc_taken_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        cc_taken_box = draw.textbbox((x, y), text, font=font)

        # --------------------------- Utility stats --------------------------------------------------------------------

        #                    -------------- static text ------------------------
        # utility box
        utility_box = [WIDTH - 400, 0, WIDTH - 30, 0]

        # title
        font = ImageFont.truetype(FONT, 40)
        text = 'Utility Statistics'
        x = utility_box[2] - draw.textlength(text, font)
        y = title_offense_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        title_utility_box = draw.textbbox((x, y), text, font=font)

        # cc done
        font = ImageFont.truetype(FONT, 30)
        text = 'CC done'
        x = utility_box[0]
        y = title_utility_box[1] + 80
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        cc_done_text_box = draw.textbbox((x, y), text, font=font)

        # shield to allies
        text = 'Shields on allies'
        y = cc_done_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        shield_ally_text_box = draw.textbbox((x, y), text, font=font)

        # heals on allies
        text = 'Heals on allies'
        y = shield_ally_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        heals_ally_text_box = draw.textbbox((x, y), text, font=font)

        # vision score
        text = 'Vision score'
        y = heals_ally_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        vision_score_text_box = draw.textbbox((x, y), text, font=font)

        # time spent dead
        text = 'Time spent dead'
        y = vision_score_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        time_dead_text_box = draw.textbbox((x, y), text, font=font)

        # max time spent alive
        text = 'Max time spent alive'
        y = time_dead_text_box[1] + STATS_MARGIN
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        time_alive_text_box = draw.textbbox((x, y), text, font=font)

        #               ----------------- statistics text -----------------------
        # cc done
        text = f'{match.cc_given():,d}'.replace(',', ' ')
        x = utility_box[2] - draw.textlength(text, font)
        y = cc_done_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        cc_done_box = draw.textbbox((x, y), text, font=font)

        # shield to allies
        text = f'{match.shield_other():,d}'.replace(',', ' ')
        x = utility_box[2] - draw.textlength(text, font)
        y = shield_ally_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        shield_ally_box = draw.textbbox((x, y), text, font=font)

        # heals on allies
        text = f'{match.heal_others():,d}'.replace(',', ' ')
        x = utility_box[2] - draw.textlength(text, font)
        y = heals_ally_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        heals_ally_box = draw.textbbox((x, y), text, font=font)

        # vision score
        text = f'{match.vision_score():,d}'.replace(',', ' ')
        x = utility_box[2] - draw.textlength(text, font)
        y = vision_score_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        vision_score_box = draw.textbbox((x, y), text, font=font)

        # time spent dead
        text = match.time_dead()
        x = utility_box[2] - draw.textlength(text, font)
        y = time_dead_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        time_dead_box = draw.textbbox((x, y), text, font=font)

        # max time spent alive
        text = match.longest_living()
        x = utility_box[2] - draw.textlength(text, font)
        y = time_alive_text_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        time_alive_box = draw.textbbox((x, y), text, font=font)

        # ------------------------------ KDA ---------------------------------------------------------------------------
        # title
        font = ImageFont.truetype(FONT, 40)
        text = 'KDA: '
        x = 30
        y = title_offense_box[1] - int((title_offense_box[1] - items_box[3]) / 3)
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        kda_box = draw.textbbox((x, y), text, font=font)

        # k/d/a
        text = f'{match.kills()}/{match.deaths()}/{match.assists()}'
        x = kda_box[2] + 10
        y = kda_box[1]
        draw.text((x, y), text, fill=(200, 200, 200, 255), font=font)
        kda_text_box = draw.textbbox((x, y), text, font=font)

        text = '(%.2f)' % match.kda()
        x = kda_text_box[2] + 10
        y = kda_box[1]
        color = (10, 210, 5, 255) if match.kda() >= 1 else (255, 70, 0, 220)
        draw.text((x, y), text, fill=color, font=font)
        tb = draw.textbbox((x, y), text, font=font)
        kda_text_box = [*kda_text_box[0:2], *tb[2:-1]]
        print(kda_text_box)

        return img
