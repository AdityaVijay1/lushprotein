import pandas as pd
from pathlib import Path
OUT = Path(__file__).parent / 'outputs'
yr = pd.read_csv(OUT / '02_orders_by_year.csv')
yr = yr[yr['year'].between(2020,2025)].copy()
yr['gross_rev']        = yr['revenue_sgd'] + yr['disc_amt']
yr['disc_pct_gross']   = (yr['disc_amt'] / yr['gross_rev'].replace(0, float('nan')) * 100).fillna(0).round(2)
yr['disc_pct_net']     = (yr['disc_amt'] / yr['revenue_sgd'].replace(0, float('nan')) * 100).fillna(0).round(2)
yr['disc_pct_orders_pct'] = (yr['disc_pct_orders'] * 100).round(1)

print(f"{'Year':<5} | {'Revenue (net)':>13} | {'Disc Given':>10} | {'Gross Rev':>10} | {'%Gross':>7} | {'%Net':>7} | {'%OrdersDisc':>12}")
print("-" * 80)
for _, r in yr.iterrows():
    yr_int = int(r['year'])
    rev    = r['revenue_sgd']
    disc   = r['disc_amt']
    gross  = r['gross_rev']
    pg     = r['disc_pct_gross']
    pn     = r['disc_pct_net']
    po     = r['disc_pct_orders_pct']
    print(f"{yr_int:<5} | {rev:>13,.0f} | {disc:>10,.0f} | {gross:>10,.0f} | {pg:>6.2f}% | {pn:>6.2f}% | {po:>11.1f}%")

print()
print("Metric definitions:")
print("  %Gross       = Discount / (Revenue + Discount)  -- % of potential (full-price) revenue sacrificed")
print("  %Net         = Discount / Revenue               -- % of collected revenue that was discounted")
print("  %OrdersDisc  = Orders with any discount / Total orders  -- % of transactions with a promo applied")
print()
print("Your OLD slide table used: %Gross (matches 3.90, 15.10, 30.90, 35.20)")
print("Current chart uses:        %OrdersDisc (shows 0, 0, 15.2, 59.3, 69.2, 49.6)")
