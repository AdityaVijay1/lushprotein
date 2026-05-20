"""
03_product_and_crosssell.py
Charts: cross-product LTV waterfall, product revenue mix, SKU checkout vs recurring,
        product x channel heatmap
FX assumption: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average rate, 2020-2026).
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

# -- Chart 1: Cross-product LTV staircase -------------------------------------
# Source: EDA/outputs/04_cross_product_ltv.csv
_cp = pd.read_csv(_outputs / "04_cross_product_ltv.csv")
_cp_order = ["1 product", "2 products", "3 products", "4+ products"]
_cp = _cp.set_index("category_label").reindex(_cp_order).reset_index()

labels      = _cp["category_label"].tolist()
ltv         = _cp["avg_ltv"].round(0).astype(int).tolist()
repeat_rate = (_cp["repeat_rate"] * 100).round(1).tolist()
n_custs     = _cp["customers"].astype(int).tolist()

fig, ax1 = plt.subplots(figsize=(12, 7))
colors = [SLATE, GOLD, ORANGE, TEAL]
bars = ax1.bar(labels, ltv, color=colors, width=0.5, zorder=3)
ax1.set_title("Cross-Product Purchasing: LTV Uplift by Breadth", fontsize=14, fontweight="bold", pad=16)
ax1.set_ylabel("Average LTV (SGD)", fontsize=11, color=NAVY)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v:,.0f}"))
ax1.set_ylim(0, 1050)  # extra headroom so bar labels don't clash with red line

# ALL LTV labels inside bar near top -- keeps them clear of the red line
# n= label centred in the middle of the bar
for bar, v, n in zip(bars, ltv, n_custs):
    bx = bar.get_x() + bar.get_width() / 2
    bh = bar.get_height()
    ax1.text(bx, bh - 28, f"S${v:,}",
             ha="center", va="top", fontsize=11, fontweight="bold", color="white")
    ax1.text(bx, bh / 2, f"n={n:,}",
             ha="center", va="center", fontsize=9.5, color="white", fontweight="bold")

# Right axis -- repeat rate line
ax2 = ax1.twinx()
ax2.plot(labels, repeat_rate, color=RED, marker="D", linewidth=2.5, markersize=9, zorder=4)
ax2.set_ylabel("Repeat Purchase Rate (%)", color=RED, fontsize=11)
ax2.set_ylim(0, 135)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(RED)
ax2.tick_params(axis="y", colors=RED)

# Red % labels -- staggered offsets so they always sit clearly above the diamond markers
# Offsets chosen so short bars (bar 0 & 1) push labels further up
_rr_offsets = [14, 12, 9, 9]
for xi, (r, off) in enumerate(zip(repeat_rate, _rr_offsets)):
    ax2.text(xi, r + off, f"{r:.1f}%", ha="center", fontsize=11,
             color=RED, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85))

# Uplift annotations -- placed in clear space above the bar, staggered x-offset
for i in range(1, len(ltv)):
    uplift = (ltv[i]-ltv[0])/ltv[0]*100
    ax1.annotate(f"+{uplift:.0f}%\nvs 1 product",
                 xy=(i, ltv[i] + 18),
                 xytext=(i + 0.24, ltv[i] + 210),
                 fontsize=8.5, color=TEAL, ha="center",
                 arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.8, linestyle="dotted"))

fig.tight_layout()
save(fig, "03a_cross_product_ltv")

# -- Chart 2: Product revenue mix (hero vs other) ------------------------------
# Revenue and unit prices read from lines.parquet (FX-corrected SGD, all markets)
_lines = pd.read_parquet(_outputs / "lines.parquet")
_prod_rev = (
    _lines[_lines["product_category"] != "Unknown"]
    .assign(line_total=lambda d: pd.to_numeric(d["Line: Total"], errors="coerce").fillna(0))
    .groupby("product_category")
    .agg(revenue=("line_total", "sum"), avg_price=("Line: Price", "mean"))
    .reset_index()
)
_cat_order = ["Clear Protein", "Lean Protein", "Collagen Glow", "Soy Protein", "Accessories", "Other"]
_prod_rev = _prod_rev.set_index("product_category").reindex(_cat_order).reset_index()

categories  = _prod_rev["product_category"].tolist()
revenues    = _prod_rev["revenue"].round(0).astype(int).tolist()
unit_prices = _prod_rev["avg_price"].round(1).tolist()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Donut chart
wedge_colors = [NAVY, TEAL, ORANGE, GOLD, SLATE, LILAC]
total = sum(revenues)
wedges, texts, autotexts = axes[0].pie(
    revenues, labels=None,
    colors=wedge_colors,
    autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
    startangle=140,
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    pctdistance=0.78,
)
for at in autotexts:
    at.set_fontsize(10); at.set_fontweight("bold"); at.set_color("white")
legend_labels = [f"{c}  (S${r/1000:.0f}K)" for c, r in zip(categories, revenues)]
axes[0].legend(wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.2),
               ncol=2, fontsize=9)
axes[0].set_title("Revenue Mix by Product Category", fontsize=12, fontweight="bold")
axes[0].text(0, 0, f"S${total/1000:.0f}K\nTotal", ha="center", va="center",
             fontsize=11, fontweight="bold", color=NAVY)

# Avg unit price comparison -- from lines.parquet (SGD, FX-corrected)
_hero_order = ["Lean Protein", "Clear Protein", "Collagen Glow", "Soy Protein"]
_hero_df = _prod_rev[_prod_rev["product_category"].isin(_hero_order)].set_index("product_category").reindex(_hero_order).reset_index()
hero_cats   = _hero_df["product_category"].tolist()
hero_prices = _hero_df["avg_price"].tolist()
hero_colors = [NAVY, TEAL, ORANGE, GOLD]
axes[1].barh(hero_cats[::-1], hero_prices[::-1], color=hero_colors[::-1], height=0.5, zorder=3)
axes[1].set_title("Avg Unit Price by Hero SKU (SGD)", fontsize=12, fontweight="bold")
axes[1].set_xlabel("Avg Line Item Price (SGD)", fontsize=10)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"S${v:.0f}"))
for i, v in enumerate(hero_prices[::-1]):
    axes[1].text(v+1, i, f"S${v:.2f}", va="center", fontsize=10, color=NAVY)
axes[1].grid(axis="x"); axes[1].grid(axis="y", visible=False)
axes[1].spines["left"].set_visible(False); axes[1].tick_params(left=False)
axes[1].set_xlim(0, 100)

fig.tight_layout()
save(fig, "03b_product_revenue_mix")

# -- Chart 3: SKU loyalty -- checkout vs recurring -----------------------------
# Source: EDA/outputs/04_sku_popularity.csv (merged checkout + recurring)
_sku = pd.read_csv(_outputs / "04_sku_popularity.csv")
_co = _sku[_sku["type"]=="checkout"].set_index(["product_title","variant_title"])["n_customers"].rename("checkout_n")
_re = _sku[_sku["type"]=="recurring"].set_index(["product_title","variant_title"])["n_customers"].rename("recurring_n")
_loyalty = pd.concat([_co, _re], axis=1).dropna().reset_index()
_loyalty["loyalty_ratio"] = (_loyalty["recurring_n"] / _loyalty["checkout_n"]).round(2)
_loyalty = _loyalty.sort_values("checkout_n", ascending=False).head(7)
# Build short display labels: "PRODUCT\nVariant key"
_sku_short = lambda row: row["product_title"].replace(" PROTEIN","").replace(" PROTEIN ISOLATE","") + "\n" + row["variant_title"].split("/")[-1].strip()[:12]
_loyalty["sku_label"] = _loyalty.apply(_sku_short, axis=1)

skus          = _loyalty["sku_label"].tolist()
checkout_n    = _loyalty["checkout_n"].astype(int).tolist()
recurring_n   = _loyalty["recurring_n"].astype(int).tolist()
loyalty_ratio = _loyalty["loyalty_ratio"].tolist()

x = np.arange(len(skus)); w = 0.38
fig, ax1 = plt.subplots(figsize=(13, 6))
b1 = ax1.bar(x-w/2, checkout_n,  width=w, color=TEAL,  label="Checkout customers",  zorder=3)
b2 = ax1.bar(x+w/2, recurring_n, width=w, color=NAVY,  label="Recurring customers", zorder=3)
ax1.set_xticks(x); ax1.set_xticklabels(skus, fontsize=8.5)
ax1.set_title("Subscription SKU Loyalty: Checkout vs Recurring Customers")
ax1.set_ylabel("Number of Customers", fontsize=11)
ax1.legend(loc="upper right")

ax2 = ax1.twinx()
ax2.plot(x, [r*100 for r in loyalty_ratio], color=RED, marker="o", linewidth=2, markersize=8, zorder=4)
ax2.set_ylabel("Loyalty Ratio (%)", color=RED, fontsize=11)
ax2.set_ylim(0, 75)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}%"))
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(RED)
ax2.tick_params(axis="y", colors=RED)
for xi, r in zip(x, loyalty_ratio):
    ax2.text(xi, r*100+2, f"{r*100:.0f}%", ha="center", fontsize=9, color=RED, fontweight="bold")

fig.tight_layout()
save(fig, "03c_sku_loyalty")

# -- Chart 4: Top product combos (repeat buyers) -------------------------------
# Source: computed from lines.parquet -- top combos that include a named hero product
_lines_full = pd.read_parquet(_outputs / "lines.parquet")
_cust_full  = pd.read_parquet(_outputs / "customers.parquet")
_cust_full["is_repeat"] = _cust_full["is_repeat"].astype(str).map({"True":True,"False":False}).fillna(False)
_rep_ids = set(_cust_full[_cust_full["is_repeat"]]["customer_id"])
_combo_all = (
    _lines_full[_lines_full["customer_id"].isin(_rep_ids)]
    .groupby("customer_id")["product_category"]
    .apply(lambda s: " + ".join(sorted(s.unique())))
    .value_counts()
)
_HERO = {"Lean Protein", "Clear Protein", "Collagen Glow", "Soy Protein", "Accessories"}
_combo_named = _combo_all[
    _combo_all.index.map(lambda c: any(h in c for h in _HERO))
].head(7)
combos       = [c.replace(" + ", " +\n") for c in _combo_named.index.tolist()]
combo_counts = _combo_named.values.tolist()

fig, ax = plt.subplots(figsize=(11, 5))
y = np.arange(len(combos))
bar_colors = [TEAL if c > 70 else GOLD if c > 60 else SLATE for c in combo_counts]
ax.barh(y, combo_counts, color=bar_colors, height=0.55, zorder=3)
ax.set_yticks(y); ax.set_yticklabels(combos, fontsize=9.5)
ax.set_title("Top Cross-Product Purchase Combinations (Repeat Buyers)")
ax.set_xlabel("Number of Customers", fontsize=10)
for i, v in enumerate(combo_counts):
    ax.text(v+0.5, i, str(v), va="center", fontsize=10, color=NAVY)
ax.grid(axis="x"); ax.grid(axis="y", visible=False)
ax.spines["left"].set_visible(False); ax.tick_params(left=False)
fig.tight_layout()
save(fig, "03d_top_product_combos")

print("Done - 03_product_and_crosssell")
