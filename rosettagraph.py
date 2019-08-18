import sqlite3
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import pdb
from scipy.interpolate import UnivariateSpline
from scipy import signal

"""
Import data from rosettacode.db and generate graphs to help us visualize how
python compares to other language.
"""

query = """
    SELECT task.task,language.name,code.loc FROM code
    INNER JOIN task ON code.task_id=task.id
    INNER JOIN language ON code.lang_id=language.id
    """
print("Connecting to SQLite db")
conn = sqlite3.connect("rosettacode.db")
# Create pandas dataframe
df = pd.read_sql(query, conn)
print("Shaping data")
loc_data = [df[df["task"] == t]["loc"] for t in df["task"].unique()]
loc_data = [(x, x.median()) for x in loc_data]
loc_data.sort(key=lambda x: x[1])  # sort by mean
loc_data = [x[0] for x in loc_data]  # drop our means

# Modify the dataframe to allow the addition of a chart for python
medians = df.groupby("task").median()
languages = {
        "COBOL":"green",
        "Assembly":"silver",
        "Fortran":"indigo",
        "Ada":"orchid",
        "Pascal":"yellow",
        "C":"coral",
        "APL":"cornflowerblue",
        "Scheme":"red",

}
for lang in languages:
    langdf = df[df["name"] == lang].set_index("task")
    langdf = langdf[~langdf.index.duplicated(keep="first")]
    medians[lang] = langdf["loc"]
medians = medians.sort_values("loc")
medians = medians.fillna(method="bfill")
medians = medians.fillna(method="ffill")

# Create boxplots
# pdb.set_trace()
print("Plotting . . .")
fig1, ax1 = plt.subplots(figsize=(48, 24), dpi=255)
ax1.set_title(
    "Distributions of Program Length by Average Task Complexity", size=80
)
ax1.set_xlabel("Tasks / Algorithms", size=65)
ax1.set_ylabel("Lines of Code", size=65)
ax1.set_ylim(0, 300)
ax1.set_yticks([50, 100, 150, 200, 250, 300])
box = ax1.boxplot(
    [n for n in loc_data], sym="x", whis=95, patch_artist=True, zorder=0.1
)
for b in box["boxes"]:
    b.set(facecolor="darkkhaki")
# get X coordinates
x = [np.average(geom._x) for geom in box["medians"]]
# Plot regression curves for specific languages
for lang in languages:
    # polynomial regression
    # curve = np.poly1d(np.polyfit(x,medians[lang],3))
    # ax1.plot(x,curve(x),color=languages[lang],alpha=0.75,label=lang,lw=3)
    # savitzky-golay filtering
    curve = signal.savgol_filter(medians[lang], 51, 3)
    ax1.plot(x, curve, color=languages[lang], alpha=0.75, label=lang, lw=3)

ax1.set_xticklabels("")  # Remove x-axis tick labels
ax1.grid(True, axis="y")
plt.legend(loc=2, fontsize=25)
print("Saving plot")
fig1.savefig("Results/more-civilized-age.png")  # save
