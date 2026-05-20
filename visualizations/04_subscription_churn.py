"""
04_subscription_churn.py
Charts: subscriber vs one-time LTV, subscription churn by cycle,
        cancellation reasons, subscriber tenure distribution

All data read from EDA/outputs CSVs -- no hardcoded values.
FX assumption: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, 2020-2026).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from style import save, TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LIGHT_BG, LILAC

_outputs = Path(__file__).resolve().parent.parent / "EDA" / "outputs"

# -- Chart 1: Subscriber vs one-time LTV metrics --------------------------------
# Source: EDA/outputs/06_sub_vs_onetime_ltv.csv
_sv = pd.read_csv(_outputs / "06_sub_vs_onetime_ltv.csv", index_col=0)
_sub    = _sv.loc["Subscriber"]
_nonsub = _sv.loc["One-time / Non-subscriber"]

sub_rr     = round(float(_sub["repeat_rate"])  * 100, 1)
sub_ltv    = round(float(_sub["avg_ltv"]),     0)
sub_orders = round(float(_sub["avg_orders"]),  2)
sub_days   = round(float(_sub["median_days_2nd"]), 0)

ns_rr     = round(float(_nonsub["repeat_rate"])  * 100, 1)
ns_ltv    = round(float(_nonsub["avg_ltv"]),     0)
ns_orders = round(float(_nonsub["avg_orders"]),  2)
ns_days   = round(float(_nonsub["median_days_2nd"]), 0)

ltv_uplift_pct = round((sub_ltv / ns_ltv - 1) * 100, 0)

# Scale values to fit same chart axis: Repeat Rate (%), LTV (SGD), Ordersx10, Days/10
sub_vals    = [sub_rr,  sub_ltv,  sub_orders * 10,  sub_days / 10]
nonsub_vals = [ns_rr,   ns_ltv,   ns_orders  * 10,  ns_days  / 10]
labels_sub  = [f"{sub_rr}%", f"S${sub_ltv:.0f}", f"{sub_orders:.2f} orders", f"{sub_days:.0f} days"]
labels_non  = [f"{ns_rr}%",  f"S${ns_ltv:.0f}",  f"{ns_orders:.2f} orders",  f"{ns_days:.0f} days"]

fig, ax = plt.subplots(figsize=(11, 6))
x = np.arange(4); w = 0.35
b1 = ax.bar(x-w/2, sub_vals,   width=w, color=TEAL, label="Subscriber",     zorder=3)
b2 = ax.bar(x+w/2, nonsub_vals,width=w, color=SLATE, label="Non-subscriber", zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(["Repeat Rate (%)", "Avg LTV (SGD)", "Avg Orders", "Median Days to 2nd"], fontsize=10)
ax.set_title("Subscriber vs Non-Subscriber: Key Metrics (Combined SG+MY+HK in SGD)")
ax.legend()

for bar, lbl in zip(b1, labels_sub):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+10,
            lbl, ha="center", va="bottom", fontsize=9, color=TEAL, fontweight="bold")
for bar, lbl in zip(b2, labels_non):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+10,
            lbl, ha="center", va="bottom", fontsize=9, color=SLATE, fontweight="bold")

ax.annotate(f"+{ltv_uplift_pct:.0f}%\nLTV uplift",
            xy=(-0.17, sub_ltv * 0.85), xytext=(0.5, sub_ltv * 1.05),
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.5), fontsize=9, color=RED, fontweight="bold")
fig.tight_layout()
save(fig, "04a_subscriber_vs_onetime")

# -- Chart 2: Subscription churn by cycle -------------------------------------
# Source: EDA/outputs/06_churn_by_cycle.csv
_cc = pd.read_csv(_outputs / "06_churn_by_cycle.csv")
_cc = _cc[_cc["approx_cycle"] <= 6].sort_values("approx_cycle").reset_index(drop=True)

cycles   = _cc["cycle_label"].tolist()
churn_n  = _cc["n_cancellations"].astype(int).tolist()
cumulative = list(np.cumsum(churn_n))

# Annotate cycle labels with day ranges
_cycle_day_labels = {
    "Cycle 0": "(<30d)", "Cycle 1": "(30-60d)", "Cycle 2": "(60-90d)",
    "Cycle 3": "(90-120d)", "Cycle 4": "(120-150d)", "Cycle 5": "(150-180d)", "Cycle 6": "(180-210d)"
}
cycles_display = [f"{c}\n{_cycle_day_labels.get(c,'')}" for c in cycles]

peak_cycle_idx = churn_n.index(max(churn_n))

fig, ax1 = plt.subplots(figsize=(12, 6))
bar_colors = [ORANGE, RED, RED, ORANGE, GOLD, SLATE, ORANGE][:len(cycles)]
bars = ax1.bar(cycles_display, churn_n, color=bar_colors, width=0.58, zorder=3)
ax1.set_title("When Do Subscribers Cancel? -- Churn by Subscription Cycle")
ax1.set_ylabel("Subscribers Cancelled", fontsize=11)
ax1.set_xlabel("Subscription Cycle  (1 cycle approx 30 days = 1 product tub)", fontsize=10)
ax1.set_ylim(0, max(churn_n) * 1.4)
for bar, v in zip(bars, churn_n):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5,
             str(v), ha="center", va="bottom", fontsize=11, fontweight="bold", color=NAVY)

ax2 = ax1.twinx()
ax2.plot(cycles_display, cumulative, color=NAVY, marker="s", linewidth=2, markersize=7, zorder=4, label="Cumulative")
ax2.set_ylabel("Cumulative Cancellations", color=NAVY, fontsize=11)
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(NAVY)
ax2.tick_params(axis="y", colors=NAVY)

ax1.axvspan(0.5, 1.5, alpha=0.08, color=RED)
ax1.text(1.0, max(churn_n)*1.25, f"Cycle 1: peak churn window\n(30-60 days)", ha="center",
         fontsize=9, color=RED, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=RED, alpha=0.8))

fig.tight_layout()
save(fig, "04b_churn_by_cycle")

# -- Chart 3: Cancellation reasons horizontal bar -----------------------------
# Source: EDA/outputs/06_churn_reasons.csv
_cr = pd.read_csv(_outputs / "06_churn_reasons.csv")
_cr = _cr.sort_values("n", ascending=False).head(7).reset_index(drop=True)

reasons      = _cr["cancellation_reason"].tolist()
counts       = _cr["n"].astype(int).tolist()
total_churn  = _cr["n"].sum()
pcts         = [round(c / total_churn * 100, 1) for c in counts]
theme_colors = [ORANGE, SLATE, GOLD, SLATE, RED, TEAL, NAVY][:len(reasons)]

fig, ax = plt.subplots(figsize=(12, 6))
y = np.arange(len(reasons))
bars = ax.barh(y, counts, color=theme_colors, height=0.58, zorder=3)
ax.set_yticks(y); ax.set_yticklabels(reasons, fontsize=9)
ax.set_title("Why Subscribers Cancel -- Cancellation Reasons Breakdown")
ax.set_xlabel("Number of Cancellations", fontsize=10)
for i, (v, p) in enumerate(zip(counts, pcts)):
    ax.text(v+1, i, f"{v}  ({p:.1f}%)", va="center", fontsize=10, color=NAVY)

top_reason = reasons[0]
if "have more" in top_reason.lower() or "already" in top_reason.lower() or "too much" in top_reason.lower():
    ax.annotate("Cadence mismatch --\nnot satisfaction failure",
                xy=(counts[0], len(reasons)-1), xytext=(counts[0]*0.65, len(reasons)-1.8),
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.5),
                fontsize=9, color=ORANGE, fontweight="bold")

ax.set_xlim(0, max(counts)*1.4)
ax.grid(axis="x"); ax.grid(axis="y", visible=False)
ax.spines["left"].set_visible(False); ax.tick_params(left=False)
fig.tight_layout()
save(fig, "04c_cancellation_reasons")

# -- Chart 4: Churn tenure distribution ----------------------------------------
# Source: EDA/outputs/06_churn_tenure.csv
_ct = pd.read_csv(_outputs / "06_churn_tenure.csv")

tenure_bins = _ct["tenure_bin"].tolist()
tenure_n    = _ct["n"].astype(int).tolist()
tenure_pct  = (_ct["pct"] * 100).round(1).tolist()

cum_first2_pct = sum(tenure_pct[:2])

fig, ax = plt.subplots(figsize=(11, 5))
colors = [RED if p > 20 else ORANGE if p > 13 else GOLD if p > 10 else SLATE for p in tenure_pct]
bars = ax.bar(tenure_bins, tenure_pct, color=colors, width=0.6, zorder=3)
ax.set_title("Subscription Tenure at Time of Cancellation")
ax.set_ylabel("% of Cancellations", fontsize=11)
ax.set_xlabel("How Long They Were Subscribed Before Cancelling", fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
for bar, v, n in zip(bars, tenure_pct, tenure_n):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
            f"{v:.1f}%\n(n={n})", ha="center", va="bottom", fontsize=9, color=NAVY)
ax.set_ylim(0, max(tenure_pct)*1.6)

ax.annotate(f"First 60 days:\n{cum_first2_pct:.0f}% of all cancellations",
            xy=(1, tenure_pct[1]), xytext=(3, max(tenure_pct)*1.3),
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.5),
            color=RED, fontsize=9, fontweight="bold")

fig.tight_layout()
save(fig, "04d_churn_tenure_distribution")

print("Done - 04_subscription_churn")
