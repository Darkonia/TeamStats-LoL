import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

# import statsmodels
# import statsmodels.api as sm
# from sklearn.datasets import load_iris

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

teamStats.columns

mod = smf.ols(
    formula="win ~ teamId + C(firstBlood) + C(firstTower) +  C(firstInhibitor) \
    + C(firstBaron) + C(firstDragon) + C(firstRiftHerald) + towerKills + \
    inhibitorKills + baronKills + dragonKills + riftHeraldKills",
    data=teamStats,
)
res1 = mod.fit()


textfile = open("output/team/regressions/win_on_teamStats.html", "w")

print(
    summary_col(
        [res1],
        stars=True,
        float_format="%0.2f",
        model_names=["\n(0)"],
        info_dict={
            "N": lambda x: "{:d}".format(int(x.nobs)),
            "R2": lambda x: f"{x.rsquared:.2f}",
        },
    ).as_latex()
)
textfile.write(
    summary_col(
        [res1],
        stars=True,
        float_format="%0.2f",
        model_names=["\n(0)"],
        info_dict={
            "N": lambda x: "{:d}".format(int(x.nobs)),
            "R2": lambda x: f"{x.rsquared:.2f}",
        },
    ).as_html()
)

textfile.close()
