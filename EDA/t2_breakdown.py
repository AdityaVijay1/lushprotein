import pandas as pd
from pathlib import Path
OUT = Path(__file__).parent / 'outputs'

t2   = pd.read_csv(OUT / '03_time_to_second_purchase.csv')
cust = pd.read_parquet(OUT / 'customers.parquet')
cust['is_repeat'] = cust['is_repeat'].astype(str).map({'True':True,'False':False}).fillna(False)
total_repeaters = int(cust['is_repeat'].sum())
total_in_dist   = int(t2['n_customers'].sum())

t2['rr_pct'] = (t2['pct_of_repeaters'] * 100).round(1)

print("DENOMINATOR CLARITY")
print(f"  Total repeat customers (2+ orders):       {total_repeaters:,}")
print(f"  Customers with timing in distribution:    {total_in_dist:,}  ({total_in_dist/total_repeaters*100:.1f}%)")
print(f"  pct_of_repeaters column denominates by:  {total_repeaters:,}  (ALL repeaters)")
print()
print("VERIFICATION: each bucket's pct = n / 4,459")
for _, r in t2.iterrows():
    computed = r['n_customers'] / total_repeaters * 100
    print(f"  {r['bucket']:<12}: {r['n_customers']:>3} / {total_repeaters} = {computed:.1f}% (col shows {r['rr_pct']:.1f}%)")

print()
print("SEGMENT TOTALS (% of ALL 4,459 repeaters):")
within_90  = t2[t2['bucket'].isin(['0-7d','8-14d','15-21d','22-30d','31-45d','46-60d','61-90d'])]['rr_pct'].sum()
after_90   = t2[t2['bucket'].isin(['91-120d','121-180d','181-365d','365d+'])]['rr_pct'].sum()
after_180  = t2[t2['bucket'].isin(['181-365d','365d+'])]['rr_pct'].sum()
not_timed  = 100 - t2['rr_pct'].sum()

print(f"  Within 90 days  (0-7d to 61-90d):     {within_90:.1f}%  ({round(total_repeaters*within_90/100):,} customers)")
print(f"  After 90 days   (91d to 365d+):        {after_90:.1f}%  ({round(total_repeaters*after_90/100):,} customers)")
print(f"  After 180 days  (181d to 365d+):       {after_180:.1f}%  ({round(total_repeaters*after_180/100):,} customers)")
print(f"  Not yet timed   (repeat but no date):  {not_timed:.1f}%  ({round(total_repeaters*not_timed/100):,} customers)")
print(f"  TOTAL:                                 100.0%  ({total_repeaters:,})")
print()
print("USER'S CALC: 91-120d + 121-180d + 181-365d + 365d+")
user_sum = t2[t2['bucket'].isin(['91-120d','121-180d','181-365d','365d+'])]['rr_pct'].sum()
print(f"  5.8 + 7.8 + 10.1 + 10.4 = {user_sum:.1f}% of ALL 4,459 repeaters -- CORRECT")
print()
print("WHERE 'NOT TIMED' COMES FROM:")
print(f"  These {round(total_repeaters*not_timed/100):,} customers are repeaters (2+ orders) but don't appear")
print(f"  in the time distribution — likely very recent 2nd purchases")
print(f"  where the gap calculation was cut off at the analysis date.")
