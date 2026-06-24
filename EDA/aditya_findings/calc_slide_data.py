import pandas as pd
import numpy as np
from pathlib import Path

FINALS = Path("EDA/outputs_finals")
cust = pd.read_parquet(FINALS / "customers.parquet")
orders = pd.read_parquet(FINALS / "orders.parquet")
fc = cust[cust["finals_eligible"] == True].copy()

print("=== SLIDE 1 PROBLEM STATS ===")
print(f"Total finals customers: {len(fc)}")
one_and_done = (fc["finals_orders"] == 1).sum()
print(f"One-and-done: {one_and_done} ({one_and_done/len(fc)*100:.1f}%)")
print(f"Repeat customers: {(fc['finals_orders'] > 1).sum()} ({(fc['finals_orders'] > 1).mean()*100:.1f}%)")
print()

# Category breakdown
cat_grp = fc.groupby("n_categories_ever").agg(
    n=("customer_id", "count"),
    avg_gp=("true_gross_profit", "mean"),
    repeat_rate=("finals_orders", lambda x: (x > 1).mean()),
    avg_orders=("finals_orders", "mean"),
).round(2)
print("Category ladder:")
print(cat_grp.to_string())
print()

# Subscriber vs non-subscriber
sub = fc[fc["ever_subscribed"] == True]
nonsub = fc[fc["ever_subscribed"] == False]
sub_repeat = (sub["finals_orders"] > 1).mean()
nonsub_repeat = (nonsub["finals_orders"] > 1).mean()
print(f"Subscribers: n={len(sub)}, repeat={sub_repeat*100:.1f}%, avg GP={sub['true_gross_profit'].mean():.0f}")
print(f"Non-subscribers: n={len(nonsub)}, repeat={nonsub_repeat*100:.1f}%, avg GP={nonsub['true_gross_profit'].mean():.0f}")
print()

# CRM tier stats
tier_grp = fc.groupby("crm_tier").agg(
    n=("customer_id", "count"),
    avg_gp=("true_gross_profit", "mean"),
    avg_orders=("finals_orders", "mean"),
    repeat_rate=("finals_orders", lambda x: (x > 1).mean()),
).round(2)
print("CRM tier breakdown:")
print(tier_grp.to_string())
print()

# Profit decile stats
print("=== PROFIT DECILE STATS ===")
decile_grp = fc.groupby("profit_decile_true").agg(
    n=("customer_id", "count"),
    avg_gp=("true_gross_profit", "mean"),
    avg_orders=("finals_orders", "mean"),
    repeat_rate=("finals_orders", lambda x: (x > 1).mean()),
    subscribed=("ever_subscribed", "mean"),
).round(2)
print(decile_grp.to_string())
print()

# Try to match the 4 new tiers from user input
# Platinum 238 @ S$388, Gold-A 130 @ S$300, Gold-B 264 @ S$105, Silver 858 @ S$100
fc_sorted = fc.sort_values("true_gross_profit", ascending=False)
top238 = fc_sorted.head(238)
next130 = fc_sorted.iloc[238:368]
next264 = fc_sorted.iloc[368:632]
next858 = fc_sorted.iloc[632:1490]
rest = fc_sorted.iloc[1490:]

print("=== NEW TIER MATCHING ===")
print(f"Platinum (top 238): avg_gp={top238['true_gross_profit'].mean():.0f}, "
      f"min_gp={top238['true_gross_profit'].min():.0f}, "
      f"repeat={( top238['finals_orders'] > 1).mean()*100:.1f}%, "
      f"sub={top238['ever_subscribed'].mean()*100:.1f}%")
print(f"Gold-A (next 130): avg_gp={next130['true_gross_profit'].mean():.0f}, "
      f"min_gp={next130['true_gross_profit'].min():.0f}, "
      f"repeat={(next130['finals_orders'] > 1).mean()*100:.1f}%, "
      f"sub={next130['ever_subscribed'].mean()*100:.1f}%")
print(f"Gold-B (next 264): avg_gp={next264['true_gross_profit'].mean():.0f}, "
      f"min_gp={next264['true_gross_profit'].min():.0f}, "
      f"repeat={(next264['finals_orders'] > 1).mean()*100:.1f}%, "
      f"sub={next264['ever_subscribed'].mean()*100:.1f}%")
print(f"Silver (next 858): avg_gp={next858['true_gross_profit'].mean():.0f}, "
      f"min_gp={next858['true_gross_profit'].min():.0f}, "
      f"repeat={(next858['finals_orders'] > 1).mean()*100:.1f}%, "
      f"sub={next858['ever_subscribed'].mean()*100:.1f}%")
print(f"Untiered rest ({len(rest)}): avg_gp={rest['true_gross_profit'].mean():.0f}, "
      f"repeat={(rest['finals_orders'] > 1).mean()*100:.1f}%")
print()

# Business value: what if we move Silver -> Gold-B -> Gold-A
# GP uplift per step
delta_silver_to_goldB = next264["true_gross_profit"].mean() - next858["true_gross_profit"].mean()
delta_goldB_to_goldA = next130["true_gross_profit"].mean() - next264["true_gross_profit"].mean()
delta_goldA_to_plat = top238["true_gross_profit"].mean() - next130["true_gross_profit"].mean()

print("=== TIER PROGRESSION VALUE ===")
print(f"Silver -> Gold-B lift: +S${delta_silver_to_goldB:.0f} GP/customer")
print(f"Gold-B -> Gold-A lift: +S${delta_goldB_to_goldA:.0f} GP/customer")
print(f"Gold-A -> Platinum lift: +S${delta_goldA_to_plat:.0f} GP/customer")
print()

# Key scenario: 5% of Silver move to Gold-B (via L3 cross-sell)
conv_rate_5pct = int(len(next858) * 0.05)
prize_5pct = conv_rate_5pct * delta_silver_to_goldB
print(f"5% Silver -> Gold-B: {conv_rate_5pct} customers x S${delta_silver_to_goldB:.0f} = S${prize_5pct:.0f} GP")
conv_rate_10pct = int(len(next858) * 0.10)
prize_10pct = conv_rate_10pct * delta_silver_to_goldB
print(f"10% Silver -> Gold-B: {conv_rate_10pct} customers x S${delta_silver_to_goldB:.0f} = S${prize_10pct:.0f} GP")
print()

# Category attach stats (for L3 narrative)
print("=== CATEGORY MOVEMENT STATS ===")
print("Single-cat customers (T4 focus pool):")
single_cat = fc[fc["n_categories_ever"] == 1]
print(f"  n={len(single_cat)}, avg_gp={single_cat['true_gross_profit'].mean():.0f}, repeat={( single_cat['finals_orders'] > 1).mean()*100:.1f}%")
two_cat = fc[fc["n_categories_ever"] == 2]
print(f"2-cat n={len(two_cat)}, avg_gp={two_cat['true_gross_profit'].mean():.0f}, repeat={(two_cat['finals_orders'] > 1).mean()*100:.1f}%")
three_plus = fc[fc["n_categories_ever"] >= 3]
print(f"3+ cat n={len(three_plus)}, avg_gp={three_plus['true_gross_profit'].mean():.0f}, repeat={(three_plus['finals_orders'] > 1).mean()*100:.1f}%")

# Reorder interval CSV
reorder = pd.read_csv("EDA/outputs/12_reorder_interval_by_sku.csv")
print()
print("=== TOP SKU REORDER INTERVALS ===")
print(reorder[reorder["repeat_buyers"] >= 25][["flavor_label", "repeat_buyers", "median_reorder_days", "mean_reorder_days"]].head(12).to_string())
