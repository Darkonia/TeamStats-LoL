import pickle

import pandas as pd


def getParticipantsId(match, summonerName):
    for p in match["participantIdentities"]:
        if p["player"]["summonerName"] == summonerName:
            return p["participantId"]


def getParticipantById(participants, id):
    for p in participants:
        if p["participantId"] == id:
            return p["stats"]


teamPlayers = ["Sopapiglobo", "Darkonia", "Scσrpiσn", "Blackéyé", "Flokii", "Strucio"]

# Load scrapped data
data = pickle.load(open("data/filteredMatches.pickle", "rb"))
df = pd.DataFrame.from_dict(data)

# prepare list with playerStats
playerStats = {}
for player in teamPlayers:
    playerStats[player] = []

# assign match data to players
for _index, match in df.iterrows():
    for player in teamPlayers:
        id = getParticipantsId(match, player)
        if id is not None:
            type(getParticipantById(match["participants"], id))
            stats = getParticipantById(match["participants"], id)
            playerStats[player].append(stats)

# save allStats

for player in teamPlayers:

    playerStats[player] = pd.DataFrame.from_dict(playerStats[player])
    playerStats[player]["counter"] = 1
    playerStats[player].to_csv("output/allStats_" + player + ".csv")

    # drop_cols = [c for c in playerStats[player].columns if c.lower()[:4]
    #     in ['perk', 'stat', 'play', 'item', 'tota', 'larg', ']
    # drop_cols.extend(['participantId'])
    playerStats[player][
        [
            "win",
            "kills",
            "deaths",
            "assists",
            "totalDamageDealt",
            "totalDamageTaken",
            "goldEarned",
            "visionScore",
        ]
    ].to_csv("output/quickReview_" + player + ".csv")


# create team summary
teamSummary = []
for player in teamPlayers:
    means = playerStats[player].mean()
    means = means[["win", "kills", "deaths", "assists"]]
    means["gamesPlayed"] = playerStats[player].sum()["counter"]
    means
    means["player"] = player
    teamSummary.append(means.to_frame().T)


teamSummary = pd.concat(teamSummary)
teamSummary["KDA"] = (teamSummary["kills"] + teamSummary["assists"]) / teamSummary[
    "deaths"
]

# format DataFrame
teamSummary = teamSummary.set_index("player")
teamSummary.columns = ["winRate", "kills", "deaths", "assists", "gamesPlayed", "KDA"]

cols = teamSummary.columns.tolist()
teamSummary = teamSummary[
    ["gamesPlayed", "winRate", "kills", "deaths", "assists", "KDA"]
]
teamSummary.index.name = None
teamSummary.sort_values("KDA", ascending="false")
teamSummary = teamSummary.round(2)
teamSummary
import numpy as np

np.round(teamSummary, decimals=2)
teamSummary.to_csv("output/teamSummary.csv")
# for player in teamPlayers:
