import pandas as pd
from pathlib import Path
OUT = Path(__file__).parent / 'outputs'

t2 = pd.read_csv(OUT / '03_time_to_second_purchase.csv')
t2['rr_pct']  = (t2['pct_of_repeaters'] * 100).round(1)
t2['cum_pct_pct'] = (t2['cum_pct'] * 100).round(1)

total_in_table = t2['n_customers'].sum()

print("03_time_to_second_purchase.csv -- FULL DATA")
print(f"{'Bucket':<12} {'n_customers':>12} {'% of Repeaters':>15} {'Cumulative %':>13}")
print("-" * 56)
for _, r in t2.iterrows():
    print(f"{r['bucket']:<12} {r['n_customers']:>12,} {r['rr_pct']:>14.1f}% {r['cum_pct_pct']:>12.1f}%")

print()
print(f"Total customers in distribution: {total_in_table:,}")

# 60-day cumulative
cum_60d = t2[t2['bucket'].isin(['0-7d','8-14d','15-21d','22-30d','31-45d','46-60d'])]['pct_of_repeaters'].sum() * 100
cum_90d = t2[t2['bucket'].isin(['0-7d','8-14d','15-21d','22-30d','31-45d','46-60d','61-90d'])]['pct_of_repeaters'].sum() * 100
print(f"Within 60 days (0-7d to 46-60d): {cum_60d:.1f}% of repeaters")
print(f"Within 90 days (0-7d to 61-90d): {cum_90d:.1f}% of repeaters")

# Largest bucket
top = t2.loc[t2['n_customers'].idxmax()]
print(f"Largest single bucket: {top['bucket']} with {top['n_customers']:,} customers ({top['rr_pct']:.1f}%)")

# Compare to presentation.md values
print()
print("CROSS-CHECK vs presentation.md (lines 461-477):")
pres_vals = {
    '0-7d': (336, 7.5),
    '8-14d': (222, 12.5),
    '15-21d': (213, 17.3),
    '22-30d': (355, 25.3),
    '31-45d': (372, 33.6),
    '46-60d': (320, 40.8),
    '61-90d': (461, 51.1),
    '91-120d': (257, 56.9),
    '121-180d': (346, 64.6),
    '181-365d': (450, 74.7),
    '365+ days': (463, 85.1),
}
# normalise bucket name for 365+
t2_dict = {row['bucket']: row for _, row in t2.iterrows()}
# map 365d+ -> 365+ days
bucket_map = {
    '0-7d': '0-7d', '8-14d': '8-14d', '15-21d': '15-21d', '22-30d': '22-30d',
    '31-45d': '31-45d', '46-60d': '46-60d', '61-90d': '61-90d',
    '91-120d': '91-120d', '121-180d': '121-180d', '181-365d': '181-365d',
    '365d+': '365+ days',
}

print(f"{'Bucket':<12} {'CSV n':>7} {'MD n':>7} {'n Match':>9} | {'CSV cum%':>9} {'MD cum%':>9} {'cum Match':>10}")
print("-" * 72)
for csv_bucket, md_bucket in bucket_map.items():
    if csv_bucket not in t2_dict:
        continue
    row = t2_dict[csv_bucket]
    md_n, md_cum = pres_vals.get(md_bucket, (None, None))
    csv_n   = int(row['n_customers'])
    csv_cum = round(float(row['cum_pct']) * 100, 1)
    n_ok    = "OK" if md_n == csv_n else f"DIFF (md={md_n})"
    cum_ok  = "OK" if abs(md_cum - csv_cum) <= 0.1 else f"DIFF (md={md_cum})"
    print(f"{csv_bucket:<12} {csv_n:>7} {str(md_n):>7} {n_ok:>9} | {csv_cum:>8.1f}% {str(md_cum):>8}% {cum_ok:>10}")
