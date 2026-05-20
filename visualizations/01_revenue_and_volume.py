"""
01_revenue_and_volume.py
Charts: annual revenue trend, order volume, discount rate escalation, monthly revenue 2024-2026
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from style import save, CAT_COLORS, TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LIGHT_BG, bar_label

# -- Data: all read from EDA outputs (FX-corrected, combined SG+MY+HK in SGD) --
# FX assumption: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, 2020-2026)
_outputs = Path(__file__).resolve().parent.parent / "EDA" / "outputs"

# Annual data from 02_orders_by_year.csv
_annual_df = pd.read_csv(_outputs / "02_orders_by_year.csv")
_annual_df = _annual_df[_annual_df["year"].between(2020, 2025)].reset_index(drop=True)
years     = _annual_df["year"].astype(str).tolist()
revenue   = _annual_df["revenue_sgd"].round(0).astype(int).tolist()
orders    = _annual_df["orders"].astype(int).tolist()
customers = _annual_df["customers"].astype(int).tolist()
disc_rate = (_annual_df["disc_pct_orders"] * 100).round(1).tolist()

# Monthly revenue from 02_revenue_by_month.csv
_monthly_df = pd.read_csv(_outputs / "02_revenue_by_month.csv")
_monthly_df["month"] = pd.to_datetime(_monthly_df["month"])
_monthly_df = _monthly_df[
    (_monthly_df["month"] >= "2024-01-01") &
    (_monthly_df["month"] <= "2026-03-31")
].reset_index(drop=True)
monthly_labels = _monthly_df["month"].dt.strftime("%b-%y").tolist()
monthly_rev    = _monthly_df["revenue"].round(0).astype(int).tolist()

# -- Chart 1: Revenue + discount rate (dual axis) -----------------------------
fig, ax1 = plt.subplots(figsize=(11, 6))
x = np.arange(len(years))
bars = ax1.bar(x, [r/1000 for r in revenue], color=[TEAL if r > 600000 else ORANGE if r < 400000 else GOLD for r in revenue], width=0.55, zorder=3)
ax1.set_xticks(x); ax1.set_xticklabels(years, fontsize=11)
ax1.set_ylabel("Revenue (SGD '000)", color=NAVY, fontsize=11)
ax1.set_title("Annual Revenue vs Discount Rate Escalation")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v:.0f}K"))
for bar, r in zip(bars, revenue):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+15,
             f"S${r/1000:.0f}K", ha="center", va="bottom", fontsize=9, color=NAVY, fontweight="bold")

ax2 = ax1.twinx()
ax2.plot(x, disc_rate, color=RED, marker="o", linewidth=2.5, markersize=7, zorder=4, label="Discount rate")
ax2.set_ylabel("% Orders With Discount", color=RED, fontsize=11)
ax2.set_ylim(0, 70)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(RED)
ax2.tick_params(axis="y", colors=RED)
for xi, dr in zip(x, disc_rate):
    if dr > 0:
        ax2.annotate(f"{dr:.0f}%", xy=(xi, dr), xytext=(5, 5), textcoords="offset points",
                     fontsize=9, color=RED)

ax1.annotate("Discounted orders\nrise: 0% to 69%", xy=(4, 284), xycoords="data",
             xytext=(2.8, 550), textcoords="data",
             arrowprops=dict(arrowstyle="->", color=RED, lw=1.5), color=RED, fontsize=9)

fig.tight_layout()
save(fig, "01a_revenue_discount_trend")

# -- Chart 2: Monthly revenue trend 2024-2026 ---------------------------------
fig, ax = plt.subplots(figsize=(14, 5))
x = np.arange(len(monthly_labels))
colors = [ORANGE if v > 50000 else TEAL if v > 30000 else SLATE for v in monthly_rev]
ax.fill_between(x, monthly_rev, alpha=0.15, color=TEAL)
ax.plot(x, monthly_rev, color=TEAL, linewidth=2.5, marker="o", markersize=5, zorder=3)
ax.set_xticks(x[::2]); ax.set_xticklabels(monthly_labels[::2], rotation=35, ha="right", fontsize=9)
ax.set_title("Monthly Revenue (SGD) -- Jan 2024 to Mar 2026")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v/1000:.0f}K"))
ax.set_ylabel("Revenue (SGD)", fontsize=11)
# Annotate Jul-24 spike dynamically using actual data
_jul24_idx = next((i for i, l in enumerate(monthly_labels) if l == "Jul-24"), None)
_mar26_idx = next((i for i, l in enumerate(monthly_labels) if l == "Mar-26"), None)
if _jul24_idx is not None:
    ax.annotate("Jul-24 spike\n(sale event)", xy=(_jul24_idx, monthly_rev[_jul24_idx]),
                xytext=(_jul24_idx + 1.5, monthly_rev[_jul24_idx] * 0.88),
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.5), color=ORANGE, fontsize=9)
if _mar26_idx is not None:
    ax.annotate("Mar-26", xy=(_mar26_idx, monthly_rev[_mar26_idx]),
                xytext=(_mar26_idx - 2, monthly_rev[_mar26_idx] * 1.12),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.5), color=TEAL, fontsize=9)
fig.tight_layout()
save(fig, "01b_monthly_revenue_2024_2026")

# -- Chart 3: Orders and unique customers by year -----------------------------
fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(years)); w = 0.38
b1 = ax.bar(x-w/2, orders, width=w, color=TEAL, label="Orders", zorder=3)
b2 = ax.bar(x+w/2, customers, width=w, color=NAVY, label="Unique customers", zorder=3)
ax.set_xticks(x); ax.set_xticklabels(years, fontsize=11)
ax.set_title("Orders vs Unique Customers by Year")
ax.legend(loc="upper left")
for bar, v in zip(b1, orders):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+40, f"{v:,}", ha="center", fontsize=8, color=TEAL)
for bar, v in zip(b2, customers):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+40, f"{v:,}", ha="center", fontsize=8, color=NAVY)
fig.tight_layout()
save(fig, "01c_orders_customers_by_year")

print("Done - 01_revenue_and_volume")
