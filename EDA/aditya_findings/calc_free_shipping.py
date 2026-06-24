import pandas as pd
import numpy as np
from pathlib import Path

FINALS = Path("EDA/outputs_finals")
orders = pd.read_parquet(FINALS / "orders.parquet")
cust = pd.read_parquet(FINALS / "customers.parquet")

finals_ids = cust[cust["finals_eligible"] == True]["customer_id"]
orders_f = orders[orders["customer_id"].isin(finals_ids)].copy()
ord_dedup = orders_f.drop_duplicates(subset="order_id").copy()

# Merge CRM tier
tier_map = cust[["customer_id", "crm_tier", "profit_decile_true"]].drop_duplicates()
ord_dedup = ord_dedup.merge(tier_map, on="customer_id", how="left")

print("=== ORDER REVENUE DISTRIBUTION ===")
print(ord_dedup["order_rev"].describe().round(2))
print()

# Free vs paid shipping
fs = ord_dedup[ord_dedup["Price: Total Shipping"] == 0]
ps = ord_dedup[ord_dedup["Price: Total Shipping"] > 0]
print("=== AVG BASKET: FREE vs PAID SHIPPING ===")
print(f"Free shipping orders  — avg basket: {fs['order_rev'].mean():.2f}, median: {fs['order_rev'].median():.2f}, n={len(fs)}")
print(f"Paid shipping orders  — avg basket: {ps['order_rev'].mean():.2f}, median: {ps['order_rev'].median():.2f}, n={len(ps)}")
avg_shipping_cost = ps["Price: Total Shipping"].mean()
print(f"Avg shipping charge paid by customer: {avg_shipping_cost:.2f}")
print()

# -- THRESHOLD ANALYSIS --
print("=== THRESHOLD UPLIFT ANALYSIS (paid-shipping orders only) ===")
avg_margin = ord_dedup["order_margin_pct"].mean()
print(f"Avg GP margin across all orders: {avg_margin*100:.1f}%")
print()

thresholds = [50, 60, 70, 80, 90, 100, 120]
results = []
for t in thresholds:
    below = ps[ps["order_rev"] < t]
    if len(below) == 0:
        continue
    gap = t - below["order_rev"]
    avg_gap = gap.mean()
    gp_from_uplift = avg_gap * avg_margin
    net_benefit = gp_from_uplift - avg_shipping_cost
    pct_below = len(below) / len(ps)
    results.append({
        "threshold": t,
        "paid_orders_below": len(below),
        "pct_paid_orders_below": round(pct_below * 100, 0),
        "avg_uplift_needed": round(avg_gap, 2),
        "gp_from_uplift": round(gp_from_uplift, 2),
        "shipping_cost_absorbed": round(avg_shipping_cost, 2),
        "net_benefit_per_order": round(net_benefit, 2),
    })

res_df = pd.DataFrame(results)
print(res_df.to_string(index=False))
print()

# -- BY CRM TIER --
print("=== PAID SHIPPING ORDERS BY CRM TIER ===")
tier_grp = ps.groupby("crm_tier").agg(
    n_orders=("order_id", "count"),
    avg_basket=("order_rev", "mean"),
    median_basket=("order_rev", "median"),
    avg_shipping=("Price: Total Shipping", "mean"),
    avg_margin=("order_margin_pct", "mean"),
).round(2)
print(tier_grp.to_string())
print()

# -- OPTIMAL THRESHOLD per tier --
print("=== BREAKEVEN THRESHOLD PER TIER ===")
# For each tier, find min threshold where GP from uplift >= shipping cost
for tier in ["T1", "T2", "T3", "T4", "T5"]:
    tier_ps = ps[ps["crm_tier"] == tier]
    if len(tier_ps) < 10:
        continue
    t_margin = tier_ps["order_margin_pct"].mean()
    t_ship = tier_ps["Price: Total Shipping"].mean()
    t_median_basket = tier_ps["order_rev"].median()
    # breakeven: avg_gap * margin = shipping_cost => avg_gap = shipping/margin
    breakeven_gap = t_ship / t_margin
    breakeven_threshold = t_median_basket + breakeven_gap
    print(f"{tier}: median basket={t_median_basket:.0f}, avg shipping={t_ship:.2f}, margin={t_margin*100:.0f}%, breakeven_gap={breakeven_gap:.0f} => recommend threshold ~{breakeven_threshold:.0f}")

# -- SUBSCRIPTION vs NON-SUBSCRIPTION --
print()
print("=== SUBSCRIPTION vs NON-SUBSCRIPTION paid-shipping orders ===")
for label, subset in [("Subscription", ps[ps["is_subscription"] == True]),
                       ("Non-subscription", ps[ps["is_subscription"] == False])]:
    if len(subset) == 0:
        continue
    print(f"{label}: n={len(subset)}, avg_basket={subset['order_rev'].mean():.2f}, median_basket={subset['order_rev'].median():.2f}, avg_shipping={subset['Price: Total Shipping'].mean():.2f}")

# -- REVENUE PERCENTILES --
print()
print("=== ALL ORDERS REVENUE PERCENTILES ===")
for p in [10, 25, 50, 60, 70, 75, 80, 90]:
    val = ord_dedup["order_rev"].quantile(p / 100)
    print(f"  {p}th percentile: {val:.2f}")
