"""
06_subscription_churn.py  aEUR"  Subscription and churn deep-dive.

Analyses
--------
A. Subscription vs one-time buyer LTV comparison
B. Subscription tenure and churn rate by product SKU
C. Cancellation reasons breakdown (education gap proxy)
D. Reactivated subscribers: time-to-reactivation and product profile
E. Churn timing: at what subscription cycle do most customers cancel?

Outputs
-------
outputs/06_sub_vs_onetme_ltv.csv
outputs/06_churn_reasons.csv
outputs/06_churn_by_product.csv
outputs/06_reactivation_analysis.csv

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
cust            = pd.read_parquet(OUTPUT_DIR / "customers.parquet")
rc_orders       = pd.read_parquet(OUTPUT_DIR / "rc_orders.parquet")
rc_checkout     = pd.read_parquet(OUTPUT_DIR / "rc_checkout.parquet")
rc_churned      = pd.read_parquet(OUTPUT_DIR / "rc_churned.parquet")
rc_recurring    = pd.read_parquet(OUTPUT_DIR / "rc_recurring.parquet")
rc_reactivated  = pd.read_parquet(OUTPUT_DIR / "rc_reactivated.parquet")

# Parse dates
for df, cols in [
    (rc_orders,     ["metric_date"]),
    (rc_checkout,   ["metric_date"]),
    (rc_churned,    ["metric_date","subscription_activation_date","subscription_churn_date"]),
    (rc_recurring,  ["metric_date"]),
    (rc_reactivated,["metric_date","first_subscription_activation_date","reactivated_date"]),
]:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# A.  SUBSCRIPTION vs ONE-TIME LTV
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n[A] SUBSCRIPTION vs ONE-TIME BUYER LTV")
print("=" * 60)

sub_vs_ot = (
    cust.groupby("ever_subscribed")
    .agg(
        customers          = ("customer_id",   "count"),
        repeat_rate        = ("is_repeat",     "mean"),
        avg_ltv            = ("total_revenue", "mean"),
        median_ltv         = ("total_revenue", "median"),
        avg_orders         = ("total_orders",  "mean"),
        avg_lifespan_days  = ("lifespan_days", "mean"),
        pct_discounted     = ("ever_discounted","mean"),
        median_days_2nd    = ("days_to_second","median"),
    )
)
sub_vs_ot.index = sub_vs_ot.index.map({True:"Subscriber", False:"One-time / Non-subscriber"})
print(sub_vs_ot.to_string())
sub_vs_ot.to_csv(OUTPUT_DIR / "06_sub_vs_onetime_ltv.csv")

ltv_uplift = (sub_vs_ot.loc["Subscriber","avg_ltv"] /
              sub_vs_ot.loc["One-time / Non-subscriber","avg_ltv"] - 1)
print(f"\n  LTV uplift (subscriber over non-subscriber): {ltv_uplift:+.1%}")

# a"EURa"EUR Subscription order-type breakdown a"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EUR
print("\n  Recharge order type breakdown:")
print(rc_orders["order_type"].value_counts().to_string())
print(f"\n  Recharge orders total: {len(rc_orders):,}")
type_rev = rc_orders.groupby("order_type")["order_gross_revenue"].agg(["sum","mean","count"])
print(type_rev.to_string())

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# B.  SUBSCRIPTION CHURN RATE BY PRODUCT
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n\n[B] SUBSCRIPTION CHURN BY PRODUCT")
print("=" * 60)

# Active subscriptions = checkout customers NOT in churned list
checkout_custs  = rc_checkout["customer_id"].unique()
churned_custs   = rc_churned["customer_id"].unique()
active_sub_custs= set(checkout_custs) - set(churned_custs)

print(f"  Checkout subscribers:  {len(checkout_custs):,}")
print(f"  Churned subscribers:   {len(churned_custs):,}")
print(f"  Active (est.):         {len(active_sub_custs):,}")
print(f"  Churn rate (raw):      {len(churned_custs)/len(checkout_custs):.1%}")

churn_by_prod = (
    rc_churned.groupby("product_title")
    .agg(
        churned_subscriptions = ("subscription_id", "count"),
        unique_customers      = ("customer_id",      "nunique"),
    )
    .sort_values("churned_subscriptions", ascending=False)
    .head(20)
)
print("\n  Churned subscriptions by product:")
print(churn_by_prod.to_string())
churn_by_prod.to_csv(OUTPUT_DIR / "06_churn_by_product.csv")

# a"EURa"EUR Subscription tenure at churn a"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EUR
rc_churned["tenure_days"] = (
    rc_churned["subscription_churn_date"] - rc_churned["subscription_activation_date"]
).dt.days

print("\n  Subscription tenure at churn (days):")
print(rc_churned["tenure_days"].describe().to_string())

bins   = [0, 30, 60, 90, 120, 180, 365, 9999]
labels = ["0-30d","31-60d","61-90d","91-120d","121-180d","181-365d","365d+"]
rc_churned["tenure_bin"] = pd.cut(rc_churned["tenure_days"], bins=bins, labels=labels, right=True)
tenure_dist = rc_churned["tenure_bin"].value_counts().reindex(labels)
tenure_dist_pct = tenure_dist / tenure_dist.sum()
print("\n  Churn tenure distribution:")
for lbl, n, pct in zip(labels, tenure_dist, tenure_dist_pct):
    print(f"    {lbl:<12}  {n:>4}  ({pct:.1%})")
tenure_df = pd.DataFrame({
    "tenure_bin": labels,
    "n": tenure_dist.values,
    "pct": tenure_dist_pct.values,
})
tenure_df.to_csv(OUTPUT_DIR / "06_churn_tenure.csv", index=False)
print("  Saved: 06_churn_tenure.csv")

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# C.  CANCELLATION REASONS aEUR" education gap proxy
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n\n[C] CANCELLATION REASONS (Education Gap Proxy)")
print("=" * 60)

reasons = (
    rc_churned.groupby("cancellation_reason")
    .agg(
        n           = ("subscription_id",   "count"),
        n_customers = ("customer_id",        "nunique"),
        avg_tenure  = ("tenure_days",        "mean"),
    )
    .assign(pct=lambda d: d["n"] / d["n"].sum())
    .sort_values("n", ascending=False)
)
print(reasons.to_string())
reasons.to_csv(OUTPUT_DIR / "06_churn_reasons.csv")

# Classify into "education gap" vs "price" vs "product fit" vs "other"
def reason_theme(r: str) -> str:
    r = str(r).lower()
    if "have more" in r or "too much" in r or "already" in r:
        return "Stockpile / Over-purchased"
    if "expensive" in r or "cost" in r or "price" in r or "afford" in r:
        return "Price Sensitivity"
    if "no longer" in r or "don't use" in r or "not use" in r:
        return "Product No Longer Needed"
    if "result" in r or "work" in r or "effective" in r or "not see" in r:
        return "No Perceived Results (Education Gap)"
    if "pause" in r or "skip" in r or "break" in r:
        return "Temporary Pause"
    if "switch" in r or "competitor" in r or "other brand" in r:
        return "Switched Brand"
    return "Other / Unclear"

rc_churned["reason_theme"] = rc_churned["cancellation_reason"].apply(reason_theme)
theme_summary = (
    rc_churned.groupby("reason_theme")
    .agg(n=("subscription_id","count"), avg_tenure=("tenure_days","mean"))
    .assign(pct=lambda d: d["n"] / d["n"].sum())
    .sort_values("n", ascending=False)
)
print("\n  Cancellation themes (grouped):")
print(theme_summary.to_string())

# a"EURa"EUR Churn timing by cycle number (inferred from tenure) a"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EUR
# Products last ~30 days/tub; a cycle is ~30 days
rc_churned["approx_cycle"] = (rc_churned["tenure_days"] / 30).fillna(0).clip(lower=0).round().astype(int)
cycle_dist = rc_churned["approx_cycle"].value_counts().sort_index().head(13)
print("\n  Approximate cycle at which subscribers cancel (1 cycle approx 30 days):")
print(cycle_dist.to_string())
cycle_df = cycle_dist.reset_index()
cycle_df.columns = ["approx_cycle", "n_cancellations"]
cycle_df["cycle_label"] = "Cycle " + cycle_df["approx_cycle"].astype(str)
cycle_df.to_csv(OUTPUT_DIR / "06_churn_by_cycle.csv", index=False)
print("  Saved: 06_churn_by_cycle.csv")

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# D.  REACTIVATED SUBSCRIBERS
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n\n[D] REACTIVATED SUBSCRIBERS (Win-backs)")
print("=" * 60)

reac = rc_reactivated.copy()
print(f"  Total reactivated subscribers: {len(reac)}")

reac["days_to_reactivate"] = (
    reac["reactivated_date"] - reac["first_subscription_activation_date"]
).dt.days

print(f"\n  Days from first activation to reactivation:")
print(reac["days_to_reactivate"].describe().to_string())

# How many of the churned customers came back?
churned_set    = set(rc_churned["customer_id"].dropna().astype(str))
reactivated_set= set(reac["customer_id"].dropna().astype(str))
overlap        = churned_set & reactivated_set
print(f"\n  Churned customers:                   {len(churned_set):,}")
print(f"  Of those, reactivated:               {len(overlap):,}")
print(f"  Win-back rate (of known churned):    {len(overlap)/max(len(churned_set),1):.1%}")

reac.to_csv(OUTPUT_DIR / "06_reactivation_analysis.csv", index=False)

print("\n[06] Done.")

