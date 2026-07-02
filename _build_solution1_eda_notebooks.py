"""Generate solution_1_from_raw.ipynb and EDA_from_raw.ipynb from shared pipeline."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "solution2_standalone_from_raw.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [ln + "\n" for ln in text.strip().split("\n")]}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": [ln + "\n" for ln in text.strip().split("\n")],
        "outputs": [],
        "execution_count": None,
    }


def save(cells: list, path: Path) -> None:
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "cells": cells,
    }
    path.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"Wrote {path.name} ({len(cells)} cells)")


def src_join(cells: list) -> str:
    return "".join(cells)


def patch_setup(source: list[str]) -> list[str]:
    text = src_join(source)
    if "N_TIERS = 5" not in text:
        text = text.replace("MARGIN_PROXY = 0.40\n", "MARGIN_PROXY = 0.40\nN_TIERS = 5\n")
    text = text.replace(
        "from sklearn.metrics.pairwise import cosine_similarity\n",
        "import matplotlib.ticker as mticker\n",
    )
    text = text.replace(
        "from IPython.display import display\n",
        "try:\n    from IPython.display import display\nexcept ImportError:\n    display = print\n",
    )
    return [ln + "\n" for ln in text.split("\n") if ln or text.endswith("\n")]


def patch_helpers(source: list[str]) -> list[str]:
    text = src_join(source)
    extra = (
        "\n\n"
        "def assign_decile_5(series: pd.Series, n_tiers: int = N_TIERS) -> pd.Series:\n"
        '    """D1 = best. Five tiers for Solution 1 (founder request)."""\n'
        '    ranks = series.rank(method="first", ascending=True)\n'
        '    return pd.qcut(ranks, q=n_tiers, labels=[f"D{i}" for i in range(n_tiers, 0, -1)])\n'
    )
    if "assign_decile_5" not in text:
        text = text.rstrip() + extra + "\n"
    return [ln + "\n" for ln in text.split("\n")]


def patch_load(source: list[str]) -> list[str]:
    text = src_join(source)
    alias = (
        "\n\n"
        "# Aliases for EDA comparisons (raw snapshot before finals filters)\n"
        "orders_all = orders_df.copy()\n"
        "lines_all = lines_df.copy()\n"
        "cust_all = cust_base.copy()\n"
    )
    if "orders_all = orders_df" not in text:
        text = text.rstrip() + alias + "\n"
    return [ln + "\n" for ln in text.split("\n")]


def patch_part_c(source: list[str], out_subdir: str) -> list[str]:
    text = src_join(source)
    text = text.replace('STANDALONE_OUT / f"{name}.parquet"', 'OUT_DIR / f"{name}.parquet"')
    text = text.replace('STANDALONE_OUT / "manifest.json"', 'OUT_DIR / "manifest.json"')
    text = text.replace('"source": "solution2_standalone_from_raw.ipynb"', f'"source": "{out_subdir}_from_raw.ipynb"')
    if not text.lstrip().startswith("OUT_DIR"):
        text = f'OUT_DIR = STANDALONE_OUT / "{out_subdir}"\nOUT_DIR.mkdir(exist_ok=True)\n\n' + text
    # Add avg_margin_pct + cogs_coverage_pct
    insert = '''
covered = lines[lines["has_cogs"]]
cust_gp = covered.groupby("customer_id").agg(
    true_gp_covered=("gross_profit", "sum"), rev_covered=("line_rev", "sum"),
).reset_index()
rev_all = lines.groupby("customer_id")["line_rev"].sum().reset_index(name="rev_total_lines")
cust_gp = rev_all.merge(cust_gp, on="customer_id", how="left")
cust_gp["cogs_coverage_pct"] = np.where(
    cust_gp["rev_total_lines"] > 0, cust_gp["rev_covered"].fillna(0) / cust_gp["rev_total_lines"], 0,
)
customers = customers.merge(cust_gp[["customer_id", "cogs_coverage_pct"]], on="customer_id", how="left")
customers["cogs_coverage_pct"] = customers["cogs_coverage_pct"].fillna(0)
customers["avg_margin_pct"] = np.where(
    customers["finals_revenue"] > 0, customers["true_gross_profit"] / customers["finals_revenue"], np.nan,
)
'''
    text = text.replace(
        'customers["n_categories_ever"] = customers["n_categories_ever"].fillna(1).astype(int)\n',
        'customers["n_categories_ever"] = customers["n_categories_ever"].fillna(1).astype(int)\n' + insert,
    )
    return [ln + "\n" for ln in text.split("\n")]


def load_base_cells() -> list[dict]:
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    cells = deepcopy(nb["cells"][:8])  # title through Part C
    cells[0] = md("""
# LushProtein — Shared Raw Pipeline (base cells)

This cell block is reused by the generator; replaced in output notebooks.
""")
    return cells


def pipeline_cells(out_subdir: str) -> list[dict]:
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    cells = deepcopy(nb["cells"][:8])
    # Fix title cell later per notebook
    cells[1] = DEPS_CELL if False else cells[1]
    cells[3]["source"] = patch_setup(cells[3]["source"])
    cells[4]["source"] = patch_helpers(cells[4]["source"])
    cells[7]["source"] = patch_part_c(cells[7]["source"], out_subdir)
    # Rename in load + finals cells for clarity
    for idx in (5, 6):
        src = src_join(cells[idx]["source"])
        src = src.replace("orders_df", "orders_all").replace("lines_df", "lines_all").replace("cust_base", "cust_all")
        cells[idx]["source"] = [ln + "\n" for ln in src.split("\n")]
    return cells


DEPS_CELL = nb_cells = None  # placeholder


def apply_base_patches(cells: list[dict], out_subdir: str) -> None:
    cells[2]["source"] = patch_setup(cells[2]["source"])
    cells[3]["source"] = patch_helpers(cells[3]["source"])
    cells[5]["source"] = patch_load(cells[5]["source"])
    cells[10]["source"] = patch_part_c(cells[10]["source"], out_subdir)


def build_solution1() -> list[dict]:
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    cells = deepcopy(nb["cells"][:11])  # through Part C margin enrichment

    cells[0] = md("""
# LushProtein — Solution 1 Standalone (Raw Data → Decile & CRM Tiers)

**Fully self-contained.** Requires only the five raw data folders at project root.

**Profit formula (founder-scoped):** `Profit = Net Revenue − COGS` (no fulfillment/refund terms).

**Pipeline:**
1. Install dependencies
2. Load & merge raw Shopify transactions
3. Apply DQ + LP founder filters → finals cohort
4. Enrich with COGS from product master
5. Reproduce Solution 1: 5-tier profit & frequency deciles, CRM tiers, charts

References: `EDA/lushprotein_decile.ipynb`, `EDA/lushprotein_decile_v2.ipynb`
""")

    apply_base_patches(cells, "solution1")

    cells.extend([
        md("## Part D — Marketplace exclusion & decile pool"),
        code("""
# Channel mix — flag 100% Marketplace accounts (Shopee/Lazada aggregator pattern)
cust = customers.copy()
orders = orders.copy()

cust_channel_mix = orders.groupby("customer_id")["channel"].value_counts(normalize=True).unstack(fill_value=0)
mkt_col = cust_channel_mix.get("Marketplace", pd.Series(0, index=cust_channel_mix.index))
all_marketplace_ids = set(cust_channel_mix[mkt_col == 1.0].index.astype(str))

cust["is_all_marketplace"] = cust["customer_id"].astype(str).isin(all_marketplace_ids)

print("Orders by channel (finals cohort):")
print(orders["channel"].value_counts().to_string())
print(f"\\nAll-Marketplace customers to exclude: {len(all_marketplace_ids):,}")

# Decile pool: finals_eligible AND not all-marketplace
pool_mask = (cust["finals_eligible"] == True) & (~cust["is_all_marketplace"])
df = cust[pool_mask].copy()

print(f"\\nFilter funnel:")
print(f"  Finals customers          : {len(cust):,}")
print(f"  - all-marketplace excluded: {len(df):,}")
print(f"  Final decile pool         : {len(df):,}")
print(f"\\nProfit range: S${df['true_gross_profit'].min():,.2f} – S${df['true_gross_profit'].max():,.2f}")
print(f"Order count range: {df['finals_orders'].min()} – {df['finals_orders'].max()}")
"""),
        md("## Part E — Two 5-tier deciles (Profit & Order Frequency)"),
        code("""
df["profit_decile"] = assign_decile_5(df["true_gross_profit"])
df["order_freq_decile"] = assign_decile_5(df["finals_orders"])

print("Profit decile counts:")
print(df["profit_decile"].value_counts().sort_index().to_string())
print("\\nOrder frequency decile counts:")
print(df["order_freq_decile"].value_counts().sort_index().to_string())

profit_summary = (
    df.groupby("profit_decile", observed=False)
    .agg(
        n_customers=("customer_id", "count"),
        total_profit=("true_gross_profit", "sum"),
        avg_profit=("true_gross_profit", "mean"),
        median_profit=("true_gross_profit", "median"),
        avg_revenue=("finals_revenue", "mean"),
        avg_orders=("finals_orders", "mean"),
        avg_margin_pct=("avg_margin_pct", "mean"),
    )
    .reset_index()
)
total_profit_pool = profit_summary["total_profit"].sum()
profit_summary["pct_of_total_profit"] = profit_summary["total_profit"] / total_profit_pool
profit_summary["cum_pct_profit"] = profit_summary["pct_of_total_profit"].cumsum()

freq_summary = (
    df.groupby("order_freq_decile", observed=False)
    .agg(
        n_customers=("customer_id", "count"),
        total_orders=("finals_orders", "sum"),
        avg_orders=("finals_orders", "mean"),
        avg_profit=("true_gross_profit", "mean"),
    )
    .reset_index()
)
total_orders_pool = freq_summary["total_orders"].sum()
freq_summary["pct_of_total_orders"] = freq_summary["total_orders"] / total_orders_pool

print(f"\\nDECILE BY PROFIT — pool={len(df):,} | total profit=S${total_profit_pool:,.0f}")
display(profit_summary)
d1_pct = profit_summary.loc[profit_summary["profit_decile"] == "D1", "pct_of_total_profit"].values[0]
print(f"Top 20% (D1) generate {d1_pct:.1%} of total profit")
"""),
        code("""
# Profit decile charts
OUT = STANDALONE_OUT / "solution1"
OUT.mkdir(exist_ok=True)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
tiers = profit_summary["profit_decile"].astype(str)
colors = ["#2E86AB" if t == "D1" else "#A8DADC" for t in tiers]

axes[0].bar(tiers, profit_summary["pct_of_total_profit"] * 100, color=colors, edgecolor="white")
axes[0].set_title("% of Total Profit by Tier")
axes[0].set_ylabel("% of profit")
axes[0].yaxis.set_major_formatter(mticker.PercentFormatter())

axes[1].bar(tiers, profit_summary["avg_profit"], color=colors, edgecolor="white")
axes[1].set_title("Avg Profit per Customer")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S${x:,.0f}"))

axes[2].plot(range(1, N_TIERS + 1), profit_summary["cum_pct_profit"] * 100, marker="o", color="#2E86AB", lw=2)
axes[2].set_title("Cumulative Profit Concentration")
axes[2].set_xticks(range(1, N_TIERS + 1))
axes[2].set_xticklabels([f"D{i}" for i in range(1, N_TIERS + 1)])
axes[2].yaxis.set_major_formatter(mticker.PercentFormatter())
axes[2].axhline(80, color="gray", ls="--", alpha=0.5)

plt.tight_layout()
plt.savefig(OUT / "decile_profit.png", dpi=150)
plt.show()
print("Saved:", OUT / "decile_profit.png")
"""),
        code("""
# Order frequency decile charts
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
tiers_f = freq_summary["order_freq_decile"].astype(str)
colors_f = ["#E76F51" if t == "D1" else "#F4A261" for t in tiers_f]

axes[0].bar(tiers_f, freq_summary["avg_orders"], color=colors_f, edgecolor="white")
axes[0].set_title("Avg Orders per Customer")

axes[1].bar(tiers_f, freq_summary["pct_of_total_orders"] * 100, color=colors_f, edgecolor="white")
axes[1].set_title("% of Total Orders")
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter())

axes[2].bar(tiers_f, freq_summary["avg_profit"], color=colors_f, edgecolor="white")
axes[2].set_title("Avg Profit by Frequency Tier")
axes[2].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S${x:,.0f}"))

plt.tight_layout()
plt.savefig(OUT / "decile_order_frequency.png", dpi=150)
plt.show()
print("Saved:", OUT / "decile_order_frequency.png")
"""),
        md("## Part F — Overlap heatmap (Profit D1 × Frequency D1)"),
        code("""
d1_profit = set(df[df["profit_decile"] == "D1"]["customer_id"])
d1_freq = set(df[df["order_freq_decile"] == "D1"]["customer_id"])
d1_both = d1_profit & d1_freq

print(f"D1 profit only     : {len(d1_profit):,}")
print(f"D1 frequency only  : {len(d1_freq):,}")
print(f"D1 BOTH (overlap)  : {len(d1_both):,}")

cross = pd.crosstab(df["profit_decile"], df["order_freq_decile"])
all_tiers = [f"D{i}" for i in range(1, N_TIERS + 1)]
cross = cross.reindex(index=all_tiers, columns=all_tiers, fill_value=0)

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(cross.values, cmap="Blues")
ax.set_xticks(range(N_TIERS))
ax.set_yticks(range(N_TIERS))
ax.set_xticklabels(all_tiers)
ax.set_yticklabels(all_tiers)
ax.set_xlabel("Order Frequency Decile")
ax.set_ylabel("Profit Decile")
ax.set_title("Profit × Frequency Tier Overlap")
for i in range(N_TIERS):
    for j in range(N_TIERS):
        ax.text(j, i, f"{cross.values[i, j]:,}", ha="center", va="center", color="black", fontsize=9)
plt.colorbar(im, ax=ax, fraction=0.046)
plt.tight_layout()
plt.savefig(OUT / "decile_overlap_heatmap.png", dpi=150)
plt.show()
print("Saved:", OUT / "decile_overlap_heatmap.png")
"""),
        md("## Part G — CRM treatment tiers (v2 logic)"),
        code("""
# Tier assignment — same priority as lushprotein_decile_v2.ipynb
d1_profit_ids = set(df[df["profit_decile"] == "D1"]["customer_id"])
d1_freq_ids = set(df[df["order_freq_decile"] == "D1"]["customer_id"])
tier1_ids = d1_profit_ids & d1_freq_ids
tier2_ids = d1_profit_ids - tier1_ids
tier3_ids = d1_freq_ids - tier1_ids

d2_profit_ids = set(df[df["profit_decile"] == "D2"]["customer_id"])
d2_freq_ids = set(df[df["order_freq_decile"] == "D2"]["customer_id"])
already_placed = tier1_ids | tier2_ids | tier3_ids
tier4_ids = (d2_profit_ids | d2_freq_ids) - already_placed

def assign_tier(cid):
    if cid in tier1_ids:
        return "Tier 1 (D1 Both)"
    if cid in tier2_ids:
        return "Tier 2 (D1 Profit Only)"
    if cid in tier3_ids:
        return "Tier 3 (D1 Frequency Only)"
    if cid in tier4_ids:
        return "Tier 4 (D2 Profit or Frequency)"
    return "Untiered"

df["customer_tier"] = df["customer_id"].apply(assign_tier)
df["is_top_profit"] = df["profit_decile"] == "D1"
df["is_top_freq"] = df["order_freq_decile"] == "D1"
df["is_top_both"] = df["is_top_profit"] & df["is_top_freq"]

print("Customers per CRM tier:")
print(df["customer_tier"].value_counts().to_string())

tier_order = [
    "Tier 1 (D1 Both)", "Tier 2 (D1 Profit Only)",
    "Tier 3 (D1 Frequency Only)", "Tier 4 (D2 Profit or Frequency)",
]
tier_margin = (
    df[df["customer_tier"] != "Untiered"]
    .groupby("customer_tier")
    .agg(
        n=("customer_id", "count"),
        avg_margin=("avg_margin_pct", "mean"),
        avg_gp=("true_gross_profit", "mean"),
        avg_rev=("finals_revenue", "mean"),
        avg_orders=("finals_orders", "mean"),
    )
    .reindex(tier_order)
)
display(tier_margin)
"""),
        code("""
# Reinvestment table (20% of contribution margin)
REINVEST_PCT = 0.20
tier_summary = (
    df[df["customer_tier"] != "Untiered"]
    .groupby("customer_tier")
    .agg(
        n_customers=("customer_id", "count"),
        total_gp=("true_gross_profit", "sum"),
        avg_gp=("true_gross_profit", "mean"),
    )
    .reindex(tier_order)
)
tier_summary["total_reinvestable"] = tier_summary["total_gp"] * REINVEST_PCT
tier_summary["reinvest_per_cust"] = tier_summary["avg_gp"] * REINVEST_PCT
print(f"Reinvestment at {REINVEST_PCT:.0%} of GP:")
display(tier_summary)
print(f"Total reinvestable: S${tier_summary['total_reinvestable'].sum():,.2f}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(tier_summary.index.astype(str), tier_summary["total_reinvestable"], color="#457B9D", edgecolor="white")
ax.set_title("Reinvestment Budget by CRM Tier (20% of GP)")
ax.set_ylabel("S$")
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig(OUT / "tier_reinvestment.png", dpi=150)
plt.show()
"""),
        md("## Part H — Behavioral profiles by tier"),
        code("""
# Recency from finals orders
most_recent = orders["order_date"].max()
if "last_order_date" not in df.columns:
    last_order = orders.groupby("customer_id")["order_date"].max().reset_index(name="last_order_date")
    df = df.merge(last_order, on="customer_id", how="left")
df["last_order_date"] = pd.to_datetime(df["last_order_date"], utc=True)
df["days_since_last_order"] = (most_recent - df["last_order_date"]).dt.days

print("=" * 70)
print("BEHAVIORAL PROFILE BY TIER")
print("=" * 70)
for tier in tier_order:
    t = df[df["customer_tier"] == tier]
    print(f"\\n{'─' * 70}")
    print(f"{tier}  ({len(t):,} customers)")
    print(f"  Ever subscribed     : {t['ever_subscribed'].mean():.1%}")
    print(f"  Avg categories      : {t['n_categories_ever'].mean():.2f}")
    print(f"  Avg first-disc depth: {t['first_disc_depth'].mean():.1%}")
    print(f"  Median recency (days): {t['days_since_last_order'].median():.0f}")
    print("  First channel (%):", t["first_channel"].value_counts(normalize=True).mul(100).round(1).head(3).to_dict())

# Stacked bar: channel mix by tier
ch = df[df["customer_tier"].isin(tier_order)].copy()
ch_pct = ch.groupby(["customer_tier", "first_channel"]).size().unstack(fill_value=0)
ch_pct = ch_pct.div(ch_pct.sum(axis=1), axis=0).reindex(tier_order)
ch_pct.plot(kind="bar", stacked=True, figsize=(10, 5), colormap="Set2")
plt.title("Acquisition Channel Mix by CRM Tier")
plt.ylabel("Share of tier")
plt.xticks(rotation=15)
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig(OUT / "tier_channel_mix.png", dpi=150)
plt.show()
"""),
        md("## Part I — Export decile customer table"),
        code("""
export_cols = [
    "customer_id", "true_gross_profit", "finals_revenue", "finals_orders",
    "avg_margin_pct", "cogs_coverage_pct", "profit_decile", "order_freq_decile",
    "customer_tier", "is_top_profit", "is_top_freq", "is_top_both",
    "first_channel", "first_product_cat", "ever_subscribed", "n_categories_ever",
    "first_order_date", "cohort_month", "acq_year",
]
export_df = df[[c for c in export_cols if c in df.columns]].copy()
export_df = export_df.sort_values(["profit_decile", "true_gross_profit"], ascending=[True, False])
for col in ["true_gross_profit", "finals_revenue"]:
    if col in export_df.columns:
        export_df[col] = export_df[col].round(2)

out_csv = OUT / "decile_customer_table.csv"
export_df.to_csv(out_csv, index=False)
print(f"Saved: {out_csv}")
print(f"Rows: {len(export_df):,}")
display(export_df[export_df["profit_decile"] == "D1"].head(8))
"""),
        md("## Part J — Summary"),
        code("""
print("=" * 65)
print("SOLUTION 1 — SUMMARY")
print("=" * 65)
print(f"Decile pool (finals, excl. all-marketplace): {len(df):,}")
d1c = profit_summary[profit_summary["profit_decile"] == "D1"].iloc[0]
d1f = freq_summary[freq_summary["order_freq_decile"] == "D1"].iloc[0]
print(f"\\nD1 by profit    : {d1c['n_customers']:,} customers | {d1c['pct_of_total_profit']:.1%} of profit")
print(f"D1 by frequency : {d1f['n_customers']:,} customers | {d1f['pct_of_total_orders']:.1%} of orders")
print(f"D1 overlap      : {len(d1_both):,} customers")
print("\\nOutputs in:", OUT)
print("  decile_customer_table.csv")
print("  decile_profit.png | decile_order_frequency.png | decile_overlap_heatmap.png")
print("  tier_reinvestment.png | tier_channel_mix.png")
print("=" * 65)
"""),
    ])
    return cells


def build_eda() -> list[dict]:
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    cells = deepcopy(nb["cells"][:11])

    cells[0] = md("""
# LushProtein — EDA from Raw Data (Data Quality & Finals Filters)

**Fully self-contained.** Loads the five raw data folders and reproduces mid-term EDA plus
post-midterm **finals cohort filters** (DQ-02/03/04, LP-F01–F04, Layer 0/3).

Includes filter funnel metrics and **20+ visualizations** documenting data quality decisions.
""")

    apply_base_patches(cells, "eda")

    cells.extend([
        md("## Part D — Rebuild filter funnel with step-by-step counts"),
        code("""
# Recompute funnel on copies for visualization (mirrors 13_build_finals_datasets.py)
o = orders_all.copy()
l = lines_all.copy()
c = cust_all.copy()

if "Payment: Status" in o.columns:
    o = o[o["Payment: Status"].isin(["paid", "partially_refunded"]) | o["Payment: Status"].isna()]
o = o[o["Order Fulfillment Status"].fillna("") != "restocked"]

_rev = pd.to_numeric(o["Price: Total"], errors="coerce").fillna(0)
_disc = pd.to_numeric(o["Price: Total Discount"], errors="coerce").fillna(0)
dq02 = (_rev == 0) & (_disc == 0)
dq03 = (_rev == 0) & (_disc > 0)
dq04 = o["Tags"].fillna("").str.lower().str.contains("wholesale") | (_rev > 5000)
o_dq = o[~(dq02 | dq03 | dq04)].copy()
l_dq = l[l["order_id"].isin(set(o_dq["order_id"]))].copy()
c_dq = rebuild_customers(o_dq, l_dq, c)

finals_ids = set(c_dq[c_dq["finals_eligible"]]["customer_id"])
o_l2 = o_dq[o_dq["customer_id"].isin(finals_ids)].copy()
o_l0 = o_l2[o_l2["order_date"] >= ANALYSIS_START].copy()
_jul = o_l0["order_date"].dt.month.isin(EXCLUDE_MONTHS)
o_f = o_l0[~_jul].copy()

funnel = pd.DataFrame({
    "step": [
        "Raw orders", "After payment/fulfillment", "After DQ-02/03/04",
        "LP-F finals customers", "Orders 2022+", "Excl Jul/Nov months",
    ],
    "orders": [len(orders_all), len(o), len(o_dq), len(o_l2), len(o_l0), len(o_f)],
    "customers": [len(c), c["customer_id"].nunique(), c_dq["customer_id"].nunique(),
                  len(finals_ids), o_l0["customer_id"].nunique(), o_f["customer_id"].nunique()],
})
display(funnel)

dq_counts = pd.Series({"DQ-02 zero/zero": dq02.sum(), "DQ-03 free fulfilment": dq03.sum(), "DQ-04 wholesale/>5k": dq04.sum()})
lp_counts = pd.Series({
    "LP-F03 pre-2022 acq": (~(c_dq["first_order_date"] >= ANALYSIS_START)).sum(),
    "LP-F01 elite SKU": c_dq["exclude_elite_buyer"].sum(),
    "LP-F02 Jul/Nov acq": c_dq["exclude_promo_month"].sum(),
    "LP-F04 51%+ 1st disc": c_dq["exclude_51pct"].sum(),
    "Finals eligible": c_dq["finals_eligible"].sum(),
})
print("\\nDQ drops:", dq_counts.to_dict())
print("LP flags:", lp_counts.to_dict())
"""),
        md("## Part E — Visualizations: raw data profile"),
        code("""
OUT = STANDALONE_OUT / "eda"
OUT.mkdir(exist_ok=True)

# 1. Orders by year
oy = orders_all.assign(year=orders_all["order_date"].dt.year).groupby("year").size()
fig, ax = plt.subplots(figsize=(8, 4))
oy.plot(kind="bar", ax=ax, color="#457B9D", edgecolor="white")
ax.set_title("Raw Order Volume by Year")
ax.set_ylabel("Orders")
plt.tight_layout()
plt.savefig(OUT / "01_orders_by_year.png", dpi=150)
plt.show()

# 2. Revenue distribution (log)
rev = pd.to_numeric(orders_all["Price: Total"], errors="coerce").fillna(0)
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(rev[rev > 0], bins=60, color="#A8DADC", edgecolor="white")
ax.set_xscale("log")
ax.set_title("Order Revenue Distribution (SGD, log scale)")
plt.tight_layout()
plt.savefig(OUT / "02_revenue_distribution.png", dpi=150)
plt.show()

# 3. Channel mix — raw vs finals
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
orders_all["channel"].value_counts().plot(kind="barh", ax=axes[0], color="#E76F51")
axes[0].set_title("Raw — Channel Mix")
orders["channel"].value_counts().plot(kind="barh", ax=axes[1], color="#2E86AB")
axes[1].set_title("Finals Cohort — Channel Mix")
plt.tight_layout()
plt.savefig(OUT / "03_channel_raw_vs_finals.png", dpi=150)
plt.show()

# 4. Store mix
orders_all["store"].value_counts().plot(kind="pie", autopct="%1.1f%%", figsize=(6, 6), ylabel="")
plt.title("Orders by Store (SG/MY/HK)")
plt.savefig(OUT / "04_store_mix.png", dpi=150)
plt.show()

# 5. Product category mix
cat = lines_all.groupby("product_category")["Line: Total"].sum().sort_values(ascending=False).head(8)
fig, ax = plt.subplots(figsize=(8, 4))
cat.plot(kind="bar", ax=ax, color="#F4A261", edgecolor="white")
ax.set_title("Line Revenue by Product Category (raw)")
ax.set_ylabel("SGD")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(OUT / "05_category_revenue.png", dpi=150)
plt.show()
"""),
        code("""
# 6. Filter funnel waterfall — orders
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(funnel["step"], funnel["orders"], color="#457B9D", edgecolor="white")
ax.set_title("Filter Funnel — Orders Remaining at Each Step")
ax.set_xlabel("Order count")
for i, v in enumerate(funnel["orders"]):
    ax.text(v + 100, i, f"{v:,}", va="center")
plt.tight_layout()
plt.savefig(OUT / "06_funnel_orders.png", dpi=150)
plt.show()

# 7. Filter funnel — customers
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(funnel["step"], funnel["customers"], color="#E76F51", edgecolor="white")
ax.set_title("Filter Funnel — Unique Customers")
ax.set_xlabel("Customer count")
for i, v in enumerate(funnel["customers"]):
    ax.text(v + 50, i, f"{v:,}", va="center")
plt.tight_layout()
plt.savefig(OUT / "07_funnel_customers.png", dpi=150)
plt.show()

# 8. DQ rule breakdown
fig, ax = plt.subplots(figsize=(7, 4))
dq_counts.plot(kind="bar", ax=ax, color=["#E63946", "#F4A261", "#457B9D"], edgecolor="white")
ax.set_title("Data Quality Drops (Layer 1)")
ax.set_ylabel("Orders removed")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig(OUT / "08_dq_drops.png", dpi=150)
plt.show()

# 9. LP founder filter flags
fig, ax = plt.subplots(figsize=(8, 4))
lp_counts.plot(kind="bar", ax=ax, color="#2A9D8F", edgecolor="white")
ax.set_title("Founder Filters (LP-F01–F04) — Customer Flags")
ax.set_ylabel("Customers")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(OUT / "09_lp_filters.png", dpi=150)
plt.show()
"""),
        code("""
# 10. Acquisition cohort heatmap (finals customers)
fc = customers[customers["finals_eligible"] == True].copy()
fc["acq_year"] = fc["first_order_date"].dt.year
fc["acq_month"] = fc["first_order_date"].dt.month
cohort = fc.groupby(["acq_year", "acq_month"]).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(cohort, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
ax.set_title("Finals Cohort — Customer Acquisition Heatmap")
plt.tight_layout()
plt.savefig(OUT / "10_acquisition_heatmap.png", dpi=150)
plt.show()

# 11. Promo month impact (Jul/Nov order share)
om = orders.copy()
om["month"] = om["order_date"].dt.month
month_cnt = om["month"].value_counts().sort_index()
colors_m = ["#E63946" if m in EXCLUDE_MONTHS else "#457B9D" for m in month_cnt.index]
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(month_cnt.index, month_cnt.values, color=colors_m, edgecolor="white")
ax.set_title("Finals Orders by Calendar Month (Jul/Nov excluded in Layer 3)")
ax.set_xlabel("Month")
plt.tight_layout()
plt.savefig(OUT / "11_orders_by_month.png", dpi=150)
plt.show()

# 12. First-order discount depth
fd = customers["first_disc_depth"].dropna()
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(fd, bins=30, color="#A8DADC", edgecolor="white")
ax.axvline(0.51, color="red", ls="--", label="LP-F04 threshold (51%)")
ax.set_title("First Retained Order — Discount Depth")
ax.set_xlabel("Discount depth")
ax.legend()
plt.tight_layout()
plt.savefig(OUT / "12_first_disc_depth.png", dpi=150)
plt.show()
"""),
        code("""
# 13. Repeat vs one-time (finals)
rep = customers["is_repeat"].value_counts()
fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(rep.values, labels=["One-time", "Repeat"], autopct="%1.1f%%", colors=["#E76F51", "#2E86AB"])
ax.set_title("Finals Customers: Repeat vs One-time")
plt.savefig(OUT / "13_repeat_rate.png", dpi=150)
plt.show()

# 14. COGS coverage
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(customers["cogs_coverage_pct"].fillna(0), bins=20, color="#457B9D", edgecolor="white")
ax.set_title("COGS Coverage % per Customer (lines with real unit cost)")
ax.set_xlabel("Share of line revenue with COGS")
plt.tight_layout()
plt.savefig(OUT / "14_cogs_coverage.png", dpi=150)
plt.show()

# 15. Monthly revenue trend (finals)
mo = orders.copy()
mo["ym"] = mo["order_date"].dt.to_period("M")
monthly_rev = mo.groupby("ym")["Price: Total"].sum()
fig, ax = plt.subplots(figsize=(12, 4))
monthly_rev.plot(ax=ax, color="#2E86AB", lw=2)
ax.set_title("Finals Cohort — Monthly Revenue (SGD)")
ax.set_ylabel("Revenue")
plt.tight_layout()
plt.savefig(OUT / "15_monthly_revenue.png", dpi=150)
plt.show()

# 16. Subscription rate over acquisition year
sub = fc.groupby("acq_year")["ever_subscribed"].mean()
fig, ax = plt.subplots(figsize=(8, 4))
sub.plot(kind="bar", ax=ax, color="#F4A261", edgecolor="white")
ax.set_title("Subscription Rate by Acquisition Year")
ax.set_ylabel("Share ever subscribed")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
plt.tight_layout()
plt.savefig(OUT / "16_sub_rate_by_year.png", dpi=150)
plt.show()

# 17. Before/after comparison panel
compare = pd.DataFrame({
    "metric": ["Orders", "Customers", "Median order value"],
    "Raw": [len(orders_all), len(cust_all), orders_all["Price: Total"].median()],
    "Finals": [len(orders), len(customers), orders["Price: Total"].median()],
})
display(compare)

fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(len(compare))
w = 0.35
ax.bar(x - w/2, compare["Raw"], w, label="Raw", color="#A8DADC")
ax.bar(x + w/2, compare["Finals"], w, label="Finals", color="#2E86AB")
ax.set_xticks(x)
ax.set_xticklabels(compare["metric"])
ax.legend()
ax.set_title("Raw vs Finals Cohort — Key Metrics")
plt.tight_layout()
plt.savefig(OUT / "17_raw_vs_finals.png", dpi=150)
plt.show()

print(f"\\nSaved 17 charts to {OUT}")
"""),
        md("## Part F — Summary"),
        code("""
print("=" * 65)
print("EDA FROM RAW — SUMMARY")
print("=" * 65)
print(f"Raw orders/customers     : {len(orders_all):,} / {len(cust_all):,}")
print(f"Finals orders/customers  : {len(orders):,} / {len(customers):,}")
print(f"COGS line coverage     : {lines['has_cogs'].mean():.1%}")
print(f"Charts saved to        : {OUT}")
print("=" * 65)
"""),
    ])
    return cells


if __name__ == "__main__":
    save(build_solution1(), ROOT / "solution_1_from_raw.ipynb")
    save(build_eda(), ROOT / "EDA_from_raw.ipynb")
