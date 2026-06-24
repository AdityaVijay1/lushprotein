import pandas as pd
import numpy as np
from pathlib import Path

FINALS = Path("EDA/outputs_finals")
orders = pd.read_parquet(FINALS / "orders.parquet")
cust = pd.read_parquet(FINALS / "customers.parquet")

finals_ids = cust[cust["finals_eligible"] == True]["customer_id"]
orders_f = orders[orders["customer_id"].isin(finals_ids)].copy()
ord_dedup = orders_f.drop_duplicates(subset="order_id").copy()

tier_map = cust[["customer_id", "crm_tier", "profit_decile_true", "ever_subscribed"]].drop_duplicates()
ord_dedup = ord_dedup.merge(tier_map, on="customer_id", how="left")

ps = ord_dedup[ord_dedup["Price: Total Shipping"] > 0].copy()

# ── Per-tier breakeven with actual threshold search ─────────────────────────
print("=== BREAKEVEN THRESHOLD PER CRM TIER ===")
print("Logic: find smallest threshold T where GP_uplift >= shipping absorbed")
print("(GP_uplift = (T - median_basket) * margin)")
print()

tier_details = {}
for tier in sorted(ps["crm_tier"].dropna().unique()):
    t_df = ps[ps["crm_tier"] == tier]
    if len(t_df) < 10:
        continue
    margin = t_df["order_margin_pct"].mean()
    ship   = t_df["Price: Total Shipping"].mean()
    med    = t_df["order_rev"].median()
    avg    = t_df["order_rev"].mean()
    # breakeven threshold (ignoring that not everyone buys up)
    breakeven_T = med + (ship / margin)
    # conservative: assume only 30% of customers below threshold actually bump up
    bump_rate = 0.30
    # annual orders below each threshold
    # Simulate: for each candidate threshold, what net GP is created?
    results = []
    for T in range(30, 160, 5):
        below = t_df[t_df["order_rev"] < T]
        if len(below) == 0:
            continue
        avg_gap = (T - below["order_rev"]).mean()
        # conservative: only 30% actually add items
        gp_per_order = avg_gap * margin * bump_rate - ship
        results.append({"T": T, "n_below": len(below), "gp_net": round(gp_per_order, 2)})
    r_df = pd.DataFrame(results)
    profitable = r_df[r_df["gp_net"] > 0]
    min_T = profitable["T"].min() if len(profitable) > 0 else None
    tier_details[tier] = {
        "n_paid_orders": len(t_df),
        "median_basket": round(med, 2),
        "avg_basket": round(avg, 2),
        "avg_margin_pct": round(margin * 100, 1),
        "avg_shipping_charged": round(ship, 2),
        "theoretical_breakeven_T": round(med + ship / margin, 0),
        "conservative_min_profitable_T": min_T,
    }
    print(f"{tier} (n={len(t_df)}): median_basket={med:.0f}, margin={margin*100:.0f}%, ship={ship:.2f}")
    print(f"  => Theoretical breakeven threshold: {med + ship/margin:.0f}")
    print(f"  => With 30% bump rate, profitable from threshold: {min_T}")
    print()

# ── What % of orders are sub-threshold at S$80? ──────────────────────────────
print("=== AT S$80 THRESHOLD: ORDERS IN RANGE (can be upsold) ===")
for tier in sorted(ps["crm_tier"].dropna().unique()):
    t_df = ps[ps["crm_tier"] == tier]
    if len(t_df) < 10:
        continue
    in_range = t_df[(t_df["order_rev"] >= 50) & (t_df["order_rev"] < 80)]
    pct = len(in_range) / len(t_df)
    print(f"  {tier}: {len(in_range)} orders ({pct*100:.0f}%) between S$50-80 (sweetspot for S$80 threshold)")

print()
# ── GP cost per year if LP absorbs all shipping above threshold ──────────────
print("=== TOTAL ANNUAL SHIPPING COST LP ABSORBS AT EACH THRESHOLD ===")
# Assume 8955 orders/year (use actuals)
total_orders = len(ord_dedup)
for T in [60, 70, 80, 100]:
    above_T = ord_dedup[ord_dedup["order_rev"] >= T]
    currently_paying = above_T[above_T["Price: Total Shipping"] > 0]
    ship_absorbed = currently_paying["Price: Total Shipping"].sum()
    pct_covered = len(above_T) / total_orders
    print(f"  Threshold S${T}: covers {pct_covered*100:.0f}% of all orders, LP absorbs S${ship_absorbed:.0f}/yr shipping (cost if extending to all >={T})")

print()
# ── Net scenario: flat S$80 threshold ────────────────────────────────────────
print("=== NET GP SCENARIO: FLAT S$80 THRESHOLD (conservative 30% uplift) ===")
T = 80
below = ps[ps["order_rev"] < T]
avg_gap = (T - below["order_rev"]).mean()
margin = ps["order_margin_pct"].mean()
gp_per_bump = avg_gap * margin
shipping_cost = ps["Price: Total Shipping"].mean()
# 30% of orders below threshold actually bump up
bump_orders_per_yr = len(below) * 0.30
gp_gain = bump_orders_per_yr * gp_per_bump
ship_absorbed = len(below) * shipping_cost  # worst case: give free shipping to all below (who don't bump)
net = gp_gain - ship_absorbed
print(f"  Orders below S$80 threshold: {len(below)} ({len(below)/len(ps)*100:.0f}% of paid-ship orders)")
print(f"  Avg gap to threshold: S${avg_gap:.2f}")
print(f"  Assumed 30% bump up: {bump_orders_per_yr:.0f} orders")
print(f"  GP generated from uplift: S${gp_gain:.0f}")
print(f"  Shipping cost absorbed (remaining 70%): S${ship_absorbed:.0f}")
print(f"  Net GP impact: S${net:.0f}")
