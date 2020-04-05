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
df = pd.DataFrame.from_dict(data)


def getMyTeam(match, teamPlayers):

    player = match.participantIdentities[0]["player"]
    if player["summonerName"] in teamPlayers:
        return 100
    else:
        return 200


# team stats
teamStats = {}
for _index, match in df.iterrows():
    date = match["gameCreation"]
    date = datetime.fromtimestamp(date / 1000)
    myTeam = int(getMyTeam(match, teamPlayers) / 100 - 1)
    matchStats = match.teams[myTeam]
    matchStats
    print(pd.DataFrame.from_dict(matchStats))
    teamStats[date] = pd.DataFrame.from_dict(matchStats, orient="index").T


teamStats = pd.concat(teamStats)
teamStats.to_csv("output/team/teamStats.csv")


# prepare list with playerStats and playerTimeline
playerStats = {}
playerTimelines = {}
for player in teamPlayers:
    playerStats[player] = {}
    playerTimelines[player] = {}

# assign match data to players
for _index, match in df.iterrows():
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
    playerStats[player].to_csv("output/raw/allStats_" + player + ".csv")

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

    playerTimelines[player].to_csv("output/raw/timelines_" + player + ".csv")

    # drop_cols = [c for c in playerStats[player].columns if c.lower()[:4]
    #     in ['perk', 'stat', 'play', 'item', 'tota', 'larg', ']
    # drop_cols.extend(['participantId'])

    # quickReviews
    pt_select = playerTimelines[player][
        [
            "creepsPerMinDeltas@0-10",
            "creepsPerMinDeltas@10-20",
            "xpPerMinDeltas@0-10",
            "csDiffPerMinDeltas@0-10",
            "csDiffPerMinDeltas@10-20",
            "xpDiffPerMinDeltas@0-10",
            "xpDiffPerMinDeltas@10-20",
        ]
    ]

    ps_select = playerStats[player][
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
    ]

    quickReviews[player] = pd.merge(
        ps_select, pt_select, left_index=True, right_index=True
    )
    quickReviews[player].astype(float).round(2).to_csv(
        "output/players/quickReview_" + player + ".csv"
    )

playerStats["Strucio"]
# create team summary
teamSummary = []
for player in teamPlayers:
    means = quickReviews[player].mean()
    means = means[
        [
            "win",
            "kills",
            "deaths",
            "assists",
            "creepsPerMinDeltas@10-20",
            "csDiffPerMinDeltas@0-10",
            "csDiffPerMinDeltas@10-20",
            "xpDiffPerMinDeltas@10-20",
        ]
    ]
    means["gamesPlayed"] = playerStats[player].sum()["counter"]
    means["player"] = player
    teamSummary.append(means.to_frame().T)


teamSummary = pd.concat(teamSummary)
teamSummary["KDA"] = (teamSummary["kills"] + teamSummary["assists"]) / teamSummary[
    "deaths"
]


# format DataFrame
teamSummary = teamSummary.set_index("player")
teamSummary.columns = [
    "winRate",
    "kills",
    "deaths",
    "assists",
    "creepsPerMin@10-20",
    "csDiffPerMin@0-10",
    "csDiffPerMin@10-20",
    "xpDiffPerMin@10-20",
    "gamesPlayed",
    "KDA",
]

cols = teamSummary.columns.tolist()
teamSummary = teamSummary[
    [
        "gamesPlayed",
        "winRate",
        "kills",
        "deaths",
        "assists",
        "KDA",
        "creepsPerMin@10-20",
        "csDiffPerMin@0-10",
        "csDiffPerMin@10-20",
        "xpDiffPerMin@10-20",
    ]
]
teamSummary.index.name = None

teamSummary = teamSummary.sort_values(by="KDA", ascending=False)
teamSummary = teamSummary.astype(float).round(2)
teamSummary
teamSummary.to_csv("output/team/teamSummary.csv")

# for player in teamPlayers:
