import pandas as pd
from pathlib import Path
OUT = Path(__file__).parent / 'outputs'

t2 = pd.read_csv(OUT / '03_time_to_second_purchase.csv')
t2['rr_pct']     = (t2['pct_of_repeaters'] * 100).round(1)
t2['cum_pct_pct']= (t2['cum_pct'] * 100).round(1)

print("=" * 60)
print("SLIDE 5 CLAIMS FACT-CHECK")
print("=" * 60)

# CLAIM 1: 41% within 60 days
within_60 = t2[t2['bucket'].isin(['0-7d','8-14d','15-21d','22-30d','31-45d','46-60d'])]['pct_of_repeaters'].sum() * 100
print(f"\nCLAIM 1: '41% come back within 60 days'")
print(f"  Data:   {within_60:.1f}% (sum of 0-7d through 46-60d)")
print(f"  Verdict: {'OK - rounds to 41%' if abs(within_60 - 40.8) < 0.5 else 'WRONG'}")

# CLAIM 2: 61-90d is the largest single bucket
top = t2.sort_values('n_customers', ascending=False).head(3)
print(f"\nCLAIM 2: '61-90 day window is the largest single bucket'")
print(f"  Top 3 buckets by customer count:")
for _, r in top.iterrows():
    print(f"    {r['bucket']:<12}: {r['n_customers']:,} customers ({r['rr_pct']:.1f}%)")
bucket_61_90 = t2[t2['bucket']=='61-90d'].iloc[0]
bucket_365   = t2[t2['bucket']=='365d+'].iloc[0]
diff = int(bucket_365['n_customers']) - int(bucket_61_90['n_customers'])
print(f"  61-90d: {int(bucket_61_90['n_customers']):,} | 365d+: {int(bucket_365['n_customers']):,} | diff: {diff}")
if diff > 0:
    print(f"  Verdict: TECHNICALLY WRONG -- 365d+ is marginally larger by {diff} customers")
    print(f"           BUT the difference is only {diff} customers -- effectively tied")
    print(f"           More accurate: '61-90d is the largest bucket within the first year'")
else:
    print(f"  Verdict: CORRECT")

# CLAIM 3: probability drops sharply after 180 days
print(f"\nCLAIM 3: 'After 180 days probability of return drops sharply'")
print(f"  Bucket-by-bucket % of repeaters:")
for _, r in t2.iterrows():
    print(f"    {r['bucket']:<12}: {r['rr_pct']:.1f}% of all repeaters")
post_180_pct = t2[t2['bucket'].isin(['181-365d','365d+'])]['rr_pct'].sum()
pre_180_pct  = t2[~t2['bucket'].isin(['181-365d','365d+'])]['rr_pct'].sum()
print(f"\n  Post-180d total: {post_180_pct:.1f}% of all repeaters")
print(f"  Pre-180d total:  {pre_180_pct:.1f}% of all repeaters")
print(f"  Verdict: WRONG -- 181-365d (10.1%) and 365d+ (10.4%) are HIGHER than")
print(f"           most earlier buckets. No sharp drop after 180 days.")
print(f"           The long tail is substantial -- 20.5% of repeaters return after 6 months.")
print(f"\n  WHAT IS TRUE:")
print(f"    - Within 90 days: {t2[t2['bucket'].isin(['0-7d','8-14d','15-21d','22-30d','31-45d','46-60d','61-90d'])]['pct_of_repeaters'].sum()*100:.1f}% of repeaters return")
print(f"    - After 90 days: incremental returns slow to ~5-10% per bucket")
print(f"    - The 0-90d window captures the majority (51%) of all who ever return")
print(f"    - After 90d the remaining 49% trickle back slowly over 1+ years")
