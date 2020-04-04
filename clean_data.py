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
    # drop_cols = [c for c in playerStats[player].columns if c.lower()[:4]
    # in ['perk', 'stat', 'play', 'item', 'tota', '2.se']]
    # drop_cols.append('participantId')
    # playerStats[player] = playerStats[player].drop(columns=drop_cols)
    playerStats[player].to_csv("output/allStats_" + player + ".csv")


# create summary
playerSummary = {}
for player in teamPlayers:
    playerSummary[player] = []

# for player in teamPlayers:
