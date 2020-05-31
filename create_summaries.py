import pandas as pd

# Parameters
teamPlayers = ["Sopapiglobo", "Darkonia", "Scσrpiσn", "Blackéyé", "Flokii", "Strucio"]

# load raw data
teamStats = pd.read_csv("data/raw/teamStats.csv")
# teamStats = teamStats.drop(columns=["Unnamed: 1"])
teamStats.columns
teamStats = teamStats.drop(["Unnamed: 0"], axis=1)
teamStats = teamStats.set_index("gameCreation")
teamStats
playerStats = {}
playerTimelines = {}
for player in teamPlayers:
    playerStats[player] = pd.read_csv("data/raw/allStats_" + player + ".csv")
    playerTimelines[player] = pd.read_csv("data/raw/timelines_" + player + ".csv")
    playerStats[player]["queueId"]
    playerStats[player].rename(columns={"Unnamed: 0": "date"}, inplace=True)
    playerStats[player] = playerStats[player].set_index("date")
    playerTimelines[player].rename(columns={"Unnamed: 0": "date"}, inplace=True)
    playerTimelines[player] = playerTimelines[player].set_index("date")

    playerStats[player].index.name = None
    playerTimelines[player].index.name = None

    playerStats[player]
rel_col = [
    "xpPerMinDeltas@0-10",
    "xpPerMinDeltas@10-20",
    "goldPerMinDeltas@0-10",
    "goldPerMinDeltas@10-20",
]

# Player Summaries

# create quickReview_players

# quickReviews
quickReviews = {}
for player in teamPlayers:
    playerTimelines[player]
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
            "week",
            "queueId",
            "championId",
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

    quickReviews[player] = quickReviews[player].round(2)
    quickReviews[player]["player"] = player
    quickReviews[player] = quickReviews[player].sort_values(
        by=["week", "queueId", "championId", "win"], ascending=True
    )
    quickReviews[player].to_csv("output/players/quickReview_" + player + ".csv")
    quickReviews[player]
# team Summaries

# create quickReview_TeamStats
cols = teamStats.columns.tolist()
teamStats
quickReview_Team = teamStats.groupby(["queueId", "week"]).mean()[
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
]


quickReview_Team["gamesPlayed"] = teamStats.groupby(["queueId", "week"]).sum()[
    "counter"
]
quickReview_Team["gamesPlayed"]
# quickReview_Team = quickReview_Team.to_frame()
# quickReview_Team.columns = ["Digital Sports Black"]
quickReview_Team = quickReview_Team.astype(float).round(2)
quickReview_Team = quickReview_Team.sort_values(by=["week"], ascending=True)

quickReview_Team.to_csv("output/team/quickReview_TeamStats.csv")
quickReview_Team

# create teamSummary
teamSummaryByWeek = []
for player in teamPlayers:
    means = quickReviews[player].groupby(["queueId", "week", "player"]).mean()
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
    means["gamesPlayed"] = (
        playerStats[player].groupby(["queueId", "week"]).sum()["counter"]
    )
    # means["player"] = player
    means
    teamSummaryByWeek.append(means)


teamSummaryByWeek = pd.concat(teamSummaryByWeek)
teamSummaryByWeek
teamSummaryByWeek["KDA"] = (
    teamSummaryByWeek["kills"] + teamSummaryByWeek["assists"]
) / teamSummaryByWeek["deaths"]


# format DataFrame


teamSummaryByWeek
teamSummaryByWeek.columns = [
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

cols = teamSummaryByWeek.columns.tolist()
cols
teamSummaryByWeek = teamSummaryByWeek[
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
teamSummaryByWeek.index.name = None

teamSummaryByWeek
teamSummaryByWeek.query("player == 'Darkonia'").groupby(
    ["queueId", "week"]
).mean().unstack("queueId")["KDA"].plot.bar()
teamSummaryByWeek.groupby(["week", "player"]).mean().unstack(["player"])["KDA"].plot(
    style=".-", marker="o"
)
teamSummaryByWeek.groupby(["week", "queueId"]).mean().unstack("queueId")[
    ["winRate"]
].plot(style=".-", marker="o")

teamSummaryByWeek = teamSummaryByWeek.sort_values(
    by=["queueId", "week"], ascending=True
)
teamSummaryByWeek = teamSummaryByWeek.astype(float).round(2)
teamSummaryByWeek.to_csv("output/team/teamSummaryByWeek.csv")

teamSummaryByWeek.groupby("week").mean().query(
    "week == " + str(teamStats["week"].max())
)

teamStats
# champion stats

teamChampionStats = []
for player in teamPlayers:
    means = quickReviews[player].groupby(["player", "championId"]).mean()
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
    quickReviews[player]["counter"] = 1
    means["gamesPlayed"] = (
        quickReviews[player].groupby(["player", "championId"]).sum()["counter"]
    )
    # means["player"] = player
    means
    teamChampionStats.append(means)


teamChampionStats = pd.concat(teamChampionStats)
teamChampionStats
teamChampionStats["KDA"] = (
    teamChampionStats["kills"] + teamChampionStats["assists"]
) / teamChampionStats["deaths"]


# format DataFrame


teamChampionStats
teamChampionStats.columns = [
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

cols = teamChampionStats.columns.tolist()
cols
teamChampionStats = teamChampionStats[
    [
        "gamesPlayed",
        "winRate",
        "KDA",
        "kills",
        "deaths",
        "assists",
        "creepsPerMin@10-20",
        "csDiffPerMin@0-10",
        "csDiffPerMin@10-20",
        "xpDiffPerMin@10-20",
    ]
]
teamChampionStats.index.name = None


teamChampionStats.query("player == 'Darkonia'").groupby(
    ["queueId", "week"]
).mean().unstack("queueId")["KDA"].plot.bar()
teamChampionStats.groupby(["week", "player"]).mean().unstack(["player"])["KDA"].plot(
    style=".-", marker="o"
)
teamChampionStats.groupby(["week", "queueId"]).mean().unstack("queueId")[
    ["winRate"]
].plot(style=".-", marker="o")
teamChampionStats
teamChampionStats = teamChampionStats.sort_values(
    by=["player", "winRate", "gamesPlayed", "KDA"],
    ascending=[True, False, False, False],
)
teamChampionStats = teamChampionStats.astype(float).round(2)
teamChampionStats.to_csv("useful/team/teamChampionStats.csv")
