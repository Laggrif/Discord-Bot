from Discord_Bot_Laggrif.LoL.LoLAPI import LoLData


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
        self.champ_data = self.champ['data'][champion]

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


