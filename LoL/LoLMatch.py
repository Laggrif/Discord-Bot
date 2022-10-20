from datetime import datetime

PARTICIPANTS = 'participants'
CHALLENGES = 'challenges'
TEAMS = 'teams'
OBJECTIVES = 'objectives'


class Match:

    def __init__(self, match, uuid: str, queues):
        self.match = match
        self.queues = queues
        self.infos = self.match['info']
        self.summoner = 0
        for player in self.match['metadata'][PARTICIPANTS]:
            if player == uuid:
                break
            else:
                self.summoner += 1
        self.player_infos = self.infos[PARTICIPANTS][self.summoner]
        self.team = 0 if self.player_infos['teamId'] == self.infos['teams'][0]['teamId'] else 1
        self.teams_infos = self.infos['teams']

        for queue in self.queues:
            if queue['queueId'] == self.infos['queueId']:
                self.queue = queue
                break

    # ------------------- game stats ---------------------

    def game_duration_string(self):
        time = self.infos['gameDuration']
        minutes = int(time / 60)
        seconds = time - minutes * 60
        return '{}:{:02d}'.format(minutes, seconds)

    def game_duration_seconds(self):
        return self.infos['gameDuration']

    def date(self):
        unix_time = self.infos['gameStartTimestamp'] / 1000
        return datetime.fromtimestamp(unix_time).strftime('%d %b %Y %H:%M')

    def game_mode(self):
        return self.queue['description']

    def map(self):
        return self.queue['map']

    # -------------------- teams stats -------------------

    def win(self):
        return self.player_infos['win']

    def team_kills(self):
        return self.teams_infos[self.team][OBJECTIVES]['champion']['kills']

    def team_deaths(self):
        deaths = 0
        for player in self.infos[PARTICIPANTS]:
            if player['teamId'] == self.teams_infos[self.team]['teamId']:
                deaths += player['deaths']
        return deaths

    def team_assists(self):
        assists = 0
        for player in self.infos[PARTICIPANTS]:
            if player['teamId'] == self.teams_infos[self.team]['teamId']:
                assists += player['assists']
        return assists

    def enemy_kills(self):
        return self.teams_infos[1 - self.team][OBJECTIVES]['champion']['kills']

    def enemy_deaths(self):
        deaths = 0
        for player in self.infos[PARTICIPANTS]:
            if player['teamId'] == self.teams_infos[1 - self.team]['teamId']:
                deaths += player['deaths']
        return deaths

    def enemy_assists(self):
        assists = 0
        for player in self.infos[PARTICIPANTS]:
            if player['teamId'] == self.teams_infos[1 - self.team]['teamId']:
                assists += player['assists']
        return assists

    def first_blood_team(self):
        return self.teams_infos[self.team][OBJECTIVES]['champion']['first']

    def team_turret_kills(self):
        return self.teams_infos[self.team][OBJECTIVES]['tower']['kills']

    def enemy_turret_kills(self):
        return self.teams_infos[1 - self.team][OBJECTIVES]['tower']['kills']

    def team_baron_kills(self):
        return self.teams_infos[self.team][OBJECTIVES]['baron']['kills']

    def enemy_baron_kills(self):
        return self.teams_infos[1 - self.team][OBJECTIVES]['baron']['kills']

    # ------------------- player stats ---------------------

    def items(self):
        items = []
        for i in range(7):
            items.append(str(self.player_infos[f'item{i}']))
        return items

    def summoners(self):
        sums = []
        for i in range(1, 3):
            sums.append(str(self.player_infos[f'summoner{i}Id']))
        return sums

    def kills(self):
        return self.player_infos['kills']

    def deaths(self):
        return self.player_infos['deaths']

    def assists(self):
        return self.player_infos['assists']

    def kda(self):
        return (self.kills() + self.assists()) / self.deaths()

    def first_blood_player(self):
        return self.player_infos['firstBloodKill']

    def damage_dealt_champ(self):
        return self.player_infos['totalDamageDealtToChampions']

    def physic_damages_champ(self):
        return self.player_infos['physicalDamageDealtToChampions']

    def magic_damages_champ(self):
        return self.player_infos['magicDamageDealtToChampions']

    def true_damages_champ(self):
        return self.player_infos['trueDamageDealtToChampions']

    def total_damages(self):
        return self.player_infos['totalDamageDealt']

    def damage_to_buildings(self):
        return self.player_infos['damageDealtToBuildings']

    def damage_to_objectives(self):
        return self.player_infos['damageDealtToObjectives']

    def damage_taken(self):
        return self.player_infos['totalDamageTaken']

    def physic_damage_taken(self):
        return self.player_infos['physicalDamageTaken']

    def magic_damage_taken(self):
        return self.player_infos['magicDamageTaken']

    def true_damage_taken(self):
        return self.player_infos['trueDamageTaken']

    def damage_mitigated(self):
        return self.player_infos['damageSelfMitigated']

    def heal_self(self):
        return self.player_infos['totalHeal']

    def heal_others(self):
        return self.player_infos['totalHealsOnTeammates']

    def shield_other(self):
        return self.player_infos['totalDamageShieldedOnTeammates']

    def minions_killed(self):
        return self.player_infos['totalMinionsKilled']

    def vision_score(self):
        return self.player_infos['visionScore']

    def cc_given(self):
        return self.player_infos['timeCCingOthers']

    def cc_taken(self):
        """
        DO NOT USE, not sure what it gives as a result
        :return: not really sure what it gives
        """
        return self.player_infos['totalTimeCCDealt']

    def level(self):
        return self.player_infos['champLevel']

    def champion(self):
        return self.player_infos['championName']

    def transform(self):
        transform = self.player_infos['championTransform']
        if transform == 0:
            return ''
        elif transform == 1:
            return ' Darkin'
        elif transform == 2:
            return ' Assassin'

    def gold_earned(self):
        return self.player_infos['goldEarned']

    def gold_spent(self):
        return self.player_infos['goldSpent']

    def longest_living(self):
        time = self.player_infos['longestTimeSpentLiving']
        minutes = int(time / 60)
        seconds = int(time - minutes * 60)
        return '{}:{}'.format(minutes, seconds)

    def time_dead(self):
        time = self.player_infos['totalTimeSpentDead']
        minutes = int(time / 60)
        seconds = int(time - minutes * 60)
        return '{}:{}'.format(minutes, seconds)
