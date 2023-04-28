from LoL.LoLAPI import LoLData


class Champ:
    def __new__(cls, lolData, champion, version=None, language=None):
        if lolData.check_language(language) == 400 \
                or lolData.check_version(version) == 400\
                or lolData.check_champion(champion, version) == 400:
            del cls
            print('no')
            return None
        return super().__new__(cls)

    def __init__(self, lolData: LoLData, champion: str, version=None, language=None):
        self.lolData = lolData
        self.champion = champion
        self.version = self.lolData.current_ddragon_version if version is None else version
        self.language = self.lolData.default_language if language is None else language
        self.champ = self.lolData.get_champ_infos(champion, version, language)
        if self.champ == 400:
            del self
            return
        self.champ_data = self.champ['data'][self.champ_id()]
        self.stats = self.champ_data['stats']

    def champ_id(self):
        return list(self.champ['data'].keys())[0]

    def champ_name(self):
        return self.champ_data['name']

    def champ_title(self):
        return self.champ_data['title']

    def resources(self):
        return self.champ_data['partype']

    def champ_lore(self):
        return self.champ_data['lore']

    def ally_tips(self):
        return self.champ_data['allytips']

    def enemy_tips(self):
        return self.champ_data['enemytips']

    def champ_skins(self):
        tmp = {}
        for skin in self.champ_data['skins']:
            tmp[skin['num']] = skin['name']
        return tmp

    # ------------stats----------------
    def armor(self):
        return self.stats['armor']

    def armor_growth(self):
        return self.stats['armorperlevel']

    def attack_damage(self):
        return self.stats['attackdamage']

    def attack_damage_growth(self):
        return self.stats['attackdamageperlevel']

    def attack_range(self):
        return self.stats['attackrange']

    def attack_speed(self):
        return self.stats['attackspeed']

    def attack_speed_growth(self):
        return self.stats['attackspeedperlevel']

    def crit(self):
        return self.stats['crit']

    def crit_growth(self):
        return self.stats['critperlevel']

    def hp(self):
        return self.stats['hp']

    def hp_growth(self):
        return self.stats['hpperlevel']

    def hp_regen(self):
        return self.stats['hpregen']

    def hp_regen_growth(self):
        return self.stats['hpregenperlevel']

    def move_speed(self):
        return self.stats['movespeed']

    def mp(self):
        return self.stats['mp']

    def mp_growth(self):
        return self.stats['mpperlevel']

    def mp_regen(self):
        return self.stats['mpregen']

    def mp_regen_growth(self):
        return self.stats['mpregenperlevel']

    def magic_resist(self):
        return self.stats['spellblock']

    def magic_resist_growth(self):
        return self.stats['spellblockperlevel']

    # -----------abilities------------
    def passive_description(self):
        return self.champ_data['passive']['description']

    def passive_image(self):
        return self.champ_data['passive']['image']['full']

    def passive_name(self):
        return self.champ_data['passive']['name']
