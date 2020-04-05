import pickle
from datetime import datetime

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


teamPlayers = ["Sopapiglobo", "Darkonia", "Scσrpiσn", "Blackéyé", "Flokii", "Strucio"]

# Load scrapped data
data = pickle.load(open("data/filteredMatches.pickle", "rb"))
matches = pd.DataFrame.from_dict(data)


def getMyTeam(match, teamPlayers):

    player = match.participantIdentities[0]["player"]
    if player["summonerName"] in teamPlayers:
        return 100
    else:
        return 200


# team stats
teamStats = {}
for _index, match in matches.iterrows():
    date = match["gameCreation"]
    date = datetime.fromtimestamp(date / 1000)
    myTeam = int(getMyTeam(match, teamPlayers) / 100 - 1)
    matchStats = match.teams[myTeam]
    teamStats[date] = pd.DataFrame.from_dict(matchStats, orient="index").T

teamStats = pd.concat(teamStats)
teamStats.loc[teamStats["win"] != "Win", "win"] = 0
teamStats.loc[teamStats["win"] == "Win", "win"] = 1
teamStats.loc[teamStats["teamId"] != 100, "teamId"] = "Red"
teamStats.loc[teamStats["teamId"] == 100, "teamId"] = "Blue"
teamStats["counter"] = 1
teamStats.to_csv("data/raw/teamStats.csv")


# prepare list with playerStats and playerTimeline
playerStats = {}
playerTimelines = {}
for player in teamPlayers:
    playerStats[player] = {}
    playerTimelines[player] = {}

# assign match data to players
for _index, match in matches.iterrows():
    date = match["gameCreation"]
    date = datetime.fromtimestamp(date / 1000)
    for player in teamPlayers:
        id = getParticipantsId(match, player)
        if id is not None:
            p = getParticipantById(match["participants"], id)
            playerStats[player][date] = p["stats"]
            playerTimelines[player][date] = p["timeline"]


# save allStats
quickReviews = {}
for player in teamPlayers:

    # stats
    playerStats[player] = pd.DataFrame.from_dict(playerStats[player]).T
    playerStats[player]["counter"] = 1
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

    playerTimelines[player].to_csv("data/raw/timelines_" + player + ".csv")
