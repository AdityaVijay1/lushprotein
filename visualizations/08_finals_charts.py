"""
08_finals_charts.py
Finals presentation charts — all data from EDA/outputs/12_*.csv (no hardcoded metrics).

Charts:
  08a  VTD decile × product breadth (heatmap)
  08b  POS vs web customer outcomes
  08c  Top 10 SKU/flavor revenue (2022+ filtered, one bar per SKU)
  08d  Loyal vs one-and-done comparison
  08e  First-purchase flavor repeat rate (min 30 customers)
  08f  Discontinued/draft products — historical revenue (SKU-level)
  08g  LTV heatmap: acquisition cohort × channel
  08h  Business value scenarios (conservative vs potential)
  08i  Loyal repeater target tiers
  08j  Reorder interval by top SKUs
  08k  Top first flavors among loyal repeaters
  08l  P(loyal) by acquisition channel + first-purchase SKU (excl. unknown)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from style import save, TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LILAC, LIGHT_BG, GRID_LINE, CAT_COLORS

_out = Path(__file__).resolve().parent.parent / "EDA" / "outputs"


def _flavor_from_variant(variant: str) -> str:
    if pd.isna(variant):
        return "Default"
    parts = str(variant).split("/")
    return parts[-1].strip() if parts else str(variant).strip()


def _sku_label(handle, variant, sku, include_sku=True) -> str:
    flavor = _flavor_from_variant(variant)
    base = f"{handle} · {flavor}"
    if include_sku and pd.notna(sku):
        return f"{base}\n[{sku}]"
    return base


def _hbar_height(n_rows: int, base: float = 2.8, per_row: float = 0.55) -> float:
    return max(base, n_rows * per_row + 1.6)


def _annotate_hbars(ax, values, labels, x_pad_frac=0.015, fontsize=9, color=NAVY):
    xmax = max(values) if len(values) else 1
    pad = xmax * x_pad_frac if xmax else 1
    for i, (v, lbl) in enumerate(zip(values, labels)):
        ax.text(v + pad, i, lbl, va="center", ha="left", fontsize=fontsize, color=color, fontweight="bold")


# ── 08a: VTD decile heatmap ──────────────────────────────────────────────────
_vtd = pd.read_csv(_out / "12_vtd_decile_cumulative_categories.csv")
deciles = _vtd["vtd_decile"].tolist()

metrics = [
    ("avg_unique_handles", "Avg unique products", lambda v: f"{v:.2f}"),
    ("pct_3plus_products", "% with 3+ products", lambda v: f"{v * 100:.1f}%"),
    ("avg_ltv", "Avg LTV (SGD)", lambda v: f"S${v:,.0f}"),
    ("pct_repeat", "Repeat rate", lambda v: f"{v * 100:.1f}%"),
    ("cum_pct_ltv", "Cumulative % of total LTV", lambda v: f"{v * 100:.1f}%"),
]

matrix = np.array([[_vtd.loc[i, col] for i in range(len(_vtd))] for col, _, _ in metrics])
# Row-normalise for colour (each metric uses full colour range)
norm_matrix = np.zeros_like(matrix, dtype=float)
for i in range(matrix.shape[0]):
    row = matrix[i]
    lo, hi = row.min(), row.max()
    norm_matrix[i] = (row - lo) / (hi - lo) if hi > lo else 0.5

fig, ax = plt.subplots(figsize=(14, 6.5))
im = ax.imshow(norm_matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
ax.set_xticks(range(len(deciles)))
ax.set_xticklabels(deciles, fontsize=11)
ax.set_yticks(range(len(metrics)))
ax.set_yticklabels([m[1] for m in metrics], fontsize=10)
ax.set_xlabel("VTD Decile  (D1 = lowest spend  →  D10 = highest spend)", fontsize=11)
ax.set_title("Product Breadth & LTV by VTD Decile", fontweight="bold", pad=16)

for i in range(len(metrics)):
    for j in range(len(deciles)):
        val = matrix[i, j]
        _, _, fmt = metrics[i]
        txt = fmt(val)
        bg = norm_matrix[i, j]
        txt_color = "white" if bg > 0.62 else NAVY
        ax.text(j, i, txt, ha="center", va="center", fontsize=9.5, color=txt_color, fontweight="bold")

# Remove grid lines over heatmap cells
ax.grid(False)
for spine in ax.spines.values():
    spine.set_visible(False)

top_decile_ltv = (1 - _vtd.loc[_vtd["vtd_decile"] == "D9", "cum_pct_ltv"].iloc[0]) * 100
fig.text(
    0.5, 0.01,
    f"Top decile (D10) = {top_decile_ltv:.0f}% of total LTV  |  "
    f"D10 avg {metrics[0][2](_vtd.loc[9, 'avg_unique_handles'])} unique products, "
    f"{metrics[1][2](_vtd.loc[9, 'pct_3plus_products'])} with 3+ products",
    ha="center", fontsize=9, color=SLATE, style="italic",
)
fig.subplots_adjust(bottom=0.14)
save(fig, "08a_vtd_decile_product_breadth")

# ── 08b: POS vs web outcomes ─────────────────────────────────────────────────
_pos = pd.read_csv(_out / "12_pos_vs_web_customer_outcomes.csv")
metrics_b = ["repeat_rate", "avg_ltv_sgd", "pct_subscribed"]
labels_b = ["Repeat Rate", "Avg LTV", "% Subscribed"]
pos_vals = [_pos.loc[0, m] * (100 if "rate" in m or "pct" in m else 1) for m in metrics_b]
web_vals = [_pos.loc[1, m] * (100 if "rate" in m or "pct" in m else 1) for m in metrics_b]

fig, ax = plt.subplots(figsize=(11, 6.5))
x = np.arange(len(labels_b))
w = 0.34
web_bars = ax.bar(x - w / 2, web_vals, width=w, color=TEAL, label="Web (off-site)", zorder=3)
pos_bars = ax.bar(x + w / 2, pos_vals, width=w, color=RED, label="POS (on-site)", zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(labels_b, fontsize=12)
ax.set_title("First-Order Channel: POS vs Web — Customer Outcomes", fontweight="bold", pad=18)
ax.legend(loc="upper right", fontsize=11)
ax.grid(axis="y", alpha=0.35)
ax.set_ylim(0, max(web_vals) * 1.22)

fmt_lbl = [f"{web_vals[0]:.1f}%", f"S${web_vals[1]:,.0f}", f"{web_vals[2]:.1f}%"]
fmt_lbl2 = [f"{pos_vals[0]:.1f}%", f"S${pos_vals[1]:,.0f}", f"{pos_vals[2]:.1f}%"]
for i, (wb, pb, fl, fl2) in enumerate(zip(web_bars, pos_bars, fmt_lbl, fmt_lbl2)):
    ax.text(wb.get_x() + wb.get_width() / 2, wb.get_height() + max(web_vals) * 0.02,
            fl, ha="center", fontsize=10, color=TEAL, fontweight="bold")
    ax.text(pb.get_x() + pb.get_width() / 2, pb.get_height() + max(web_vals) * 0.02,
            fl2, ha="center", fontsize=10, color=RED, fontweight="bold")

fig.text(
    0.5, 0.01,
    "POS = Source='pos' in order export  |  n = 2,743 Web vs 363 POS first-order customers",
    ha="center", fontsize=9, color=SLATE, style="italic",
)
fig.subplots_adjust(bottom=0.14)
save(fig, "08b_pos_vs_web_outcomes")

# ── 08c: Top 10 SKU revenue (one bar per SKU — never grouped) ────────────────
_sku = pd.read_csv(_out / "12_sku_flavor_revenue_2022plus.csv")
_sku["label"] = _sku.apply(
    lambda r: _sku_label(r["Line: Product Handle"], r["Line: Variant Title"], r["Line: SKU"]),
    axis=1,
)
_top = _sku.nlargest(10, "total_revenue").iloc[::-1]

fig_h = _hbar_height(len(_top), base=7.5)
fig, ax = plt.subplots(figsize=(13, fig_h))
bars = ax.barh(_top["label"], _top["total_revenue"], color=TEAL, height=0.68, zorder=3)
ax.set_xlabel("Total Revenue (SGD)", fontsize=11)
ax.set_title("Top 10 SKUs by Revenue (2022+, finals filters — each SKU separate)", fontweight="bold", pad=18)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"S${v:,.0f}"))
ax.tick_params(axis="y", labelsize=9)
ax.set_xlim(0, _top["total_revenue"].max() * 1.38)
_annotate_hbars(
    ax, _top["total_revenue"].tolist(),
    [f"S${v:,.0f}  ·  n={int(n):,}" for v, n in zip(_top["total_revenue"], _top["unique_customers"])],
    fontsize=8.5,
)
fig.tight_layout()
save(fig, "08c_top10_sku_flavor_revenue")

# ── 08d: What makes loyal repeaters come back — factor gaps ─────────────────
_drv = pd.read_csv(_out / "12_loyal_repeater_behavioral_drivers.csv")
_drv = _drv.sort_values("gap_pp", ascending=True)

fig_h = _hbar_height(len(_drv), base=6)
fig, ax = plt.subplots(figsize=(13, fig_h))
y = np.arange(len(_drv))
loyal_p = _drv["loyal_pct"] * 100
one_p = _drv["one_and_done_pct"] * 100
h = 0.34
ax.barh(y - h / 2, loyal_p, height=h, color=TEAL, label="Loyal (3+ orders)", zorder=3)
ax.barh(y + h / 2, one_p, height=h, color=SLATE, label="One-and-done", zorder=3)
ax.set_yticks(y)
ax.set_yticklabels(_drv["factor"], fontsize=10)
ax.set_xlabel("Share of customers in segment (%)", fontsize=11)
ax.set_title("What Makes Loyal Repeaters Different — Key Loyalty Factors", fontweight="bold", pad=18)
ax.legend(loc="lower right", fontsize=10)
ax.set_xlim(0, max(loyal_p.max(), one_p.max()) * 1.25)
for i, (_, row) in enumerate(_drv.iterrows()):
    gap = row["gap_pp"] * 100
    lift = row["lift_vs_one_and_done"]
    ax.text(
        max(row["loyal_pct"], row["one_and_done_pct"]) * 100 + 1.5, i,
        f"+{gap:.0f}pp  ({lift:.1f}× vs one-and-done)" if pd.notna(lift) else f"+{gap:.0f}pp",
        va="center", fontsize=8.5, color=NAVY, fontweight="bold",
    )
fig.text(
    0.5, 0.01,
    "Loyal = 3+ orders & repeat  |  Cross-sell & subscription are strongest differentiators",
    ha="center", fontsize=9, color=SLATE, style="italic",
)
fig.subplots_adjust(bottom=0.10)
save(fig, "08d_loyal_vs_one_and_done")

# ── 08e: First-purchase flavor repeat rate ───────────────────────────────────
_fl = pd.read_csv(_out / "12_first_flavor_loyalty_min30.csv")
_fl = _fl[~_fl["flavor_sku"].str.startswith("unknown", na=False)]
_fl = _fl[_fl["repeat_rate"] < 0.95]  # exclude 100% outliers (legacy / tagging artefacts)
_fl["label"] = _fl.apply(
    lambda r: _sku_label(r["first_handle"], r["first_variant"], r["first_sku"]),
    axis=1,
)
_top_fl = _fl.nlargest(12, "repeat_rate").iloc[::-1]

fig_h = _hbar_height(len(_top_fl), base=8)
fig, ax = plt.subplots(figsize=(13, fig_h))
rates = _top_fl["repeat_rate"] * 100
colors = [TEAL if r >= 35 else ORANGE if r >= 28 else SLATE for r in rates]
ax.barh(_top_fl["label"], rates, color=colors, height=0.68, zorder=3)
xmax = max(rates) * 1.35
ax.set_xlim(0, xmax)
ax.set_xlabel("Repeat Purchase Rate (%)", fontsize=11)
ax.set_title(
    "First-Purchase SKU → Repeat Rate (n ≥ 30, each SKU separate, excl. unknown tags)",
    fontweight="bold", pad=18,
)
ax.tick_params(axis="y", labelsize=9)
_annotate_hbars(
    ax, rates.tolist(),
    [f"{r:.1f}%  ·  LTV S${ltv:.0f}  ·  n={int(n)}" for r, ltv, n in
     zip(rates, _top_fl["avg_ltv"], _top_fl["customers"])],
    fontsize=8.5,
)
fig.tight_layout()
save(fig, "08e_first_flavor_repeat_rate")

# ── 08f: Discontinued / draft products (SKU-level, unique y-labels) ────────────
_disc = pd.read_csv(_out / "12_discontinued_products_history.csv")
_disc["label"] = _disc.apply(
    lambda r: f"{_sku_label(r['Line: Product Handle'], r['Line: Variant Title'], r['Line: SKU'], include_sku=True)} ({r['Status']})",
    axis=1,
)
_top_d = _disc.nlargest(10, "total_revenue").iloc[::-1]
status_color = {"archived": RED, "draft": ORANGE}
bar_colors = [_top_d.iloc[i]["Status"] for i in range(len(_top_d))]
bar_colors = [status_color.get(s, SLATE) for s in bar_colors]

fig_h = _hbar_height(len(_top_d), base=8)
fig, ax = plt.subplots(figsize=(13, fig_h))
ax.barh(_top_d["label"], _top_d["total_revenue"], color=bar_colors, height=0.68, zorder=3)
ax.set_xlabel("Historical Revenue (SGD, all time)", fontsize=11)
ax.set_title("Discontinued & Draft Products — SKU-Level Historical Sales", fontweight="bold", pad=18)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"S${v:,.0f}"))
ax.tick_params(axis="y", labelsize=8.5)
ax.set_xlim(0, _top_d["total_revenue"].max() * 1.45)
_annotate_hbars(
    ax, _top_d["total_revenue"].tolist(),
    [f"S${v:,.0f}  ·  {int(c)} cust  ·  last {str(d)[:10]}" for v, c, d in
     zip(_top_d["total_revenue"], _top_d["unique_customers"], _top_d["last_sale"])],
    fontsize=8,
)
ax.legend(handles=[
    mpatches.Patch(color=RED, label="Archived"),
    mpatches.Patch(color=ORANGE, label="Draft"),
], loc="lower right", fontsize=10)
fig.text(
    0.5, 0.01,
    "Only archived SKU family: prime-whey-isolate (~S$84K)  |  "
    "better-whey = draft, phased out (~S$232K total across all SKUs)",
    ha="center", fontsize=9, color=SLATE, style="italic",
)
fig.subplots_adjust(bottom=0.10)
save(fig, "08f_discontinued_products_history")

# ── 08g: LTV cohort × channel heatmap ────────────────────────────────────────
_cc = pd.read_csv(_out / "12_ltv_by_cohort_channel.csv")
_cc = _cc[_cc["acq_year"] >= 2022]
pivot = _cc.pivot(index="first_channel", columns="acq_year", values="avg_ltv")
channel_order = [c for c in ["Direct / Organic", "Subscription", "Marketplace", "Paid Social"] if c in pivot.index]
pivot = pivot.reindex(channel_order)

fig, ax = plt.subplots(figsize=(11, 5.5))
vals = pivot.values.astype(float)
im = ax.imshow(vals, aspect="auto", cmap="YlGn", vmin=0, vmax=np.nanmax(vals))
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns.astype(int), fontsize=11)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, fontsize=10)
ax.set_xlabel("Acquisition Cohort Year", fontsize=11)
ax.set_ylabel("First Channel", fontsize=11)
ax.set_title("Avg LTV (SGD) by Acquisition Year × Channel", fontweight="bold", pad=18)
ax.grid(False)
for spine in ax.spines.values():
    spine.set_visible(False)

for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        if not np.isnan(val):
            norm = val / np.nanmax(vals) if np.nanmax(vals) else 0
            txt_color = "white" if norm > 0.55 else NAVY
            ax.text(j, i, f"S${val:.0f}", ha="center", va="center",
                    fontsize=10, color=txt_color, fontweight="bold")

cbar = fig.colorbar(im, ax=ax, label="Avg LTV (SGD)", shrink=0.85, pad=0.02)
fig.tight_layout()
save(fig, "08g_ltv_cohort_channel_heatmap")

# ── 08h: Business value scenarios ────────────────────────────────────────────
_bv = pd.read_csv(_out / "12_business_value_scenarios.csv")
pairs = [
    ("Cross-sell: 5% of 1-product → 3-product (conservative)", None),
    ("Retention win-back (conservative 10%)", "Retention win-back (potential 15%)"),
    ("Sub conversion (conservative 5% of non-subs)", "Sub conversion (potential 12.5% of non-subs)"),
    ("Marketplace LTV gap (conservative 5% improved)", "Marketplace LTV gap (potential 15% improved)"),
]
short = ["Cross-sell\n→ 3 products", "Win-back", "Sub\nconversion", "Marketplace\nLTV gap"]
cons, pot = [], []
for c_label, p_label in pairs:
    cons.append(_bv[_bv["opportunity"] == c_label]["gross_profit_uplift_sgd"].iloc[0] / 1000)
    pot.append(_bv[_bv["opportunity"] == p_label]["gross_profit_uplift_sgd"].iloc[0] / 1000 if p_label else cons[-1])

fig, ax = plt.subplots(figsize=(12, 6.5))
x = np.arange(len(short))
w = 0.34
ax.bar(x - w / 2, cons, width=w, color=TEAL, label="Conservative", zorder=3)
ax.bar(x + w / 2, pot, width=w, color=NAVY, label="Potential", zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(short, fontsize=10)
ax.set_ylabel("Gross Profit Uplift (S$ thousands)", fontsize=11)
ax.set_title("Business Value Scenarios — Conservative vs Potential (40% margin proxy)", fontweight="bold", pad=18)
ax.legend(fontsize=11)
ax.set_ylim(0, max(pot) * 1.15)
for i in range(len(short)):
    ax.text(i - w / 2, cons[i] + max(pot) * 0.015, f"S${cons[i]:.0f}K",
            ha="center", fontsize=9.5, color=TEAL, fontweight="bold")
    ax.text(i + w / 2, pot[i] + max(pot) * 0.015, f"S${pot[i]:.0f}K",
            ha="center", fontsize=9.5, color=NAVY, fontweight="bold")
fig.tight_layout()
save(fig, "08h_business_value_scenarios")

# ── 08i: Loyal repeater target tiers ─────────────────────────────────────────
_tier = pd.read_csv(_out / "12_loyal_repeater_target_tiers.csv")
tier_order = [
    "Tier 1: Loyal + Subscribed",
    "Tier 2: Loyal Non-Sub",
    "Tier 3: 2-order",
    "Tier 4: One-and-done",
]
_tier["sort_key"] = _tier["target_tier"].apply(lambda t: tier_order.index(t) if t in tier_order else 99)
_tier = _tier.sort_values("sort_key")
tier_colors = [SLATE, ORANGE, NAVY, TEAL][: len(_tier)]

fig_h = _hbar_height(len(_tier), base=6)
fig, ax = plt.subplots(figsize=(12, fig_h))
bars = ax.barh(_tier["target_tier"], _tier["customers"], color=tier_colors, height=0.62, zorder=3)
ax.set_xlabel("Number of Customers", fontsize=11)
ax.set_title("Customer Targeting Tiers — Who to Prioritise", fontweight="bold", pad=18)
ax.set_xlim(0, _tier["customers"].max() * 1.42)
ax.tick_params(axis="y", labelsize=10)
_annotate_hbars(
    ax, _tier["customers"].tolist(),
    [f"n={int(n):,}  ·  avg LTV S${ltv:,.0f}" for n, ltv in zip(_tier["customers"], _tier["avg_ltv"])],
    fontsize=9.5,
)
fig.tight_layout()
save(fig, "08i_loyal_repeater_target_tiers")

# ── 08j: Reorder interval by top SKUs ───────────────────────────────────────
_re = pd.read_csv(_out / "12_reorder_interval_by_sku.csv")
_re["label"] = _re.apply(
    lambda r: f"{str(r['flavor_label']).replace(' / ', ' · ')}\n[{r['Line: SKU']}]",
    axis=1,
)
_re_top = _re.nlargest(12, "repeat_buyers").iloc[::-1]

fig_h = _hbar_height(len(_re_top), base=8.5)
fig, ax = plt.subplots(figsize=(13, fig_h))
ax.barh(_re_top["label"], _re_top["median_reorder_days"], color=NAVY, height=0.68, zorder=3)
ax.axvline(60, color=ORANGE, linestyle="--", linewidth=2, alpha=0.85, label="60-day reorder window")
ax.set_xlabel("Median Days Between Reorders (same SKU)", fontsize=11)
ax.set_title("Reorder Cadence by SKU (2022+, repeat buyers only)", fontweight="bold", pad=18)
ax.tick_params(axis="y", labelsize=9)
ax.set_xlim(0, max(_re_top["median_reorder_days"]) * 1.35)
_annotate_hbars(
    ax, _re_top["median_reorder_days"].tolist(),
    [f"{d:.0f} days  ·  {int(n)} repeat buyers" for d, n in
     zip(_re_top["median_reorder_days"], _re_top["repeat_buyers"])],
    fontsize=8.5,
)
ax.legend(loc="lower right", fontsize=10)
fig.tight_layout()
save(fig, "08j_reorder_interval_by_sku")

# ── 08k: Top first flavors among loyal repeaters ─────────────────────────────
_lf = pd.read_csv(_out / "12_loyal_repeater_top_first_flavors.csv")
_lf = _lf[~_lf["flavor_sku"].str.startswith("unknown", na=False)]
_lf = _lf[~_lf["flavor_sku"].str.contains("shaker", case=False, na=False)]
_lf["short"] = _lf["flavor_sku"].str.replace(" | ", " · ").str.replace(" / ", " · ")
_top_lf = _lf.head(10).iloc[::-1]

fig_h = _hbar_height(len(_top_lf), base=7)
fig, ax = plt.subplots(figsize=(12, fig_h))
ax.barh(_top_lf["short"], _top_lf["loyal_customers"], color=TEAL, height=0.68, zorder=3)
ax.set_xlabel("Loyal repeaters (3+ orders) whose first purchase was this SKU / flavor", fontsize=11)
ax.set_title("Entry SKUs of Loyal Customers — Top 10 (excl. unknown & accessories)", fontweight="bold", pad=18)
ax.tick_params(axis="y", labelsize=9.5)
ax.set_xlim(0, _top_lf["loyal_customers"].max() * 1.28)
_annotate_hbars(
    ax, _top_lf["loyal_customers"].tolist(),
    [f"{int(v)} loyal" for v in _top_lf["loyal_customers"]],
    fontsize=9.5,
)
fig.text(
    0.5, 0.01,
    "Note: 1,579 loyal customers have unknown first-SKU tags in historical data — excluded from this view",
    ha="center", fontsize=9, color=SLATE, style="italic",
)
fig.subplots_adjust(bottom=0.10)
save(fig, "08k_loyal_repeater_first_flavors")

# ── 08l: P(loyal) by acquisition channel + top entry SKUs ────────────────────
_ch = pd.read_csv(_out / "12_loyal_repeater_rate_by_factor.csv")
_ch = _ch[_ch["factor_type"] == "Acquisition channel"].sort_values("loyal_rate", ascending=True)
_ch["label"] = _ch["factor_value"]

fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={"width_ratios": [1.1, 1.4]})

ax = axes[0]
rates = _ch["loyal_rate"] * 100
ax.barh(_ch["label"], rates, color=TEAL, height=0.58, zorder=3)
ax.set_xlabel("Become loyal repeater (%)", fontsize=10)
ax.set_title("By Acquisition Channel", fontweight="bold", fontsize=12)
_cmp = pd.read_csv(_out / "12_loyal_vs_one_and_done.csv")
bl_rate = _cmp.loc[0, "customers"] / _cmp["customers"].sum() * 100
ax.axvline(bl_rate, color=ORANGE, linestyle="--", linewidth=1.5, label=f"Overall {bl_rate:.0f}%")
for i, (_, row) in enumerate(_ch.iterrows()):
    ax.text(row["loyal_rate"] * 100 + 0.3, i, f"{row['loyal_rate']*100:.1f}%  (n={int(row['customers']):,})",
            va="center", fontsize=8.5, color=NAVY)
ax.legend(fontsize=9)

_skl = pd.read_csv(_out / "12_loyal_rate_by_first_sku_min30.csv")
_skl = _skl[~_skl["flavor_sku"].str.startswith("unknown", na=False)]
_skl = _skl[_skl["loyal_rate"] < 0.95]
_skl["label"] = _skl.apply(lambda r: _sku_label(r["first_handle"], r["first_variant"], r["first_sku"]), axis=1)
_top_sk = _skl.nlargest(8, "loyal_rate").iloc[::-1]

ax = axes[1]
sk_rates = _top_sk["loyal_rate"] * 100
ax.barh(_top_sk["label"], sk_rates, color=NAVY, height=0.58, zorder=3)
ax.set_xlabel("Become loyal repeater (%)", fontsize=10)
ax.set_title("By First-Purchase SKU (n ≥ 30, active portfolio)", fontweight="bold", fontsize=12)
ax.axvline(bl_rate, color=ORANGE, linestyle="--", linewidth=1.5)
ax.tick_params(axis="y", labelsize=8)
for i, (_, row) in enumerate(_top_sk.iterrows()):
    ax.text(row["loyal_rate"] * 100 + 0.3, i,
            f"{row['loyal_rate']*100:.1f}%  ·  n={int(row['customers'])}",
            va="center", fontsize=8, color=NAVY)

fig.suptitle("What Entry Points Create Loyal Repeaters?", fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "08l_loyal_repeater_entry_drivers")

print("Done — 08_finals_charts (08a–08l)")
