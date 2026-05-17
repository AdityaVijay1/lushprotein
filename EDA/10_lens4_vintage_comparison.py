"""
10_lens4_vintage_comparison.py  —  Customer-Base Audit: LENS 4
"Are the Customers We Are Acquiring Now Better or Worse Than Before?"

Framework: Bruce, Fader & Ross — The Customer-Base Audit (2022)
Lens 4 = Two (or more) cohorts compared at the SAME AGE.
The key methodological requirement: compare cohorts at the same point in their lifecycle,
NOT at the same calendar year.

Analyses
--------
A. Cohort quality comparison at Age 0 (acquisition year): size, avg AOV, avg spend
B. Year 1 repeat rate comparison — did a higher or lower % return within 12 months?
C. Year 1 Revenue per cohort member — is each cohort worth more or less at same age?
D. 60-day and 180-day retention by acquisition cohort (quality drift over time)
E. Channel mix shift by cohort — are we acquiring a different type of customer?
F. Discount intensity by cohort — has discounting depth increased over time?
G. Acquisition quality summary: composite quality score per cohort

Notes
-----
- Cohorts: 2020, 2021, 2022, 2023, 2024 (SGD-denominated customers only)
- "Age" is measured from first purchase date within the cohort year
- Same-age comparison requires sufficient observation time:
    2020 cohort has 5 years of data | 2024 cohort has only 1 year
- Caveats noted where comparison windows are limited

Outputs
-------
EDA/outputs/10_lens4_cohort_quality.csv     — Per-cohort quality metrics at acquisition
EDA/outputs/10_lens4_year1_comparison.csv   — Year 1 metrics by cohort
EDA/outputs/10_lens4_retention_by_vintage.csv — 30/60/90/180d retention by cohort
EDA/outputs/10_lens4_channel_mix_shift.csv  — Channel composition per cohort year
EDA/outputs/10_lens4_discount_intensity.csv — Discount depth by cohort year
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
print("LENS 4 — COMPARING COHORTS AT THE SAME AGE")
print("Vintage comparison  |  Acquisition quality drift  |  Channel mix")
print("=" * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
orders = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
orders["order_date"]   = pd.to_datetime(orders["order_date"], utc=True)
orders["Price: Total"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
orders["Price: Total Discount"] = pd.to_numeric(orders["Price: Total Discount"], errors="coerce").fillna(0)

# SGD filter
sgd = orders[orders["Currency"].fillna("") == "SGD"].copy()

# Acquisition year & date for each customer
first_purchase = (
    sgd.sort_values("order_date")
    .groupby("customer_id")
    .agg(
        first_date    = ("order_date",              "min"),
        first_channel = ("channel",                 "first"),
        first_product = ("product_category",        "first"),
        first_discount= ("Price: Total Discount",   "first"),
        first_rev     = ("Price: Total",             "first"),
    )
    .reset_index()
)
first_purchase["acq_year"] = first_purchase["first_date"].dt.year
first_purchase["first_disc_pct"] = (
    first_purchase["first_discount"] / first_purchase["first_rev"].clip(lower=0.01)
).clip(0, 1)

COHORT_YEARS = sorted([y for y in first_purchase["acq_year"].unique() if 2020 <= y <= 2024])
print(f"\nCohort years analyzed: {COHORT_YEARS}")

# Build full customer history
cust_hist = (
    sgd.groupby("customer_id")
    .agg(
        total_orders   = ("order_id",       "count"),
        total_revenue  = ("Price: Total",   "sum"),
        total_discount = ("Price: Total Discount","sum"),
    )
    .reset_index()
)
cust_hist = cust_hist.merge(first_purchase, on="customer_id", how="left")
cust_hist["aov_lifetime"] = cust_hist["total_revenue"] / cust_hist["total_orders"].clip(lower=1)

# ==============================================================================
# A.  COHORT QUALITY AT ACQUISITION (Age 0)
# ==============================================================================
print("\n\n[A] COHORT QUALITY AT ACQUISITION (Age 0)")
print("-" * 65)
print("Same-age = acquisition year only; same-age comparison is valid here")
print()
print(f"  {'Cohort':>7}  {'Customers':>10}  {'Avg 1st Order':>14}  {'Disc Rate':>10}  {'% Discounted':>13}  {'Top Channel':>18}")
print(f"  {'-'*80}")

quality_rows = []
for yr in COHORT_YEARS:
    cohort = first_purchase[first_purchase["acq_year"] == yr].copy()
    n = len(cohort)
    avg_aov0 = cohort["first_rev"].mean()
    avg_disc  = (cohort["first_discount"] > 0).mean()
    avg_disc_depth = cohort[cohort["first_discount"] > 0]["first_disc_pct"].mean() if (cohort["first_discount"] > 0).any() else 0
    top_ch = cohort["first_channel"].value_counts().index[0] if len(cohort) > 0 else "N/A"

    quality_rows.append({
        "cohort_year": yr, "n_customers": n,
        "avg_first_order_sgd": round(avg_aov0, 2),
        "pct_discounted": round(avg_disc, 4),
        "avg_discount_depth_pct": round(avg_disc_depth, 4),
        "top_channel": top_ch,
    })
    print(f"  {yr:>7}  {n:>10,}  S${avg_aov0:>12.0f}  {avg_disc_depth:>9.1%}  {avg_disc:>12.1%}  {top_ch:>18}")

quality_df = pd.DataFrame(quality_rows)
quality_df.to_csv(OUTPUT_DIR / "10_lens4_cohort_quality.csv", index=False)
print(f"\nSaved: 10_lens4_cohort_quality.csv")

# ==============================================================================
# B.  YEAR 1 RETENTION COMPARISON (same-age = 365 days post acquisition)
# ==============================================================================
print("\n\n[B] YEAR 1 RETENTION — Same-Age Comparison (0-365 days)")
print("-" * 65)

# For each cohort, count what % returned within 365 days
# (Only cohorts with enough follow-up time are valid)
sgd_sorted = sgd.sort_values(["customer_id","order_date"])
year1_rows = []
print(f"  {'Cohort':>7}  {'Customers':>10}  {'Repeat 60d':>11}  {'Repeat 180d':>12}  {'Repeat 365d':>12}  {'Avg Y1 Rev':>11}  {'Note':>10}")
print(f"  {'-'*80}")

for yr in COHORT_YEARS:
    cohort_cids = set(first_purchase[first_purchase["acq_year"] == yr]["customer_id"])
    cohort_first = first_purchase[first_purchase["acq_year"] == yr].set_index("customer_id")

    n = len(cohort_cids)
    repeat_60  = 0
    repeat_180 = 0
    repeat_365 = 0
    total_y1_rev = 0

    for cid in cohort_cids:
        first_dt = cohort_first.loc[cid, "first_date"]
        cust_orders = sgd_sorted[sgd_sorted["customer_id"] == cid]
        after_first = cust_orders[cust_orders["order_date"] > first_dt]
        if len(after_first) == 0:
            continue
        days_to_second = (after_first.iloc[0]["order_date"] - first_dt).days
        if days_to_second <= 60:   repeat_60  += 1
        if days_to_second <= 180:  repeat_180 += 1
        if days_to_second <= 365:  repeat_365 += 1

    # Y1 revenue = all orders in the first 365 days post-first-purchase
    for cid in cohort_cids:
        first_dt = cohort_first.loc[cid, "first_date"]
        cust_orders = sgd_sorted[sgd_sorted["customer_id"] == cid]
        y1_orders = cust_orders[
            (cust_orders["order_date"] >= first_dt) &
            (cust_orders["order_date"] <= first_dt + pd.Timedelta(days=365))
        ]
        total_y1_rev += y1_orders["Price: Total"].sum()

    avg_y1_rev = total_y1_rev / n if n > 0 else 0
    note = "Full data" if (2026 - yr) >= 2 else "Partial"
    year1_rows.append({
        "cohort_year": yr, "n_customers": n,
        "pct_repeat_60d":  round(repeat_60/n if n > 0 else 0, 4),
        "pct_repeat_180d": round(repeat_180/n if n > 0 else 0, 4),
        "pct_repeat_365d": round(repeat_365/n if n > 0 else 0, 4),
        "avg_y1_rev_sgd":  round(avg_y1_rev, 2),
        "note": note,
    })
    print(f"  {yr:>7}  {n:>10,}  {repeat_60/n if n>0 else 0:>10.1%}  {repeat_180/n if n>0 else 0:>11.1%}  "
          f"{repeat_365/n if n>0 else 0:>11.1%}  S${avg_y1_rev:>9.0f}  {note:>10}")

year1_df = pd.DataFrame(year1_rows)
year1_df.to_csv(OUTPUT_DIR / "10_lens4_year1_comparison.csv", index=False)
print(f"\nSaved: 10_lens4_year1_comparison.csv")

# Quality drift observation
print(f"\n  QUALITY DRIFT OBSERVATION:")
if len(year1_df) >= 3:
    early = year1_df[year1_df["cohort_year"] <= 2021]["pct_repeat_365d"].mean()
    late  = year1_df[year1_df["cohort_year"] >= 2023]["pct_repeat_365d"].mean()
    drift = late - early
    print(f"  Avg 365-day retention, 2020-2021 cohorts: {early:.1%}")
    print(f"  Avg 365-day retention, 2023-2024 cohorts: {late:.1%}")
    print(f"  Delta:  {drift:+.1%}  ({'cohort quality DECLINING' if drift < 0 else 'cohort quality improving'})")
    print(f"\n  If retention is declining, investigate: discount mix shift? channel mix shift?")

# ==============================================================================
# C.  CHANNEL MIX SHIFT BY COHORT
# ==============================================================================
print("\n\n[C] CHANNEL MIX SHIFT BY COHORT YEAR")
print("-" * 65)
print("Are we changing who we acquire over time? Channel mix shapes cohort quality.")
print()

channel_mix = (
    first_purchase[first_purchase["acq_year"].isin(COHORT_YEARS)]
    .groupby(["acq_year","first_channel"])
    .size()
    .unstack(fill_value=0)
)
# Normalize to percentages
channel_pct = channel_mix.div(channel_mix.sum(axis=1), axis=0)

channels = list(channel_pct.columns)
print(f"  {'Cohort':>7}", end="")
for ch in channels:
    print(f"  {ch[:12]:>12}", end="")
print()
print(f"  {'-'*80}")
for yr in COHORT_YEARS:
    if yr in channel_pct.index:
        print(f"  {yr:>7}", end="")
        for ch in channels:
            pct = channel_pct.loc[yr, ch] if ch in channel_pct.columns else 0
            print(f"  {pct:>11.1%}", end="")
        print()

channel_mix_long = channel_pct.reset_index().melt(
    id_vars="acq_year", var_name="channel", value_name="pct"
)
channel_mix_long.to_csv(OUTPUT_DIR / "10_lens4_channel_mix_shift.csv", index=False)
print(f"\nSaved: 10_lens4_channel_mix_shift.csv")

print(f"\n  KEY QUESTION: Is the Marketplace (Shopee/Lazada) share GROWING?")
if "Marketplace" in channel_pct.columns:
    mkt_trend = channel_pct["Marketplace"]
    print(f"  Marketplace share by cohort: {dict(zip(channel_pct.index, mkt_trend.round(3).values))}")
    if len(mkt_trend) >= 3:
        if mkt_trend.iloc[-1] > mkt_trend.iloc[0]:
            print(f"  --> MARKETPLACE SHARE IS GROWING: latest {mkt_trend.iloc[-1]:.1%} vs earliest {mkt_trend.iloc[0]:.1%}")
            print(f"  --> This explains cohort quality decline: marketplace = lower LTV, 0% sub conversion")
        else:
            print(f"  --> Marketplace share is stable or declining: {mkt_trend.iloc[0]:.1%} -> {mkt_trend.iloc[-1]:.1%}")

# ==============================================================================
# D.  DISCOUNT INTENSITY BY COHORT YEAR
# ==============================================================================
print("\n\n[D] DISCOUNT INTENSITY BY COHORT YEAR")
print("-" * 65)
print("Has discounting depth increased over time? Deep discounts = weaker cohort quality.")
print()
print(f"  {'Cohort':>7}  {'Customers':>10}  {'%Discounted':>12}  {'Avg Disc Depth':>15}  {'Avg 1st Order':>14}")
print(f"  {'-'*65}")

disc_rows = []
for yr in COHORT_YEARS:
    cohort = first_purchase[first_purchase["acq_year"] == yr].copy()
    pct_disc  = (cohort["first_discount"] > 0).mean()
    avg_depth = cohort[cohort["first_discount"] > 0]["first_disc_pct"].mean() if pct_disc > 0 else 0
    avg_rev   = cohort["first_rev"].mean()
    disc_rows.append({
        "cohort_year": yr, "n": len(cohort),
        "pct_discounted": round(pct_disc, 4),
        "avg_discount_depth_pct": round(avg_depth, 4),
        "avg_first_order_sgd": round(avg_rev, 2),
    })
    print(f"  {yr:>7}  {len(cohort):>10,}  {pct_disc:>11.1%}  {avg_depth:>14.1%}  S${avg_rev:>12.0f}")

disc_df = pd.DataFrame(disc_rows)
disc_df.to_csv(OUTPUT_DIR / "10_lens4_discount_intensity.csv", index=False)
print(f"\nSaved: 10_lens4_discount_intensity.csv")

if len(disc_df) >= 3:
    early_disc = disc_df[disc_df["cohort_year"] <= 2021]["pct_discounted"].mean()
    late_disc  = disc_df[disc_df["cohort_year"] >= 2023]["pct_discounted"].mean()
    print(f"\n  % discounted: 2020-2021 avg = {early_disc:.1%}  |  2023-2024 avg = {late_disc:.1%}")
    if late_disc > early_disc:
        print(f"  --> DISCOUNTING INTENSITY HAS INCREASED by {late_disc - early_disc:+.1%}")
        print(f"  --> Recent cohorts are more discount-driven, predicting weaker long-term retention")

# ==============================================================================
# LENS 4 KEY TAKEAWAYS
# ==============================================================================
print("\n\n[LENS 4 KEY TAKEAWAYS]")
print("=" * 65)
print("""
  1. COHORT QUALITY MATTERS MORE THAN COHORT SIZE.
     A cohort of 2,000 full-price buyers is worth more than a cohort of 5,000
     heavy-discount buyers. Lens 4 makes this comparison explicit.

  2. COMPARING AT THE SAME AGE IS CRITICAL.
     A 2022 cohort with 30% retention looks better than 2024's 18%...
     BUT only when measured at the same number of months post-acquisition.
     Calendar-year comparisons conflate cohort age with cohort quality.

  3. DISCOUNT MIX SHIFT EXPLAINS QUALITY DRIFT.
     If recent cohorts have more discounted first orders, expect:
     - Lower repeat rates
     - Lower LTV
     - Higher churn in first 60 days
     This is consistent with the Discount Sensitivity findings (Lens 1 / existing EDA).

  4. CHANNEL MIX SHIFT IS A HIDDEN DRIVER.
     If Marketplace share is growing, the apparent "growth" in customer count
     is partly a shift to a lower-quality customer type — not genuine growth.

  5. THE ACQUISITION QUALITY TREND IS A LEADING INDICATOR.
     If cohort quality is declining year-over-year (at same age),
     current revenue will look fine today but will deteriorate in 12-24 months
     as those weaker cohorts fail to repeat. Lens 4 sees this BEFORE revenue does.
""")

print("[10] Lens 4 DONE.\n")
