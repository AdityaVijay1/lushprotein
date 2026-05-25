"""
12_finals_deep_dive.py
Finals deliverables: LTV by cohort/channel, on-site vs off-site discounts,
loyal-customer profiling, VTD decile x product breadth, business value scenarios,
SKU-level margin view.

DATA DROPS APPLIED (Option B — finals layer only; base parquet unchanged):
  DQ-02  Zero-revenue + zero-discount orders (−336)
  DQ-03  100%-discount / free-fulfilment orders (−1,281)
  DQ-04  Wholesale-tagged OR Price: Total > S$5,000 (−78)

LUSHPROTEIN FEEDBACK FILTERS (applied to finals_eligible cohort):
  LP-F01  Exclude better-whey-protein-elite buyers (bulk distortion)
  LP-F02  Exclude customers acquired in July or November (promo months)
  LP-F03  Analysis window: 2022-01-01 onwards
  LP-F04  Exclude customers whose first order was 51%+ discounted (acquisition experiments)

Run after: python EDA/run_eda.py  (or at least 01_load_and_merge.py)
"""
import warnings
warnings.filterwarnings("ignore")

import importlib.util
import numpy as np
import pandas as pd
from pathlib import Path

def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", Path(__file__).parent / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg = _load_config()
OUT = cfg.OUTPUT_DIR
BASE = cfg.BASE_DIR
ORDER_FILES = cfg.ORDER_FILES
MARGIN_RATE = 0.40
EXCLUDE_HANDLE = "better-whey-protein-elite"
EXCLUDE_MONTHS = {7, 11}
ANALYSIS_START = pd.Timestamp("2022-01-01", tz="Asia/Singapore")

print("=" * 70)
print("FINALS DEEP DIVE — 12_finals_deep_dive.py")
print("=" * 70)

# ── Load cached tables ───────────────────────────────────────────────────────
orders = pd.read_parquet(OUT / "orders.parquet")
lines  = pd.read_parquet(OUT / "lines.parquet")
cust   = pd.read_parquet(OUT / "customers.parquet")
products = pd.read_parquet(OUT / "products.parquet")

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
cust["first_order_date"] = pd.to_datetime(cust["first_order_date"], utc=True)
cust["acq_year"] = cust["first_order_date"].dt.year
cust["acq_month"] = cust["first_order_date"].dt.month

# ── Enrich orders with Source (POS vs web) from raw exports ────────────────
print("\n[1] Loading Source column from raw order files for POS analysis...")
src_chunks = []
for f in ORDER_FILES:
    if f.stat().st_size < 1000:
        continue
    df = pd.read_excel(f, usecols=["ID", "Top Row", "Source"], dtype=str, engine="openpyxl")
    df = df[df["Top Row"] == "1"].rename(columns={"ID": "order_id"})
    src_chunks.append(df[["order_id", "Source"]])
src_df = pd.concat(src_chunks, ignore_index=True).drop_duplicates("order_id")
src_df["order_id"] = src_df["order_id"].astype(str)
orders = orders.merge(src_df, on="order_id", how="left")
orders["order_source"] = orders["Source"].fillna("unknown").str.lower()
orders["is_pos"] = orders["order_source"] == "pos"
orders["is_web"] = orders["order_source"] == "web"
print(f"  Orders with Source: {orders['Source'].notna().sum():,} / {len(orders):,}")
print(f"  POS orders: {orders['is_pos'].sum():,} | Web orders: {orders['is_web'].sum():,}")

# ══════════════════════════════════════════════════════════════════════════════
# OPTION B — FINALS-LAYER DATA QUALITY DROPS
# Base parquet (27,350 orders, 13,780 customers) is unchanged.
# Midterm scripts 01–11 are unaffected. Drops applied here only.
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1b] Finals-layer data quality drops (Option B — base parquet unchanged)...")
_n_start = len(orders)

_rev  = pd.to_numeric(orders["Price: Total"],          errors="coerce").fillna(0)
_disc = pd.to_numeric(orders["Price: Total Discount"], errors="coerce").fillna(0)

# DQ-02: Zero-revenue + zero-discount orders
# 336 export artifacts / system-placeholder events (2021 spike: 173 orders).
# Inflate order counts; contribute S$0 revenue. LP confirmed safe to drop.
_dq02 = (_rev == 0) & (_disc == 0)
print(f"  DQ-02 (zero rev + zero disc):             {_dq02.sum():>5,} orders dropped")

# DQ-03: 100%-discounted orders (free fulfilments)
# 1,281 real shipments (referral rewards, PR, subscription gifts) at zero revenue.
# Distort discount-rate metrics; inflate repeat counts. LP confirmed safe to drop.
_dq03 = (_rev == 0) & (_disc > 0)
print(f"  DQ-03 (100%-discount / free fulfilment):  {_dq03.sum():>5,} orders dropped")

# DQ-04: Wholesale / bulk outlier orders
# Drop if tagged 'wholesale-sale' OR Price: Total > S$5,000.
# Excludes B2B/reseller orders that distort consumer LTV and AOV. LP confirmed.
_dq04_tag = orders["Tags"].fillna("").str.lower().str.contains("wholesale")
_dq04_rev = _rev > 5000
_dq04 = _dq04_tag | _dq04_rev
print(f"  DQ-04 (wholesale-tag OR > S$5,000):       {_dq04.sum():>5,} orders dropped")

_drop_mask = _dq02 | _dq03 | _dq04
orders = orders[~_drop_mask].copy()
lines  = lines[lines["order_id"].isin(set(orders["order_id"]))].copy()
print(f"  {'-' * 58}")
print(f"  Unique dropped: {_drop_mask.sum():,}  |  Retained: {len(orders):,} / {_n_start:,} orders")

# Rebuild per-customer stats from the cleaned order set so that
# total_orders / total_revenue / is_repeat reflect only retained orders.
orders["_rev_sgd"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
_cust_rebuild = (
    orders.groupby("customer_id")
    .agg(_total_orders=("order_id", "count"), _total_revenue=("_rev_sgd", "sum"))
    .reset_index()
)
orders.drop(columns=["_rev_sgd"], inplace=True)
cust = cust.merge(_cust_rebuild, on="customer_id", how="left")
cust["total_orders"]  = cust["_total_orders"].fillna(0).astype(int)
cust["total_revenue"] = cust["_total_revenue"].fillna(0)
cust["is_repeat"]     = cust["total_orders"] >= 2
cust.drop(columns=["_total_orders", "_total_revenue"], inplace=True)
print(f"  Customer stats rebuilt from clean orders.")
print(f"  Customers with 0 retained orders (all orders dropped): {(cust['total_orders'] == 0).sum():,}")

# ── First-order discount depth (used for LP-F04 exclusion flag) ───────────
first_ord = orders.sort_values("order_date").groupby("customer_id").first().reset_index()
first_ord["order_id"] = first_ord["order_id"].astype(str)
first_ord["first_rev"] = pd.to_numeric(first_ord["Price: Total"], errors="coerce").fillna(0)
first_ord["first_disc"] = pd.to_numeric(first_ord["Price: Total Discount"], errors="coerce").fillna(0)
first_ord["first_disc_depth"] = np.where(
    (first_ord["first_rev"] + first_ord["first_disc"]) > 0,
    first_ord["first_disc"] / (first_ord["first_rev"] + first_ord["first_disc"]),
    0,
)
first_ord["first_disc_bin"] = pd.cut(
    first_ord["first_disc_depth"],
    bins=[-0.001, 0.001, 0.05, 0.10, 0.20, 0.30, 0.50, 1.01],
    labels=["0%", "1-5%", "6-10%", "11-20%", "21-30%", "31-50%", "51%+"],
)
first_ord["first_order_source"] = first_ord["Source"].fillna("unknown").str.lower()
cust = cust.merge(
    first_ord[["customer_id", "first_disc_depth", "first_disc_bin", "first_order_source"]],
    on="customer_id", how="left",
)
cust["first_order_pos"] = cust["first_order_source"] == "pos"

# ══════════════════════════════════════════════════════════════════════════════
# LUSHPROTEIN FEEDBACK — APPLIED ANALYSIS FILTERS (finals cohort only)
# These are analytical scope decisions requested by LushProtein, not data errors.
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Building LushProtein feedback filters (finals cohort)...")

# LP-F01: Exclude better-whey-protein-elite buyers
# LP confirmed this is a bulk/unsustainable product not representative of
# the core consumer base. ~200 customers affected.
elite_customers = set(
    lines[lines["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)]["customer_id"]
)
cust["exclude_elite_buyer"] = cust["customer_id"].isin(elite_customers)

# LP-F04: Exclude customers whose first order was 51%+ discounted
# LP confirmed these are acquisition/gifting experiments, not organic buyers.
cust["exclude_51pct"] = cust["first_disc_bin"].astype(str) == "51%+"

# LP-F02: Exclude customers acquired in July or November (promo months)
# July = LP birthday month; November = Black Friday/Cyber Monday.
# Promo-month cohorts have atypical discount intensity that distorts
# LTV and repeat-rate benchmarks. LP confirmed to exclude.
cust["exclude_promo_month"] = cust["acq_month"].isin(EXCLUDE_MONTHS)

# LP-F03: Restrict analysis window to 2022-01-01 onwards
# Pre-2022 = market acquisition / product experimentation phase per LP.
# Post-2022 portfolio and pricing strategy is the stable reference period.
cust["finals_eligible"] = (
    (cust["first_order_date"] >= ANALYSIS_START)   # LP-F03
    & ~cust["exclude_elite_buyer"]                  # LP-F01
    & ~cust["exclude_51pct"]                        # LP-F04
    & ~cust["exclude_promo_month"]                  # LP-F02
)
print(f"  LP-F01  Elite-product buyers excluded:           {cust['exclude_elite_buyer'].sum():,}")
print(f"  LP-F02  Acquired Jul/Nov excluded:               {cust['exclude_promo_month'].sum():,}")
print(f"  LP-F03  Pre-2022 acquisitions excluded:          {(cust['first_order_date'] < ANALYSIS_START).sum():,}")
print(f"  LP-F04  First order 51%+ discount excluded:      {cust['exclude_51pct'].sum():,}")
print(f"  Finals-eligible customers (all LP filters):      {cust['finals_eligible'].sum():,}")

# ── LTV DEFINITION ───────────────────────────────────────────────────────────
# LTV = sum(Price: Total) per customer in SGD (FX applied at load in 01_load_and_merge)
# Optional: gross_profit_ltv = revenue * margin_rate (proxy when COGS missing)

# A) LTV by acquisition cohort year
ltv_cohort = (
    cust.groupby("acq_year")
    .agg(
        customers=("customer_id", "count"),
        avg_ltv=("total_revenue", "mean"),
        median_ltv=("total_revenue", "median"),
        repeat_rate=("is_repeat", "mean"),
        avg_orders=("total_orders", "mean"),
        pct_subscribed=("ever_subscribed", "mean"),
    )
    .reset_index()
)
ltv_cohort["avg_gross_profit_ltv"] = ltv_cohort["avg_ltv"] * MARGIN_RATE
ltv_cohort.to_csv(OUT / "12_ltv_by_acq_cohort.csv", index=False)

ltv_cohort_f = cust[cust["finals_eligible"]].groupby("acq_year").agg(
    customers=("customer_id", "count"),
    avg_ltv=("total_revenue", "mean"),
    repeat_rate=("is_repeat", "mean"),
).reset_index()
ltv_cohort_f.to_csv(OUT / "12_ltv_by_acq_cohort_finals_filtered.csv", index=False)

# B) LTV by first channel
ltv_channel = (
    cust.groupby("first_channel")
    .agg(
        customers=("customer_id", "count"),
        repeaters=("is_repeat", "sum"),
        avg_ltv=("total_revenue", "mean"),
        median_ltv=("total_revenue", "median"),
        avg_orders=("total_orders", "mean"),
        pct_subscribed=("ever_subscribed", "mean"),
    )
    .reset_index()
)
ltv_channel["repeat_rate"] = ltv_channel["repeaters"] / ltv_channel["customers"]
ltv_channel["avg_gross_profit_ltv"] = ltv_channel["avg_ltv"] * MARGIN_RATE
ltv_channel.to_csv(OUT / "12_ltv_by_first_channel.csv", index=False)

# C) LTV by cohort × channel (cross-tab)
ltv_cohort_channel = (
    cust.groupby(["acq_year", "first_channel"])
    .agg(customers=("customer_id", "count"), avg_ltv=("total_revenue", "mean"), repeat_rate=("is_repeat", "mean"))
    .reset_index()
)
ltv_cohort_channel.to_csv(OUT / "12_ltv_by_cohort_channel.csv", index=False)

# D) Acquisition rate by year
acq_by_year = cust.groupby("acq_year").size().reset_index(name="new_customers")
acq_by_year["pct_of_base"] = acq_by_year["new_customers"] / len(cust)
acq_by_year.to_csv(OUT / "12_acquisition_by_year.csv", index=False)

# ── On-site (POS) vs off-site (web) discount comparison ────────────────────
print("\n[3] On-site (POS) vs off-site (web) discount analysis...")
pos_orders = orders[orders["is_pos"]].copy()
web_orders = orders[orders["is_web"]].copy()

def _channel_stats(df, label):
    rev = pd.to_numeric(df["Price: Total"], errors="coerce").fillna(0)
    disc = pd.to_numeric(df["Price: Total Discount"], errors="coerce").fillna(0)
    return {
        "channel": label,
        "orders": len(df),
        "unique_customers": df["customer_id"].nunique(),
        "pct_discounted": (disc > 0).mean(),
        "avg_order_value": rev.mean(),
        "avg_discount": disc.mean(),
        "total_revenue": rev.sum(),
        "total_discount": disc.sum(),
    }

pos_web = pd.DataFrame([
    _channel_stats(pos_orders, "POS (on-site)"),
    _channel_stats(web_orders, "Web (off-site)"),
])
pos_web.to_csv(OUT / "12_pos_vs_web_orders.csv", index=False)

# Customer outcomes: first order via POS vs web
first_src = first_ord[["customer_id", "order_id", "first_order_source"]].copy()
first_src["order_source"] = first_src["first_order_source"]
pos_custs = set(first_src[first_src["order_source"] == "pos"]["customer_id"])
web_custs = set(first_src[first_src["order_source"] == "web"]["customer_id"])
cust["first_acq_pos"] = cust["customer_id"].isin(pos_custs)
cust["first_acq_web"] = cust["customer_id"].isin(web_custs)

def _cust_segment_stats(df, label):
    return {
        "acquisition_source": label,
        "customers": len(df),
        "repeat_rate": df["is_repeat"].mean(),
        "avg_ltv_sgd": df["total_revenue"].mean(),
        "median_ltv_sgd": df["total_revenue"].median(),
        "pct_subscribed": df["ever_subscribed"].mean(),
        "avg_orders": df["total_orders"].mean(),
    }

pos_web_cust = pd.DataFrame([
    _cust_segment_stats(cust[cust["first_acq_pos"]], "POS first-order"),
    _cust_segment_stats(cust[cust["first_acq_web"]], "Web first-order"),
])
pos_web_cust.to_csv(OUT / "12_pos_vs_web_customer_outcomes.csv", index=False)

# ── Loyal customer profile (Champions proxy: top VTD decile OR repeat + high LTV) ─
print("\n[4] Loyal customer profiling...")
cust["profit_proxy"] = cust["total_revenue"] * MARGIN_RATE
cust["vtd_decile"] = pd.qcut(cust["total_revenue"].rank(method="first"), 10, labels=[f"D{i}" for i in range(1, 11)])

# Product breadth per customer (unique handles, excl elite)
lines_clean = lines[~lines["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)].copy()
breadth = (
    lines_clean.groupby("customer_id")["Line: Product Handle"]
    .nunique().reset_index(name="unique_handles")
)
lines_clean["flavor_sku"] = (
    lines_clean["Line: Product Handle"].fillna("unknown")
    + " | "
    + lines_clean["Line: Variant Title"].fillna("Default")
)
flavor_breadth = lines_clean.groupby("customer_id")["flavor_sku"].nunique().reset_index(name="unique_flavor_skus")
cust = cust.merge(breadth, on="customer_id", how="left").merge(flavor_breadth, on="customer_id", how="left")
cust["unique_handles"] = cust["unique_handles"].fillna(0).astype(int)
cust["unique_flavor_skus"] = cust["unique_flavor_skus"].fillna(0).astype(int)

loyal = cust[(cust["is_repeat"]) & (cust["total_orders"] >= 3)].copy()
loyal_profile = pd.DataFrame({
    "metric": [
        "count", "avg_ltv", "median_ltv", "avg_orders", "median_days_to_2nd",
        "pct_subscribed", "avg_unique_handles", "avg_unique_flavor_skus",
        "pct_first_channel_direct", "pct_first_channel_subscription", "pct_first_channel_marketplace",
        "pct_first_order_full_price",
    ],
    "loyal_repeaters_3plus_orders": [
        len(loyal),
        loyal["total_revenue"].mean(),
        loyal["total_revenue"].median(),
        loyal["total_orders"].mean(),
        loyal["days_to_second"].median(),
        loyal["ever_subscribed"].mean(),
        loyal["unique_handles"].mean(),
        loyal["unique_flavor_skus"].mean(),
        (loyal["first_channel"] == "Direct / Organic").mean(),
        (loyal["first_channel"] == "Subscription").mean(),
        (loyal["first_channel"] == "Marketplace").mean(),
        (loyal["first_disc_bin"].astype(str) == "0%").mean(),
    ],
})
loyal_profile.to_csv(OUT / "12_loyal_customer_profile.csv", index=False)

# Compare loyal vs one-and-done — full factor table written in section 11b

# ── VTD decile × cumulative product categories ─────────────────────────────
print("\n[5] VTD decile × product breadth...")
vtd_breadth = (
    cust.groupby("vtd_decile")
    .agg(
        customers=("customer_id", "count"),
        avg_ltv=("total_revenue", "mean"),
        avg_unique_handles=("unique_handles", "mean"),
        avg_unique_flavors=("unique_flavor_skus", "mean"),
        pct_repeat=("is_repeat", "mean"),
        pct_multi_product=("unique_handles", lambda s: (s >= 2).mean()),
        pct_3plus_products=("unique_handles", lambda s: (s >= 3).mean()),
    )
    .reset_index()
)
vtd_breadth["cum_pct_customers"] = vtd_breadth["customers"].cumsum() / vtd_breadth["customers"].sum()
vtd_breadth["cum_pct_ltv"] = (
    (vtd_breadth["avg_ltv"] * vtd_breadth["customers"]).cumsum()
    / (vtd_breadth["avg_ltv"] * vtd_breadth["customers"]).sum()
)
vtd_breadth.to_csv(OUT / "12_vtd_decile_cumulative_categories.csv", index=False)

# ── SKU / flavor level (2022+, finals filters) ─────────────────────────────
print("\n[6] SKU-level analysis...")
lines_f = lines_clean.merge(cust[["customer_id", "finals_eligible"]], on="customer_id")
lines_f = lines_f[lines_f["finals_eligible"]]
lines_f["order_date"] = pd.to_datetime(lines_f["order_date"], utc=True)
lines_f = lines_f[lines_f["order_date"] >= ANALYSIS_START]
lines_f = lines_f[~lines_f["order_date"].dt.month.isin(EXCLUDE_MONTHS)]

sku_stats = (
    lines_f.groupby(["Line: Product Handle", "Line: Variant Title", "Line: SKU"])
    .agg(
        line_items=("order_id", "count"),
        unique_customers=("customer_id", "nunique"),
        total_revenue=("Line: Total", "sum"),
    )
    .reset_index()
    .sort_values("total_revenue", ascending=False)
)
sku_stats.to_csv(OUT / "12_sku_flavor_revenue_2022plus.csv", index=False)

# Margin join from product master
pm = products.copy()
pm = pm.rename(columns={"Variant SKU": "Line: SKU", "Cost per item": "unit_cost"})
sku_margin = sku_stats.merge(pm[["Line: SKU", "unit_cost", "Price / Singapore", "Status"]], on="Line: SKU", how="left")
sku_margin["unit_cost"] = pd.to_numeric(sku_margin["unit_cost"], errors="coerce")
sku_margin["has_cost"] = sku_margin["unit_cost"].notna()
sku_margin.to_csv(OUT / "12_sku_margin_coverage.csv", index=False)

# Discontinued / archived products in master not in recent orders
active_handles = set(lines_f["Line: Product Handle"].dropna())
archived = products[products["Status"].isin(["archived", "draft"])]
disc = archived[~archived["Handle"].isin(active_handles)][["Handle", "Title", "Variant SKU", "Status"]].drop_duplicates()
disc.to_csv(OUT / "12_discontinued_products_not_in_recent_orders.csv", index=False)

# ── Business value scenarios ─────────────────────────────────────────────────
print("\n[7] Business value scenarios...")
eligible = cust[cust["finals_eligible"]]
one_prod = eligible[eligible["unique_handles"] == 1]
at_risk_no_second = eligible[(~eligible["is_repeat"]) & (eligible["acq_year"].isin([2024, 2025]))]

cross = pd.read_csv(OUT / "04_cross_product_ltv.csv")
ltv_1 = cross[cross["category_label"] == "1 product"]["avg_ltv"].iloc[0]
ltv_2 = cross[cross["category_label"] == "2 products"]["avg_ltv"].iloc[0]
ltv_3 = cross[cross["category_label"] == "3 products"]["avg_ltv"].iloc[0]

sub_ltv = cust[cust["ever_subscribed"]]["total_revenue"].mean()
nonsub_ltv = cust[~cust["ever_subscribed"]]["total_revenue"].mean()
sub_uplift = sub_ltv - nonsub_ltv

scenarios = []

# Cross-sell
for label, pct, target_ltv in [
    ("Cross-sell: 10% of 1-product → 2-product (conservative)", 0.10, ltv_2),
    ("Cross-sell: 10% of 1-product → 2-product (potential)", 0.10, ltv_2),
    ("Cross-sell: 5% of 1-product → 3-product (conservative)", 0.05, ltv_3),
]:
    pool = int(one_prod.shape[0]) if len(one_prod) else int(cross[cross["category_label"] == "1 product"]["customers"].iloc[0])
    n_conv = pool * (0.05 if "5%" in label else 0.10)
    uplift = n_conv * (target_ltv - ltv_1)
    scenarios.append({"opportunity": label, "pool": pool, "conversion_rate": 0.05 if "5%" in label else 0.10,
                      "uplift_per_customer": target_ltv - ltv_1, "gross_ltv_uplift_sgd": uplift,
                      "gross_profit_uplift_sgd": uplift * MARGIN_RATE})

# Retention win-back 2024-25 no second
pool = len(at_risk_no_second) if len(at_risk_no_second) else 4100
for label, rate in [("Retention win-back (conservative 10%)", 0.10), ("Retention win-back (potential 15%)", 0.15)]:
    avg_return_ltv = eligible[eligible["is_repeat"]]["total_revenue"].mean() if eligible["is_repeat"].any() else 356
    scenarios.append({"opportunity": label, "pool": pool, "conversion_rate": rate,
                      "uplift_per_customer": avg_return_ltv, "gross_ltv_uplift_sgd": pool * rate * avg_return_ltv,
                      "gross_profit_uplift_sgd": pool * rate * avg_return_ltv * MARGIN_RATE})

# Subscription conversion
nonsub = int((~cust["ever_subscribed"]).sum())
for label, rate in [("Sub conversion (conservative 5% of non-subs)", 0.05), ("Sub conversion (potential 12.5% of non-subs)", 0.125)]:
    scenarios.append({"opportunity": label, "pool": nonsub, "conversion_rate": rate,
                      "uplift_per_customer": sub_uplift, "gross_ltv_uplift_sgd": nonsub * rate * sub_uplift,
                      "gross_profit_uplift_sgd": nonsub * rate * sub_uplift * MARGIN_RATE})

# Marketplace redirect
mkt = cust[cust["first_channel"] == "Marketplace"]
direct_ltv = cust[cust["first_channel"] == "Direct / Organic"]["total_revenue"].mean()
mkt_ltv = mkt["total_revenue"].mean()
gap = direct_ltv - mkt_ltv
for label, rate in [("Marketplace LTV gap (conservative 5% improved)", 0.05), ("Marketplace LTV gap (potential 15% improved)", 0.15)]:
    scenarios.append({"opportunity": label, "pool": len(mkt), "conversion_rate": rate,
                      "uplift_per_customer": gap, "gross_ltv_uplift_sgd": len(mkt) * rate * gap,
                      "gross_profit_uplift_sgd": len(mkt) * rate * gap * MARGIN_RATE})

pd.DataFrame(scenarios).to_csv(OUT / "12_business_value_scenarios.csv", index=False)

# ── 8. First-purchase flavor/SKU → loyalty outcomes ───────────────────────
print("\n[8] First-purchase flavor/SKU loyalty...")
first_lines = (
    lines_clean.sort_values("order_date")
    .groupby("customer_id")
    .first()
    .reset_index()[["customer_id", "Line: Product Handle", "Line: Variant Title", "Line: SKU", "flavor_sku"]]
)
first_lines = first_lines.rename(columns={
    "Line: Product Handle": "first_handle",
    "Line: Variant Title": "first_variant",
    "Line: SKU": "first_sku",
})
flavor_loyalty = first_lines.merge(
    cust[["customer_id", "total_revenue", "total_orders", "is_repeat", "ever_subscribed", "finals_eligible"]],
    on="customer_id",
)
flavor_stats = (
    flavor_loyalty.groupby(["first_handle", "first_variant", "first_sku", "flavor_sku"])
    .agg(
        customers=("customer_id", "count"),
        repeat_rate=("is_repeat", "mean"),
        avg_ltv=("total_revenue", "mean"),
        avg_orders=("total_orders", "mean"),
        pct_subscribed=("ever_subscribed", "mean"),
    )
    .reset_index()
    .sort_values("customers", ascending=False)
)
flavor_stats.to_csv(OUT / "12_first_flavor_loyalty_all.csv", index=False)
flavor_stats[flavor_stats["customers"] >= 30].sort_values("repeat_rate", ascending=False).to_csv(
    OUT / "12_first_flavor_loyalty_min30.csv", index=False
)

# Finals-filtered flavor loyalty
flavor_stats_f = (
    flavor_loyalty[flavor_loyalty["finals_eligible"]]
    .groupby(["first_handle", "first_variant", "first_sku", "flavor_sku"])
    .agg(customers=("customer_id", "count"), repeat_rate=("is_repeat", "mean"), avg_ltv=("total_revenue", "mean"))
    .reset_index()
    .sort_values("customers", ascending=False)
)
flavor_stats_f.to_csv(OUT / "12_first_flavor_loyalty_2022plus_filtered.csv", index=False)

# ── 9. Discontinued / draft products — full historical sales ───────────────
print("\n[9] Discontinued & draft product history...")
inactive_handles = set(products[products["Status"].isin(["archived", "draft"])]["Handle"])
disc_hist = (
    lines_clean[lines_clean["Line: Product Handle"].isin(inactive_handles)]
    .groupby(["Line: Product Handle", "Line: Variant Title", "Line: SKU"])
    .agg(
        total_orders=("order_id", "nunique"),
        unique_customers=("customer_id", "nunique"),
        total_revenue=("Line: Total", "sum"),
        first_sale=("order_date", "min"),
        last_sale=("order_date", "max"),
    )
    .reset_index()
)
disc_hist = disc_hist.merge(
    products[["Handle", "Status"]].drop_duplicates("Handle").rename(columns={"Handle": "Line: Product Handle"}),
    on="Line: Product Handle", how="left",
)
disc_hist = disc_hist.sort_values("total_revenue", ascending=False)
disc_hist.to_csv(OUT / "12_discontinued_products_history.csv", index=False)

# ── 10. Reorder interval by SKU (repeat buyers, same SKU) ───────────────────
print("\n[10] Reorder interval by SKU...")
lines_clean["order_date"] = pd.to_datetime(lines_clean["order_date"], utc=True)
lines_clean = lines_clean[lines_clean["order_date"] >= ANALYSIS_START]
lines_clean = lines_clean[~lines_clean["order_date"].dt.month.isin(EXCLUDE_MONTHS)]
lines_clean["flavor_label"] = (
    lines_clean["Line: Product Handle"].fillna("") + " / "
    + lines_clean["Line: Variant Title"].fillna("Default")
)

def _median_reorder_gap(g):
    dates = g.sort_values("order_date")["order_date"].drop_duplicates()
    if len(dates) < 2:
        return np.nan
    gaps = dates.diff().dt.days.dropna()
    return gaps.median() if len(gaps) else np.nan

reorder_rows = []
for (sku, label), grp in lines_clean.groupby(["Line: SKU", "flavor_label"]):
    cust_gaps = grp.groupby("customer_id", group_keys=False).apply(_median_reorder_gap, include_groups=False)
    cust_gaps = cust_gaps.dropna()
    if len(cust_gaps) < 5:
        continue
    reorder_rows.append({
        "Line: SKU": sku,
        "flavor_label": label,
        "repeat_buyers": len(cust_gaps),
        "median_reorder_days": cust_gaps.median(),
        "mean_reorder_days": cust_gaps.mean(),
    })
reorder_df = pd.DataFrame(reorder_rows).sort_values("repeat_buyers", ascending=False)
reorder_df.to_csv(OUT / "12_reorder_interval_by_sku.csv", index=False)

# ── 11. Loyal repeater targeting criteria ───────────────────────────────────
print("\n[11] Loyal repeater targeting criteria...")
cust["loyal_repeater"] = cust["is_repeat"] & (cust["total_orders"] >= 3)
cust["target_tier"] = np.select(
    [
        cust["loyal_repeater"] & cust["ever_subscribed"],
        cust["loyal_repeater"] & ~cust["ever_subscribed"],
        cust["is_repeat"] & (cust["total_orders"] == 2),
        cust["total_orders"] == 1,
    ],
    ["Tier 1: Loyal + Subscribed", "Tier 2: Loyal Non-Sub", "Tier 3: 2-order", "Tier 4: One-and-done"],
    default="Other",
)
target_summary = (
    cust.groupby("target_tier")
    .agg(customers=("customer_id", "count"), avg_ltv=("total_revenue", "mean"), avg_orders=("total_orders", "mean"))
    .reset_index()
    .sort_values("avg_ltv", ascending=False)
)
target_summary.to_csv(OUT / "12_loyal_repeater_target_tiers.csv", index=False)

# ── 11b. What makes loyal repeaters come back? (loyalty drivers) ─────────────
print("\n[11b] Loyal repeater loyalty drivers...")
BASELINE_LOYAL = cust["loyal_repeater"].mean()

cust["returned_within_60d"] = cust["days_to_second"].le(60)
cust["has_2plus_products"] = cust["unique_handles"] >= 2
cust["has_3plus_products"] = cust["unique_handles"] >= 3
cust["first_order_full_price"] = cust["first_disc_bin"].astype(str) == "0%"
cust["first_order_web"] = ~cust["first_order_pos"].fillna(True)

loyal = cust[cust["loyal_repeater"]].copy()
one_done = cust[cust["total_orders"] == 1].copy()
two_order = cust[cust["is_repeat"] & (cust["total_orders"] == 2)].copy()

def _driver_compare(name, loyal_mask, one_done_mask):
    lv = loyal_mask(loyal).mean() if len(loyal) else np.nan
    ov = one_done_mask(one_done).mean() if len(one_done) else np.nan
    return {
        "factor": name,
        "loyal_pct": lv,
        "one_and_done_pct": ov,
        "gap_pp": lv - ov,
        "lift_vs_one_and_done": lv / ov if ov and ov > 0 else np.nan,
        "lift_vs_baseline": lv / BASELINE_LOYAL if BASELINE_LOYAL else np.nan,
    }

behavioral_drivers = pd.DataFrame([
    _driver_compare("Ever subscribed", lambda s: s["ever_subscribed"], lambda s: s["ever_subscribed"]),
    _driver_compare("First order full-price (0% discount)", lambda s: s["first_order_full_price"], lambda s: s["first_order_full_price"]),
    _driver_compare("First order via web (not POS)", lambda s: s["first_order_web"], lambda s: s["first_order_web"]),
    _driver_compare("2+ unique product handles purchased", lambda s: s["has_2plus_products"], lambda s: s["has_2plus_products"]),
    _driver_compare("3+ unique product handles purchased", lambda s: s["has_3plus_products"], lambda s: s["has_3plus_products"]),
]).sort_values("gap_pp", ascending=False)
behavioral_drivers.to_csv(OUT / "12_loyal_repeater_behavioral_drivers.csv", index=False)

# Pathway marker (repeaters only — not comparable to one-and-done)
pathway = pd.DataFrame([{
    "factor": "Returned within 60 days of 1st order",
    "loyal_pct": loyal["returned_within_60d"].mean(),
    "two_order_pct": two_order["returned_within_60d"].mean(),
    "loyal_median_days_to_2nd": loyal["days_to_second"].median(),
    "two_order_median_days_to_2nd": two_order["days_to_second"].median(),
}])
pathway.to_csv(OUT / "12_loyal_repeater_return_pathway.csv", index=False)

# Continuous metrics — loyal vs one-and-done vs 2-order (speed to 2nd order)
speed_compare = pd.DataFrame({
    "segment": ["Loyal (3+ orders)", "2-order", "One-and-done"],
    "customers": [len(loyal), len(two_order), len(one_done)],
    "median_days_to_2nd": [
        loyal["days_to_second"].median(),
        two_order["days_to_second"].median(),
        np.nan,
    ],
    "pct_returned_within_60d": [
        loyal["returned_within_60d"].mean(),
        two_order["returned_within_60d"].mean(),
        np.nan,
    ],
    "avg_unique_handles": [loyal["unique_handles"].mean(), two_order["unique_handles"].mean(), one_done["unique_handles"].mean()],
    "avg_unique_flavor_skus": [loyal["unique_flavor_skus"].mean(), two_order["unique_flavor_skus"].mean(), one_done["unique_flavor_skus"].mean()],
})
speed_compare.to_csv(OUT / "12_loyal_repeater_speed_and_breadth.csv", index=False)

# Categorical: P(loyal repeater) by acquisition channel, first product, discount depth
cat_rows = []
for dim, label in [
    ("first_channel", "Acquisition channel"),
    ("first_product_cat", "First product category"),
    ("first_disc_bin", "First-order discount depth"),
]:
    grp = (
        cust.groupby(dim, observed=True)
        .agg(customers=("customer_id", "count"), loyal_rate=("loyal_repeater", "mean"))
        .reset_index()
    )
    grp["factor_type"] = label
    grp["factor_value"] = grp[dim].astype(str)
    grp["lift_vs_baseline"] = grp["loyal_rate"] / BASELINE_LOYAL
    cat_rows.append(grp[["factor_type", "factor_value", "customers", "loyal_rate", "lift_vs_baseline"]])
pd.concat(cat_rows, ignore_index=True).sort_values("loyal_rate", ascending=False).to_csv(
    OUT / "12_loyal_repeater_rate_by_factor.csv", index=False
)

# First-purchase SKU → P(loyal repeater)  (which entry products create loyalty?)
fl_loyal = flavor_loyalty.merge(cust[["customer_id", "loyal_repeater"]], on="customer_id")
sku_loyal_rate = (
    fl_loyal.groupby(["first_handle", "first_variant", "first_sku", "flavor_sku"])
    .agg(
        customers=("customer_id", "count"),
        loyal_rate=("loyal_repeater", "mean"),
        avg_ltv=("total_revenue", "mean"),
        avg_orders=("total_orders", "mean"),
        pct_subscribed=("ever_subscribed", "mean"),
    )
    .reset_index()
)
sku_loyal_rate["lift_vs_baseline"] = sku_loyal_rate["loyal_rate"] / BASELINE_LOYAL
sku_loyal_rate.to_csv(OUT / "12_loyal_rate_by_first_sku.csv", index=False)
sku_loyal_rate[sku_loyal_rate["customers"] >= 30].sort_values("loyal_rate", ascending=False).to_csv(
    OUT / "12_loyal_rate_by_first_sku_min30.csv", index=False
)

# Among loyal repeaters: which SKUs do they keep reordering? (all purchases, not just first)
loyal_ids = set(loyal["customer_id"])
loyal_lines = lines_clean[lines_clean["customer_id"].isin(loyal_ids)].copy()
loyal_lines["flavor_label"] = (
    loyal_lines["Line: Product Handle"].fillna("") + " / "
    + loyal_lines["Line: Variant Title"].fillna("Default")
)
loyal_reorder_skus = (
    loyal_lines.groupby(["Line: Product Handle", "Line: Variant Title", "Line: SKU", "flavor_label"])
    .agg(
        loyal_buyers=("customer_id", "nunique"),
        total_line_items=("order_id", "count"),
        total_revenue=("Line: Total", "sum"),
    )
    .reset_index()
)
loyal_reorder_skus["avg_purchases_per_loyal_buyer"] = (
    loyal_reorder_skus["total_line_items"] / loyal_reorder_skus["loyal_buyers"]
)
loyal_reorder_skus = loyal_reorder_skus.sort_values("loyal_buyers", ascending=False)
loyal_reorder_skus.to_csv(OUT / "12_loyal_repeater_reorder_skus.csv", index=False)

# Enriched loyal vs one-and-done comparison (all key factors in one table)
compare = pd.DataFrame({
    "segment": ["Loyal (3+ orders, repeat)", "One-and-done"],
    "customers": [len(loyal), len(one_done)],
    "avg_ltv": [loyal["total_revenue"].mean(), one_done["total_revenue"].mean()],
    "pct_subscribed": [loyal["ever_subscribed"].mean(), one_done["ever_subscribed"].mean()],
    "avg_unique_handles": [loyal["unique_handles"].mean(), one_done["unique_handles"].mean()],
    "avg_unique_flavor_skus": [loyal["unique_flavor_skus"].mean(), one_done["unique_flavor_skus"].mean()],
    "median_days_to_2nd": [loyal["days_to_second"].median(), np.nan],
    "pct_returned_within_60d": [loyal["returned_within_60d"].mean(), np.nan],
    "pct_direct_acq": [
        (loyal["first_channel"] == "Direct / Organic").mean(),
        (one_done["first_channel"] == "Direct / Organic").mean(),
    ],
    "pct_subscription_acq": [
        (loyal["first_channel"] == "Subscription").mean(),
        (one_done["first_channel"] == "Subscription").mean(),
    ],
    "pct_marketplace_acq": [
        (loyal["first_channel"] == "Marketplace").mean(),
        (one_done["first_channel"] == "Marketplace").mean(),
    ],
    "pct_full_price_first": [loyal["first_order_full_price"].mean(), one_done["first_order_full_price"].mean()],
    "pct_first_order_web": [loyal["first_order_web"].mean(), one_done["first_order_web"].mean()],
    "pct_2plus_products": [loyal["has_2plus_products"].mean(), one_done["has_2plus_products"].mean()],
})
compare.to_csv(OUT / "12_loyal_vs_one_and_done.csv", index=False)

loyal_first_flavors = (
    flavor_loyalty[flavor_loyalty["customer_id"].isin(cust[cust["loyal_repeater"]]["customer_id"])]
    .groupby("flavor_sku")
    .size()
    .reset_index(name="loyal_customers")
    .sort_values("loyal_customers", ascending=False)
    .head(20)
)
loyal_first_flavors.to_csv(OUT / "12_loyal_repeater_top_first_flavors.csv", index=False)

# Save enriched customer table (for report)
cust_out_cols = [
    "customer_id", "acq_year", "acq_month", "first_channel", "total_revenue", "total_orders",
    "is_repeat", "ever_subscribed", "first_disc_bin", "first_order_pos", "unique_handles",
    "unique_flavor_skus", "vtd_decile", "finals_eligible", "profit_proxy", "loyal_repeater", "target_tier",
]
cust[cust_out_cols].to_csv(OUT / "12_customer_enriched_finals.csv", index=False)

print("\nDone. Outputs saved to EDA/outputs/12_*.csv")
print("=" * 70)
