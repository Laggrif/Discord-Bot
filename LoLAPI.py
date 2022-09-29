import os.path

import requests
import json
from Assets import assets
from pathlib import Path

res = assets() + 'League of Legends/Data'

Path(res).mkdir(parents=True, exist_ok=True)

with open(assets() + 'settings/Tokens.json', 'r') as fp:
    tokens = json.load(fp)
API_Key = tokens['LoL']
url_token = "?api_key=" + API_Key


class LoLData:
    def __init__(self):
        self.default_language = "en_US"
        self.default_region = 'euw1'
        self.ddragon_versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json" + url_token)
        self.ddragon_versions_json = self.ddragon_versions.json()
        self.current_ddragon_version = self.ddragon_versions_json[0]
        self.champ_list = self.get_champ_list()

    def check_version_language(self, version, language):
        if version is None:
            version = self.current_ddragon_version
        if language is None:
            language = self.default_language
        return version, language

    def reload_api_key(self):
        with open(assets() + 'settings/Tokens.json', 'r') as fp:
            tokens = json.load(fp)
        global API_Key
        global url_token
        API_Key = tokens['LoL']
        url_token = "?api_key=" + API_Key

    def actualise(self):
        self.ddragon_versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json" + url_token)
        self.ddragon_versions_json = self.ddragon_versions.json()
        if self.current_ddragon_version != self.ddragon_versions_json[0]:
            self.current_ddragon_version = self.ddragon_versions_json[0]
            self.champ_list = self.get_champ_list()
            self.get_all_champs_infos()

    def get_champ_list(self, version=None, language=None):
        version, language = self.check_version_language(version, language)

        file_name = res + '/champ_list_{}_{}.json'.format(version, language)

        champ_list_json = requests.get(
            "https://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion.json".format(version,
                                                                                      language) + url_token)
        with open(file_name, 'w') as fb:
            json.dump(champ_list_json.json(), fb, sort_keys=True, indent=4, separators=(',', ': '))

        tmp_champ_list = []
        for champ in champ_list_json.json()['data']:
            tmp_champ_list.append(champ)
        return tmp_champ_list

    def get_champ_infos(self, champion, version=None, language=None):
        version, language = self.check_version_language(version, language)

        if champion not in self.champ_list:
            return 400

        champ = requests.get("https://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion/{}.json"
                             .format(version, language, champion) + url_token)
        Path(res + '/Champions/{}/{}'.format(version, language)).mkdir(parents=True, exist_ok=True)
        with open(res + '/Champions/{}/{}/{}.json'.format(version, language, champion), 'w') as fb:
            json.dump(champ.json(), fb, sort_keys=True, indent=4, separators=(',', ': '))
        return champ.json()

    def get_champ_icon(self, champion, version=None):
        if champion not in self.champ_list:
            return 400

        version, language = self.check_version_language(version, None)

        if not os.path.isfile(res + '/Champions_icons/{}/{}.png'.format(version, champion)):
            image = requests.get(
                'https://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png'.format(version, champion)).content
            Path(res + '/Champions_icons/{}'.format(version)).mkdir(parents=True, exist_ok=True)
            with open(res + '/Champions_icons/{}/{}.png'.format(version, champion), 'wb') as fb:
                fb.write(image)

    def get_all_champs_infos(self, version=None, language=None):
        version, language = self.check_version_language(version, language)

        for champ in self.get_champ_list(version=version, language=language):
            self.get_champ_infos(champ, version, language)

    def get_player_uuid(self, summoner, region=None):
        if region is None:
            region = self.default_region
        elif region == 'euw':
            region = 'euw1'
        elif region == 'br':
            region = 'br1'
        elif region == 'eun':
            region = 'eun1'
        elif region == 'jp':
            region = 'jp1'
        elif region == 'kr':
            region = 'kr'
        elif region == 'la':
            region = 'la1'
        elif region == 'na':
            region = 'na1'
        elif region == 'oc':
            region = 'oc1'
        elif region == 'tr':
            region = 'tr1'
        elif region == 'ru':
            region = 'ru1'
        else:
            return 400

        summoner = requests.get(
            'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format(region, summoner) + url_token)
        if summoner.status_code != 200:
            return 400
        return summoner.json()['puuid']

    def get_match_history(self, summoner_uuid, games_count=None, type=None):
        if games_count is None:
            games_count = 5

        if type is None:
            type = 'normal'

        history = requests.get(
            "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type={}&start=0&count={}&api_key={}"
            .format(summoner_uuid, type, games_count, API_Key))

        if history.status_code != 200:
            return history.status_code, None

        match_list = []
        for matchId in history.json():
            match_infos = requests.get(
                'https://europe.api.riotgames.com/lol/match/v5/matches/{}'.format(matchId) + url_token)
            match_list.append(match_infos.json())
        return 200, match_list



"""
ldt = LoLData()
with open(res + "/his_ex.json", 'w') as f:
    json.dump(ldt.get_match_history(ldt.get_player_uuid('Laggrif'), games_count=1)[1], f, sort_keys=True, indent=2)

"""

"""
Orianna = get_champ_infos('Orianna')

img = requests.get("https://ddragon.leagueoflegends.com/cdn/12.14.1/img/spell/{}".format(
    Orianna['data']['Orianna']['spells'][3]['image']['full']) + "?api_key=" + token)

with open(res + '/img.png', 'wb') as i:
    i.write(img.content)

img_pil = Image.open('img.png', 'r')
img_pil.show('')
"""
