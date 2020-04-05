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


# teamStats_by_win
ts_byWin = teamStats.groupby("win").mean()
ts_byWin.index.name = None
ts_byWin = ts_byWin[
    [
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
        "counter",
    ]
]
ts_byWin["counter"] = teamStats.groupby("win").sum()["counter"]
ts_byWin = ts_byWin.astype(float).round(2)
ts_byWin.to_csv("output/team/teamStats_ByWin.csv")
ts_byWin


# teamStats_by_side
ts_bySide = teamStats.groupby("teamId").mean()
ts_bySide.index.name = None
ts_bySide = ts_bySide[
    [
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
        "counter",
    ]
]
ts_bySide["counter"] = teamStats.groupby("teamId").sum()["counter"]
ts_bySide = ts_bySide.astype(float).round(2)
ts_bySide.to_csv("output/team/teamStats_BySide.csv")


teamStats.groupby(["teamId", "win"]).mean().unstack().plot()
