import datetime
import json
import pickle

import numpy as np
import pandas as pd


def getParticipantsId(match, summonerName):
    for p in match["participantIdentities"]:
        if p["player"]["summonerName"] == summonerName:
            return p["participantId"]


def getParticipantById(participants, id):
    for p in participants:
        if p["participantId"] == id:
            return p


# decoding RitoAPI
def getChampionNameById(championId):
    with open("data/Riot/champion.json") as f:
        data = json.load(f)
        df = pd.DataFrame.from_dict(data["data"]).T.set_index("key")

    return df.query('key == "' + str(championId) + '"')["name"][0]


def getQueueNameById(queueId):
    with open("data/Riot/queues.json") as f:
        data = json.load(f)
        df = pd.DataFrame.from_dict(data).set_index("queueId")
        df.query("queueId == " + str(queueId))["description"]
    return df.query("queueId == " + str(queueId))["description"][0]


def sortByWeek(matches, startDate):
    startDatetime = datetime.datetime.strptime(startDate, "%d %B, %Y")
    startDatetime
    d = datetime.timedelta(days=7)
    d
    matches["week"] = np.nan

    matches["gameCreation"]
    flag = True
    counter = 1
    while flag:

        startTimestamp = datetime.datetime.timestamp(startDatetime)
        startTimestamp
        # matches[matches["gameCreation"] / 1000 < startTimestamp]['week'] = counter
        matches.loc[
            (matches["gameCreation"] / 1000 > startTimestamp), ["week"]
        ] = counter
        counter += 1
        startDatetime = startDatetime + d
        if counter == 26:
            flag = False

    return matches


def getMyTeam(match, teamPlayers):

    player = match.participantIdentities[0]["player"]
    if player["summonerName"] in teamPlayers:
        return 100
    else:
        return 200


teamPlayers = ["Sopapiglobo", "Darkonia", "Scσrpiσn", "Blackéyé", "Flokii", "Strucio"]
startDate = "30 March, 2020"
# Load scrapped data
data = pickle.load(open("data/filteredMatches.pickle", "rb"))
matches = pd.DataFrame.from_dict(data)
matches = sortByWeek(matches, startDate)

matches
# team stats
teamStats = {}
for _index, match in matches.iterrows():
    date = match["gameCreation"]
    myTeam = int(getMyTeam(match, teamPlayers) / 100 - 1)
    matchStats = match.teams[myTeam]
    matchStats["queueId"] = match["queueId"]
    matchStats["week"] = match["week"]
    teamStats[date] = pd.DataFrame.from_dict(matchStats, orient="index").T

booleans = [
    "firstBlood",
    "firstTower",
    "firstInhibitor",
    "firstBaron",
    "firstDragon",
    "firstRiftHerald",
    "towerKills",
    "inhibitorKills",
    "baronKills",
    "dragonKills",
    "vilemawKills",
    "riftHeraldKills",
    "dominionVictoryScore",
    "win",
]
teamStats = pd.concat(teamStats)
teamStats = teamStats.droplevel(level=1)
teamStats.loc[teamStats["win"] != "Win", "win"] = 0
teamStats.loc[teamStats["win"] == "Win", "win"] = 1

teamStats.loc[teamStats["queueId"] == 440, "queueId"] = "Flex"
teamStats.loc[teamStats["queueId"] == 700, "queueId"] = "Clash"

teamStats.loc[teamStats["teamId"] != 100, "teamId"] = "Red"
teamStats.loc[teamStats["teamId"] == 100, "teamId"] = "Blue"
teamStats["counter"] = 1
teamStats["gameCreation"] = teamStats.index
teamStats

teamStats[booleans] = teamStats[booleans].astype(int)
teamStats.to_csv("data/raw/teamStats.csv")
teamStats

# t = teamStats.drop(["gameCreation", "vilemawKills", "dominionVictoryScore"], axis=1)
# t[t["queueId"] == 700].groupby("week").mean().plot()
# s = t.groupby(["queueId", "week"]).sum()
# s["winrate"] = s["win"] / s["counter"]
# s
# s.unstack("queueId")["winrate"].plot(style=".-", marker="o")


# prepare list with playerStats and playerTimeline
playerStats = {}
playerTimelines = {}
for player in teamPlayers:
    playerStats[player] = {}
    playerTimelines[player] = {}

# assign match data to players
for _index, match in matches.iterrows():
    date = match["gameCreation"]
    for player in teamPlayers:
        id = getParticipantsId(match, player)
        if id is not None:
            p = getParticipantById(match["participants"], id)

            playerStats[player][date] = p["stats"]
            playerStats[player][date]["championId"] = getChampionNameById(
                p["championId"]
            )
            playerStats[player][date]["queueId"] = np.where(
                match["queueId"] == 440, "Flex", "Clash"
            )
            playerStats[player][date]["week"] = match["week"]

            playerTimelines[player][date] = p["timeline"]
            playerTimelines[player][date]["championId"] = getChampionNameById(
                p["championId"]
            )
            playerTimelines[player][date]["queueId"] = np.where(
                match["queueId"] == 440, "Flex", "Clash"
            )
            playerTimelines[player]


# save allStats
for player in teamPlayers:

    # stats
    playerStats[player] = pd.DataFrame.from_dict(playerStats[player]).T
    playerStats[player]["counter"] = 1
    (playerStats[player]).columns
    playerStats[player]
    playerStats[player]["gameCreation"] = playerStats[player].index
    playerStats[player] = sortByWeek(playerStats[player], startDate)
    playerStats[player].to_csv("data/raw/allStats_" + player + ".csv")

    # timelines
    playerTimelines[player] = pd.DataFrame.from_dict(
        playerTimelines[player], orient="index"
    )
    playerTimelines[player]["counter"] = 1

    # unpack dictionaries
    cols = [
        "creepsPerMinDeltas",
        "xpPerMinDeltas",
        "goldPerMinDeltas",
        "damageTakenPerMinDeltas",
        "csDiffPerMinDeltas",
        "xpDiffPerMinDeltas",
        "damageTakenDiffPerMinDeltas",
    ]
    time_windows = ["0-10", "10-20", "20-30", "30-end"]

    # create placeholders
    for col in cols:
        for win in time_windows:
            type(playerTimelines[player][col])
            playerTimelines[player][col + "@" + win] = playerTimelines[player][col]

    # fill placeholders by unpacking dicts
    for col in cols:
        for win in time_windows:
            for index, _row in playerTimelines[player].iterrows():
                try:
                    playerTimelines[player].at[
                        index, col + "@" + win
                    ] = playerTimelines[player][col][index][win]
                except (KeyError, TypeError):
                    playerTimelines[player].at[index, col + "@" + win] = np.nan

    playerTimelines[player]["gameCreation"] = playerTimelines[player].index
    playerTimelines[player] = sortByWeek(playerTimelines[player], startDate)
    playerTimelines[player].to_csv("data/raw/timelines_" + player + ".csv")
