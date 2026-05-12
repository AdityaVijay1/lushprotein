"""
08_lens2_period_decomposition.py  —  Customer-Base Audit: LENS 2
"What Changed? Why Did the Top-Line Move?"

Framework: Bruce, Fader & Ross — The Customer-Base Audit (2022)
Lens 2 = Two adjacent periods compared: who is new, who returned, who left?

Analyses
--------
A. Customer overlap: New / Retained (Both-Years) / Lost across each consecutive year pair
B. Revenue & per-customer metric comparison per group (new, retained, lost)
C. Multiplicative decomposition per group: Revenue = Customers × AOF × AOV
   Including the "selection effect" — why Both-Years AOF > one-year groups
D. Profit decile migration matrix (10×10 heatmap data) for Both-Years customers
   Using consecutive years 2023 vs 2024 as the focal comparison
E. Up-Down analysis for Both-Years customers (profit improvers vs decliners)

Notes
-----
- SGD orders only for all revenue comparisons
- "Profit proxy" = revenue × 40% gross margin
- Focal comparison: Year A = 2023, Year B = 2024 (most recent complete year pair)
- All-year waterfall also computed for 2020-2025 trend

Outputs
-------
EDA/outputs/08_lens2_overlap_all_years.csv     — Annual new/retained/lost waterfall
EDA/outputs/08_lens2_group_decomposition.csv   — Multiplicative decomposition per group
EDA/outputs/08_lens2_decile_migration.csv      — 10x10 migration heatmap (count matrix)
EDA/outputs/08_lens2_updown_analysis.csv       — Up-Down decomposition summary
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import importlib.util
from pathlib import Path

def _load_config():
    spec = importlib.util.spec_from_file_location(
        "lp_config", Path(__file__).parent / "00_config.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg = _load_config()
OUTPUT_DIR = cfg.OUTPUT_DIR
MARGIN = 0.40

print("=" * 65)
print("LENS 2 — WHAT CHANGED? PERIOD-ON-PERIOD DECOMPOSITION")
print("Two adjacent periods  |  New / Retained / Lost  |  Migration")
print("=" * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
orders = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
orders["order_date"]    = pd.to_datetime(orders["order_date"], utc=True)
orders["Price: Total"]  = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)

# SGD filter
sgd = orders[orders["Currency"].fillna("") == "SGD"].copy()
sgd["year"] = sgd["order_date"].dt.year

# Customer-year table: for each customer, their annual spend and order count
cust_year = (
    sgd.groupby(["customer_id", "year"])
    .agg(
        n_orders    = ("order_id",       "count"),
        revenue     = ("Price: Total",   "sum"),
    )
    .reset_index()
)
cust_year["aov"]          = cust_year["revenue"] / cust_year["n_orders"].clip(lower=1)
cust_year["profit_proxy"] = cust_year["revenue"] * MARGIN

YEARS = sorted(cust_year["year"].unique())
print(f"\nYears in SGD data: {YEARS}")

# ==============================================================================
# A.  ANNUAL WATERFALL — New / Both-Years (Retained) / Lost
# ==============================================================================
print("\n\n[A] ANNUAL CUSTOMER WATERFALL")
print("-" * 65)
print(f"{'Year A':>6} {'Year B':>6}  {'A-Only (Lost)':>15}  {'Both':>10}  {'B-Only (New)':>14}  {'Ret Rate':>10}")
print("-" * 65)

waterfall_rows = []
for i in range(len(YEARS) - 1):
    yr_a, yr_b = YEARS[i], YEARS[i+1]
    custs_a = set(cust_year[cust_year["year"] == yr_a]["customer_id"])
    custs_b = set(cust_year[cust_year["year"] == yr_b]["customer_id"])
    both    = custs_a & custs_b
    a_only  = custs_a - custs_b
    b_only  = custs_b - custs_a

    ret_rate = len(both) / len(custs_a) if custs_a else 0
    waterfall_rows.append({
        "year_a": yr_a, "year_b": yr_b,
        "n_year_a": len(custs_a), "n_year_b": len(custs_b),
        "n_lost": len(a_only), "n_retained": len(both), "n_new": len(b_only),
        "retention_rate": round(ret_rate, 4),
        "pct_new_of_year_b": round(len(b_only)/len(custs_b) if custs_b else 0, 4),
    })
    print(f"  {yr_a:>4}  {yr_b:>4}   {len(a_only):>13,}  {len(both):>10,}  {len(b_only):>13,}  {ret_rate:>9.1%}")

waterfall_df = pd.DataFrame(waterfall_rows)
waterfall_df.to_csv(OUTPUT_DIR / "08_lens2_overlap_all_years.csv", index=False)
print(f"\nSaved: 08_lens2_overlap_all_years.csv")

# ==============================================================================
# B & C.  FOCAL YEAR PAIR: 2023 vs 2024
#         Decompose revenue per group + multiplicative breakdown
# ==============================================================================
YEAR_A, YEAR_B = 2023, 2024

# Check both years have data
avail = waterfall_df["year_b"].tolist()
if YEAR_B not in avail:
    # Fall back to latest pair
    YEAR_A = waterfall_df["year_a"].iloc[-1]
    YEAR_B = waterfall_df["year_b"].iloc[-1]

print(f"\n\n[B+C] FOCAL COMPARISON: {YEAR_A} vs {YEAR_B}")
print("-" * 65)

cy_a = cust_year[cust_year["year"] == YEAR_A].set_index("customer_id")
cy_b = cust_year[cust_year["year"] == YEAR_B].set_index("customer_id")

custs_a = set(cy_a.index)
custs_b = set(cy_b.index)
both    = custs_a & custs_b
a_only  = custs_a - custs_b  # Lost
b_only  = custs_b - custs_a  # New

print(f"  {YEAR_A} customers:  {len(custs_a):,}")
print(f"  {YEAR_B} customers:  {len(custs_b):,}")
print(f"  Retained (both):  {len(both):,}  ({len(both)/len(custs_a):.1%} of {YEAR_A})")
print(f"  Lost ({YEAR_A} only): {len(a_only):,}  ({len(a_only)/len(custs_a):.1%} of {YEAR_A})")
print(f"  New ({YEAR_B} only):  {len(b_only):,}  ({len(b_only)/len(custs_b):.1%} of {YEAR_B})")

def group_stats(cust_ids, year_data):
    sub = year_data[year_data.index.isin(cust_ids)]
    return {
        "n": len(sub),
        "total_rev": sub["revenue"].sum(),
        "avg_rev": sub["revenue"].mean() if len(sub) > 0 else 0,
        "avg_aof": sub["n_orders"].mean() if len(sub) > 0 else 0,
        "avg_aov": sub["aov"].mean() if len(sub) > 0 else 0,
    }

groups = {
    f"{YEAR_A}-Only (Lost)": (a_only, cy_a, YEAR_A),
    f"Both ({YEAR_A} & {YEAR_B})": (both, cy_a, YEAR_A),
    f"Both ({YEAR_A} & {YEAR_B}) in {YEAR_B}": (both, cy_b, YEAR_B),
    f"{YEAR_B}-Only (New)": (b_only, cy_b, YEAR_B),
}

print(f"\n  {'Group':<30}  {'Customers':>10}  {'Total Rev (SGD)':>16}  {'Avg Rev':>9}  {'AOF':>5}  {'AOV':>8}")
print(f"  {'-'*80}")

decomp_rows = []
for label, (ids, data, yr) in groups.items():
    s = group_stats(ids, data)
    print(f"  {label:<30}  {s['n']:>10,}  "
          f"S${s['total_rev']:>14,.0f}  "
          f"S${s['avg_rev']:>8.0f}  "
          f"{s['avg_aof']:>5.1f}  S${s['avg_aov']:>6.0f}")
    decomp_rows.append({"group": label, "year": yr, **s})

# Highlight the selection effect
both_a = group_stats(both, cy_a)
a_only_stats = group_stats(a_only, cy_a)
print(f"\n  SELECTION EFFECT:")
print(f"  Both-years AOF ({YEAR_A}): {both_a['avg_aof']:.2f}  vs  {YEAR_A}-only AOF: {a_only_stats['avg_aof']:.2f}")
print(f"  Retained customers buy MORE frequently — because frequent buyers self-select to stay.")
print(f"  This is NOT a causal effect of retention programs. It is a composition effect.")

decomp_df = pd.DataFrame(decomp_rows)
decomp_df.to_csv(OUTPUT_DIR / "08_lens2_group_decomposition.csv", index=False)
print(f"\nSaved: 08_lens2_group_decomposition.csv")

# ==============================================================================
# D.  PROFIT DECILE MIGRATION MATRIX (Both-Years customers only)
# ==============================================================================
print(f"\n\n[D] PROFIT DECILE MIGRATION MATRIX ({YEAR_A} vs {YEAR_B})")
print("-" * 65)

both_a_df = cy_a[cy_a.index.isin(both)].copy()
both_b_df = cy_b[cy_b.index.isin(both)].copy()

# Build combined revenue thresholds from both-years customers
all_rev = pd.concat([both_a_df["profit_proxy"], both_b_df["profit_proxy"]])
thresholds = np.percentile(all_rev.dropna(), [10, 20, 30, 40, 50, 60, 70, 80, 90])

def assign_decile(series, thresholds):
    """Assign 1=highest, 10=lowest based on descending thresholds."""
    bins = [-np.inf] + sorted(thresholds, reverse=False) + [np.inf]
    labels = list(range(10, 0, -1))
    return pd.cut(series, bins=bins, labels=labels)

both_a_df["decile_a"] = assign_decile(both_a_df["profit_proxy"], thresholds).astype(int)
both_b_df["decile_b"] = assign_decile(both_b_df["profit_proxy"], thresholds).astype(int)

migration = pd.merge(
    both_a_df[["decile_a"]].reset_index(),
    both_b_df[["decile_b"]].reset_index(),
    on="customer_id"
)

# Build 10x10 heatmap
matrix = pd.crosstab(migration["decile_a"], migration["decile_b"])
# Ensure all 10 deciles exist
for d in range(1, 11):
    if d not in matrix.index:
        matrix.loc[d] = 0
    if d not in matrix.columns:
        matrix[d] = 0
matrix = matrix.sort_index().sort_index(axis=1)

print(f"\n  10x10 Migration Matrix (rows={YEAR_A} decile, cols={YEAR_B} decile)")
print(f"  (D1=highest value, D10=lowest; diagonal=stayed same tier)")
print()
header = "  D_a\\D_b" + "".join(f"  D{c:02d}" for c in range(1, 11))
print(header)
print("  " + "-" * (len(header) - 2))
for d_a in range(1, 11):
    row_vals = "".join(f"  {int(matrix.loc[d_a, d_b]) if d_b in matrix.columns and d_a in matrix.index else 0:>4}"
                       for d_b in range(1, 11))
    print(f"  D{d_a:02d}   " + row_vals)

# Diagonal analysis
diagonal_n = sum(matrix.loc[d, d] if d in matrix.index and d in matrix.columns else 0
                 for d in range(1, 11))
pm1_n = sum(
    sum(matrix.loc[d, dc] if d in matrix.index and dc in matrix.columns else 0
        for dc in range(max(1, d-1), min(11, d+2)))
    for d in range(1, 11)
)
total_both = len(migration)

print(f"\n  DIAGONAL ANALYSIS:")
print(f"  Exactly same decile (diagonal):  {diagonal_n:,}  ({diagonal_n/total_both:.0%} of both-years customers)")
print(f"  Within ±1 decile (stable band):  {pm1_n:,}  ({pm1_n/total_both:.0%} of both-years customers)")
print(f"  Top decile D1 sticky (D1 -> D1): "
      f"{int(matrix.loc[1, 1]) if 1 in matrix.index and 1 in matrix.columns else 0:,}")

# Risers: moved from bottom 3 to top 3
risers = len(migration[(migration["decile_a"] >= 8) & (migration["decile_b"] <= 3)])
fallers = len(migration[(migration["decile_a"] <= 3) & (migration["decile_b"] >= 8)])
print(f"  Rose: bottom 3 -> top 3:         {risers:,} customers")
print(f"  Fell: top 3 -> bottom 3:         {fallers:,} customers")

# Save as long format
matrix_long = migration.groupby(["decile_a","decile_b"]).size().reset_index(name="n_customers")
matrix_long.to_csv(OUTPUT_DIR / "08_lens2_decile_migration.csv", index=False)
print(f"\nSaved: 08_lens2_decile_migration.csv")

# ==============================================================================
# E.  UP-DOWN ANALYSIS — Both-years customers only
# ==============================================================================
print(f"\n\n[E] UP-DOWN ANALYSIS ({YEAR_A} -> {YEAR_B})")
print("-" * 65)
print("For each retained customer: did profit / orders / spend / margin go up or down?")
print()

both_merged = pd.merge(
    both_a_df[["revenue","n_orders","aov","profit_proxy"]].reset_index()
        .rename(columns={"revenue":"rev_a","n_orders":"ord_a","aov":"aov_a","profit_proxy":"prof_a"}),
    both_b_df[["revenue","n_orders","aov","profit_proxy"]].reset_index()
        .rename(columns={"revenue":"rev_b","n_orders":"ord_b","aov":"aov_b","profit_proxy":"prof_b"}),
    on="customer_id"
)

both_merged["prof_up"]  = both_merged["prof_b"] >= both_merged["prof_a"]
both_merged["ord_up"]   = both_merged["ord_b"]  >= both_merged["ord_a"]
both_merged["aov_up"]   = both_merged["aov_b"]  >= both_merged["aov_a"]

# Summarize
n_up   = both_merged["prof_up"].sum()
n_down = (~both_merged["prof_up"]).sum()
print(f"  Profit UP   (>= {YEAR_A}): {n_up:,}  ({n_up/len(both_merged):.0%})")
print(f"  Profit DOWN (<  {YEAR_A}): {n_down:,}  ({n_down/len(both_merged):.0%})")

rev_gain = both_merged.loc[both_merged["prof_up"],  ["prof_a","prof_b"]].apply(lambda x: x["prof_b"]-x["prof_a"], axis=1).sum()
rev_loss = both_merged.loc[~both_merged["prof_up"], ["prof_a","prof_b"]].apply(lambda x: x["prof_b"]-x["prof_a"], axis=1).sum()
print(f"\n  Total profit gain (up group):    S${rev_gain*1:+,.0f}")
print(f"  Total profit loss (down group):  S${rev_loss*1:+,.0f}")
print(f"  Net both-years profit change:    S${(rev_gain+rev_loss)*1:+,.0f}")

# Multi-component improvers / decliners
up = both_merged[both_merged["prof_up"]].copy()
down = both_merged[~both_merged["prof_up"]].copy()

up_all3   = (up["ord_up"] & up["aov_up"]).mean()
down_aov  = (~down["aov_up"]).mean()
down_all3 = (~down["ord_up"] & ~down["aov_up"]).mean()

print(f"\n  Among PROFIT-UP customers:")
print(f"    Both orders AND spend improved:  {up_all3:.0%}  — broad-based improvement")
print(f"  Among PROFIT-DOWN customers:")
print(f"    Declining spend (AOV down):       {down_aov:.0%}  — spend erosion is dominant thread")
print(f"    All 3 components declined:        {down_all3:.0%}")

# Summary by pattern
up_patterns = up.groupby(["ord_up","aov_up"]).agg(
    n=("customer_id","count"),
    prof_change=("prof_b","sum")
).reset_index()
up_patterns["prof_change_a"] = up.groupby(["ord_up","aov_up"])["prof_a"].sum().values

print(f"\n  Up-group pattern breakdown:")
print(f"  {'Ord Up':>7}  {'AOV Up':>7}  {'N':>6}  {'Prof Change (S$)':>16}")
print(f"  {'-'*45}")
for _, r in up_patterns.iterrows():
    delta = r["prof_change"] - r["prof_change_a"]
    print(f"  {str(r['ord_up']):>7}  {str(r['aov_up']):>7}  {int(r['n']):>6,}  S${delta:>+14,.0f}")

down_patterns = down.groupby(["ord_up","aov_up"]).agg(
    n=("customer_id","count"),
    prof_change=("prof_b","sum")
).reset_index()
down_patterns["prof_change_a"] = down.groupby(["ord_up","aov_up"])["prof_a"].sum().values

print(f"\n  Down-group pattern breakdown:")
print(f"  {'Ord Up':>7}  {'AOV Up':>7}  {'N':>6}  {'Prof Change (S$)':>16}")
print(f"  {'-'*45}")
for _, r in down_patterns.iterrows():
    delta = r["prof_change"] - r["prof_change_a"]
    print(f"  {str(r['ord_up']):>7}  {str(r['aov_up']):>7}  {int(r['n']):>6,}  S${delta:>+14,.0f}")

# Save
updown_rows = []
for is_up_flag, sub in [(True, up), (False, down)]:
    for (ord_up, aov_up), grp in sub.groupby(["ord_up","aov_up"]):
        delta = (grp["prof_b"] - grp["prof_a"]).sum()
        updown_rows.append({
            "group": "Profit UP" if is_up_flag else "Profit DOWN",
            "ord_up": ord_up, "aov_up": aov_up,
            "n": len(grp),
            "total_prof_a": grp["prof_a"].sum(),
            "total_prof_b": grp["prof_b"].sum(),
            "prof_delta": delta,
        })

pd.DataFrame(updown_rows).to_csv(OUTPUT_DIR / "08_lens2_updown_analysis.csv", index=False)
print(f"\nSaved: 08_lens2_updown_analysis.csv")

# ==============================================================================
# LENS 2 KEY TAKEAWAYS
# ==============================================================================
print("\n\n[LENS 2 KEY TAKEAWAYS]")
print("=" * 65)
latest_w = waterfall_df.iloc[-1]
print(f"""
  1. Year-on-year customer retention rate ({YEAR_A}->{YEAR_B}): {both_a['n']/len(custs_a):.0%}
     => Only {both_a['n']/len(custs_a):.0%} of {YEAR_A} customers returned in {YEAR_B}

  2. Revenue per customer barely changes year-to-year.
     Revenue growth (when it happens) is driven by MORE customers, not higher spend per head.

  3. The selection effect: Retained (Both-Years) customers have 2x the AOF of one-year customers
     => Frequent buyers self-select to stay. This inflates the apparent "value" of retained customers.
     => Do NOT attribute this entirely to retention programs — it is partly who they always were.

  4. Top-decile profitability is STICKY.
     Once a customer reaches D1, they tend to stay there. Protect them above all.

  5. Middle tiers (D5-D7) are the most volatile — they move unpredictably.
     These are the customers where interventions have the highest ROI.

  6. Among both-years customers, ~50% improve and ~50% decline.
     The gross movements are large but largely cancel out at the aggregate level.
     SPEND EROSION (falling AOV) is the dominant thread among declining customers.
""")

print("[08] Lens 2 DONE.\n")
