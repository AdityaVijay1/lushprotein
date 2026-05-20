"""
slide1_verify.py -- verify all slide 1 numbers for combined vs SG-only
"""
import sys, importlib.util, pathlib
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('cfg', '00_config.py')
cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)

import pandas as pd
OUT = pathlib.Path(cfg.OUTPUT_DIR)
orders = pd.read_parquet(OUT / 'orders.parquet')
cust   = pd.read_parquet(OUT / 'customers.parquet')

print("=== SLIDE 1 NUMBER VERIFICATION ===\n")
print("--- Dataset scope ---")
print(f"orders.parquet rows              : {len(orders):,}")
print(f"orders unique customer_id count  : {orders.customer_id.nunique():,}  <- these are UNIQUE customers")
print(f"cust.parquet rows (unique cust)  : {len(cust):,}  <- same, one row per customer")
print()

sg_ord   = orders[orders.store == 'SG']
my_ord   = orders[orders.store == 'MY']
hk_ord   = orders[orders.store == 'HK']
sg_cust  = cust[cust.customer_id.isin(sg_ord.customer_id)]
my_cust  = cust[cust.customer_id.isin(my_ord.customer_id)]
print(f"SG orders                        : {len(sg_ord):,}")
print(f"MY orders                        : {len(my_ord):,}")
print(f"HK orders                        : {len(hk_ord):,}")
print(f"SG-only unique customers         : {len(sg_cust):,}")
print(f"MY-only unique customers         : {len(my_cust):,}")
print(f"Combined (all stores)            : {len(cust):,}")
print()

print("--- Repeat rates ---")
total = len(cust)
rep_all  = int(cust['is_repeat'].sum())
rep_sg   = int(sg_cust['is_repeat'].sum())
print(f"All-market unique customers      : {total:,}")
print(f"All-market repeaters             : {rep_all:,}")
print(f"All-market repeat rate           : {rep_all/total*100:.1f}%")
print(f"SG-only unique customers         : {len(sg_cust):,}")
print(f"SG-only repeaters                : {rep_sg:,}")
print(f"SG-only repeat rate              : {rep_sg/len(sg_cust)*100:.1f}%")
print()

print("--- Subscriber LTV ---")
sub_all  = cust[cust.ever_subscribed == True]
non_all  = cust[cust.ever_subscribed == False]
sub_sg   = sg_cust[sg_cust.ever_subscribed == True]
non_sg   = sg_cust[sg_cust.ever_subscribed == False]
print(f"ALL markets sub LTV              : SGD {sub_all.total_revenue.mean():.0f}")
print(f"ALL markets non-sub LTV          : SGD {non_all.total_revenue.mean():.0f}")
print(f"ALL markets sub LTV uplift       : +{(sub_all.total_revenue.mean()/non_all.total_revenue.mean()-1)*100:.0f}%")
print(f"SG-only sub LTV                  : SGD {sub_sg.total_revenue.mean():.0f}")
print(f"SG-only non-sub LTV              : SGD {non_sg.total_revenue.mean():.0f}")
print(f"SG-only sub LTV uplift           : +{(sub_sg.total_revenue.mean()/non_sg.total_revenue.mean()-1)*100:.0f}%")
print(f"Ever-subscribed (ALL markets)    : {len(sub_all):,}  ({len(sub_all)/total*100:.1f}%)")
print(f"Ever-subscribed (SG-only)        : {len(sub_sg):,}  ({len(sub_sg)/len(sg_cust)*100:.1f}%)")
print()

print("--- Median days to 2nd purchase ---")
rpt_all = cust[cust.is_repeat == True]
rpt_sg  = sg_cust[sg_cust.is_repeat == True]
print(f"All-market median days to 2nd    : {rpt_all.days_to_second.median():.0f}")
print(f"SG-only median days to 2nd       : {rpt_sg.days_to_second.median():.0f}")
print()

print("=== WHY SG-ONLY AND COMBINED LOOK SIMILAR FOR COUNTS ===")
print("The customers.parquet contains ALL markets (SG+MY+HK).")
print("The 'SG-Only (prev.)' column in presentation.md did NOT mean SG-filtered data.")
print("It meant: same dataset, but MYR revenue treated as if it were SGD (no FX conversion).")
print("That inflated MY customers' revenue figures, making avg LTV higher.")
print("Customer/order COUNTS are identical because same dataset; only REVENUE changes.")
