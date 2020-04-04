import json
import requests
import pandas as pd;

#Parameters
summonerName = "Darkonia"
teamPlayers = ['Sopapiglobo', 'Darkonia', 'Scσrpiσn', 'Blackéyé', 'Flokii', 'Strucio']
APIKey = "RGAPI-8766373a-9f14-45b7-94ae-ccdeafee806a"
season = "13"
queueId = "440"




# Get account details by providing the account name
def requestSummonerData(summonerName, APIKey):
    URL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + \
        summonerName + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()
requestSummonerData(summonerName, APIKey)['accountId']

# Get accountIds for each member of the team
def requestMatchByAccountId(accountId, season, queueId, APIKey):
    URL = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + \
        str(accountId) + "?queue=" + queueId + "&season=" + season + \
        "&api_key=" + APIKey
    response = requests.get(URL)
    return response.json()


def requestMatchById(matchId, APIKey):
    URL = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + \
        str(matchId) + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()


def getMatchPlayers(match):
    players = []
    for p in match['participantIdentities']:
        players.append(p['player']['summonerName'])
    return players



getMatchPlayers(match)
len(set(teamPlayers) & set())


def requestTeamData(summonerList, APIKey):
    teamIds = []
    for summonerName in summonerList:
        summonerId = requesSummonerData(summonerName, APIKey)['accountId']
        teamIds.append(summonerId)
    return teamIds





#Main
#get Ids
accountId = requestSummonerData(summonerName, APIKey)['accountId']

#get Matches
matches = requestMatchByAccountId(accountId, season, queueId, APIKey)


matches = pd.DataFrame.from_dict(matches['matches'])
for gameId in match['gameId']:
    match = requestMatchById(gameId, APIKey)
    matchPlayers = getMatchPlayers(match)
    if len(set(teamPlayers) & set(matchPlayers))  == 5
        print('uwu')
