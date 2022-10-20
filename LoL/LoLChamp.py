from LoL import LoLAPI
from LoL.LoLAPI import LoLData


class Champ:
    def __new__(cls, champion, version=None, language=None):
        if LoLAPI.check_language(language) == 400 or LoLAPI.check_version(version) == 400:
            del cls
            print('no')
            return None

        return super().__new__(cls)

    def __init__(self, champion: str, version=None, language=None):
        self.lolData = LoLData()
        self.champion = champion
        self.version = self.lolData.current_ddragon_version if version is None else version
        self.language = language
        self.champ = self.lolData.get_champ_infos(champion, version, language)
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


