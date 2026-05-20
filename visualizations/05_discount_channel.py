"""
05_discount_channel.py
Charts: discount depth vs repeat rate + LTV, marketplace vs website comparison,
        RFM segments, country mix

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
from style import save, TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LIGHT_BG, LILAC

_outputs = Path(__file__).resolve().parent.parent / "EDA" / "outputs"

# ── Chart 1: Discount depth — repeat rate and LTV ────────────────────────────
# Source: EDA/outputs/05_discount_depth_bins.csv
_dd = pd.read_csv(_outputs / "05_discount_depth_bins.csv")
_bin_order = ["0% (full price)", "1-5%", "6-10%", "11-20%", "21-30%", "31-50%", "51%+"]
_bin_display = ["Full price", "1-5% off", "6-10% off", "11-20% off", "21-30% off", "31-50% off", "51%+ off"]
_dd = _dd[_dd["discount_bin"].isin(_bin_order)].set_index("discount_bin").reindex(_bin_order).reset_index()

disc_bins = _bin_display
rr_vals   = (_dd["repeat_rate"] * 100).round(1).tolist()
ltv_vals  = _dd["avg_ltv"].round(0).astype(int).tolist()
n_custs   = _dd["customers"].astype(int).tolist()

fig, ax1 = plt.subplots(figsize=(13, 6))
x = np.arange(len(disc_bins))
bar_colors = [TEAL] + [ORANGE if r > 24 else RED for r in rr_vals[1:]]
bars = ax1.bar(x, rr_vals, color=bar_colors, width=0.55, zorder=3, alpha=0.9)
ax1.set_xticks(x); ax1.set_xticklabels(disc_bins, fontsize=10.5)
ax1.set_title("Discount Depth vs Repeat Rate and LTV — First Order")
ax1.set_ylabel("Repeat Purchase Rate (%)", fontsize=11, color=NAVY)
ax1.set_ylim(0, max(rr_vals) * 1.5)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))

for bar, v, n in zip(bars, rr_vals, n_custs):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
             f"{v:.1f}%", ha="center", va="bottom", fontsize=9.5, color=NAVY, fontweight="bold")
    ax1.text(bar.get_x()+bar.get_width()/2, 1,
             f"n={n:,}", ha="center", va="bottom", fontsize=7.5, color="white")

ax2 = ax1.twinx()
ax2.plot(x, ltv_vals, color=RED, marker="D", linewidth=2.5, markersize=8, zorder=4, label="Avg LTV")
ax2.set_ylabel("Average LTV (SGD)", color=RED, fontsize=11)
ax2.set_ylim(0, max(ltv_vals) * 1.6)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v:.0f}"))
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(RED)
ax2.tick_params(axis="y", colors=RED)
for xi, v in enumerate(ltv_vals):
    ax2.text(xi, v + max(ltv_vals)*0.05, f"S${v}", ha="center", fontsize=9, color=RED)

drop_pct = round((rr_vals[-1] - rr_vals[0]) / rr_vals[0] * 100, 0)
ax1.annotate("", xy=(len(disc_bins)-1, rr_vals[-1]), xytext=(0, rr_vals[0]),
             arrowprops=dict(arrowstyle="->", color=RED, lw=2))
ax1.text(len(disc_bins)//2, max(rr_vals)*1.2,
         f"{drop_pct:.0f}% repeat rate drop\nfull price → 51%+ off",
         ha="center", fontsize=9, color=RED, fontweight="bold")

fig.tight_layout()
save(fig, "05a_discount_depth_impact")

# ── Chart 2: Marketplace vs website spider/bar comparison ─────────────────────
# Source: EDA/outputs/05_channel_quality.csv
_cq = pd.read_csv(_outputs / "05_channel_quality.csv")
_cq["first_channel"] = _cq["first_channel"].str.replace(" / ", "/", regex=False)

_mkt = _cq[_cq["first_channel"] == "Marketplace"].iloc[0]
_web_channels = ["Direct/Organic", "Paid Social", "Paid Search", "Email", "Affiliate"]
_web = _cq[_cq["first_channel"].isin(_web_channels)]
_web_custs = _web["customers"].sum()

mkt_rr       = round(float(_mkt["repeat_rate"]) * 100, 1)
mkt_ltv      = round(float(_mkt["avg_ltv"]), 0)
mkt_orders   = round(float(_mkt["avg_orders"]), 2)
mkt_sub_pct  = round(float(_mkt["pct_subscribed"]) * 100, 1)

web_rr       = round((_web["repeaters"].sum() / _web["customers"].sum()) * 100, 1)
web_ltv      = round((_web["avg_ltv"] * _web["customers"]).sum() / _web_custs, 0)
web_orders   = round((_web["avg_orders"] * _web["customers"]).sum() / _web_custs, 2)
web_sub_pct  = round((_web["pct_subscribed"] * _web["customers"]).sum() / _web_custs * 100, 1)

metrics_labels = ["Repeat Rate (%)", "Avg LTV (SGD)", "Avg Orders", "% Subscribed*"]
mkt_vals = [mkt_rr, mkt_ltv, mkt_orders, mkt_sub_pct]
web_vals = [web_rr, web_ltv, web_orders, web_sub_pct]
mkt_norm = [m/w*100 if w > 0 else 0 for m, w in zip(mkt_vals, web_vals)]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
x = np.arange(len(metrics_labels)); w = 0.38
b1 = axes[0].bar(x-w/2, [100]*4, width=w, color=TEAL, label="Own Website", zorder=3)
b2 = axes[0].bar(x+w/2, mkt_norm, width=w, color=RED,  label="Marketplace",  zorder=3)
axes[0].set_xticks(x); axes[0].set_xticklabels(metrics_labels, fontsize=9.5, rotation=10)
axes[0].set_title("Marketplace vs Own Website\n(Indexed: Website = 100 | *Shopify subscriptions only)",
                  fontsize=10, fontweight="bold")
axes[0].set_ylabel("Index (Website = 100)", fontsize=10)
axes[0].legend()
axes[0].axhline(100, color=SLATE, linewidth=1, linestyle="--", alpha=0.5)

actual_web = [f"{web_rr}%", f"S${web_ltv:.0f}", f"{web_orders:.2f}", f"{web_sub_pct}%"]
actual_mkt = [f"{mkt_rr}%", f"S${mkt_ltv:.0f}", f"{mkt_orders:.2f}", f"{mkt_sub_pct}%*"]
for bar, lbl in zip(b1, actual_web):
    axes[0].text(bar.get_x()+bar.get_width()/2, 103, lbl, ha="center", fontsize=8, color=TEAL)
for i, (bar, lbl, mn) in enumerate(zip(b2, actual_mkt, mkt_norm)):
    axes[0].text(bar.get_x()+bar.get_width()/2, mn+2, lbl, ha="center", fontsize=8, color=RED)

# Country mix — order counts from 02_orders_by_country.csv
_ctry = pd.read_csv(_outputs / "02_orders_by_country.csv")
_ctry = _ctry.sort_values("orders", ascending=False).reset_index(drop=True)
_top5 = _ctry.head(5)
_other_orders = _ctry.iloc[5:]["orders"].sum()
countries = _top5["Shipping: Country"].tolist() + ["Other"]
order_n   = _top5["orders"].astype(int).tolist() + [int(_other_orders)]
c_colors  = [NAVY, TEAL, ORANGE, GOLD, SLATE, LILAC]

wedges, _, autotexts = axes[1].pie(
    order_n, labels=None, colors=c_colors,
    autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
    startangle=90,
    wedgeprops=dict(width=0.6, edgecolor="white", linewidth=2),
    pctdistance=0.75,
)
for at in autotexts:
    at.set_fontsize(10); at.set_fontweight("bold"); at.set_color("white")
legend_labels = [f"{c}  ({n:,} orders)" for c, n in zip(countries, order_n)]
axes[1].legend(wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.22),
               ncol=2, fontsize=8.5)
axes[1].set_title("Order Volume by Country", fontsize=11, fontweight="bold")

fig.tight_layout()
save(fig, "05b_marketplace_vs_website")

# ── Chart 3: RFM segment breakdown ───────────────────────────────────────────
# Source: EDA/outputs/03_rfm_segments.csv
_rfm_full = pd.read_csv(_outputs / "03_rfm_segments.csv")
_rfm_seg = (
    _rfm_full.groupby("segment")
    .agg(n=("customer_id","count"), avg_ltv=("total_revenue","mean"))
    .reset_index()
    .sort_values("n", ascending=False)
)
_seg_order = ["Loyal", "Hibernating", "At Risk", "Champions", "Cant Lose", "Promising", "New Customers"]
_rfm_seg = _rfm_seg[_rfm_seg["segment"].isin(_seg_order)].set_index("segment").reindex(_seg_order).reset_index()

segments     = _rfm_seg["segment"].tolist()
seg_counts   = _rfm_seg["n"].astype(int).tolist()
seg_ltv      = _rfm_seg["avg_ltv"].round(0).astype(int).tolist()
seg_colors   = [TEAL, SLATE, ORANGE, NAVY, RED, GOLD, LILAC]
seg_priority = ["Cross-sell","Reactivate low-cost","Win-back NOW","Reward & upsell",
                "Re-engage urgently","Nurture to 2nd order","Welcome"]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

ax = axes[0]
for i, (s, c, l, col) in enumerate(zip(segments, seg_counts, seg_ltv, seg_colors)):
    ax.scatter(l, c, s=c/8, color=col, alpha=0.7, zorder=3)
    ax.annotate(s, xy=(l, c), xytext=(5, 5), textcoords="offset points",
                fontsize=9, color=col, fontweight="bold")
ax.set_xlabel("Average LTV (SGD)", fontsize=11)
ax.set_ylabel("Number of Customers", fontsize=11)
ax.set_title("RFM Segments — Customers vs LTV\n(Bubble size = customer count)", fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v:,.0f}"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,}"))
ax.grid(True, alpha=0.4)

y = np.arange(len(segments))
axes[1].barh(y, seg_counts, color=seg_colors, height=0.58, zorder=3)
axes[1].set_yticks(y)
axes[1].set_yticklabels([f"{s}\n{p}" for s, p in zip(segments, seg_priority)], fontsize=9)
axes[1].set_title("RFM Segment Size & Priority Actions", fontsize=12, fontweight="bold")
axes[1].set_xlabel("Number of Customers", fontsize=10)
for i, v in enumerate(seg_counts):
    axes[1].text(v+30, i, f"{v:,}  (avg S${seg_ltv[i]:,})", va="center", fontsize=8.5, color=NAVY)
axes[1].set_xlim(0, max(seg_counts)*1.4)
axes[1].grid(axis="x"); axes[1].grid(axis="y", visible=False)
axes[1].spines["left"].set_visible(False); axes[1].tick_params(left=False)

fig.tight_layout()
save(fig, "05c_rfm_segments")

# ── Chart 4: Discount code taxonomy ──────────────────────────────────────────
# Source: EDA/outputs/05_discount_code_taxonomy.csv
_dt = pd.read_csv(_outputs / "05_discount_code_taxonomy.csv")
_dt = _dt.sort_values("total_redemptions", ascending=False).reset_index(drop=True)
code_types  = _dt["code_type"].tolist()
redemptions = _dt["total_redemptions"].astype(int).tolist()
total_redemptions = sum(redemptions)
type_colors = [SLATE, TEAL, NAVY, ORANGE, RED, GOLD, LILAC][:len(code_types)]

fig, ax = plt.subplots(figsize=(10, 5))
wedges, _, autotexts = ax.pie(
    redemptions, labels=None, colors=type_colors,
    autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
    startangle=120,
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    pctdistance=0.75,
)
for at in autotexts:
    at.set_fontsize(10); at.set_fontweight("bold"); at.set_color("white")
legend_labels = [f"{t}  ({r:,} uses)" for t, r in zip(code_types, redemptions)]
ax.legend(wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9)
ax.set_title(f"Discount Code Redemptions by Type\n({total_redemptions:,} total redemptions)",
             fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "05d_discount_code_taxonomy")

print("Done – 05_discount_channel")
