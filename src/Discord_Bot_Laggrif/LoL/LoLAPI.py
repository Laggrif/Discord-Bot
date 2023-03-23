import json
import os.path
from pathlib import Path

import requests

from src.Discord_Bot_Laggrif.Assets import res_folder

res = res_folder() + 'League of Legends/Data'

Path(res).mkdir(parents=True, exist_ok=True)

with open(res_folder() + 'settings/Tokens.json', 'r') as fp:
    tokens = json.load(fp)
API_Key = tokens['LoL']
url_token = "?api_key=" + API_Key


def check_language(language):
    if language is None:
        return
    languages = requests.get('https://ddragon.leagueoflegends.com/cdn/languages.json')
    if language not in languages.json():
        print('bad language')
        return 400


def check_version(version):
    if version is None:
        return
    versions = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
    if version not in versions.json():
        print('bad version')
        return 400


class LoLData:
    def __init__(self):
        self.languages = requests.get('https://ddragon.leagueoflegends.com/cdn/languages.json').json()
        self.default_language = "en_US"
        self.default_region = 'euw1'
        self.ddragon_versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json" + url_token)
        self.ddragon_versions_json = self.ddragon_versions.json()
        self.current_ddragon_version = self.ddragon_versions_json[0]
        self.queues = self.get_queues()
        self.champ_list = self.get_champ_list()
        self.item_list = self.get_item_list()
        self.sums_list = self.get_sums_list()

    def check_version_language(self, version, language):
        if version is None:
            version = self.current_ddragon_version
        if language is None:
            language = self.default_language
        return version, language

    def check_language(self, language):
        if language is None:
            return
        if language not in self.languages:
            print('bad language')
            return 400

    def check_version(self, version):
        if version is None:
            return
        if version not in self.ddragon_versions_json:
            print('bad version')
            return 400

    def check_champion(self, champion, version):
        ch_l = self.get_champ_list(version)
        if champion not in ch_l:
            if champion not in ch_l.values():
                return 400
            else:
                return list(ch_l.keys())[list(ch_l.values()).index(champion)]
        return champion

    @staticmethod
    def reload_api_key():
        with open(res_folder() + 'settings/Tokens.json', 'r') as fp:
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
            self.item_list = self.get_item_list()
            self.sums_list = self.get_sums_list()
            self.queues = self.get_queues()
            self.get_all_champs_infos()

    @staticmethod
    def get_queues():
        queues = requests.get('https://static.developer.riotgames.com/docs/lol/queues.json')
        with open(res + '/queues.json', 'w') as fp:
            json.dump(queues.json(), fp, indent=4, separators=(',', ': '))

        return queues.json()

    def get_champ_list(self, version=None):
        version, language = self.check_version_language(version, None)

        file_name = res + '/champs_lists/champ_list_{}_{}.json'.format(version, language)

        champ_list_json = requests.get(
            "https://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion.json".format(version,
                                                                                      language) + url_token)
        Path(res + '/champs_lists').mkdir(parents=True, exist_ok=True)
        with open(file_name, 'w') as fb:
            json.dump(champ_list_json.json(), fb, sort_keys=True, indent=4, separators=(',', ': '))

        tmp_champ_list = {}
        for champ in champ_list_json.json()['data']:
            tmp_champ_list[champ] = champ_list_json.json()['data'][champ]['name']
        return tmp_champ_list

    def get_champ_infos(self, champion, version=None, language=None):
        version, language = self.check_version_language(version, language)

        champion = self.check_champion(champion, version)

        path = res + '/champions/{}/{}/{}.json'.format(version, language, champion)
        if not os.path.isfile(path):
            champ = requests.get("https://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion/{}.json"
                                 .format(version, language, champion) + url_token)
            if not champ.status_code == 200:
                print(champ.content)
                return 400
            champ = champ.json()
            Path(res + '/champions/{}/{}'.format(version, language)).mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as fb:
                json.dump(champ, fb, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            with open(path, 'r') as fb:
                champ = json.load(fb)
        return champ

    def get_champ_icon(self, champion, version=None):
        if champion not in self.champ_list.keys():
            return 400

        version, language = self.check_version_language(version, None)

        if not os.path.isfile(res_folder() + 'images/lol/Champions_icons/{}/{}.png'.format(version, champion)):
            image = requests.get(
                'https://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png'.format(version, champion)).content
            Path(res_folder() + 'images/lol/Champions_icons/{}'.format(version)).mkdir(parents=True, exist_ok=True)
            with open(res_folder() + 'images/lol/Champions_icons/{}/{}.png'.format(version, champion), 'wb') as fb:
                fb.write(image)

    def get_champ_splashart(self, champion, version=None, skin_id=0):
        champion = self.check_champion(champion, version)
        path = res_folder() + f'images/lol/Champions_splasharts/{version}/{champion}/'

        if not os.path.isfile(path + f'{skin_id}.png'):
            image = requests.get(f'http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion}_{skin_id}.jpg')\
                .content
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(path + f'{skin_id}.png', 'wb') as fb:
                fb.write(image)

    def get_champ_loading(self, champion, version=None, skin_id=0):
        champion = self.check_champion(champion, version)
        path = res_folder() + f'images/lol/Champions_loading/{version}/{champion}/'

        if not os.path.isfile(path + f'{skin_id}.png'):
            image = requests.\
                get(f'http://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion}_{skin_id}.jpg').content
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(path + f'{skin_id}.png', 'wb') as fb:
                fb.write(image)

    def get_all_champs_infos(self, version=None, language=None):
        version, language = self.check_version_language(version, language)

        for champ in self.get_champ_list(version=version).keys():
            self.get_champ_infos(champ, version, language)

    def get_item_list(self, version=None, language=None):
        version, language = self.check_version_language(version, language)

        file_name = res + '/items_lists/items_list_{}_{}.json'.format(version, language)

        item_list_json = requests.get(
            "http://ddragon.leagueoflegends.com/cdn/{}/data/{}/item.json".format(version,
                                                                                 language) + url_token)
        Path(res + '/items_lists').mkdir(parents=True, exist_ok=True)
        with open(file_name, 'w') as fb:
            json.dump(item_list_json.json(), fb, sort_keys=True, indent=4, separators=(',', ': '))

        tmp_item_list = []
        for item in item_list_json.json()['data']:
            tmp_item_list.append(str(item))
        return tmp_item_list

    def get_item_icon(self, item_id, version=None):
        if item_id not in self.item_list:
            return 400

        version, language = self.check_version_language(version, None)

        if not os.path.isfile(res_folder() + 'images/lol/Items_icons/{}/{}.png'.format(version, item_id)):
            image = requests.get(
                'https://ddragon.leagueoflegends.com/cdn/{}/img/item/{}.png'.format(version, item_id)).content
            Path(res_folder() + 'images/lol/Items_icons/{}'.format(version)).mkdir(parents=True, exist_ok=True)
            with open(res_folder() + 'images/lol/Items_icons/{}/{}.png'.format(version, item_id), 'wb') as fb:
                fb.write(image)

    def get_sums_list(self, version=None, language=None):
        version, language = self.check_version_language(version, language)

        file_name = res + '/sums_lists/sums_list_{}_{}.json'.format(version, language)

        sums_list_json = requests.get(
            "http://ddragon.leagueoflegends.com/cdn/{}/data/{}/summoner.json".format(version,
                                                                                     language) + url_token)
        Path(res + '/sums_lists').mkdir(parents=True, exist_ok=True)
        with open(file_name, 'w') as fb:
            json.dump(sums_list_json.json(), fb, sort_keys=True, indent=4, separators=(',', ': '))

        tmp_sums_list = {}
        for sum in sums_list_json.json()['data']:
            tmp_sums_list[sums_list_json.json()['data'][sum]['key']] = sum
        return tmp_sums_list

    def get_sum_icon(self, sum_id, version=None):
        if sum_id not in self.sums_list.keys():
            return 400

        version, language = self.check_version_language(version, None)

        if not os.path.isfile(res_folder() + 'images/lol/Summoner_spells_icons/{}/{}.png'.format(version, sum_id)):
            image = requests.get(
                'https://ddragon.leagueoflegends.com/cdn/{}/img/spell/{}.png'
                .format(version, self.sums_list[sum_id])) \
                .content
            Path(res_folder() + 'images/lol/Summoner_spells_icons/{}'.format(version)).mkdir(parents=True, exist_ok=True)
            with open(res_folder() + 'images/lol/Summoner_spells_icons/{}/{}.png'.format(version, sum_id), 'wb') as fb:
                fb.write(image)

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
            print(summoner.status_code)
            return 400
        return summoner.json()['puuid']

    @staticmethod
    def get_match_history(summoner_uuid, games_count=None):
        if games_count is None:
            games_count = 5

        history = requests.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_uuid}/ids?start=0&count={games_count}&api_key={API_Key}")

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
