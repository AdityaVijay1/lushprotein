"""
05_channel_discount.py  aEUR"  Channel quality and discount sensitivity.

Analyses
--------
A. Channel-level repeat rate, LTV, AOV comparison
   (Website direct vs Paid Social vs Paid Search vs Marketplace vs Subscription)
B. Discount sensitivity:
   - Do discount-acquired customers repurchase less at full price?
   - LTV comparison: discounted first order vs full-price first order
C. Discount code taxonomy: welcome / event / affiliate / bundle / other
D. Marketplace vs own-website customer quality comparison

Outputs
-------
outputs/05_channel_quality.csv
outputs/05_discount_sensitivity.csv
outputs/05_discount_code_taxonomy.csv

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
orders    = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
cust      = pd.read_parquet(OUTPUT_DIR / "customers.parquet")
discounts = pd.read_parquet(OUTPUT_DIR / "discounts.parquet")

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# A.  CHANNEL QUALITY COMPARISON
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n[A] CHANNEL QUALITY COMPARISON")
print("=" * 65)

channel_quality = (
    cust.groupby("first_channel")
    .agg(
        customers         = ("customer_id",    "count"),
        repeaters         = ("is_repeat",      "sum"),
        avg_ltv           = ("total_revenue",  "mean"),
        avg_orders        = ("total_orders",   "mean"),
        avg_lifespan_days = ("lifespan_days",  "mean"),
        pct_subscribed    = ("ever_subscribed","mean"),
        pct_discounted    = ("ever_discounted","mean"),
        median_days_2nd   = ("days_to_second", "median"),
    )
    .assign(repeat_rate=lambda d: d["repeaters"] / d["customers"])
    .sort_values("avg_ltv", ascending=False)
)

print(channel_quality.to_string())
channel_quality.to_csv(OUTPUT_DIR / "05_channel_quality.csv")

# a"EURa"EUR Compare marketplace vs website customers directly a"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EUR
print("\n  MARKETPLACE vs OWN-WEBSITE (direct comparison)")
mkt  = cust[cust["first_channel"] == "Marketplace"]
web  = cust[cust["first_channel"].isin(["Direct / Organic","Paid Social","Paid Search","Email","Affiliate"])]

for label, group in [("Marketplace", mkt), ("Own Website", web)]:
    print(f"\n  {label} (n={len(group):,}):")
    print(f"    Repeat rate:        {group['is_repeat'].mean():.1%}")
    print(f"    Avg LTV (SGD):      {group['total_revenue'].mean():.2f}")
    print(f"    Avg orders:         {group['total_orders'].mean():.2f}")
    print(f"    Median days to 2nd: {group['days_to_second'].median():.0f} days")
    print(f"    % ever subscribed:  {group['ever_subscribed'].mean():.1%}")

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# B.  DISCOUNT SENSITIVITY ANALYSIS
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n\n[B] DISCOUNT SENSITIVITY ANALYSIS")
print("=" * 65)

disc_sens = (
    cust.groupby("ever_discounted")
    .agg(
        customers         = ("customer_id",   "count"),
        repeat_rate       = ("is_repeat",     "mean"),
        avg_ltv           = ("total_revenue", "mean"),
        avg_orders        = ("total_orders",  "mean"),
        avg_lifespan_days = ("lifespan_days", "mean"),
        pct_subscribed    = ("ever_subscribed","mean"),
        median_days_2nd   = ("days_to_second","median"),
    )
)
disc_sens.index = disc_sens.index.map({True: "Discounted (any order)", False: "Full-price only"})
print(disc_sens.to_string())
disc_sens.to_csv(OUTPUT_DIR / "05_discount_sensitivity.csv")

# a"EURa"EUR Did first-order discount predict repeat? a"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EURa"EUR
print("\n  FIRST-ORDER discount vs repeat behaviour:")
first_order_orders = (
    orders.sort_values("order_date")
    .groupby("customer_id")
    .first()
    .reset_index()
    [["customer_id","has_discount","Price: Total Discount","Price: Total"]]
    .rename(columns={"has_discount":"first_discounted",
                     "Price: Total Discount": "first_disc_amt",
                     "Price: Total":          "first_order_value"})
)

disc_first = cust.merge(first_order_orders, on="customer_id", how="left")

fo_summary = (
    disc_first.groupby("first_discounted")
    .agg(
        customers    = ("customer_id",      "count"),
        repeat_rate  = ("is_repeat",        "mean"),
        avg_ltv      = ("total_revenue",    "mean"),
        avg_fov      = ("first_order_value","mean"),
        avg_disc_amt = ("first_disc_amt",   "mean"),
    )
)
fo_summary.index = fo_summary.index.map({True: "First order discounted", False: "First order full-price"})
print(fo_summary.to_string())

# Discount depth bins
disc_first["disc_depth"] = (
    disc_first["first_disc_amt"].fillna(0) /
    disc_first["first_order_value"].replace(0, np.nan)
).fillna(0)

bins   = [-0.001, 0, 0.05, 0.10, 0.20, 0.30, 0.50, 1.01]
labels = ["0% (full price)","1-5%","6-10%","11-20%","21-30%","31-50%","51%+"]
disc_first["disc_bin"] = pd.cut(disc_first["disc_depth"], bins=bins, labels=labels)

depth_summary = (
    disc_first.groupby("disc_bin", observed=True)
    .agg(customers=("customer_id","count"),
         repeat_rate=("is_repeat","mean"),
         avg_ltv=("total_revenue","mean"))
)
print("\n  Repeat rate by discount depth on first order:")
print(depth_summary.to_string())
depth_summary.reset_index().rename(columns={"disc_bin": "discount_bin"}).to_csv(
    OUTPUT_DIR / "05_discount_depth_bins.csv", index=False
)
print(f"  Saved: 05_discount_depth_bins.csv")

# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
# C.  DISCOUNT CODE TAXONOMY
# a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*
print("\n\n[C] DISCOUNT CODE TAXONOMY")
print("=" * 65)

disc = discounts.copy()
disc["code_upper"] = disc["Name"].str.upper().fillna("")

def classify_code(code: str) -> str:
    c = str(code).upper()
    if "WELCOME" in c or "FIRST" in c or "NEW" in c:
        return "Welcome / New Customer"
    if "AFFILIATE" in c:
        return "Affiliate"
    if any(x in c for x in ["HYROX","POPUP","EVENT","GYM","FIT"]):
        return "Event / Partnership"
    if any(x in c for x in ["BUNDLE","KIT","COMBO","SET"]):
        return "Bundle"
    if any(x in c for x in ["FRIEND","REFER","REF"]):
        return "Referral"
    if any(x in c for x in ["FLASH","SALE","PROMO","OFF"]):
        return "Flash / Sale"
    return "Other"

disc["code_type"] = disc["code_upper"].apply(classify_code)
disc["times_used"] = pd.to_numeric(disc["Times Used In Total"], errors="coerce").fillna(0)
disc["value"]      = pd.to_numeric(disc["Value"], errors="coerce")

taxonomy = (
    disc[disc["times_used"] > 0]
    .groupby("code_type")
    .agg(
        n_codes          = ("Name",             "count"),
        total_redemptions= ("times_used",        "sum"),
        avg_discount_val = ("value",             "mean"),
    )
    .sort_values("total_redemptions", ascending=False)
)
print(taxonomy.to_string())
taxonomy.to_csv(OUTPUT_DIR / "05_discount_code_taxonomy.csv")

print(f"\n  Total active discount codes: {(disc['times_used'] > 0).sum()}")
print(f"  Total redemptions: {disc['times_used'].sum():,.0f}")

print("\n[05] Done.")

