"""
12_finals_deep_dive.py
Finals deliverables: LTV by cohort/channel, on-site vs off-site discounts,
loyal-customer profiling, VTD decile x product breadth, business value scenarios,
SKU-level margin view, 2022+ filters (excl. Jul/Nov promo months, 51%+ depth,
better-whey-protein-elite).

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

# ── First-order discount depth (for 51%+ exclusion flag) ───────────────────
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

# ── Finals analysis cohort: 2022+, excl promo months, excl 51%+, excl elite ──
print("\n[2] Building finals analysis filters...")
elite_customers = set(
    lines[lines["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)]["customer_id"]
)
cust["exclude_elite_buyer"] = cust["customer_id"].isin(elite_customers)
cust["exclude_51pct"] = cust["first_disc_bin"].astype(str) == "51%+"
cust["exclude_promo_month"] = cust["acq_month"].isin(EXCLUDE_MONTHS)

cust["finals_eligible"] = (
    (cust["first_order_date"] >= ANALYSIS_START)
    & ~cust["exclude_elite_buyer"]
    & ~cust["exclude_51pct"]
    & ~cust["exclude_promo_month"]
)
print(f"  Elite-product buyers (excluded): {cust['exclude_elite_buyer'].sum():,}")
print(f"  First order 51%+ depth (excluded): {cust['exclude_51pct'].sum():,}")
print(f"  Acquired Jul/Nov (excluded): {cust['exclude_promo_month'].sum():,}")
print(f"  Finals-eligible customers (2022+, filters): {cust['finals_eligible'].sum():,}")

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

# Compare loyal vs one-and-done
one_done = cust[cust["total_orders"] == 1]
compare = pd.DataFrame({
    "segment": ["Loyal (3+ orders, repeat)", "One-and-done"],
    "customers": [len(loyal), len(one_done)],
    "avg_ltv": [loyal["total_revenue"].mean(), one_done["total_revenue"].mean()],
    "pct_subscribed": [loyal["ever_subscribed"].mean(), one_done["ever_subscribed"].mean()],
    "avg_unique_handles": [loyal["unique_handles"].mean(), one_done["unique_handles"].mean()],
    "pct_direct_acq": [
        (loyal["first_channel"] == "Direct / Organic").mean(),
        (one_done["first_channel"] == "Direct / Organic").mean(),
    ],
    "pct_full_price_first": [
        (loyal["first_disc_bin"].astype(str) == "0%").mean(),
        (one_done["first_disc_bin"].astype(str) == "0%").mean(),
    ],
})
compare.to_csv(OUT / "12_loyal_vs_one_and_done.csv", index=False)

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

# Save enriched customer table (for report)
cust_out_cols = [
    "customer_id", "acq_year", "acq_month", "first_channel", "total_revenue", "total_orders",
    "is_repeat", "ever_subscribed", "first_disc_bin", "first_order_pos", "unique_handles",
    "unique_flavor_skus", "vtd_decile", "finals_eligible", "profit_proxy",
]
cust[cust_out_cols].to_csv(OUT / "12_customer_enriched_finals.csv", index=False)

print("\nDone. Outputs saved to EDA/outputs/12_*.csv")
print("=" * 70)
