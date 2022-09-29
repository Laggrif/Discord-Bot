PARTICIPANTS = 'participants'
CHALLENGES = 'challenges'
TEAMS = 'teams'
OBJECTIVES = 'objectives'


class Match:

    def __init__(self, match, uuid: str):
        self.match = match[1]
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

    # ------------------- game stats ---------------------

    def game_duration_string(self):
        time = self.infos['gameDuration']
        minutes = time / 60
        seconds = time - minutes * 60
        return '{}:{:02d}'.format(minutes, seconds)

    def game_duration_seconds(self):
        return self.infos['gameDuration']

    # -------------------- teams stats -------------------

    def win(self):
        return self.player_infos['win']

    def team_kills(self):
        return self.teams_infos[self.team][OBJECTIVES]['champion']['kills']

    def team_deaths(self):
        deaths = 0
        for player in self.infos[PARTICIPANTS]:
            deaths += player['kills']
        return deaths

    def team_assists(self):
        assists = 0
        for player in self.infos[PARTICIPANTS]:
            assists += player['assists']
        return assists

    def first_blood_team(self):
        return self.teams_infos[self.team][OBJECTIVES]['champion']['first']

    # ------------------- player stats ---------------------

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

    def damage_dealt(self):
        return self.player_infos['totalDamageDealtToChampions']

    def damage_to_buildings(self):
        return self.player_infos['damageDealtToBuildings']

    def damage_to_objectives(self):
        return self.player_infos['damageDealtToObjectives']

    def damage_taken(self):
        return self.player_infos['totalDamageTaken']

    def damage_mitigated(self):
        return self.player_infos['damageSelfMitigated']

    def heal_self(self):
        return self.player_infos['totalHeal']

    def heal_others(self):
        return self.player_infos['totalHealsOnTeammates']

    def minions_killed(self):
        return self.player_infos['totalMinionsKilled']

    def vision_score(self):
        return self.player_infos['visionScore']

    def cc_given(self):
        return self.player_infos['totalTimeCCingOthers']

    def cc_taken(self):
        """
        DO NOT USE, not sure what it gives as a result
        :return: not really sure what it gives
        """
        return self.player_infos['totalTimeCCDealt']

    def level(self):
        return self.player_infos['championLevel']

    def champion(self):
        return self.player_infos['championName']

    def transform(self):
        return self.player_infos['championTransform']

    def gold_earned(self):
        return self.player_infos['goldEarned']

    def gold_spent(self):
        return self.player_infos['goldSpent']

    def longest_living(self):
        time = self.player_infos['longestTimeSpentLiving']
        minutes = time / 60
        seconds = time - minutes * 60
        return '{}:{:02d}'.format(minutes, seconds)






