"""
03_customer_retention.py   €“  Core retention analysis.

Analyses
--------
A. Repeat purchase rate overall and by key cohort slices
B. Time-to-second-purchase distribution + 30/60/90-day cumulative rates
C. Monthly cohort retention heatmap (% who repurchase within 90 days)
D. RFM segmentation snapshot

Outputs
-------
outputs/03_repeat_rate_by_slice.csv
outputs/03_time_to_second_purchase.csv
outputs/03_cohort_retention_heatmap.csv
outputs/03_rfm_segments.csv

Run AFTER 01_load_and_merge.py
"""

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
OUTPUT_DIR    = cfg.OUTPUT_DIR
ANALYSIS_DATE = cfg.ANALYSIS_DATE

print("Loading cached tables...")
orders = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
cust   = pd.read_parquet(OUTPUT_DIR / "customers.parquet")

orders["order_date"]       = pd.to_datetime(orders["order_date"], utc=True)
cust["first_order_date"]   = pd.to_datetime(cust["first_order_date"], utc=True)
cust["second_order_date"]  = pd.to_datetime(cust["second_order_date"], utc=True, errors="coerce")

#                                                                                                                                                             
# A.  OVERALL REPEAT RATE + BY COHORT SLICE
#                                                                                                                                                             
print("\n[A] REPEAT PURCHASE RATE BY SLICE")
print("=" * 55)

def repeat_rate_table(groupcol: str, df=cust) -> pd.DataFrame:
    return (
        df.groupby(groupcol)
        .agg(
            customers    = ("customer_id", "count"),
            repeaters    = ("is_repeat",   "sum"),
            avg_orders   = ("total_orders","mean"),
            avg_revenue  = ("total_revenue","mean"),
        )
        .assign(repeat_rate=lambda d: d["repeaters"] / d["customers"])
        .sort_values("customers", ascending=False)
    )

slices = {
    "first_product_cat": "First Product Category",
    "first_channel"    : "Acquisition Channel",
    "first_store"      : "Store (Country)",
    "ever_subscribed"  : "Ever Subscribed",
    "ever_discounted"  : "First Order Discounted",
}

results = {}
for col, label in slices.items():
    tbl = repeat_rate_table(col)
    results[col] = tbl
    print(f"\n--- {label} ---")
    print(tbl.to_string())

# Combine into one CSV
all_slices = []
for col, label in slices.items():
    t = results[col].reset_index()
    t.insert(0, "slice_dimension", label)
    t = t.rename(columns={col: "slice_value"})
    all_slices.append(t)

combined = pd.concat(all_slices, ignore_index=True)
combined.to_csv(OUTPUT_DIR / "03_repeat_rate_by_slice.csv", index=False)
print(f"\nSaved: 03_repeat_rate_by_slice.csv")

#                                                                                                                                                             
# B.  TIME-TO-SECOND-PURCHASE DISTRIBUTION
#                                                                                                                                                             
print("\n\n[B] TIME-TO-SECOND-PURCHASE DISTRIBUTION")
print("=" * 55)

repeaters = cust[cust["is_repeat"]].copy()
repeaters["days_to_second"] = pd.to_numeric(repeaters["days_to_second"], errors="coerce")
repeaters = repeaters.dropna(subset=["days_to_second"])

# Cumulative distribution at key windows
windows = [7, 14, 30, 45, 60, 75, 90, 120, 180, 365]
total_repeaters = len(repeaters)
total_customers = len(cust)

print(f"\nOf {total_customers:,} customers who ever bought:")
print(f"  Repeated (2+ orders): {total_repeaters:,}  ({total_repeaters/total_customers:.1%})")
print()
print(f"{'Window':>8}  {'Cum. repeaters':>15}  {'% of ALL customers':>20}  {'% of repeaters':>16}")
print("-" * 65)
for w in windows:
    n = (repeaters["days_to_second"] <= w).sum()
    print(f"  {w:>4}d    {n:>10,}          {n/total_customers:>18.1%}    {n/total_repeaters:>14.1%}")

# Histogram buckets (0 €“7, 8 €“14, ..., 86 €“90, 91 €“120, 121 €“180, 181 €“365, 365+)
bins = [0,7,14,21,30,45,60,90,120,180,365,99999]
labels = ["0-7d","8-14d","15-21d","22-30d","31-45d","46-60d","61-90d",
          "91-120d","121-180d","181-365d","365d+"]
repeaters["days_bucket"] = pd.cut(repeaters["days_to_second"], bins=bins, labels=labels, right=True)
bucket_dist = (
    repeaters["days_bucket"].value_counts()
    .reindex(labels)
    .reset_index()
    .rename(columns={"days_bucket": "bucket", "count": "n_customers"})
    .assign(pct_of_repeaters=lambda d: d["n_customers"] / total_repeaters)
    .assign(cum_pct=lambda d: d["pct_of_repeaters"].cumsum())
)

print("\nDays-to-2nd-purchase histogram:")
print(bucket_dist.to_string(index=False))

# Percentiles
print("\nPercentiles of days-to-second:")
for p in [25, 50, 75, 90]:
    val = np.percentile(repeaters["days_to_second"].dropna(), p)
    print(f"  P{p:2d}: {val:.0f} days")

bucket_dist.to_csv(OUTPUT_DIR / "03_time_to_second_purchase.csv", index=False)

#                                                                                                                                                             
# C.  MONTHLY COHORT RETENTION HEATMAP
#     % of each acquisition cohort that made a 2nd purchase within 90 days
#                                                                                                                                                             
print("\n\n[C] MONTHLY COHORT 90-DAY RETENTION")
print("=" * 55)

# Only include cohorts that have had at least 90 days since first order
cutoff = ANALYSIS_DATE - pd.Timedelta(days=90)
cohort_data = cust.copy()
cohort_data["cohort_month"] = cohort_data["first_order_date"].dt.to_period("M")
cohort_data["eligible"] = cohort_data["first_order_date"] <= cutoff

eligible = cohort_data[cohort_data["eligible"]].copy()
eligible["repeat_in_90d"] = (
    eligible["is_repeat"] &
    (eligible["days_to_second"].fillna(9999) <= 90)
)

cohort_retention = (
    eligible.groupby("cohort_month")
    .agg(
        cohort_size     = ("customer_id",   "count"),
        repeat_in_90d   = ("repeat_in_90d", "sum"),
        repeat_any_time = ("is_repeat",     "sum"),
    )
    .assign(
        retention_90d  = lambda d: d["repeat_in_90d"]   / d["cohort_size"],
        retention_ever = lambda d: d["repeat_any_time"]  / d["cohort_size"],
    )
    .reset_index()
)

print(cohort_retention.tail(24).to_string(index=False))
cohort_retention.to_csv(OUTPUT_DIR / "03_cohort_retention_heatmap.csv", index=False)

overall_90d = eligible["repeat_in_90d"].sum() / len(eligible)
print(f"\nOverall 90-day retention rate (all eligible cohorts): {overall_90d:.1%}")

#                                                                                                                                                             
# D.  RFM SEGMENTATION
#                                                                                                                                                             
print("\n\n[D] RFM SEGMENTATION")
print("=" * 55)

rfm = cust.copy()
rfm["recency_days"]   = pd.to_numeric(rfm["recency_days"],   errors="coerce")
rfm["total_orders"]   = pd.to_numeric(rfm["total_orders"],   errors="coerce")
rfm["total_revenue"]  = pd.to_numeric(rfm["total_revenue"],  errors="coerce")

# Score 1 €“4 (4 = best)  €“ use rank-based scoring to handle duplicate bin edges
def score_col(series, ascending=True, n=4):
    ranked = series.rank(method="first", ascending=ascending)
    bins   = np.linspace(ranked.min() - 0.001, ranked.max() + 0.001, n + 1)
    labels = list(range(1, n + 1))
    return pd.cut(ranked, bins=bins, labels=labels).astype(int)

rfm["R"] = score_col(rfm["recency_days"],  ascending=False)  # lower recency = better
rfm["F"] = score_col(rfm["total_orders"],  ascending=True)
rfm["M"] = score_col(rfm["total_revenue"], ascending=True)

rfm["RFM_score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)

def rfm_segment(r, f, m):
    score = r + f + m
    if r == 4 and f >= 3 and m >= 3: return "Champions"
    if r >= 3 and f >= 2:            return "Loyal"
    if r == 4 and f == 1:            return "New Customers"
    if r == 3 and f == 1:            return "Promising"
    if r <= 2 and f >= 3:            return "At Risk"
    if r == 1 and f >= 2:            return "Cant Lose"
    if r <= 2 and f <= 2:            return "Hibernating"
    return "Others"

rfm["segment"] = rfm.apply(lambda x: rfm_segment(x["R"], x["F"], x["M"]), axis=1)

seg_summary = (
    rfm.groupby("segment")
    .agg(
        customers     = ("customer_id",   "count"),
        avg_orders    = ("total_orders",  "mean"),
        avg_revenue   = ("total_revenue", "mean"),
        avg_recency   = ("recency_days",  "mean"),
    )
    .assign(pct_customers=lambda d: d["customers"] / d["customers"].sum())
    .sort_values("customers", ascending=False)
)

print(seg_summary.to_string())
rfm[["customer_id","R","F","M","RFM_score","segment",
     "total_orders","total_revenue","recency_days",
     "first_product_cat","first_channel","ever_subscribed"]].to_csv(
    OUTPUT_DIR / "03_rfm_segments.csv", index=False
)

print(f"\nSaved: 03_rfm_segments.csv")
print("\n[03] Done.")

