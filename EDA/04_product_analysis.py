"""
04_product_analysis.py  â€“  Product stickiness and SKU-level analysis.

Analyses
--------
A. Repeat purchase rate by FIRST product purchased
B. Cross-product purchasing: does buying 2+ categories raise LTV?
C. Product-level revenue, AOV, and basket composition
D. SKU popularity at first checkout vs at renewal
E. Subscription vs one-time split per product

Outputs
-------
outputs/04_repeat_by_first_product.csv
outputs/04_cross_product_ltv.csv
outputs/04_sku_popularity.csv
outputs/04_product_revenue_summary.csv

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
OUTPUT_DIR = cfg.OUTPUT_DIR

print("Loading cached tables...")
orders      = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
lines       = pd.read_parquet(OUTPUT_DIR / "lines.parquet")
cust        = pd.read_parquet(OUTPUT_DIR / "customers.parquet")
rc_checkout = pd.read_parquet(OUTPUT_DIR / "rc_checkout.parquet")
rc_recurring= pd.read_parquet(OUTPUT_DIR / "rc_recurring.parquet")

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
lines["order_date"]  = pd.to_datetime(lines["order_date"],  utc=True)

#                                                                             
# A.  REPEAT RATE BY FIRST PRODUCT PURCHASED
#                                                                             
print("\n[A] REPEAT RATE BY FIRST PRODUCT PURCHASED")
print("=" * 60)

rep_by_prod = (
    cust.groupby("first_product_cat")
    .agg(
        customers         = ("customer_id",   "count"),
        repeaters         = ("is_repeat",     "sum"),
        avg_total_orders  = ("total_orders",  "mean"),
        avg_ltv           = ("total_revenue", "mean"),
        median_days_2nd   = ("days_to_second","median"),
    )
    .assign(repeat_rate=lambda d: d["repeaters"] / d["customers"])
    .sort_values("repeat_rate", ascending=False)
)
print(rep_by_prod.to_string())
rep_by_prod.to_csv(OUTPUT_DIR / "04_repeat_by_first_product.csv")

#                                                                             
# B.  CROSS-PRODUCT PURCHASING & LTV UPLIFT
#                                                                             
print("\n\n[B] CROSS-PRODUCT PURCHASING & LTV UPLIFT")
print("=" * 60)

# Per customer: how many distinct product categories did they buy?
cat_per_cust = (
    lines.groupby("customer_id")["product_category"]
    .nunique()
    .reset_index()
    .rename(columns={"product_category": "n_categories"})
)
cat_per_cust["n_categories"] = cat_per_cust["n_categories"].clip(upper=4)
cat_per_cust["category_label"] = cat_per_cust["n_categories"].map({
    1: "1 product",
    2: "2 products",
    3: "3 products",
    4: "4+ products",
})

cross = cust.merge(cat_per_cust, on="customer_id", how="left")
cross["n_categories"] = cross["n_categories"].fillna(1)

cross_summary = (
    cross.groupby("category_label")
    .agg(
        customers        = ("customer_id",   "count"),
        repeat_rate      = ("is_repeat",     "mean"),
        avg_ltv          = ("total_revenue", "mean"),
        avg_orders       = ("total_orders",  "mean"),
        avg_lifespan_days= ("lifespan_days", "mean"),
    )
    .reindex(["1 product","2 products","3 products","4+ products"])
)
print(cross_summary.to_string())
cross_summary.to_csv(OUTPUT_DIR / "04_cross_product_ltv.csv")

# What combinations of products do repeat buyers purchase?
print("\n  Top product category combinations (repeat buyers):")
repeater_ids = cust[cust["is_repeat"]]["customer_id"]
rep_lines = lines[lines["customer_id"].isin(repeater_ids)]
combo = (
    rep_lines.groupby("customer_id")["product_category"]
    .apply(lambda s: " + ".join(sorted(s.unique())))
    .value_counts()
    .head(15)
)
print(combo.to_string())

#                                                                             
# C.  PRODUCT-LEVEL REVENUE AND BASKET METRICS
#                                                                             
print("\n\n[C] PRODUCT-LEVEL REVENUE SUMMARY")
print("=" * 60)

# Hero categories only: Lean Protein, Clear Protein, Collagen Glow
hero_cats = ["Lean Protein", "Clear Protein", "Collagen Glow"]

prod_rev = (
    lines.groupby("product_category")
    .agg(
        total_units     = ("Line: Quantity", "sum"),
        total_revenue   = ("Line: Total",    "sum"),
        n_orders        = ("order_id",        "nunique"),
        n_customers     = ("customer_id",     "nunique"),
        avg_unit_price  = ("Line: Price",     "mean"),
    )
    .assign(revenue_per_customer=lambda d: d["total_revenue"] / d["n_customers"])
    .sort_values("total_revenue", ascending=False)
)
print(prod_rev.to_string())
prod_rev.to_csv(OUTPUT_DIR / "04_product_revenue_summary.csv")

#                                                                             
# D.  TOP SKUs AT FIRST CHECKOUT vs AT RENEWAL (Recharge data)
#                                                                             
print("\n\n[D] TOP SKUs: FIRST CHECKOUT vs RECURRING (Recharge)")
print("=" * 60)

def sku_rank(df, label, topn=15):
    ranked = (
        df.groupby(["product_title","variant_title"])
        .agg(n_orders=("recharge_order_id","nunique"),
             n_customers=("customer_id","nunique"),
             total_units=("order_item_quantity","sum"))
        .sort_values("n_orders", ascending=False)
        .head(topn)
        .reset_index()
    )
    ranked.insert(0, "type", label)
    return ranked

checkout_top  = sku_rank(rc_checkout,  "checkout")
recurring_top = sku_rank(rc_recurring, "recurring")

print("  --- TOP CHECKOUT SKUs ---")
print(checkout_top[["product_title","variant_title","n_orders","n_customers"]].to_string(index=False))
print()
print("  --- TOP RECURRING SKUs ---")
print(recurring_top[["product_title","variant_title","n_orders","n_customers"]].to_string(index=False))

pd.concat([checkout_top, recurring_top]).to_csv(OUTPUT_DIR / "04_sku_popularity.csv", index=False)

# â”€â”€ Loyalty ratio: what % of checkout SKU customers stay for recurring? â”€â”€â”€â”€
print("\n  SKU loyalty ratio (recurring customers / checkout customers):")
checkout_custs  = rc_checkout.groupby("product_sku")["customer_id"].nunique().rename("checkout_custs")
recurring_custs = rc_recurring.groupby("product_sku")["customer_id"].nunique().rename("recurring_custs")
loyalty = pd.concat([checkout_custs, recurring_custs], axis=1).dropna()
loyalty["loyalty_ratio"] = loyalty["recurring_custs"] / loyalty["checkout_custs"]
loyalty = loyalty.sort_values("loyalty_ratio", ascending=False).head(20)
print(loyalty.to_string())

#                                                                             
# E.  PRODUCT Ã— CHANNEL CROSS-TAB
#                                                                             
print("\n\n[E] PRODUCT Ã— CHANNEL CROSS-TAB (% of orders)")
print("=" * 60)
prod_channel = pd.crosstab(
    orders["product_category"],
    orders["channel"],
    normalize="index",
).round(3)
print(prod_channel.to_string())

print("\n[04] Done.")

