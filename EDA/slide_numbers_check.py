import pandas as pd, warnings; warnings.filterwarnings('ignore')
from pathlib import Path
OUT = Path(__file__).parent / 'outputs'

t2 = pd.read_csv(OUT / '03_time_to_second_purchase.csv')
within90_buckets = ['0-7d','8-14d','15-21d','22-30d','31-45d','46-60d','61-90d']
within_90 = t2[t2['bucket'].isin(within90_buckets)]['n_customers'].sum()
total_in_table = t2['n_customers'].sum()
pct_90 = within_90 / total_in_table
top_bucket = t2.sort_values('n_customers', ascending=False).iloc[0]
print("=== Slide 5: Time to 2nd Purchase ===")
print(f"  Within 90d: {within_90}/{total_in_table} = {pct_90:.1%}")
print(f"  Largest bucket: {top_bucket['bucket']} ({top_bucket['n_customers']} customers)")

cp = pd.read_csv(OUT / '04_cross_product_ltv.csv')
ltv_1 = float(cp[cp['category_label'].str.strip() == '1 product']['avg_ltv'].iloc[0])
ltv_3 = float(cp[cp['category_label'].str.strip() == '3 products']['avg_ltv'].iloc[0])
rr_1  = float(cp[cp['category_label'].str.strip() == '1 product']['repeat_rate'].iloc[0])
rr_3  = float(cp[cp['category_label'].str.strip() == '3 products']['repeat_rate'].iloc[0])
print("\n=== Slide 6: Cross-sell ===")
print(f"  RR: {rr_1*100:.1f}% -> {rr_3*100:.1f}% (+{(rr_3-rr_1)/rr_1*100:.0f}%)")
print(f"  LTV: S${ltv_1:.0f} -> S${ltv_3:.0f} (+{(ltv_3-ltv_1)/ltv_1*100:.0f}%)")

yr = pd.read_csv(OUT / '02_orders_by_year.csv')
r21 = float(yr[yr['year']==2021]['revenue_sgd'].iloc[0])
r25 = float(yr[yr['year']==2025]['revenue_sgd'].iloc[0])
c21 = float(yr[yr['year']==2021]['customers'].iloc[0])
c25 = float(yr[yr['year']==2025]['customers'].iloc[0])
print("\n=== Slide 3: Revenue & Customer Trend ===")
print(f"  Rev/customer 2021: S${r21/c21:.0f}  2025: S${r25/c25:.0f}  ({(r25/c25-r21/c21)/(r21/c21)*100:.0f}%)")
print(f"  Revenue change 2021->2025: {(r25-r21)/r21*100:.0f}%")
print(f"  Customers 2021: {c21:.0f}  2025: {c25:.0f}  change: {(c25-c21)/c21*100:.0f}%")
print("  Order/customer counts per year:")
for _, row in yr.iterrows():
    print(f"    {int(row['year'])}: {int(row['customers'])} customers | {int(row['orders'])} orders | S${row['revenue_sgd']:,.0f} revenue")

sv = pd.read_csv(OUT / '06_sub_vs_onetime_ltv.csv', index_col=0)
sub_ltv = float(sv.loc['Subscriber','avg_ltv'])
ns_ltv  = float(sv.loc['One-time / Non-subscriber','avg_ltv'])
print(f"\n=== Slide 2: Subscriber LTV ===")
print(f"  Subscriber: S${sub_ltv:.0f}  Non-sub: S${ns_ltv:.0f}  Uplift: +{(sub_ltv-ns_ltv)/ns_ltv*100:.0f}%")
