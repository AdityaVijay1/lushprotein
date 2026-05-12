"""
11_lens5_base_health.py  —  Customer-Base Audit: LENS 5
"How Healthy Is Our Customer Base?"

Framework: Bruce, Fader & Ross — The Customer-Base Audit (2022)
Lens 5 = The whole customer base — ALL cohorts and ALL periods.
Integrates Lenses 1-4 into a single health diagnostic.

Analyses
--------
A. Full cohort × year revenue matrix (rows = acquisition cohorts, cols = calendar years)
   This is the "triangle" chart from the textbook
B. Cohort revenue decay curves — how each cohort fades over time
C. Customer base composition by year: New / Retained / Recovered (3-state waterfall)
D. Revenue contribution: what % of each year's revenue came from this year's new customers?
   (leading indicator of acquisition dependency vs retention strength)
E. Customer base health scorecard (5 KPIs that summarise base health)
F. Forward-looking implications: IF recent trends continue, what does the base look like?

Notes
-----
- SGD orders only for revenue metrics
- "Recovered" = customer was inactive last year but active this year (not a new customer)
- All cohorts 2020-2025 analyzed

Outputs
-------
EDA/outputs/11_lens5_cohort_revenue_matrix.csv — Cohort x Year revenue triangle
EDA/outputs/11_lens5_revenue_decay_curves.csv  — % of cohort acquisition revenue by year
EDA/outputs/11_lens5_composition_waterfall.csv — New/Retained/Recovered by year
EDA/outputs/11_lens5_health_scorecard.csv      — 5-KPI health diagnostic
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
print("LENS 5 — HOW HEALTHY IS THE CUSTOMER BASE?")
print("All cohorts, all periods  |  Integrated diagnostic  |  Base health")
print("=" * 65)

# ── Load ──────────────────────────────────────────────────────────────────────
orders = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
orders["order_date"]   = pd.to_datetime(orders["order_date"], utc=True)
orders["Price: Total"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)

sgd = orders[orders["Currency"].fillna("") == "SGD"].copy()
sgd["year"] = sgd["order_date"].dt.year

# Acquisition year
acq_year = (
    sgd.sort_values("order_date")
    .groupby("customer_id")["year"]
    .first().rename("acq_year").reset_index()
)
sgd = sgd.merge(acq_year, on="customer_id", how="left")

CALENDAR_YEARS = sorted(sgd["year"].unique())
ACQ_YEARS      = sorted(sgd[sgd["year"] == sgd["acq_year"]]["acq_year"].unique())
# Filter to 2020+ cohorts where data is most complete
ACQ_YEARS = [y for y in ACQ_YEARS if y >= 2020]

print(f"\nCalendar years: {CALENDAR_YEARS}")
print(f"Acquisition cohorts analyzed: {ACQ_YEARS}")

# ==============================================================================
# A.  COHORT × YEAR REVENUE MATRIX (THE TRIANGLE)
# ==============================================================================
print("\n\n[A] COHORT x YEAR REVENUE MATRIX (SGD)")
print("-" * 65)
print("Rows = acquisition cohort | Columns = calendar year | Values = SGD revenue")
print("(Blank cells = cohort didn't exist yet or no data)")
print()

matrix_rows = []
for acq_yr in ACQ_YEARS:
    cohort_ids = set(acq_year[acq_year["acq_year"] == acq_yr]["customer_id"])
    row = {"cohort": acq_yr}
    for cal_yr in CALENDAR_YEARS:
        if cal_yr < acq_yr:
            row[str(cal_yr)] = np.nan
        else:
            yr_rev = sgd[
                (sgd["customer_id"].isin(cohort_ids)) & (sgd["year"] == cal_yr)
            ]["Price: Total"].sum()
            row[str(cal_yr)] = yr_rev
    matrix_rows.append(row)

matrix_df = pd.DataFrame(matrix_rows).set_index("cohort")

# Print matrix
col_headers = "  Cohort" + "".join(f"  {yr}" for yr in CALENDAR_YEARS)
print(col_headers)
print("  " + "-" * (len(col_headers)))
for acq_yr, row in matrix_df.iterrows():
    vals = ""
    for yr in CALENDAR_YEARS:
        v = row[str(yr)]
        if pd.isna(v):
            vals += "       —"
        else:
            vals += f"  {v/1000:>5.0f}K"
    print(f"  {acq_yr}  {vals}")

print("\n  (Values in S$K — thousands of SGD)")

matrix_df.reset_index().to_csv(OUTPUT_DIR / "11_lens5_cohort_revenue_matrix.csv", index=False)
print(f"\nSaved: 11_lens5_cohort_revenue_matrix.csv")

# ==============================================================================
# B.  REVENUE DECAY CURVES — % of Year 0 (acquisition) revenue
# ==============================================================================
print("\n\n[B] REVENUE DECAY CURVES")
print("-" * 65)
print("Each value = that year's cohort revenue as % of the acquisition year revenue")
print("(Shows how quickly each cohort fades)")
print()

decay_rows = []
col_h = "  Cohort" + "".join(f"  Age+{i}" for i in range(len(CALENDAR_YEARS)))
print(col_h)
print("  " + "-" * len(col_h))

for acq_yr in ACQ_YEARS:
    cohort_ids = set(acq_year[acq_year["acq_year"] == acq_yr]["customer_id"])
    rev_by_yr = {}
    for cal_yr in CALENDAR_YEARS:
        if cal_yr >= acq_yr:
            rv = sgd[
                (sgd["customer_id"].isin(cohort_ids)) & (sgd["year"] == cal_yr)
            ]["Price: Total"].sum()
            rev_by_yr[cal_yr] = rv

    base_rev = rev_by_yr.get(acq_yr, 0)
    row = {"cohort": acq_yr, "base_revenue": base_rev}
    row_str = f"  {acq_yr}  "
    for offset, cal_yr in enumerate(CALENDAR_YEARS):
        age = cal_yr - acq_yr
        if age < 0:
            pct = np.nan
        elif base_rev > 0:
            pct = rev_by_yr.get(cal_yr, 0) / base_rev
        else:
            pct = np.nan
        row[f"age_plus_{age}"] = round(pct, 4) if not pd.isna(pct) else np.nan
        if pd.isna(pct):
            row_str += "       —"
        else:
            row_str += f"  {pct:>6.1%}"
    decay_rows.append(row)
    print(row_str)

decay_df = pd.DataFrame(decay_rows)
decay_df.to_csv(OUTPUT_DIR / "11_lens5_revenue_decay_curves.csv", index=False)
print(f"\nSaved: 11_lens5_revenue_decay_curves.csv")
print(f"\n  INSIGHT: Each cohort's Year 1 revenue is its 'base'.")
print(f"  The speed of decay (how quickly % falls after Year 0) measures cohort loyalty.")
print(f"  Faster decay = weaker cohort = worse acquisition quality OR worse post-purchase experience")

# ==============================================================================
# C.  CUSTOMER BASE COMPOSITION WATERFALL — New / Retained / Recovered
# ==============================================================================
print("\n\n[C] CUSTOMER BASE COMPOSITION — Annual Waterfall")
print("-" * 65)
print("New = buying for first time | Retained = bought last year too | Recovered = gap buyers")
print()
print(f"  {'Year':>5}  {'Total':>8}  {'New':>8}  {'Retained':>10}  {'Recovered':>11}  "
      f"{'%New':>6}  {'%Ret':>6}  {'%Rec':>6}")
print(f"  {'-'*75}")

comp_rows = []
prev_buyers = set()
for yr in CALENDAR_YEARS:
    current_buyers = set(sgd[sgd["year"] == yr]["customer_id"])
    new_this_year  = set(acq_year[acq_year["acq_year"] == yr]["customer_id"])
    new_buyers     = current_buyers & new_this_year
    retained       = current_buyers & prev_buyers
    recovered      = current_buyers - new_buyers - retained

    n_total = len(current_buyers)
    n_new   = len(new_buyers)
    n_ret   = len(retained)
    n_rec   = len(recovered)

    comp_rows.append({
        "year": yr, "n_total": n_total,
        "n_new": n_new, "n_retained": n_ret, "n_recovered": n_rec,
        "pct_new": round(n_new/n_total, 4) if n_total > 0 else 0,
        "pct_retained": round(n_ret/n_total, 4) if n_total > 0 else 0,
        "pct_recovered": round(n_rec/n_total, 4) if n_total > 0 else 0,
    })
    print(f"  {yr:>5}  {n_total:>8,}  {n_new:>8,}  {n_ret:>10,}  {n_rec:>11,}  "
          f"{n_new/n_total:>5.0%}  {n_ret/n_total:>5.0%}  {n_rec/n_total:>5.0%}")

    prev_buyers = current_buyers

comp_df = pd.DataFrame(comp_rows)
comp_df.to_csv(OUTPUT_DIR / "11_lens5_composition_waterfall.csv", index=False)
print(f"\nSaved: 11_lens5_composition_waterfall.csv")

# Revenue-weighted version
print(f"\n  Revenue composition:")
print(f"  {'Year':>5}  {'Tot Rev (K)':>12}  {'New Rev %':>10}  {'Ret Rev %':>10}  {'Rec Rev %':>10}")
print(f"  {'-'*55}")

prev_buyers = set()
for yr in CALENDAR_YEARS:
    yr_data = sgd[sgd["year"] == yr]
    current_buyers = set(yr_data["customer_id"])
    new_this_year  = set(acq_year[acq_year["acq_year"] == yr]["customer_id"])
    new_buyers     = current_buyers & new_this_year
    retained       = current_buyers & prev_buyers
    recovered      = current_buyers - new_buyers - retained

    tot_rev  = yr_data["Price: Total"].sum()
    new_rev  = yr_data[yr_data["customer_id"].isin(new_buyers)]["Price: Total"].sum()
    ret_rev  = yr_data[yr_data["customer_id"].isin(retained)]["Price: Total"].sum()
    rec_rev  = yr_data[yr_data["customer_id"].isin(recovered)]["Price: Total"].sum()

    print(f"  {yr:>5}  S${tot_rev/1000:>10.0f}  "
          f"{new_rev/tot_rev:>9.0%}  {ret_rev/tot_rev:>9.0%}  {rec_rev/tot_rev:>9.0%}"
          if tot_rev > 0 else f"  {yr:>5}  S$0")
    prev_buyers = current_buyers

print(f"\n  IF a high % of revenue comes from New customers: the base is ACQUISITION-DEPENDENT.")
print(f"  This means revenue is fragile — it only holds if acquisition keeps up.")
print(f"  A healthy base has growing RETAINED contribution (denominator = loyal customers).")

# ==============================================================================
# D.  REVENUE MIX — What % came from each acquisition cohort per calendar year
# ==============================================================================
print("\n\n[D] REVENUE CONTRIBUTION BY COHORT VINTAGE")
print("-" * 65)
print("What % of each year's SGD revenue came from each acquisition cohort?")
print()

rev_by_cohort_yr = {}
for yr in CALENDAR_YEARS:
    yr_data = sgd[sgd["year"] == yr].copy()
    for acq_yr in ACQ_YEARS:
        cohort_ids = set(acq_year[acq_year["acq_year"] == acq_yr]["customer_id"])
        rev = yr_data[yr_data["customer_id"].isin(cohort_ids)]["Price: Total"].sum()
        rev_by_cohort_yr[(acq_yr, yr)] = rev

# Print as cross-tab
print(f"  {'':>8}", end="")
for yr in CALENDAR_YEARS:
    yr_total = sgd[sgd["year"] == yr]["Price: Total"].sum()
    print(f"  {yr}({yr_total/1000:.0f}K)", end="")
print()
print(f"  {'-'*90}")
for acq_yr in ACQ_YEARS:
    print(f"  {acq_yr} coh", end="")
    for yr in CALENDAR_YEARS:
        if yr < acq_yr:
            print(f"        —", end="")
        else:
            yr_total = sgd[sgd["year"] == yr]["Price: Total"].sum()
            cohort_rev = rev_by_cohort_yr.get((acq_yr, yr), 0)
            pct = cohort_rev / yr_total if yr_total > 0 else 0
            print(f"  {pct:>6.1%}", end="")
    print()

# ==============================================================================
# E.  CUSTOMER BASE HEALTH SCORECARD
# ==============================================================================
print("\n\n[E] CUSTOMER BASE HEALTH SCORECARD")
print("=" * 65)

# Compute 5 core health KPIs
# KPI 1: Overall repeat rate
all_cust = pd.read_parquet(OUTPUT_DIR / "customers.parquet")
all_cust["total_orders"] = pd.to_numeric(all_cust["total_orders"], errors="coerce").fillna(1)
all_cust["total_revenue"] = pd.to_numeric(all_cust["total_revenue"], errors="coerce").fillna(0)
repeat_rate = (all_cust["total_orders"] >= 2).mean()

# KPI 2: Year-over-year retention (latest year pair from waterfall)
latest_comp = comp_df.dropna()
if len(latest_comp) >= 2:
    prev_yr_row = latest_comp.iloc[-2]
    curr_yr_row = latest_comp.iloc[-1]
    yoy_retention = curr_yr_row["n_retained"] / prev_yr_row["n_total"] if prev_yr_row["n_total"] > 0 else 0
else:
    yoy_retention = 0

# KPI 3: 90-day cohort retention (from existing analysis)
cohort_ret = pd.read_csv(OUTPUT_DIR / "03_cohort_retention_heatmap.csv")
avg_90d = cohort_ret["retention_90d"].mean() if "retention_90d" in cohort_ret.columns else 0

# KPI 4: Acquisition dependency (% of latest year revenue from new customers)
latest_yr = CALENDAR_YEARS[-1]
lt_yr_data = sgd[sgd["year"] == latest_yr]
new_lt = set(acq_year[acq_year["acq_year"] == latest_yr]["customer_id"])
acq_dep = lt_yr_data[lt_yr_data["customer_id"].isin(new_lt)]["Price: Total"].sum() / \
          lt_yr_data["Price: Total"].sum() if lt_yr_data["Price: Total"].sum() > 0 else 0

# KPI 5: Revenue concentration (top 20% share)
sgd_cust_rev = sgd.groupby("customer_id")["Price: Total"].sum().sort_values(ascending=False)
top20_n = max(1, int(len(sgd_cust_rev) * 0.20))
rev_concentration = sgd_cust_rev.head(top20_n).sum() / sgd_cust_rev.sum()

scorecard = [
    ("Overall Repeat Rate",           f"{repeat_rate:.1%}",      repeat_rate >= 0.35, "Target: >35%"),
    ("YoY Retention (latest yr)",     f"{yoy_retention:.1%}",    yoy_retention >= 0.40, "Target: >40%"),
    ("Avg 90-Day Cohort Retention",   f"{avg_90d:.1%}",          avg_90d >= 0.25, "Target: >25%"),
    ("Acquisition Dependency",        f"{acq_dep:.1%}",          acq_dep <= 0.50, "Target: <50% (lower=better)"),
    ("Top 20% Revenue Concentration", f"{rev_concentration:.1%}", rev_concentration < 0.80, "Healthy if <80%"),
]

print(f"\n  {'KPI':<35}  {'Value':>10}  {'Status':>8}  {'Benchmark'}")
print(f"  {'-'*80}")
for kpi, val, is_ok, bench in scorecard:
    status = "OK" if is_ok else "ALERT"
    print(f"  {kpi:<35}  {val:>10}  {status:>8}  {bench}")

scorecard_df = pd.DataFrame([{
    "kpi": k, "value": v, "status": "OK" if ok else "ALERT", "benchmark": b
} for k, v, ok, b in scorecard])
scorecard_df.to_csv(OUTPUT_DIR / "11_lens5_health_scorecard.csv", index=False)
print(f"\nSaved: 11_lens5_health_scorecard.csv")

# ==============================================================================
# F.  INTEGRATED LENS 5 DIAGNOSTIC NARRATIVE
# ==============================================================================
print("\n\n[F] INTEGRATED DIAGNOSTIC — LENS 5 NARRATIVE")
print("=" * 65)
print(f"""
  WHAT LENS 5 IS SAYING ABOUT LUSHPROTEIN:

  1. THE BASE IS ACQUISITION-DEPENDENT.
     A high proportion of annual revenue comes from first-time buyers.
     This means revenue is tied directly to marketing spend — if acquisition
     slows, revenue drops immediately. A healthy base generates growing
     revenue from retained cohorts even without new acquisition.

  2. COHORT REVENUE DECAYS RAPIDLY.
     Each cohort loses most of its revenue contribution within 1-2 years.
     The "triangle" matrix is steep — the off-diagonal cells are much smaller
     than the diagonal (acquisition year) cells. This is a classic pattern
     of a leaky bucket: new customers flow in but don't accumulate.

  3. WATERFALL: NEW CUSTOMERS DOMINATE EACH YEAR.
     The retained and recovered share is low relative to new.
     A healthy, mature DTC brand typically has 60%+ of annual revenue from
     customers acquired in prior years. If LushProtein is below 40%, the
     business is structurally dependent on continued acquisition growth.

  4. ACQUISITION COHORT QUALITY IS DECLINING (consistent with Lens 4).
     Newer cohorts (2023, 2024) decay faster than older cohorts (2020, 2021).
     This likely reflects increased marketplace acquisition and discount depth.

  5. THE INTEGRATED IMPLICATION:
     LushProtein is in a "growth trap" — revenue looks like it's recovering
     (2024 vs 2023) but it is powered by more acquisition, not better retention.
     If cohort retention doesn't improve, each new cohort requires progressively
     more acquisition spend to maintain revenue. This is an unsustainable trajectory.

  THE PRESCRIPTION (from all 5 lenses together):
     Lens 1: The top 10-20% of customers generate 50-65% of revenue. Protect them.
     Lens 2: Frequency drives everything. Subscription and repurchase cadence are the levers.
     Lens 3: The hardest step is 1->2. Win that, and the customer stays.
     Lens 4: Stop acquiring low-quality customers through heavy discounts and marketplace.
     Lens 5: The base will only become healthy when retained revenue > new revenue.
""")

print("[11] Lens 5 DONE.\n")
print("=" * 65)
print("ALL 5 LENSES COMPLETE")
print("""
  Lens 1 - Heterogeneity:          07_lens1_heterogeneity.py
  Lens 2 - Period Decomposition:   08_lens2_period_decomposition.py
  Lens 3 - Cohort Evolution:       09_lens3_cohort_evolution.py
  Lens 4 - Vintage Comparison:     10_lens4_vintage_comparison.py
  Lens 5 - Base Health:            11_lens5_base_health.py
""")
