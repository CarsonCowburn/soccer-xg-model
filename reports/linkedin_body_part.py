import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
root = sys.argv[1]
d = pd.read_parquet(f"{root}/data/processed/shots_clean.parquet")
d["distance"] = np.hypot(120 - d.x, 40 - d.y)
d = d[d.shot_body_part.isin(["Head", "Left Foot", "Right Foot"])]
t = d.groupby("shot_body_part").agg(rate=("is_goal", "mean"), n=("is_goal", "size"), med=("distance", "median"))
t = t.loc[["Right Foot", "Left Foot", "Head"]]   # bottom -> top
overall = pd.read_parquet(f"{root}/data/processed/shots_clean.parquet").is_goal.mean()

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#d9d8d3"
ACCENT, NEUTRAL, BG = "#2a78d6", "#bdbcb6", "#fcfcfb"

fig = plt.figure(figsize=(6, 6), dpi=200, facecolor=BG)
ax = fig.add_axes([0.30, 0.24, 0.62, 0.47], facecolor=BG)
y = np.arange(len(t))
colors = [NEUTRAL, NEUTRAL, ACCENT]
ax.barh(y, t.rate * 100, height=0.52, color=colors, zorder=3)
for yi, (r, c) in enumerate(zip(t.rate * 100, colors)):
    ax.text(r - 0.3, yi, f"{r:.1f}%", va="center", ha="right", fontsize=15,
            fontweight="bold", color="white" if c == ACCENT else INK, zorder=4)
ax.vlines(overall * 100, -0.6, len(t) - 0.42, color=MUTED, ls=(0, (3, 3)), lw=1.2, zorder=2)
ax.text(overall * 100, len(t) - 0.38, f"All shots {overall:.1%}", ha="center", va="bottom",
        fontsize=9.5, color=MUTED)
ax.set_yticks(y)
ax.set_yticklabels([])
for yi, (name, row) in enumerate(t.iterrows()):
    label = "Header" if name == "Head" else name
    ax.text(-0.4, yi + 0.09, label, ha="right", va="center", fontsize=13,
            fontweight="bold" if name == "Head" else "normal", color=INK)
    ax.text(-0.4, yi - 0.22, f"taken {row.med:.1f} yd out*", ha="right", va="center", fontsize=9.5, color=INK2)
ax.set_xlim(0, 11.5)
ax.set_ylim(-0.6, len(t) - 0.1)
ax.tick_params(left=False, bottom=False, labelbottom=False)
for s in ax.spines.values(): s.set_visible(False)

fig.text(0.06, 0.92, "Headers go in more often\nthan shots with the feet", fontsize=20,
         fontweight="bold", color=INK, va="top", linespacing=1.15)
fig.text(0.06, 0.785, "Goal rate by body part · non-penalty shots", fontsize=10.5, color=INK2)
fig.text(0.06, 0.165, "…because they're taken from much closer to goal. From the same spot,\n"
         "a header has about a third of the odds of scoring.", fontsize=10.5, color=INK, va="top", linespacing=1.35)
fig.text(0.06, 0.04, "*Median distance to goal centre.  Data: StatsBomb Open Data (WC 2018/22, Euro 2020/24, PL 2015/16)\n"
         "github.com/CarsonCowburn/soccer-xg-model", fontsize=7.5, color=MUTED, va="bottom", linespacing=1.4)
out = f"{root}/reports/figures/linkedin_body_part.png"
fig.savefig(out, dpi=200, facecolor=BG)
print(out, t.round(3).to_dict())
