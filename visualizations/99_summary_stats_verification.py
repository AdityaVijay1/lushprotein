"""
99_summary_stats_verification.py
Verification charts for DATA_QUALITY_REPORT_FINAL.md Section 2.
Generates: visualizations/charts/99_summary_stats_verification.png
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

BASE  = Path(__file__).resolve().parent.parent
OUT_P = BASE / "EDA" / "outputs"
CHART = Path(__file__).resolve().parent / "charts"
CHART.mkdir(exist_ok=True)

# ── Colours ──────────────────────────────────────────────────────────────────
TEAL  = "#2A9D8F"
AMBER = "#E9C46A"
CORAL = "#E76F51"
NAVY  = "#264653"
SLATE = "#6C757D"
LIGHT = "#F4F4F4"

# ── Load data ─────────────────────────────────────────────────────────────────
o = pd.read_parquet(OUT_P / "orders.parquet")
o["rev"]  = pd.to_numeric(o["Price: Total"],          errors="coerce").fillna(0)
o["disc"] = pd.to_numeric(o["Price: Total Discount"], errors="coerce").fillna(0)
c = pd.read_parquet(OUT_P / "customers.parquet")

sg  = o[o["store"] == "SG"]
my  = o[o["store"] == "MY"]
all_ = o.copy()

# ── Fig setup: 2×3 grid ───────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 14), facecolor="white")
fig.suptitle(
    "LushProtein — Summary Statistics Verification\n"
    "All figures in SGD after FX conversion  |  Source: orders.parquet (27,350 orders)",
    fontsize=14, fontweight="bold", y=0.98, color=NAVY
)

# ── Panel 1: Revenue histogram (log-scale x, all markets) ────────────────────
ax1 = fig.add_subplot(2, 3, 1)
# remove S$0 for log plot but note count
rev_pos = all_["rev"][all_["rev"] > 0]
sg_pos  = sg["rev"][sg["rev"] > 0]
my_pos  = my["rev"][my["rev"] > 0]

bins = np.logspace(np.log10(1), np.log10(40000), 60)
ax1.hist(rev_pos,  bins=bins, alpha=0.65, color=NAVY,  label=f"All markets (n={len(rev_pos):,})", zorder=3)
ax1.hist(sg_pos,   bins=bins, alpha=0.65, color=TEAL,  label=f"SG only (n={len(sg_pos):,})",  zorder=4)
ax1.axvline(all_["rev"].median(), color=NAVY,  lw=1.8, ls="--", label=f"All median S${all_['rev'].median():.2f}")
ax1.axvline(sg["rev"].median(),   color=TEAL,  lw=1.8, ls=":",  label=f"SG median S${sg['rev'].median():.2f}")
ax1.set_xscale("log")
ax1.set_xlabel("Order revenue (SGD, log scale)", fontsize=10)
ax1.set_ylabel("Order count", fontsize=10)
ax1.set_title("Order Revenue Distribution\n(positive-revenue orders only; log x-axis)", fontsize=11, fontweight="bold")
ax1.legend(fontsize=8.5)
ax1.grid(axis="y", alpha=0.3)
ax1.set_facecolor(LIGHT)
zero_count = (all_["rev"] == 0).sum()
ax1.text(0.02, 0.97, f"S$0 orders excluded from plot: {zero_count:,}", transform=ax1.transAxes,
         fontsize=7.5, va="top", color=SLATE, style="italic")

# ── Panel 2: Revenue distribution — box plots by store ───────────────────────
ax2 = fig.add_subplot(2, 3, 2)
data_for_box = [
    all_["rev"][all_["rev"] <= 500].values,
    sg["rev"][sg["rev"]   <= 500].values,
    my["rev"][my["rev"]   <= 500].values,
]
bp = ax2.boxplot(
    data_for_box,
    labels=["All markets", "SG only", "MY only"],
    patch_artist=True,
    medianprops=dict(color="white", linewidth=2.5),
    widths=0.5,
    showfliers=False,
)
colours = [NAVY, TEAL, AMBER]
for patch, col in zip(bp["boxes"], colours):
    patch.set_facecolor(col)
    patch.set_alpha(0.75)
for whisker in bp["whiskers"]:
    whisker.set(color=SLATE, linewidth=1.2)
for cap in bp["caps"]:
    cap.set(color=SLATE, linewidth=1.2)

medians = [all_["rev"].median(), sg["rev"].median(), my["rev"].median()]
means   = [all_["rev"].mean(),   sg["rev"].mean(),   my["rev"].mean()]
for i, (med, mn) in enumerate(zip(medians, means), 1):
    ax2.text(i, med + 5, f"Median\nS${med:.2f}", ha="center", fontsize=7.5, color="white",
             fontweight="bold", va="bottom")
    ax2.text(i, -22, f"Mean: S${mn:.0f}", ha="center", fontsize=7.5, color=NAVY)

ax2.set_ylabel("Order revenue (SGD)", fontsize=10)
ax2.set_title("Revenue Box Plot by Market\n(capped at S$500; outliers hidden)", fontsize=11, fontweight="bold")
ax2.grid(axis="y", alpha=0.3)
ax2.set_facecolor(LIGHT)
ax2.set_ylim(-30, 510)

# ── Panel 3: Orders per customer distribution ─────────────────────────────────
ax3 = fig.add_subplot(2, 3, 3)
cust_all = o.groupby("customer_id")["order_id"].count()
cust_sg  = sg.groupby("customer_id")["order_id"].count()

bins_ord = [1, 2, 3, 4, 5, 6, 8, 10, 15, 25, 670]
labels_ord = ["1", "2", "3", "4", "5", "6–7", "8–9", "10–14", "15–24", "25+"]
cat_all = pd.cut(cust_all, bins=bins_ord, labels=labels_ord, right=True, include_lowest=True)
cat_sg  = pd.cut(cust_sg,  bins=bins_ord, labels=labels_ord, right=True, include_lowest=True)

cnt_all = cat_all.value_counts().sort_index()
cnt_sg  = cat_sg.value_counts().sort_index()

x = np.arange(len(labels_ord))
w = 0.38
ax3.bar(x - w/2, cnt_all.values, width=w, color=NAVY,  alpha=0.8, label=f"All markets (n={len(cust_all):,})", zorder=3)
ax3.bar(x + w/2, cnt_sg.values,  width=w, color=TEAL,  alpha=0.8, label=f"SG only (n={len(cust_sg):,})",  zorder=3)
ax3.set_xticks(x)
ax3.set_xticklabels(labels_ord, rotation=0, fontsize=9)
ax3.set_xlabel("Number of orders placed", fontsize=10)
ax3.set_ylabel("Customer count", fontsize=10)
ax3.set_title("Orders Per Customer Distribution\n(All Markets Combined vs SG Only)", fontsize=11, fontweight="bold")
ax3.legend(fontsize=9)
ax3.grid(axis="y", alpha=0.3)
ax3.set_facecolor(LIGHT)

one_done_all = (cust_all == 1).mean() * 100
one_done_sg  = (cust_sg  == 1).mean() * 100
ax3.text(0.98, 0.97,
         f"One-and-done:\nAll: {one_done_all:.1f}%\nSG: {one_done_sg:.1f}%",
         transform=ax3.transAxes, ha="right", va="top", fontsize=8.5,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=SLATE, alpha=0.8))

# ── Panel 4: Discount depth distribution ──────────────────────────────────────
ax4 = fig.add_subplot(2, 3, 4)
gross = o["rev"] + o["disc"]
depth = np.where(gross > 0, o["disc"] / gross, 0)
o["depth"] = depth

disc_orders = o[o["disc"] > 0].copy()
bins_d  = [-0.001, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.001]
label_d = ["0–5%","5–10%","10–15%","15–20%","20–30%","30–40%","40–50%",
           "50–60%","60–70%","70–80%","80–90%","90–100%"]
db = pd.cut(disc_orders["depth"], bins=bins_d, labels=label_d)
counts_d = db.value_counts().sort_index()
pcts_d   = counts_d / counts_d.sum() * 100

bar_colors = [TEAL if "90" not in l else CORAL for l in label_d]
bars = ax4.bar(range(len(label_d)), counts_d.values, color=bar_colors, alpha=0.85, zorder=3)
ax4.set_xticks(range(len(label_d)))
ax4.set_xticklabels(label_d, rotation=45, ha="right", fontsize=8.5)
ax4.set_xlabel("Discount depth (% of gross order value)", fontsize=10)
ax4.set_ylabel("Order count", fontsize=10)
ax4.set_title(f"Discount Depth Distribution — All Markets\n({len(disc_orders):,} orders with any discount; {len(disc_orders)/len(o)*100:.1f}% of total)",
              fontsize=11, fontweight="bold")
ax4.grid(axis="y", alpha=0.3)
ax4.set_facecolor(LIGHT)
for bar, cnt, pct in zip(bars, counts_d.values, pcts_d.values):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
             f"{cnt:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=7, color=NAVY)
ax4.text(0.98, 0.97, "Red = 90–100% off\n(free fulfilments — DQ-03)",
         transform=ax4.transAxes, ha="right", va="top", fontsize=8,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=CORAL, alpha=0.9))

# ── Panel 5: Revenue by store ──────────────────────────────────────────────────
ax5 = fig.add_subplot(2, 3, 5)
store_rev = o.groupby("store")["rev"].agg(["sum", "count", "mean", "median"]).reset_index()
store_rev.columns = ["store", "total_rev", "orders", "mean_rev", "median_rev"]
store_rev = store_rev[store_rev["store"].isin(["SG", "MY"])].reset_index(drop=True)

x5 = np.arange(len(store_rev))
w5 = 0.35
col5 = [TEAL, AMBER]
bars5 = ax5.bar(x5, store_rev["total_rev"] / 1000, color=col5, alpha=0.85, zorder=3, width=0.5)
ax5.set_xticks(x5)
ax5.set_xticklabels([f"{r['store']}\n{r['orders']:,} orders" for _, r in store_rev.iterrows()], fontsize=10)
ax5.set_ylabel("Total revenue (S$000)", fontsize=10)
ax5.set_title("Total Revenue by Store (SGD)\n(HK: 2 orders, S$319 — excluded from bar)", fontsize=11, fontweight="bold")
ax5.grid(axis="y", alpha=0.3)
ax5.set_facecolor(LIGHT)
for bar, (_, row) in zip(bars5, store_rev.iterrows()):
    pct = row["total_rev"] / o["rev"].sum() * 100
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
             f"S${row['total_rev']/1000:.0f}K\n({pct:.1f}%)\nMed: S${row['median_rev']:.2f}",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=NAVY)
ax5.set_ylim(0, store_rev["total_rev"].max() / 1000 * 1.3)

# ── Panel 6: Revenue percentile comparison (all vs SG vs MY) ─────────────────
ax6 = fig.add_subplot(2, 3, 6)
pcts_vals = [10, 25, 50, 75, 90, 95, 99]
all_pcts = [np.percentile(o["rev"], p) for p in pcts_vals]
sg_pcts  = [np.percentile(sg["rev"], p) for p in pcts_vals]
my_pcts  = [np.percentile(my["rev"], p) for p in pcts_vals]

x6 = np.arange(len(pcts_vals))
w6 = 0.28
ax6.bar(x6 - w6,     all_pcts, width=w6, color=NAVY,  alpha=0.8, label="All markets", zorder=3)
ax6.bar(x6,          sg_pcts,  width=w6, color=TEAL,  alpha=0.8, label="SG only",     zorder=3)
ax6.bar(x6 + w6,     my_pcts,  width=w6, color=AMBER, alpha=0.8, label="MY only",     zorder=3)
ax6.set_xticks(x6)
ax6.set_xticklabels([f"P{p}" for p in pcts_vals], fontsize=9)
ax6.set_ylabel("Order revenue (SGD)", fontsize=10)
ax6.set_title("Revenue Percentiles by Market\n(Confirms different distributions per store)", fontsize=11, fontweight="bold")
ax6.legend(fontsize=9)
ax6.grid(axis="y", alpha=0.3)
ax6.set_facecolor(LIGHT)
for bars_grp, vals, col in zip(
    [ax6.patches[:len(pcts_vals)], ax6.patches[len(pcts_vals):2*len(pcts_vals)], ax6.patches[2*len(pcts_vals):]],
    [all_pcts, sg_pcts, my_pcts],
    [NAVY, TEAL, AMBER]
):
    pass  # annotations would be too crowded

# Add stat table at bottom of p6
table_data = [
    ["", "All markets", "SG only", "MY only"],
    ["Count",  f"27,350", f"16,039", f"11,309"],
    ["Mean",   f"S$113.82", f"S$119.28", f"S$106.07"],
    ["Median", f"S$59.90",  f"S$62.10",  f"S$55.48"],
    ["Max",    f"S$34,618", f"S$26,520", f"S$34,618"],
    ["Std",    f"S$413.76", f"S$405.16", f"S$425.60"],
]
tbl = ax6.table(cellText=table_data[1:], colLabels=table_data[0],
                cellLoc="center", loc="lower right", bbox=[0.0, -0.55, 1.0, 0.45])
tbl.auto_set_font_size(False)
tbl.set_fontsize(8)
for (r, c), cell in tbl.get_celld().items():
    if r == 0:
        cell.set_facecolor(NAVY)
        cell.set_text_props(color="white", fontweight="bold")
    elif c == 0:
        cell.set_facecolor("#E8F4F8")
    cell.set_edgecolor("#cccccc")
ax6.set_ylim(0, max(all_pcts) * 1.3)

fig.subplots_adjust(hspace=0.65, wspace=0.35, top=0.93, bottom=0.10)

out_path = CHART / "99_summary_stats_verification.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: charts/99_summary_stats_verification.png")

# ── Print verification numbers ────────────────────────────────────────────────
print("\n=== VERIFIED STATISTICS FOR REPORT ===")
print(f"All markets - Count: {len(o):,} | Mean: S${o['rev'].mean():.2f} | Median: S${o['rev'].median():.2f} | Std: S${o['rev'].std():.2f}")
print(f"All markets - P25: S${o['rev'].quantile(0.25):.2f} | P75: S${o['rev'].quantile(0.75):.2f} | Max: S${o['rev'].max():,.2f}")
print(f"SG only     - Count: {len(sg):,} | Mean: S${sg['rev'].mean():.2f} | Median: S${sg['rev'].median():.2f} | Std: S${sg['rev'].std():.2f}")
print(f"SG only     - P25: S${sg['rev'].quantile(0.25):.2f} | P75: S${sg['rev'].quantile(0.75):.2f} | Max: S${sg['rev'].max():,.2f}")
print(f"MY only     - Count: {len(my):,} | Mean: S${my['rev'].mean():.2f} | Median: S${my['rev'].median():.2f} | Std: S${my['rev'].std():.2f}")
print(f"MY only     - P25: S${my['rev'].quantile(0.25):.2f} | P75: S${my['rev'].quantile(0.75):.2f} | Max: S${my['rev'].max():,.2f}")
print()
cust_all = o.groupby("customer_id")["order_id"].count()
cust_sg_c = sg.groupby("customer_id")["order_id"].count()
print(f"Orders/cust ALL - Mean: {cust_all.mean():.2f} | Median: {cust_all.median():.1f} | Max: {cust_all.max()} | 1-order: {(cust_all==1).mean()*100:.1f}%")
print(f"Orders/cust SG  - Mean: {cust_sg_c.mean():.2f} | Median: {cust_sg_c.median():.1f} | Max: {cust_sg_c.max()} | 1-order: {(cust_sg_c==1).mean()*100:.1f}%")
print()
print(f"Discount orders: {len(disc_orders):,} of {len(o):,} = {len(disc_orders)/len(o)*100:.1f}%")
print(f"90-100% depth bucket: {(db=='90–100%').sum():,} = {(db=='90–100%').sum()/len(disc_orders)*100:.1f}% of discounted orders")
