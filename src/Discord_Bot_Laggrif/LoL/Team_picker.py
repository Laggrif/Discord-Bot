import random

from riotwatcher import LolWatcher

roles = ['adc', 'supp', 'mid', 'jung', 'top']
lol = LolWatcher('API')

def role(players):
    rolep = {}
    for i in range(len(players)):
        truc = random.randrange(0, len(players))
        rolep[players[i]] = roles[truc]
        roles.pop(truc)
    print(rolep)

def champ(players, bans=[]):
    riotwatcher.LolWatcher.champion =

role(['LaLoutre', 'Fred', 'Laggrif'])
