"""
07_slide3_charts.py
Generates the two Slide 3 charts in the clean Excel-like presentation style:
  slide3a_revenue_discounts.png        – Revenue & Discounts Given
  slide3b_customers_rev_per_customer.png – Revenue per Customer vs # of Unique Customers

All data loaded dynamically from EDA/outputs/02_orders_by_year.csv
FX: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, 2020-2026)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np

# ── Data ──────────────────────────────────────────────────────────────────────
_outputs = Path(__file__).resolve().parent.parent / "EDA" / "outputs"
yr = pd.read_csv(_outputs / "02_orders_by_year.csv")
yr = yr[yr["year"].between(2020, 2025)].reset_index(drop=True)

years            = yr["year"].astype(int).tolist()
customers        = yr["customers"].astype(int).tolist()
orders_n         = yr["orders"].astype(int).tolist()
revenue          = yr["revenue_sgd"].tolist()
disc_amt         = yr["disc_amt"].tolist()
disc_pct         = (yr["disc_pct_orders"] * 100).tolist()   # % of orders with a discount
rev_per_cust     = (yr["revenue_sgd"] / yr["customers"]).tolist()

x = np.arange(len(years))

# ── Colour palette (Excel-like) ───────────────────────────────────────────────
BLUE    = "#4472C4"
ORANGE  = "#C55A11"
GREEN   = "#70AD47"
RED     = "#FF0000"
BLACK   = "#000000"
LGRAY   = "#E0E0E0"

CHARTS  = Path(__file__).resolve().parent / "charts"
CHARTS.mkdir(exist_ok=True)

def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", which="both", length=0)
    ax.set_facecolor("white")

# ═══════════════════════════════════════════════════════════════════════════════
# CHART A — Revenue & Discounts Given
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(figsize=(7, 4.5))
fig.patch.set_facecolor("white")

BAR_W = 0.35
ax1.bar(x - BAR_W/2, revenue,  width=BAR_W, color=GREEN, label="Revenue",
        zorder=3, edgecolor="white", linewidth=0.5)
ax1.bar(x + BAR_W/2, disc_amt, width=BAR_W, color=RED,   label="Discounts Given",
        zorder=3, edgecolor="white", linewidth=0.5)

ax1.set_xticks(x)
ax1.set_xticklabels([str(y) for y in years], fontsize=11)
ax1.set_xlim(-0.6, len(years) - 0.4)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f},000" if v >= 1000 else "0"))
ax1.set_ylim(0, 1_050_000)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(100_000))
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax1.tick_params(axis="y", labelsize=9)
ax1.set_title("Revenue & Discounts Given", fontsize=14, fontweight="bold", pad=12)
clean_axes(ax1)
ax1.spines["left"].set_color(LGRAY)
ax1.spines["bottom"].set_color(LGRAY)
ax1.grid(axis="y", color=LGRAY, linewidth=0.8, zorder=0)

# Right axis — % Discounted
ax2 = ax1.twinx()
ax2.plot(x, disc_pct, color=BLACK, marker="o", linewidth=2, markersize=5,
         label="% Discounted", zorder=4)
ax2.set_ylim(0, 90)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax2.tick_params(axis="y", labelsize=9)
ax2.spines["top"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
ax2.tick_params(axis="both", which="both", length=0)

# -52% annotation: 2021 peak → 2025 revenue (dashed line at top of bars)
_peak_i = years.index(2021)
_end_i  = years.index(2025)
_peak_y = revenue[_peak_i]
_end_y  = revenue[_end_i]
_top    = 920_000
ax1.annotate(
    "", xy=(x[_end_i] - 0.18, _top),
    xytext=(x[_peak_i] + 0.18, _top),
    arrowprops=dict(arrowstyle="-", color="#999999", linestyle="dashed", lw=1.2),
)
ax1.annotate(
    "-52%",
    xy=((x[_peak_i] + x[_end_i]) / 2, _top + 25_000),
    ha="center", va="bottom", fontsize=10, color=RED, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=RED, linewidth=1.5),
)

# Bottom label row — # of customers per year (spaced to avoid overlap)
fig.subplots_adjust(bottom=0.22)
row_y = -0.165
ax1.text(-0.62, row_y, "# of customers", transform=ax1.get_xaxis_transform(),
         fontsize=8.5, color="#444444", va="top", ha="left")
for xi, n in enumerate(customers):
    ax1.text(xi, row_y, f"{n:,}", transform=ax1.get_xaxis_transform(),
             fontsize=8.5, color="#444444", va="top", ha="center")

# Combined legend
handles1 = [
    mpatches.Patch(color=GREEN, label="Revenue"),
    mpatches.Patch(color=RED,   label="Discounts Given"),
    plt.Line2D([0], [0], color=BLACK, linewidth=2, marker="o", markersize=5, label="% Discounted"),
]
fig.legend(handles=handles1, loc="lower center", ncol=3, fontsize=9,
           frameon=False, bbox_to_anchor=(0.5, 0.0))

fig.tight_layout(rect=[0, 0.08, 1, 1])
out_a = CHARTS / "slide3a_revenue_discounts.png"
fig.savefig(out_a, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"  Saved: {out_a.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# CHART B — Revenue per Customer vs # of Unique Customers
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(figsize=(7, 4.5))
fig.patch.set_facecolor("white")

ax1.bar(x, customers, width=0.5, color=BLUE, label="# of Unique Customers",
        zorder=3, edgecolor="white", linewidth=0.5)
ax1.set_xticks(x)
ax1.set_xticklabels([str(y) for y in years], fontsize=11)
ax1.set_xlim(-0.6, len(years) - 0.4)
ax1.set_ylim(0, 5500)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(500))
ax1.tick_params(axis="y", labelsize=9)
ax1.yaxis.label.set_color(BLUE)
ax1.set_title("Revenue per Customer vs # of\nUnique Customers", fontsize=13,
              fontweight="bold", pad=12)
clean_axes(ax1)
ax1.spines["left"].set_color(LGRAY)
ax1.spines["bottom"].set_color(LGRAY)
ax1.grid(axis="y", color=LGRAY, linewidth=0.8, zorder=0)

# Right axis — Revenue per Customer
ax2 = ax1.twinx()
rpc = [r / c for r, c in zip(revenue, customers)]
ax2.plot(x, rpc, color=ORANGE, marker="o", linewidth=2.5, markersize=7,
         label="Revenue per Customer", zorder=4)
ax2.set_ylim(0, 400)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
ax2.tick_params(axis="y", labelsize=9)
ax2.yaxis.label.set_color(ORANGE)
ax2.spines["top"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
ax2.tick_params(axis="both", which="both", length=0)

# +8% annotation: customers 2021 vs 2025 (dashed line connecting bar tops)
_i21 = years.index(2021)
_i25 = years.index(2025)
c21  = customers[_i21]
c25  = customers[_i25]
pct_cust = round((c25 - c21) / c21 * 100)
_mid_x   = (x[_i21] + x[_i25]) / 2
_bar_top  = 4800
ax1.annotate(
    "", xy=(x[_i25] - 0.18, _bar_top),
    xytext=(x[_i21] + 0.18, _bar_top),
    arrowprops=dict(arrowstyle="-", color="#999999", linestyle="dashed", lw=1.0),
)
ax1.annotate(
    f"+{pct_cust}%",
    xy=(_mid_x, _bar_top + 100),
    ha="center", va="bottom", fontsize=10, color="#375623", fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#E2EFDA", edgecolor="#70AD47", linewidth=1.5),
)

# -55% annotation: revenue per customer 2021 vs 2025 (on the orange line)
rpc21 = rpc[_i21]
rpc25 = rpc[_i25]
pct_rpc = round((rpc25 - rpc21) / rpc21 * 100)
_mid_x_rpc = (x[_i21] + x[_i25]) / 2
ax2.annotate(
    "", xy=(x[_i25] - 0.18, rpc25 + 5),
    xytext=(x[_i21] + 0.18, rpc21 + 5),
    arrowprops=dict(arrowstyle="-", color="#999999", linestyle="dashed", lw=1.0),
)
ax2.annotate(
    f"{pct_rpc}%",
    xy=(_mid_x_rpc, (rpc21 + rpc25) / 2 + 30),
    ha="center", va="bottom", fontsize=10, color="#833C00", fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#FCE4D6", edgecolor="#C55A11", linewidth=1.5),
)

# Combined legend
handles2 = [
    mpatches.Patch(color=BLUE,   label="# of Unique Customers"),
    plt.Line2D([0], [0], color=ORANGE, linewidth=2.5, marker="o", markersize=7,
               label="Revenue per Customer"),
]
fig.legend(handles=handles2, loc="lower center", ncol=2, fontsize=9,
           frameon=False, bbox_to_anchor=(0.5, 0.0))

fig.tight_layout(rect=[0, 0.08, 1, 1])
out_b = CHARTS / "slide3b_customers_rev_per_customer.png"
fig.savefig(out_b, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"  Saved: {out_b.name}")

print("Done – 07_slide3_charts")
