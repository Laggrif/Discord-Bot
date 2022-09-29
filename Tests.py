import json

import Assets
import LoLAPI

res = Assets.assets()

"""
def fetch_channel_ids():
    with open(res + 'settings/Active_Chatbot_Channels.json', 'r') as fp:
        ids = json.load(fp)
    return ids

with open(Assets.assets() + 'settings/Active_Chatbot_Channels.json', 'r') as fp:
    guild_id = 988494917737250826
    data = json.load(fp)
    stri = "il me fume"
    pref = ""
    print(data)
    print(str(guild_id) in data)
    print(fetch_channel_ids())
    print(str(guild_id) in fetch_channel_ids())
    print(stri.startswith(pref))
    print(stri[len(pref):])
"""
with open('./res/League of Legends/f.json', 'w') as fb:
    ldt = LoLAPI.LoLData()
    i = ldt.get_match_history('La Loutre Verte', games_count=1)
    json.dump(i[0], fb, indent=4, separators=(',', ': '))
