"""
02_retention_overview.py
Charts: repeat rate by channel, repeat rate by product, time-to-2nd-purchase,
        monthly cohort 60-day retention

All data read from EDA/outputs CSVs — no hardcoded values.
FX assumption: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, 2020–2026).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from style import save, TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LIGHT_BG, LILAC, bar_label, hbar_label

_outputs = Path(__file__).resolve().parent.parent / "EDA" / "outputs"

# ── Chart 1: Repeat rate + avg LTV by channel ─────────────────────────────────
# Source: EDA/outputs/05_channel_quality.csv
_cq = pd.read_csv(_outputs / "05_channel_quality.csv")
_cq["first_channel"] = _cq["first_channel"].str.replace(" / ", "/", regex=False)
_ch_order = ["Subscription", "Direct/Organic", "Paid Social", "Affiliate", "Marketplace", "Email"]
_cq = _cq[_cq["first_channel"].isin(_ch_order)].set_index("first_channel").reindex(_ch_order).reset_index()

channels     = _cq["first_channel"].tolist()
repeat_rates = (_cq["repeat_rate"] * 100).round(1).tolist()
avg_ltv      = _cq["avg_ltv"].round(0).astype(int).tolist()
n_customers  = _cq["customers"].astype(int).tolist()
overall_avg  = round((_cq["repeaters"].sum() / _cq["customers"].sum()) * 100, 1)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

colors_rr = [TEAL if r > 25 else ORANGE if r > 15 else RED for r in repeat_rates]
axes[0].barh(channels[::-1], repeat_rates[::-1], color=colors_rr[::-1], height=0.55, zorder=3)
axes[0].set_title("Repeat Rate by Acquisition Channel", fontsize=13, fontweight="bold")
axes[0].set_xlabel("Repeat Purchase Rate (%)", fontsize=10)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
axes[0].axvline(overall_avg, color=NAVY, linewidth=1.5, linestyle="--", alpha=0.6)
axes[0].annotate(f"Overall avg\n{overall_avg}%", xy=(overall_avg, 0.3), xytext=(overall_avg+2, 1.2),
                 fontsize=8, color=NAVY, arrowprops=dict(arrowstyle="->", color=NAVY, lw=1))
for i, (v, n) in enumerate(zip(repeat_rates[::-1], n_customers[::-1])):
    axes[0].text(v+0.5, i, f"{v:.1f}%  (n={n:,})", va="center", fontsize=9, color=NAVY)
axes[0].set_xlim(0, 60)
axes[0].spines["left"].set_visible(False); axes[0].tick_params(left=False)

ltv_colors = [TEAL if l > 300 else GOLD if l > 150 else RED for l in avg_ltv]
axes[1].barh(channels[::-1], avg_ltv[::-1], color=ltv_colors[::-1], height=0.55, zorder=3)
axes[1].set_title("Average LTV by Acquisition Channel (SGD)", fontsize=13, fontweight="bold")
axes[1].set_xlabel("Avg Customer LTV (SGD)", fontsize=10)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v:.0f}"))
for i, v in enumerate(avg_ltv[::-1]):
    axes[1].text(v+5, i, f"S${v:,}", va="center", fontsize=9, color=NAVY)
axes[1].set_xlim(0, 420)
axes[1].spines["left"].set_visible(False); axes[1].tick_params(left=False)

for ax in axes:
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)

fig.tight_layout(pad=2)
save(fig, "02a_retention_by_channel")

# ── Chart 2: Repeat rate by first product ─────────────────────────────────────
# Source: EDA/outputs/04_repeat_by_first_product.csv
_pp = pd.read_csv(_outputs / "04_repeat_by_first_product.csv")
_hero_cats = ["Collagen Glow", "Lean Protein", "Clear Protein", "Accessories", "Soy Protein"]
_pp = _pp[_pp["first_product_cat"].isin(_hero_cats)].copy()
_pp["repeat_rate"] = pd.to_numeric(_pp["repeat_rate"], errors="coerce")
_pp["avg_ltv"]     = pd.to_numeric(_pp["avg_ltv"],     errors="coerce")
_pp["median_days_2nd"] = pd.to_numeric(_pp["median_days_2nd"], errors="coerce")
_pp = _pp.set_index("first_product_cat").reindex(_hero_cats).reset_index()

products  = _pp["first_product_cat"].tolist()
prod_rr   = (_pp["repeat_rate"] * 100).round(1).tolist()
prod_ltv  = _pp["avg_ltv"].round(0).astype(int).tolist()
prod_days = _pp["median_days_2nd"].round(0).astype(int).tolist()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
prod_colors = [TEAL, NAVY, ORANGE, SLATE, GOLD]

for ax, vals, title, fmt in [
    (axes[0], prod_rr,  "Repeat Rate (%)",           "{:.1f}%"),
    (axes[1], prod_ltv, "Avg LTV (SGD)",              "S${:.0f}"),
    (axes[2], prod_days,"Median Days to 2nd Purchase","{}d"),
]:
    x = np.arange(len(products))
    bars = ax.bar(x, vals, color=prod_colors, width=0.55, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(products, rotation=25, ha="right", fontsize=9)
    ax.set_title(title, fontsize=12, fontweight="bold")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                fmt.format(v), ha="center", va="bottom", fontsize=9, color=NAVY)

axes[0].set_ylim(0, max(prod_rr)*1.3)
axes[1].set_ylim(0, max(prod_ltv)*1.3)
axes[2].set_ylim(0, max(prod_days)*1.3)
fig.suptitle("Hero Product Comparison — Retention Metrics", fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "02b_retention_by_product")

# ── Chart 3: Time-to-second-purchase histogram ────────────────────────────────
# Source: EDA/outputs/03_time_to_second_purchase.csv
_t2 = pd.read_csv(_outputs / "03_time_to_second_purchase.csv")
buckets    = _t2["bucket"].tolist()
pct        = (_t2["pct_of_repeaters"] * 100).round(1).tolist()
cumulative = (_t2["cum_pct"] * 100).round(1).tolist()

# 60-day mark: find last bucket that starts before/at 60d
_60d_cum = round((_t2[_t2["bucket"].isin(["0-7d","8-14d","15-21d","22-30d","31-45d","46-60d"])]["pct_of_repeaters"].sum())*100, 1)

fig, ax1 = plt.subplots(figsize=(13, 6))
bar_colors = [TEAL if i == 6 else (ORANGE if i < 4 else SLATE) for i in range(len(buckets))]
bars = ax1.bar(buckets, pct, color=bar_colors, width=0.65, zorder=3)
ax1.set_title("Time to Second Purchase — Distribution of Repeating Customers")
ax1.set_ylabel("% of Repeaters in Window", fontsize=11)
ax1.set_xlabel("Days Since First Order", fontsize=11)
for bar, v in zip(bars, pct):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.15,
             f"{v:.1f}%", ha="center", va="bottom", fontsize=9, color=NAVY)

ax2 = ax1.twinx()
ax2.plot(buckets, cumulative, color=NAVY, marker="o", linewidth=2, markersize=6, zorder=4)
ax2.set_ylabel("Cumulative % of Repeaters", color=NAVY, fontsize=11)
ax2.set_ylim(0, 115)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(NAVY)
ax2.axvline(x=5.5, color=RED, linestyle="--", linewidth=1.5, alpha=0.7)
ax2.text(5.7, 50, f"60-day mark\n~{_60d_cum:.0f}% have returned", color=RED, fontsize=9)
ax1.annotate("Last bucket\nin 60-day window", xy=(5, pct[5]), xytext=(6.5, 12),
             arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.5), color=TEAL, fontsize=9)

fig.tight_layout()
save(fig, "02c_time_to_second_purchase")

# ── Chart 4: Monthly cohort 60-day retention ─────────────────────────────────
# Source: EDA/outputs/03_cohort_retention_heatmap.csv
_cr = pd.read_csv(_outputs / "03_cohort_retention_heatmap.csv")
_cr["cohort_month"] = _cr["cohort_month"].astype(str)
_cr = _cr.tail(24).reset_index(drop=True)

cohort_labels = pd.to_datetime(_cr["cohort_month"]).dt.strftime("%b-%y").tolist()
retention_60d = (_cr["retention_60d"] * 100).round(1).tolist()
cohort_sizes  = _cr["cohort_size"].astype(int).tolist()

fig, ax = plt.subplots(figsize=(14, 6))
x = np.arange(len(cohort_labels))
bar_colors = [TEAL if r > 18 else ORANGE if r > 13 else RED for r in retention_60d]
bars = ax.bar(x, retention_60d, color=bar_colors, width=0.65, zorder=3, alpha=0.85)
avg_60d = sum(r * s for r, s in zip(retention_60d, cohort_sizes)) / sum(cohort_sizes)
ax.axhline(avg_60d, color=NAVY, linewidth=2, linestyle="--", alpha=0.8,
           label=f"Wtd avg {avg_60d:.1f}%")
ax.set_xticks(x); ax.set_xticklabels(cohort_labels, rotation=40, ha="right", fontsize=8.5)
ax.set_title("60-Day Retention Rate by Monthly Acquisition Cohort")
ax.set_ylabel("% Returning Within 60 Days", fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax.set_ylim(0, max(retention_60d) * 1.5)

peak_idx = retention_60d.index(max(retention_60d))
ax.annotate(f"{cohort_labels[peak_idx]} peak\n({retention_60d[peak_idx]:.1f}%)",
            xy=(peak_idx, retention_60d[peak_idx]), xytext=(peak_idx+2, retention_60d[peak_idx]+3),
            arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.3), color=TEAL, fontsize=8.5)

patches = [
    mpatches.Patch(color=TEAL,   label=">18% retention"),
    mpatches.Patch(color=ORANGE, label="13-18% retention"),
    mpatches.Patch(color=RED,    label="<13% retention"),
]
ax.legend(handles=patches + [plt.Line2D([0],[0],color=NAVY,linewidth=2,linestyle="--",
          label=f"Wtd avg {avg_60d:.1f}%")], loc="upper right", fontsize=9)

fig.tight_layout()
save(fig, "02d_cohort_60d_retention")

print("Done – 02_retention_overview")
