import pickle
import time
from datetime import datetime

import pandas as pd
import requests


# Parameters
summonerName = "Darkonia"
teamPlayers = ["Sopapiglobo", "Darkonia", "Scσrpiσn", "Blackéyé", "Flokii", "Strucio"]
APIKey = "RGAPI-2045c3a3-0d61-40b5-a741-869067293ee1"
season = "13"
queueId = ["440", "700"]
startDate = "30 March, 2020"


# Get account details by providing the account name
def requestSummonerData(summonerName, APIKey):
    URL = (
        "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        + summonerName
        + "?api_key="
        + APIKey
    )
    response = requests.get(URL)
    return response.json()


# Get accountIds for each member of the team
def requestMatchByAccountId(accountId, season, queueId, APIKey):
    URL = (
        "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
        + str(accountId)
        + "?queue="
        + queueId
        + "&season="
        + season
        + "&api_key="
        + APIKey
    )
    response = requests.get(URL)
    return response.json()


def requestMatchById(matchId, APIKey):
    URL = (
        "https://euw1.api.riotgames.com/lol/match/v4/matches/"
        + str(matchId)
        + "?api_key="
        + APIKey
    )
    response = requests.get(URL)
    return response.json()


def getMatchPlayers(match):
    players = []
    for p in match["participantIdentities"]:
        players.append(p["player"]["summonerName"])
    return players


def filterMatchesByDate(matches, startDate):
    startDatetime = datetime.strptime(startDate, "%d %B, %Y")
    startTimestamp = datetime.timestamp(startDatetime)

    matches = matches[matches["timestamp"] / 1000 > startTimestamp]

    return matches


def filterMatches(matches, minMembers, APIKey):
    """get all gameIds of matches with at least <minMembers> player of the team """

    filteredMatches = []
    for gameId in matches["gameId"]:
        time.sleep(0.85)
        match = requestMatchById(gameId, APIKey)

        matchPlayers = getMatchPlayers(match)
        if len(set(teamPlayers) & set(matchPlayers)) >= minMembers:
            filteredMatches.append(match)

    return filteredMatches


# Team Methods
def requestTeamData(summonerList, APIKey):
    teamIds = []
    for summonerName in summonerList:
        summonerId = requestSummonerData(summonerName, APIKey)["accountId"]
        teamIds.append(summonerId)
    return teamIds


# Main
# get Ids
accountId = requestSummonerData(summonerName, APIKey)["accountId"]

# get Matches
matchesFlex = requestMatchByAccountId(accountId, season, queueId[0], APIKey)
matchesClash = requestMatchByAccountId(accountId, season, queueId[1], APIKey)
matchesClash
# create DataFrame
matchesFlex = pd.DataFrame.from_dict(matchesFlex["matches"])
matchesClash = pd.DataFrame.from_dict(matchesClash["matches"])
matches = pd.concat([matchesFlex, matchesClash])

# Filter by date
matches = filterMatchesByDate(matches, startDate)

# request matches and filter by at least 5 team member is a team
filteredMatches = filterMatches(matches, 5, APIKey)

# export as pickle
with open("data/filteredMatches.pickle", "wb") as out_file:
    pickle.dump(filteredMatches, out_file)

name = requestSummonerData(summonerName, APIKey)
name
# id = name['accountId']
# requestMatchByAccountId(id, season, str(0), APIKey)
