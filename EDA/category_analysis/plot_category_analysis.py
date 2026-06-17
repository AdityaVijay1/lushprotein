"""
plot_category_analysis.py — Charts for category_analysis outputs.

Reads CSVs from EDA/category_analysis/outputs/ (run run_category_analysis.py first).
Saves PNGs to EDA/category_analysis/outputs/charts/

Run: python EDA/category_analysis/plot_category_analysis.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# Shared LushProtein chart style
VIZ_DIR = Path(__file__).resolve().parent.parent.parent / "visualizations"
sys.path.insert(0, str(VIZ_DIR))
from style import (  # noqa: E402
    TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LILAC, LIGHT_BG, CAT_COLORS, save,
)

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "outputs"
CHART_DIR = OUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Override save() to write into category_analysis/charts
def save_local(fig: plt.Figure, name: str) -> Path:
    path = CHART_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=LIGHT_BG)
    plt.close(fig)
    print(f"  Saved: outputs/charts/{name}.png")
    return path


HERO_ORDER = [
    "Clear Protein", "Lean Protein", "Collagen Glow",
    "Soy Protein", "Accessories", "Other", "Unknown",
]


def _order_categories(df, col="category"):
    cats = [c for c in HERO_ORDER if c in df[col].values]
    extra = [c for c in df[col].unique() if c not in HERO_ORDER]
    order = cats + sorted(extra)
    return df.set_index(col).reindex(order).reset_index()


def _order_first_product(df):
    cats = [c for c in HERO_ORDER if c in df["first_product_cat"].values]
    extra = [c for c in df["first_product_cat"].unique() if c not in HERO_ORDER]
    order = cats + sorted(extra)
    return df.set_index("first_product_cat").reindex(order).reset_index()


def _color_map(labels):
    return {lab: CAT_COLORS[i % len(CAT_COLORS)] for i, lab in enumerate(labels)}


print("=" * 72)
print("CATEGORY ANALYSIS — building charts")
print("=" * 72)

pen = pd.read_csv(OUT_DIR / "01_category_penetration.csv")
rep = pd.read_csv(OUT_DIR / "01_repeat_by_first_product.csv")
t3 = pd.read_csv(OUT_DIR / "02_t3_cross_category_behavior.csv")
t9 = pd.read_csv(OUT_DIR / "03_t9_first_transaction_index.csv")

pen = _order_categories(pen.rename(columns={"product_category": "category"}))
t3 = _order_categories(t3)
t9 = _order_categories(t9)
rep = _order_first_product(rep)

n_cohort = int(pen["n_customers_ever"].sum() / pen["pct_customers_ever"].sum() * pen["pct_customers_ever"].iloc[0])
# Better: read from summary or compute from penetration
with open(OUT_DIR / "summary.txt", encoding="utf-8") as f:
    for line in f:
        if "Cohort size:" in line:
            n_cohort = int(line.split(":")[1].strip().split()[0].replace(",", ""))
            break

# ══════════════════════════════════════════════════════════════════════════════
# Chart 1A — Category penetration (% ever bought + revenue share)
# ══════════════════════════════════════════════════════════════════════════════
cats = pen["category"].tolist()
pct_cust = (pen["pct_customers_ever"] * 100).tolist()
pct_rev = (pen["pct_revenue"] * 100).tolist()
colors = [_color_map(cats)[c] for c in cats]

fig, ax1 = plt.subplots(figsize=(12, 6.5))
y = np.arange(len(cats))
h = 0.35
ax1.barh(y + h / 2, pct_cust, height=h, color=colors, label="% of cohort (ever bought)", zorder=3)
ax1.barh(y - h / 2, pct_rev, height=h, color=[c + "88" for c in colors], edgecolor=colors,
         linewidth=1.2, label="% of total revenue", zorder=3)
ax1.set_yticks(y)
ax1.set_yticklabels(cats, fontsize=10)
ax1.invert_yaxis()
ax1.set_xlabel("% of cohort / revenue", fontsize=11, color=NAVY)
ax1.set_title(
    "[1A] Category Penetration — Ever Bought vs Revenue Share",
    fontsize=14, fontweight="bold", pad=14,
)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax1.set_xlim(0, max(max(pct_cust), max(pct_rev)) * 1.25)
for i, (pc, pr, n) in enumerate(zip(pct_cust, pct_rev, pen["n_customers_ever"])):
    ax1.text(pc + 0.8, i + h / 2, f"{pc:.1f}%  (n={int(n):,})", va="center", fontsize=9, color=NAVY)
    ax1.text(pr + 0.8, i - h / 2, f"{pr:.1f}%", va="center", fontsize=9, color=SLATE)
ax1.legend(loc="lower right", fontsize=9)
ax1.grid(axis="x")
ax1.grid(axis="y", visible=False)
fig.text(0.12, 0.02, f"Cohort: {n_cohort:,} customers  |  Product-level categories (not flavour)",
         fontsize=9, color=SLATE)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_local(fig, "fig_01a_category_penetration")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 1B — Repeat rate by first product purchased (image A style)
# ══════════════════════════════════════════════════════════════════════════════
rep_sorted = rep.sort_values("repeat_rate", ascending=True)
labels = rep_sorted["first_product_cat"].tolist()
rr = (rep_sorted["repeat_rate"] * 100).tolist()
ltv = rep_sorted["avg_ltv"].tolist()
n_cust = rep_sorted["customers"].astype(int).tolist()
bar_colors = [_color_map(labels)[c] for c in labels]

fig, ax1 = plt.subplots(figsize=(12, 7))
y = np.arange(len(labels))
bars = ax1.barh(y, rr, color=bar_colors, height=0.55, zorder=3)
ax1.set_yticks(y)
ax1.set_yticklabels(labels, fontsize=10)
ax1.set_xlabel("Repeat Purchase Rate (%)", fontsize=11, color=NAVY)
ax1.set_title(
    "[1B] Repeat Rate by First Product Purchased",
    fontsize=14, fontweight="bold", pad=14,
)
ax1.set_xlim(0, max(rr) * 1.35)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))

for i, (bar, r, l, n) in enumerate(zip(bars, rr, ltv, n_cust)):
    ax1.text(r + 1.2, bar.get_y() + bar.get_height() / 2,
             f"{r:.1f}%  |  n={n:,}  |  avg LTV S${l:,.0f}",
             va="center", fontsize=9, color=NAVY)

ax2 = ax1.twiny()
ax2.plot(ltv, y, color=ORANGE, marker="o", linewidth=2, markersize=7, zorder=4)
ax2.set_xlabel("Avg LTV (SGD)", color=ORANGE, fontsize=10)
ax2.tick_params(axis="x", colors=ORANGE)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"S${v:,.0f}"))
ax2.spines["top"].set_visible(True)
ax2.spines["top"].set_color(ORANGE)
ax2.grid(False)

ax1.grid(axis="x")
ax1.grid(axis="y", visible=False)
fig.tight_layout()
save_local(fig, "fig_01b_repeat_by_first_product")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 2 — T3 cross-category behavior (4-metric panel)
# ══════════════════════════════════════════════════════════════════════════════
t3_plot = t3.copy()
x = np.arange(len(t3_plot))
w = 0.2
metrics = [
    ("pct_sole_cat_buyers", "% Sole-Cat Buyers", TEAL, 100),
    ("avg_n_categories", "Avg # Categories", NAVY, 1),
    ("cat_share_of_buyers_profit", "Cat Share of Profit", ORANGE, 100),
    ("pct_also_buying", "% Also Buying Top Addl", GOLD, 100),
]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
cat_labels = t3_plot["category"].tolist()

for ax, (col, title, color, mult) in zip(axes, metrics):
    vals = (t3_plot[col] * mult).tolist()
    bars = ax.bar(x, vals, color=color, width=0.55, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, rotation=35, ha="right", fontsize=8.5)
    ax.set_title(title, fontsize=11, fontweight="bold", color=NAVY)
    ymax = max(vals) * 1.18 if max(vals) > 0 else 1
    ax.set_ylim(0, ymax)
    fmt = "{:.1f}" if mult == 1 else "{:.0f}"
    suffix = "" if mult == 1 else "%"
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + ymax * 0.02,
                f"{fmt.format(v)}{suffix}", ha="center", va="bottom", fontsize=8, color=NAVY)
    ax.grid(axis="y")

# Annotate most common additional cat on bottom-right panel
ax_addl = axes[3]
for i, row in t3_plot.iterrows():
    if row["most_common_additional_cat"]:
        ax_addl.annotate(
            f"→ {row['most_common_additional_cat'][:12]}",
            xy=(list(t3_plot["category"]).index(row["category"]), row["pct_also_buying"] * 100),
            xytext=(0, 18), textcoords="offset points",
            ha="center", fontsize=7, color=SLATE, rotation=0,
        )

fig.suptitle(
    "[T3] Category Buying Behavior & Cross-Purchasing",
    fontsize=15, fontweight="bold", color=NAVY, y=1.01,
)
fig.tight_layout()
save_local(fig, "fig_02_t3_cross_category")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 2B — T3 summary table-style horizontal (sole vs cross-shop)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 6.5))
sole = (t3_plot["pct_sole_cat_buyers"] * 100).tolist()
cross = [100 - s for s in sole]
y = np.arange(len(cat_labels))
ax.barh(y, sole, color=TEAL, height=0.6, label="Sole-category buyers", zorder=3)
ax.barh(y, cross, left=sole, color=SLATE + "55", height=0.6, label="Cross-category buyers", zorder=3)
ax.set_yticks(y)
ax.set_yticklabels(cat_labels, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel("% of category buyers", fontsize=11)
ax.set_title("[T3] Sole vs Cross-Category Buyers", fontsize=14, fontweight="bold", pad=12)
ax.set_xlim(0, 100)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
for i, (s, c, avg) in enumerate(zip(sole, cross, t3_plot["avg_n_categories"])):
    ax.text(s / 2, i, f"{s:.0f}%", ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    ax.text(s + c / 2, i, f"{c:.0f}%", ha="center", va="center", fontsize=9, color=NAVY)
    ax.text(102, i, f"avg {avg:.1f} cats", va="center", fontsize=8.5, color=SLATE)
ax.legend(loc="lower right", fontsize=9)
ax.grid(axis="x")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save_local(fig, "fig_02b_t3_sole_vs_cross")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 3 — T9 VTD index (100 = cohort average)
# ══════════════════════════════════════════════════════════════════════════════
t9_plot = t9.sort_values("vtd_index", ascending=True)
cats9 = t9_plot["category"].tolist()
index_vals = t9_plot["vtd_index"].tolist()
n_first = t9_plot["n_first_tx_buyers"].astype(int).tolist()
bar_colors9 = [
    TEAL if v >= 100 else ORANGE if v >= 85 else SLATE for v in index_vals
]

fig, ax = plt.subplots(figsize=(12, 7))
y = np.arange(len(cats9))
bars = ax.barh(y, index_vals, color=bar_colors9, height=0.55, zorder=3)
ax.axvline(100, color=RED, linewidth=2, linestyle="--", zorder=2, label="Cohort avg (100)")
ax.set_yticks(y)
ax.set_yticklabels(cats9, fontsize=10)
ax.set_xlabel("VTD Index (100 = cohort average)", fontsize=11, color=NAVY)
ax.set_title(
    "[T9] First-Transaction Category — VTD Index",
    fontsize=14, fontweight="bold", pad=14,
)
xmin = min(min(index_vals) - 15, 60)
xmax = max(max(index_vals) + 20, 120)
ax.set_xlim(xmin, xmax)

for bar, idx, n, avg in zip(bars, index_vals, n_first, t9_plot["avg_vtd_SGD"]):
    ax.text(
        bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
        f"{idx:.0f}  |  n={n:,}  |  S${avg:,.0f} avg VTD",
        va="center", fontsize=9, color=NAVY,
    )
ax.legend(loc="lower right", fontsize=9)
ax.grid(axis="x")
ax.grid(axis="y", visible=False)
fig.text(0.12, 0.02, "VTD = profit proxy (revenue × 40%)  |  Customers whose first order included category",
         fontsize=9, color=SLATE)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save_local(fig, "fig_03_t9_vtd_index")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 3B — T9 volume vs value (bubble)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 7))
sizes = (t9["tot_vtd_SGD"] / t9["tot_vtd_SGD"].max() * 1200).clip(lower=80)
for i, row in t9.iterrows():
    color = TEAL if row["vtd_index"] >= 100 else ORANGE if row["vtd_index"] >= 85 else SLATE
    ax.scatter(
        row["pct_buying_cat_on_first_trans"] * 100,
        row["vtd_index"],
        s=sizes.iloc[i],
        color=color,
        alpha=0.75,
        edgecolors="white",
        linewidth=1.5,
        zorder=3,
    )
    ax.annotate(
        row["category"],
        (row["pct_buying_cat_on_first_trans"] * 100, row["vtd_index"]),
        textcoords="offset points", xytext=(6, 4),
        fontsize=9, color=NAVY,
    )

ax.axhline(100, color=RED, linewidth=1.5, linestyle="--", alpha=0.8, label="Cohort avg index")
ax.set_xlabel("% of cohort — first transaction included category", fontsize=11)
ax.set_ylabel("VTD Index", fontsize=11)
ax.set_title("[T9] Volume vs Value — First-Transaction Categories", fontsize=14, fontweight="bold", pad=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.5)

# Bubble size legend
for label, frac in [("High total VTD", 1.0), ("Mid", 0.4), ("Low", 0.15)]:
    ax.scatter([], [], s=frac * 1200, color=SLATE, alpha=0.5, label=label)
handles, lbls = ax.get_legend_handles_labels()
ax.legend(handles[:1] + handles[-3:], ["Cohort avg (100)"] + lbls[-3:],
          loc="upper right", fontsize=8, title="Bubble = tot VTD")

fig.tight_layout()
save_local(fig, "fig_03b_t9_volume_vs_value")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 3C — T9 ever vs first-tx funnel bars
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(t9_plot))
w = 0.35
ever_pct = (t9_plot["pct_ever_buying_cat"] * 100).tolist()
first_pct = (t9_plot["pct_buying_cat_on_first_trans"] * 100).tolist()
ax.bar(x - w / 2, ever_pct, w, color=NAVY, label="% ever bought category", zorder=3)
ax.bar(x + w / 2, first_pct, w, color=TEAL, label="% first transaction included", zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(t9_plot["category"], rotation=30, ha="right", fontsize=9)
ax.set_ylabel("% of cohort", fontsize=11)
ax.set_title("[T9] Ever Buyers vs First-Transaction Entry", fontsize=14, fontweight="bold", pad=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.legend(fontsize=9)
for i, (e, f, r) in enumerate(zip(ever_pct, first_pct, t9_plot["pct_ever_buyers_buying_cat_on_first_trans"])):
    ax.text(i, max(e, f) + 1.2, f"{r*100:.0f}% entry", ha="center", fontsize=8, color=SLATE)
ax.grid(axis="y")
fig.tight_layout()
save_local(fig, "fig_03c_t9_ever_vs_first_tx")

# ══════════════════════════════════════════════════════════════════════════════
# Chart 4 — Co-purchase heatmap (from finals lines)
# ══════════════════════════════════════════════════════════════════════════════
FINALS_DIR = SCRIPT_DIR.parent / "outputs_finals"
lines = pd.read_parquet(FINALS_DIR / "lines.parquet")

import importlib.util
spec = importlib.util.spec_from_file_location("lp_config", SCRIPT_DIR.parent / "00_config.py")
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)
lines["product_category"] = lines["Line: Product Handle"].apply(cfg.classify_product)

cust_cats = (
    lines.groupby("customer_id")["product_category"]
    .apply(lambda s: sorted(set(s)))
)
cats_in_data = [c for c in HERO_ORDER if c in lines["product_category"].unique()]
n = len(cats_in_data)
co = np.zeros((n, n))
for cats_list in cust_cats:
    for i, a in enumerate(cats_in_data):
        if a not in cats_list:
            continue
        for j, b in enumerate(cats_in_data):
            if b in cats_list and i != j:
                co[i, j] += 1

# Normalize: % of focal category buyers who also bought column category
buyer_counts = {c: sum(1 for cats in cust_cats if c in cats) for c in cats_in_data}
for i, a in enumerate(cats_in_data):
    denom = buyer_counts[a]
    if denom > 0:
        co[i, :] = co[i, :] / denom * 100

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(co, cmap="YlGnBu", vmin=0, vmax=min(50, co.max() + 5))
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(cats_in_data, rotation=45, ha="right", fontsize=9)
ax.set_yticklabels(cats_in_data, fontsize=9)
ax.set_title(
    "Cross-Category Co-Purchase Rate (% of row buyers who also bought column)",
    fontsize=13, fontweight="bold", pad=14,
)
for i in range(n):
    for j in range(n):
        if i == j:
            text = "—"
            color = SLATE
        else:
            text = f"{co[i, j]:.0f}%"
            color = "white" if co[i, j] > 25 else NAVY
        ax.text(j, i, text, ha="center", va="center", fontsize=8, color=color)
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("% of focal buyers", fontsize=9)
fig.tight_layout()
save_local(fig, "fig_04_co_purchase_heatmap")

# Update README
chart_list = sorted(CHART_DIR.glob("*.png"))
readme_add = "\n## Charts\n\n| File | Description |\n|------|-------------|\n"
desc_map = {
    "fig_01a_category_penetration": "Penetration vs revenue share by category",
    "fig_01b_repeat_by_first_product": "Repeat rate by first product purchased",
    "fig_02_t3_cross_category": "T3 four-metric dashboard",
    "fig_02b_t3_sole_vs_cross": "T3 sole vs cross-category buyers",
    "fig_03_t9_vtd_index": "T9 VTD index by first-transaction category",
    "fig_03b_t9_volume_vs_value": "T9 volume vs value bubble chart",
    "fig_03c_t9_ever_vs_first_tx": "T9 ever buyers vs first-transaction entry",
    "fig_04_co_purchase_heatmap": "Cross-category co-purchase heatmap",
}
for p in chart_list:
    stem = p.stem
    readme_add += f"| `charts/{p.name}` | {desc_map.get(stem, stem)} |\n"
readme_add += "\nGenerate: `python EDA/category_analysis/plot_category_analysis.py`\n"

readme_path = OUT_DIR / "README.md"
existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
if "## Charts" in existing:
    existing = existing.split("## Charts")[0].rstrip()
readme_path.write_text(existing + readme_add, encoding="utf-8")

print("\n" + "=" * 72)
print(f"DONE — {len(chart_list)} charts in EDA/category_analysis/outputs/charts/")
print("=" * 72)
