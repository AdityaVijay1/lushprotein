"""
06_channel_quality_chart.py
Recreates the dual-panel channel quality chart (Picture1 style):
  Left  — Repeat Rate by Acquisition Channel (horizontal bars, color-coded, n= labels)
  Right — Average LTV by Acquisition Channel (SGD) (horizontal bars, S$ labels)

Data: combined SG + MY + HK markets, all revenue in SGD.
FX assumption: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average rate, 2020–2026).
Source: EDA/outputs/05_channel_quality.csv  (verified May 2026)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
from style import save, TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LIGHT_BG, GRID_LINE

# ── Data: read from EDA/outputs/05_channel_quality.csv (no hardcoded values) ──
_outputs = Path(__file__).resolve().parent.parent / "EDA" / "outputs"
_cq = pd.read_csv(_outputs / "05_channel_quality.csv")
_cq["first_channel"] = _cq["first_channel"].str.replace(" / ", "/", regex=False)
_ch_order = ["Subscription", "Direct/Organic", "Paid Social", "Affiliate", "Marketplace", "Email"]
_cq = _cq[_cq["first_channel"].isin(_ch_order)].set_index("first_channel").reindex(_ch_order).reset_index()

channels    = _cq["first_channel"].tolist()
rr          = (_cq["repeat_rate"] * 100).round(1).tolist()
ltv         = _cq["avg_ltv"].round(0).astype(int).tolist()
n_custs     = _cq["customers"].astype(int).tolist()
overall_avg = round(_cq["repeaters"].sum() / _cq["customers"].sum() * 100, 1)

# ── Colour coding — green (high), orange (mid), red (low) ────────────────────
def rr_color(r):
    if r >= 30: return TEAL
    if r >= 18: return ORANGE
    return RED

def ltv_color(v):
    if v >= 300: return TEAL
    if v >= 100: return GOLD
    return RED

rr_colors  = [rr_color(r)  for r in rr]
ltv_colors = [ltv_color(v) for v in ltv]

# ── Build figure (two panels, 14 × 5) ────────────────────────────────────────
fig, (ax_rr, ax_ltv) = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor(LIGHT_BG)

BAR_H = 0.52

# ─── LEFT: Repeat Rate ───────────────────────────────────────────────────────
y_pos = np.arange(len(channels))
bars_rr = ax_rr.barh(
    y_pos, rr[::-1], color=rr_colors[::-1],
    height=BAR_H, zorder=3, edgecolor="white", linewidth=0.4
)

# Overall average dashed line
ax_rr.axvline(overall_avg, color=NAVY, linewidth=1.5, linestyle="--", alpha=0.7, zorder=4)
ax_rr.annotate(
    f"Overall avg\n{overall_avg}%",
    xy=(overall_avg, 0.15), xytext=(overall_avg + 2.5, 1.35),
    fontsize=8.5, color=NAVY, fontweight="bold",
    arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2),
)

# Bar labels: "40.9%  (n=4,275)"
for i, (r, n) in enumerate(zip(rr[::-1], n_custs[::-1])):
    ax_rr.text(
        r + 0.6, i,
        f"{r:.1f}%  (n={n:,})",
        va="center", ha="left", fontsize=9, color=NAVY, fontweight="bold"
    )

ax_rr.set_yticks(y_pos)
ax_rr.set_yticklabels(channels[::-1], fontsize=10.5, color=NAVY)
ax_rr.set_xlabel("Repeat Purchase Rate (%)", fontsize=10, color=SLATE)
ax_rr.set_title("Repeat Rate by Acquisition Channel", fontsize=13, fontweight="bold", color=NAVY, pad=14)
ax_rr.set_xlim(0, 62)
ax_rr.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax_rr.spines["left"].set_visible(False)
ax_rr.spines["bottom"].set_alpha(0.3)
ax_rr.tick_params(left=False)
ax_rr.grid(axis="x", color=GRID_LINE, linewidth=1, zorder=0)
ax_rr.grid(axis="y", visible=False)
ax_rr.set_facecolor(LIGHT_BG)

# ─── RIGHT: Average LTV ──────────────────────────────────────────────────────
ax_ltv.barh(
    y_pos, ltv[::-1], color=ltv_colors[::-1],
    height=BAR_H, zorder=3, edgecolor="white", linewidth=0.4
)

# Bar labels: "S$343"
for i, v in enumerate(ltv[::-1]):
    ax_ltv.text(
        v + 4, i,
        f"S${v:,}",
        va="center", ha="left", fontsize=9, color=NAVY, fontweight="bold"
    )

ax_ltv.set_yticks(y_pos)
ax_ltv.set_yticklabels(channels[::-1], fontsize=10.5, color=NAVY)
ax_ltv.set_xlabel("Avg Customer LTV (SGD)", fontsize=10, color=SLATE)
ax_ltv.set_title("Average LTV by Acquisition Channel (SGD)", fontsize=13, fontweight="bold", color=NAVY, pad=14)
ax_ltv.set_xlim(0, 430)
ax_ltv.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"S${v:.0f}"))
ax_ltv.spines["left"].set_visible(False)
ax_ltv.spines["bottom"].set_alpha(0.3)
ax_ltv.tick_params(left=False)
ax_ltv.grid(axis="x", color=GRID_LINE, linewidth=1, zorder=0)
ax_ltv.grid(axis="y", visible=False)
ax_ltv.set_facecolor(LIGHT_BG)

# ─── Legend ──────────────────────────────────────────────────────────────────
legend_patches = [
    mpatches.Patch(color=TEAL,   label="High performer  (RR ≥ 30%)"),
    mpatches.Patch(color=ORANGE, label="Mid performer   (18–30%)"),
    mpatches.Patch(color=RED,    label="Low performer   (< 18%)"),
]
fig.legend(
    handles=legend_patches,
    loc="lower center", ncol=3,
    fontsize=9, frameon=False,
    bbox_to_anchor=(0.5, -0.06),
)

# ─── Footnote ─────────────────────────────────────────────────────────────────
fig.text(
    0.5, -0.10,
    "Combined SG + MY + HK markets · All revenue in SGD (1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD)\n"
    "Marketplace 0% subscribed = Shopify subscriptions only; Shopee/Lazada subscriptions not tracked here.",
    ha="center", fontsize=8, color=SLATE, style="italic"
)

fig.tight_layout(pad=2.5)
save(fig, "06a_channel_quality_dual")
print("Done: charts/06a_channel_quality_dual.png")
