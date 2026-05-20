import pandas as pd
from pathlib import Path
OUT = Path(__file__).parent / 'outputs'

dd = pd.read_csv(OUT / '05_discount_depth_bins.csv')
dd['rr_pct']  = (dd['repeat_rate'] * 100).round(1)
dd['ltv_sgd'] = dd['avg_ltv'].round(0).astype(int)
total = dd['customers'].sum()
dd['cust_pct'] = (dd['customers'] / total * 100).round(1)

print("05_discount_depth_bins.csv -- full detail")
print(f"{'Bin':<18} {'Customers':>10} {'Cust%':>7} {'Repeat Rate':>12} {'Avg LTV':>9}")
print("-" * 62)
for _, r in dd.iterrows():
    print(f"{r['discount_bin']:<18} {r['customers']:>10,} {r['cust_pct']:>6.1f}% {r['rr_pct']:>10.1f}% {r['ltv_sgd']:>8,}")

fp  = dd[dd['discount_bin'] == '0% (full price)'].iloc[0]
top = dd[dd['discount_bin'] == '51%+'].iloc[0]
heavy = dd[dd['discount_bin'].isin(['31-50% off','51%+'])]
heavy_cust = heavy['customers'].sum()

rr_drop     = (top['rr_pct'] - fp['rr_pct']) / fp['rr_pct'] * 100
ltv_drop    = (top['ltv_sgd'] - fp['ltv_sgd']) / fp['ltv_sgd'] * 100
fp_vs_any   = dd[dd['discount_bin'] != '0% (full price)']
fp_rr       = fp['rr_pct']
avg_disc_rr = fp_vs_any['rr_pct'].mean()

print()
print("KEY METRICS FOR SLIDE NOTES:")
print(f"  Full-price repeat rate:        {fp['rr_pct']:.1f}%  (n={fp['customers']:,})")
print(f"  51%+ off repeat rate:          {top['rr_pct']:.1f}%  (n={top['customers']:,})")
print(f"  RR drop full price -> 51%+ :   {rr_drop:.0f}%")
print(f"  LTV full price:                S${fp['ltv_sgd']:,}")
print(f"  LTV 51%+ off:                  S${top['ltv_sgd']:,}")
print(f"  LTV drop full price -> 51%+:   {ltv_drop:.0f}%")
print(f"  Customers getting 31%+ disc:   {heavy_cust:,} ({heavy_cust/total*100:.1f}% of all first-buyers)")
print(f"  Avg RR across ALL disc tiers:  {avg_disc_rr:.1f}%  vs {fp_rr:.1f}% full price")
