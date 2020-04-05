import pandas as pd

# Parameters
teamPlayers = ["Sopapiglobo", "Darkonia", "Scσrpiσn", "Blackéyé", "Flokii", "Strucio"]

# load raw data
teamStats = pd.read_csv("data/raw/teamStats.csv")
teamStats = teamStats.drop(columns=["Unnamed: 1"])
teamStats.rename(columns={"Unnamed: 0": "date"}, inplace=True)
teamStats.set_index("date")

playerStats = {}
playerTimelines = {}
for player in teamPlayers:
    playerStats[player] = pd.read_csv("data/raw/allStats_" + player + ".csv")
    playerTimelines[player] = pd.read_csv("data/raw/timelines_" + player + ".csv")

    playerStats[player].rename(columns={"Unnamed: 0": "date"}, inplace=True)
    playerStats[player] = playerStats[player].set_index("date")
    playerTimelines[player].rename(columns={"Unnamed: 0": "date"}, inplace=True)
    playerTimelines[player] = playerTimelines[player].set_index("date")

    playerStats[player].index.name = None
    playerTimelines[player].index.name = None

# Player Summaries

# create quickReview_players

# quickReviews
quickReviews = {}
for player in teamPlayers:
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

# team Summaries

# create quickReview_TeamStats
cols = teamStats.columns.tolist()
quickReview_Team = teamStats[
    [
        "win",
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
        "riftHeraldKills",
    ]
].mean()
quickReview_Team = quickReview_Team.to_frame()
quickReview_Team.columns = ["Team Placeholder"]
quickReview_Team = quickReview_Team.astype(float).round(2)
quickReview_Team.to_csv("output/team/quickReview_TeamStats.csv")

# create teamSummary
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
