"""
run_decile_analysis.py — Export decile CSVs from outputs_finals data.

Mirrors decile_lens1.ipynb + decile_lens2.ipynb logic:
  - Pool: finals customers (outputs_finals/customers.parquet) minus 100% marketplace
  - Lens 1: profit decile (profit_proxy = revenue × 40%) + frequency decile (clean_orders)
  - Lens 2: 5-tier migration 2022–2023 vs 2024–2025 (both-period customers)

Outputs → data/gold/analytics/decile/ (legacy: EDA/decile_analysis/outputs/)

Run: python EDA/decile_analysis/run_decile_analysis.py
"""
import warnings
warnings.filterwarnings("ignore")

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EDA_DIR = SCRIPT_DIR.parent

def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_cfg = _load_config()
FINALS_DIR = _cfg.FINALS_DIR
OUT_DIR = _cfg.GOLD_ANALYTICS_DECILE
OUT_DIR.mkdir(parents=True, exist_ok=True)

MARGIN_RATE = 0.40
DECILE_BEST_FIRST = [f"D{i}" for i in range(1, 11)]   # D1 = best (for summary CSV row order)
DECILE_CHART_ORDER = [f"D{i}" for i in range(10, 0, -1)]  # D10 → D1 (matches notebook charts)

PERIOD_1_START = pd.Timestamp("2022-01-01", tz="Asia/Singapore")
PERIOD_1_END = pd.Timestamp("2023-12-31", tz="Asia/Singapore")
PERIOD_2_START = pd.Timestamp("2024-01-01", tz="Asia/Singapore")
PERIOD_2_END = pd.Timestamp("2025-12-31", tz="Asia/Singapore")


def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def assign_decile(series: pd.Series) -> pd.Series:
    """D1 = best, D10 = worst — rank + qcut, matches decile_lens1.ipynb."""
    ranks = series.rank(method="first", ascending=True)
    return pd.qcut(ranks, q=10, labels=DECILE_CHART_ORDER)


def assign_tier(series: pd.Series, n_tiers: int = 5) -> pd.Series:
    ranks = series.rank(method="first", ascending=True)
    return pd.qcut(ranks, q=n_tiers, labels=[f"T{i}" for i in range(n_tiers, 0, -1)])


def _reindex_deciles(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.set_index(col).reindex(DECILE_BEST_FIRST).reset_index()
    return out.rename(columns={"index": col}) if "index" in out.columns else out


cfg = _load_config()

print("=" * 72)
print("DECILE ANALYSIS — CSV export")
print("=" * 72)
print(f"Input:  {FINALS_DIR}")
print(f"Output: {OUT_DIR}")

# ── Load finals parquets ───────────────────────────────────────────────────────
orders = pd.read_parquet(FINALS_DIR / "orders.parquet")
cust = pd.read_parquet(FINALS_DIR / "customers.parquet")

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True).dt.tz_convert("Asia/Singapore")
orders["price_total"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
orders["price_disc"] = pd.to_numeric(orders["Price: Total Discount"], errors="coerce").fillna(0)

# Marketplace anomaly exclusion (decile_lens1.ipynb)
cust_channel_mix = (
    orders.groupby("customer_id")["channel"]
    .value_counts(normalize=True)
    .unstack(fill_value=0)
)
all_mkt_ids = (
    set(cust_channel_mix[cust_channel_mix["Marketplace"] == 1.0].index.astype(str))
    if "Marketplace" in cust_channel_mix.columns
    else set()
)

cust = cust.copy()
cust["is_all_marketplace"] = cust["customer_id"].astype(str).isin(all_mkt_ids)
cust = cust[~cust["is_all_marketplace"] & (cust["total_orders"] > 0)].copy()
orders = orders[orders["customer_id"].isin(set(cust["customer_id"]))].copy()

_cust_rebuild = orders.groupby("customer_id").agg(
    clean_orders=("order_id", "count"),
    clean_revenue=("price_total", "sum"),
).reset_index()

df = cust.merge(_cust_rebuild, on="customer_id", how="inner")
df["clean_orders"] = df["clean_orders"].astype(int)
df["aov"] = df["clean_revenue"] / df["clean_orders"].clip(lower=1)
df["profit_proxy"] = df["clean_revenue"] * MARGIN_RATE

print(f"\nDecile pool: {len(df):,} customers (excl. 100% marketplace)")
print(f"Revenue: S${df['clean_revenue'].sum():,.0f} | Orders: {df['clean_orders'].sum():,}")

# ══════════════════════════════════════════════════════════════════════════════
# LENS 1 — Profit + Frequency deciles
# ══════════════════════════════════════════════════════════════════════════════
df["profit_decile"] = assign_decile(df["profit_proxy"])
df["freq_decile"] = assign_decile(df["clean_orders"])

total_rev = df["clean_revenue"].sum()
total_ord = df["clean_orders"].sum()
total_pft = df["profit_proxy"].sum()

profit_summary = (
    df.groupby("profit_decile", observed=False)
    .agg(
        n_customers=("customer_id", "count"),
        total_revenue=("clean_revenue", "sum"),
        total_profit=("profit_proxy", "sum"),
        total_orders=("clean_orders", "sum"),
        avg_revenue=("clean_revenue", "mean"),
        median_revenue=("clean_revenue", "median"),
        avg_profit=("profit_proxy", "mean"),
        avg_orders=("clean_orders", "mean"),
        avg_aov=("aov", "mean"),
    )
    .reset_index()
)
profit_summary["pct_customers"] = profit_summary["n_customers"] / len(df)
profit_summary["pct_revenue"] = profit_summary["total_revenue"] / total_rev
profit_summary["pct_profit"] = profit_summary["total_profit"] / total_pft
profit_summary["pct_transactions"] = profit_summary["total_orders"] / total_ord
profit_summary = _reindex_deciles(profit_summary, "profit_decile")
profit_summary["cum_pct_revenue"] = profit_summary["pct_revenue"].cumsum()

freq_summary = (
    df.groupby("freq_decile", observed=False)
    .agg(
        n_customers=("customer_id", "count"),
        total_orders=("clean_orders", "sum"),
        total_revenue=("clean_revenue", "sum"),
        total_profit=("profit_proxy", "sum"),
        avg_orders=("clean_orders", "mean"),
        median_orders=("clean_orders", "median"),
        avg_revenue=("clean_revenue", "mean"),
        avg_aov=("aov", "mean"),
        avg_profit=("profit_proxy", "mean"),
    )
    .reset_index()
)
freq_summary["pct_customers"] = freq_summary["n_customers"] / len(df)
freq_summary["pct_transactions"] = freq_summary["total_orders"] / total_ord
freq_summary["pct_revenue"] = freq_summary["total_revenue"] / total_rev
freq_summary = _reindex_deciles(freq_summary, "freq_decile")
freq_summary["cum_pct_transactions"] = freq_summary["pct_transactions"].cumsum()

# Overlap matrix + summary
overlap = pd.crosstab(df["profit_decile"], df["freq_decile"])
overlap = overlap.reindex(index=DECILE_CHART_ORDER, columns=DECILE_CHART_ORDER, fill_value=0)
overlap.index.name = "profit_decile"
overlap.columns.name = "freq_decile"

d1_profit_ids = set(df.loc[df["profit_decile"] == "D1", "customer_id"])
d1_freq_ids = set(df.loc[df["freq_decile"] == "D1", "customer_id"])
d1_both_ids = d1_profit_ids & d1_freq_ids

overlap_summary = pd.DataFrame([
    {"segment": "D1_profit_only", "n_customers": len(d1_profit_ids - d1_freq_ids)},
    {"segment": "D1_frequency_only", "n_customers": len(d1_freq_ids - d1_profit_ids)},
    {"segment": "D1_both", "n_customers": len(d1_both_ids)},
    {"segment": "pool_total", "n_customers": len(df)},
])

# Equal-revenue slicing (decile_lens1 section 10)
sorted_df = df.sort_values("clean_revenue", ascending=False).reset_index(drop=True)
cum_rev = sorted_df["clean_revenue"].cumsum()
targets = [total_rev * (i / 10) for i in range(1, 11)]
slice_rows = []
prev_idx = 0
for i, target in enumerate(targets):
    idx = int(cum_rev.searchsorted(target, side="right"))
    chunk = sorted_df.iloc[prev_idx:idx]
    slice_rows.append({
        "revenue_slice": f"{i * 10}-{(i + 1) * 10}%",
        "slice_rank": i + 1,
        "n_customers": len(chunk),
        "pct_of_pool": len(chunk) / len(df) if len(df) else 0,
        "revenue_in_slice": chunk["clean_revenue"].sum() if len(chunk) else 0,
        "rev_min": chunk["clean_revenue"].min() if len(chunk) else np.nan,
        "rev_max": chunk["clean_revenue"].max() if len(chunk) else np.nan,
        "rev_mean": chunk["clean_revenue"].mean() if len(chunk) else np.nan,
        "rev_median": chunk["clean_revenue"].median() if len(chunk) else np.nan,
    })
    prev_idx = idx
equal_revenue_df = pd.DataFrame(slice_rows)

# Customer-level export table
export_cols = [
    "customer_id", "clean_orders", "clean_revenue", "profit_proxy", "aov",
    "profit_decile", "freq_decile",
]
for col in [
    "first_channel", "first_product_cat", "first_store", "ever_subscribed",
    "cohort_month", "acq_year", "acq_month", "is_repeat", "first_order_date",
    "total_orders", "total_revenue", "loyal_repeater",
]:
    if col in df.columns and col not in export_cols:
        export_cols.append(col)

export_df = df[export_cols].copy()
decile_rank = {d: i for i, d in enumerate(DECILE_BEST_FIRST)}
export_df["_profit_rank"] = export_df["profit_decile"].astype(str).map(decile_rank)
export_df = export_df.sort_values(["_profit_rank", "clean_revenue"], ascending=[True, False])
export_df = export_df.drop(columns=["_profit_rank"])

export_df["is_top_profit"] = export_df["profit_decile"] == "D1"
export_df["is_top_freq"] = export_df["freq_decile"] == "D1"
export_df["is_top_both"] = export_df["is_top_profit"] & export_df["is_top_freq"]
for col in ["clean_revenue", "profit_proxy", "aov"]:
    export_df[col] = export_df[col].round(2)

# ══════════════════════════════════════════════════════════════════════════════
# LENS 2 — Migration (decile_lens2.ipynb)
# ══════════════════════════════════════════════════════════════════════════════
p1_orders = orders[(orders["order_date"] >= PERIOD_1_START) & (orders["order_date"] <= PERIOD_1_END)]
p2_orders = orders[(orders["order_date"] >= PERIOD_2_START) & (orders["order_date"] <= PERIOD_2_END)]

p1_customers = set(p1_orders["customer_id"].unique())
p2_customers = set(p2_orders["customer_id"].unique())
both_customers = p1_customers & p2_customers

p1_rev = (
    p1_orders[p1_orders["customer_id"].isin(both_customers)]
    .groupby("customer_id")["price_total"].sum().rename("p1_revenue").reset_index()
)
p2_rev = (
    p2_orders[p2_orders["customer_id"].isin(both_customers)]
    .groupby("customer_id")["price_total"].sum().rename("p2_revenue").reset_index()
)
migration_df = p1_rev.merge(p2_rev, on="customer_id", how="inner")
migration_df["p1_tier"] = assign_tier(migration_df["p1_revenue"])
migration_df["p2_tier"] = assign_tier(migration_df["p2_revenue"])
migration_df["p1_tier_num"] = migration_df["p1_tier"].astype(str).str[1].astype(int)
migration_df["p2_tier_num"] = migration_df["p2_tier"].astype(str).str[1].astype(int)
migration_df["movement"] = migration_df["p1_tier_num"] - migration_df["p2_tier_num"]
migration_df["revenue_change"] = migration_df["p2_revenue"] - migration_df["p1_revenue"]
migration_df["revenue_pct_change"] = migration_df["revenue_change"] / migration_df["p1_revenue"].replace(0, np.nan)

# Enrich migration with Lens 1 deciles where available
migration_df = migration_df.merge(
    export_df[["customer_id", "profit_decile", "freq_decile", "clean_revenue", "clean_orders"]],
    on="customer_id", how="left",
)

migration_matrix = pd.crosstab(migration_df["p1_tier"], migration_df["p2_tier"])
all_tiers = [f"T{i}" for i in range(1, 6)]
migration_matrix = migration_matrix.reindex(index=all_tiers, columns=all_tiers, fill_value=0)
migration_matrix.index.name = "p1_tier"
migration_matrix.columns.name = "p2_tier"

t5_to_t1 = (
    migration_df[(migration_df["p1_tier"] == "T5") & (migration_df["p2_tier"] == "T1")]
    .sort_values("revenue_change", ascending=False)
)
t1_dropped = (
    migration_df[(migration_df["p1_tier"] == "T1") & (migration_df["p2_tier"] != "T1")]
    .sort_values("revenue_change", ascending=True)
)

churned_ids = p1_customers - p2_customers
churned_profile = (
    p1_orders[p1_orders["customer_id"].isin(churned_ids)]
    .groupby("customer_id")
    .agg(
        p1_revenue=("price_total", "sum"),
        p1_orders=("order_id", "count"),
        last_order=("order_date", "max"),
        first_channel=("channel", "first"),
    )
    .reset_index()
    .sort_values("p1_revenue", ascending=False)
)

tier_rev_change = migration_df.groupby("p1_tier", observed=False).agg(
    n_customers=("customer_id", "count"),
    avg_p1_rev=("p1_revenue", "mean"),
    avg_p2_rev=("p2_revenue", "mean"),
    total_p1_rev=("p1_revenue", "sum"),
    total_p2_rev=("p2_revenue", "sum"),
).reset_index()
tier_rev_change["avg_change"] = tier_rev_change["avg_p2_rev"] - tier_rev_change["avg_p1_rev"]
tier_rev_change["pct_change"] = tier_rev_change["avg_change"] / tier_rev_change["avg_p1_rev"].replace(0, np.nan)

# ── Save CSVs ────────────────────────────────────────────────────────────────
print("\nSaving CSV files...")

files_written = {}

def _save_csv(dataframe, name):
    path = OUT_DIR / name
    dataframe.to_csv(path, index=False if name != "decile_overlap_matrix.csv" else True)
    files_written[name] = len(dataframe) if name != "decile_overlap_matrix.csv" else f"{dataframe.shape[0]}x{dataframe.shape[1]}"
    print(f"  {name}")

_save_csv(export_df, "customers_decile_table.csv")
_save_csv(profit_summary, "profit_decile_summary.csv")
_save_csv(freq_summary, "frequency_decile_summary.csv")
overlap.to_csv(OUT_DIR / "decile_overlap_matrix.csv")
files_written["decile_overlap_matrix.csv"] = f"{overlap.shape[0]}x{overlap.shape[1]}"
print("  decile_overlap_matrix.csv")
_save_csv(overlap_summary, "decile_overlap_summary.csv")
_save_csv(equal_revenue_df, "equal_revenue_slicing.csv")
_save_csv(migration_df, "migration_customer_table.csv")
migration_matrix.to_csv(OUT_DIR / "migration_matrix.csv")
files_written["migration_matrix.csv"] = f"{migration_matrix.shape[0]}x{migration_matrix.shape[1]}"
print("  migration_matrix.csv")
_save_csv(t5_to_t1, "next_t5_to_t1_jumpers.csv")
_save_csv(t1_dropped, "next_t1_dropped.csv")
_save_csv(churned_profile, "next_churned_customers.csv")
_save_csv(tier_rev_change, "next_tier_revenue_change.csv")

# Pool metadata
d1p = profit_summary.loc[profit_summary["profit_decile"] == "D1"].iloc[0]
d1f = freq_summary.loc[freq_summary["freq_decile"] == "D1"].iloc[0]

manifest = {
    "generated_by": "EDA/decile_analysis/run_decile_analysis.py",
    "source": str(FINALS_DIR),
    "pool_customers": len(df),
    "pool_revenue_sgd": round(total_rev, 2),
    "margin_rate": MARGIN_RATE,
    "filters": [
        "outputs_finals customers.parquet (all LP finals filters pre-applied)",
        "exclude 100% marketplace channel customers",
        "exclude customers with 0 retained orders",
    ],
    "decile_logic": {
        "profit_decile": "pd.qcut on rank(profit_proxy); D1=highest profit",
        "freq_decile": "pd.qcut on rank(clean_orders); D1=most frequent",
        "profit_proxy": f"clean_revenue * {MARGIN_RATE}",
    },
    "lens2_periods": {
        "period_1": "2022-01-01 to 2023-12-31",
        "period_2": "2024-01-01 to 2025-12-31",
        "both_period_customers": len(migration_df),
        "churned_p1_only": len(churned_profile),
    },
    "headline_stats": {
        "d1_profit_pct_revenue": round(float(d1p["pct_revenue"]), 4),
        "d1_freq_pct_transactions": round(float(d1f["pct_transactions"]), 4),
        "d1_both_customers": len(d1_both_ids),
        "equal_rev_slice1_customers": int(equal_revenue_df.iloc[0]["n_customers"]),
    },
    "files": files_written,
}
with open(OUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

readme = f"""# Decile Analysis CSVs

Generated by `run_decile_analysis.py` from `outputs_finals/` data.

**Pool:** {len(df):,} customers (finals cohort, excl. 100% marketplace)  
**Deciles:** D1 = best, D10 = worst | Equal-sized bins via `pd.qcut` on ranked values

## Lens 1 — Profit & Frequency deciles

| File | Description |
|------|-------------|
| `customers_decile_table.csv` | **Primary** — one row per customer with `profit_decile`, `freq_decile`, flags |
| `profit_decile_summary.csv` | Aggregated metrics per profit decile |
| `frequency_decile_summary.csv` | Aggregated metrics per frequency decile |
| `decile_overlap_matrix.csv` | Cross-tab: profit decile × frequency decile |
| `decile_overlap_summary.csv` | D1 profit-only / D1 freq-only / D1 both counts |
| `equal_revenue_slicing.csv` | Customers needed per 10% revenue slice |

### Key flags in `customers_decile_table.csv`
- `is_top_profit` — D1 by profit
- `is_top_freq` — D1 by frequency
- `is_top_both` — D1 in both deciles

## Lens 2 — Period migration (2022–2023 vs 2024–2025)

| File | Description |
|------|-------------|
| `migration_customer_table.csv` | Both-period customers with P1/P2 tiers + Lens 1 deciles |
| `migration_matrix.csv` | 5×5 tier migration matrix |
| `next_t5_to_t1_jumpers.csv` | T5→T1 upgraders |
| `next_t1_dropped.csv` | T1 customers who dropped tier in P2 |
| `next_churned_customers.csv` | Active P1 only, not in P2 |
| `next_tier_revenue_change.csv` | Avg revenue change by P1 tier |

Re-run: `python EDA/decile_analysis/run_decile_analysis.py`
"""
(OUT_DIR / "README.md").write_text(readme, encoding="utf-8")

print("\n" + "=" * 72)
print("LENS 1 SUMMARY")
print("=" * 72)
print(f"Pool:           {len(df):,} customers (~{len(df) // 10} per decile)")
print(f"D1 profit:      {d1p['pct_revenue']:.1%} of revenue | avg S${d1p['avg_revenue']:,.0f}")
print(f"D1 frequency:   {d1f['pct_transactions']:.1%} of orders | avg {d1f['avg_orders']:.1f} orders")
print(f"D1 both:        {len(d1_both_ids):,} customers")
print(f"Equal-rev slice 1: {equal_revenue_df.iloc[0]['n_customers']} customers ({equal_revenue_df.iloc[0]['pct_of_pool']:.1%})")

print("\n" + "=" * 72)
print("LENS 2 SUMMARY")
print("=" * 72)
print(f"P1 active:      {len(p1_customers):,}")
print(f"P2 active:      {len(p2_customers):,}")
print(f"Both periods:   {len(migration_df):,}")
print(f"Churned P1-only:{len(churned_profile):,}")

print("\n" + "=" * 72)
print(f"DONE — CSVs in {OUT_DIR}")
print("=" * 72)
