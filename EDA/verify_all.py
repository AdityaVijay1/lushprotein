"""
verify_all.py  —  Comprehensive verification of all data, CSVs, and numbers.
Run from any directory. Prints a full report with PASS/FAIL/WARN tags.
"""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT  = BASE / "EDA" / "outputs"

issues = []

def chk(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    if not condition:
        issues.append(label)
    print(f"  [{status}] {label}" + (f"  >> {detail}" if detail else ""))

print("="*70)
print("LUSHPROTEIN — FULL VERIFICATION REPORT")
print("="*70)

# ─────────────────────────────────────────────────────────────────────────────
# 1. PARQUET FILES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1] PARQUET FILES")
orders = pd.read_parquet(OUT / "orders.parquet")
lines  = pd.read_parquet(OUT / "lines.parquet")
cust   = pd.read_parquet(OUT / "customers.parquet")

orders["order_date"]   = pd.to_datetime(orders["order_date"], utc=True)
orders["Price: Total"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
orders["Price: Total Discount"] = pd.to_numeric(orders["Price: Total Discount"], errors="coerce").fillna(0)
cust["total_revenue"]  = pd.to_numeric(cust["total_revenue"], errors="coerce").fillna(0)
cust["is_repeat"]      = cust["is_repeat"].astype(str).map({"True":True,"False":False}).fillna(False)
cust["total_orders"]   = pd.to_numeric(cust["total_orders"], errors="coerce").fillna(1)

total_orders    = len(orders)
uniq_customers  = orders["customer_id"].nunique()
total_rev       = orders["Price: Total"].sum()
overall_rr      = cust["is_repeat"].mean()

chk("orders.parquet exists", total_orders > 0, f"{total_orders:,} rows")
chk("customers.parquet consistent", len(cust) == uniq_customers,
    f"cust table {len(cust):,} vs orders unique {uniq_customers:,}")
chk("All currencies = SGD after FX", (orders["Currency"].fillna("") == "SGD").all())
chk("No negative revenue", (orders["Price: Total"] >= 0).all())
chk("Date range 2019-2026", orders["order_date"].min().year <= 2020
    and orders["order_date"].max().year >= 2025,
    str(orders["order_date"].min().date()) + " to " + str(orders["order_date"].max().date()))

sg_avg = orders[orders["store"]=="SG"]["Price: Total"].mean()
my_avg = orders[orders["store"]=="MY"]["Price: Total"].mean()
hk_avg = orders[orders["store"]=="HK"]["Price: Total"].mean()
chk("SG avg order value 50-200 SGD (sanity)", 50 <= sg_avg <= 200, f"S${sg_avg:.1f}")
chk("MY avg order value 40-180 SGD (post FX /3.30)", 40 <= my_avg <= 180, f"S${my_avg:.1f}")
chk("HK avg order value 40-180 SGD (post FX /6.10)", 40 <= hk_avg <= 180, f"S${hk_avg:.1f}")

print(f"\n  Total combined revenue: S${total_rev:,.0f}")
print(f"  Stores: {orders.groupby('store')['order_id'].count().to_dict()}")
print(f"  Overall repeat rate: {overall_rr:.1%}  ({cust['is_repeat'].sum():,} / {len(cust):,})")

# ─────────────────────────────────────────────────────────────────────────────
# 2. CSV OUTPUTS — verify each one exists and spot-check key numbers
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2] CSV OUTPUT FILES")

csv_files = [
    "02_orders_by_year.csv", "02_orders_by_country.csv",
    "02_orders_by_channel.csv", "02_revenue_by_month.csv",
    "03_repeat_rate_by_slice.csv", "03_time_to_second_purchase.csv",
    "03_cohort_retention_heatmap.csv", "03_rfm_segments.csv",
    "04_repeat_by_first_product.csv", "04_cross_product_ltv.csv",
    "04_sku_popularity.csv", "04_product_revenue_summary.csv",
    "05_channel_quality.csv", "05_discount_sensitivity.csv",
    "05_discount_depth_bins.csv", "05_discount_code_taxonomy.csv",
    "06_sub_vs_onetime_ltv.csv", "06_churn_reasons.csv",
    "06_churn_by_product.csv", "06_churn_by_cycle.csv", "06_churn_tenure.csv",
    "06_reactivation_analysis.csv",
]
for f in csv_files:
    p = OUT / f
    chk(f, p.exists() and p.stat().st_size > 100, "exists & non-empty" if p.exists() else "MISSING")

# ─────────────────────────────────────────────────────────────────────────────
# 3. KEY METRIC SPOT-CHECKS (CSV vs recomputed from parquet)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3] KEY METRIC SPOT-CHECKS (CSV vs live parquet recompute)")

# 3a. Overall repeat rate matches
cq = pd.read_csv(OUT / "05_channel_quality.csv")
csv_total_repeaters = cq["repeaters"].sum()
csv_total_customers = cq["customers"].sum()
csv_rr = csv_total_repeaters / csv_total_customers
chk("Overall RR: CSV matches parquet", abs(csv_rr - overall_rr) < 0.005,
    f"CSV {csv_rr:.1%} vs parquet {overall_rr:.1%}")

# 3b. Annual revenue totals match
yr = pd.read_csv(OUT / "02_orders_by_year.csv")
csv_rev_sum = yr["revenue_sgd"].sum()
chk("Annual revenue sum matches total", abs(csv_rev_sum - total_rev) < 100,
    f"CSV sum S${csv_rev_sum:,.0f} vs parquet S${total_rev:,.0f}")

# 3c. Monthly revenue sum = annual sum (approx)
monthly = pd.read_csv(OUT / "02_revenue_by_month.csv")
monthly_sum = monthly["revenue"].sum()
chk("Monthly revenue sum matches annual sum", abs(monthly_sum - total_rev) < 100,
    f"Monthly sum S${monthly_sum:,.0f} vs total S${total_rev:,.0f}")

# 3d. Channel quality: Marketplace 14.x%, Subscription 40+%
cq["first_channel"] = cq["first_channel"].str.replace(" / ", "/")
mkt  = cq[cq["first_channel"]=="Marketplace"]
sub  = cq[cq["first_channel"]=="Subscription"]
mkt_rr = float(mkt["repeat_rate"].iloc[0]) if not mkt.empty else None
sub_rr_v = float(sub["repeat_rate"].iloc[0]) if not sub.empty else None
chk("Marketplace repeat rate 10-20%", mkt_rr is not None and 0.10 <= mkt_rr <= 0.20,
    f"{mkt_rr:.1%}" if mkt_rr else "missing")
chk("Subscription repeat rate >35%", sub_rr_v is not None and sub_rr_v > 0.35,
    f"{sub_rr_v:.1%}" if sub_rr_v else "missing")

# 3e. Cross-product LTV: 4+ products > 1 product
cp = pd.read_csv(OUT / "04_cross_product_ltv.csv")
ltv_1 = float(cp[cp["category_label"]=="1 product"]["avg_ltv"].iloc[0])
ltv_4 = float(cp[cp["category_label"]=="4+ products"]["avg_ltv"].iloc[0])
chk("Cross-product LTV: 4+ products > 1 product", ltv_4 > ltv_1,
    f"1 prod: S${ltv_1:.0f} vs 4+ prod: S${ltv_4:.0f}")

# 3f. Subscriber LTV > non-subscriber
sv = pd.read_csv(OUT / "06_sub_vs_onetime_ltv.csv", index_col=0)
sub_ltv = float(sv.loc["Subscriber","avg_ltv"])
ns_ltv  = float(sv.loc["One-time / Non-subscriber","avg_ltv"])
chk("Subscriber LTV > non-subscriber LTV", sub_ltv > ns_ltv,
    f"Sub: S${sub_ltv:.0f} vs Non-sub: S${ns_ltv:.0f}")

# 3g. Discount depth: full-price RR > 51%+ off
dd = pd.read_csv(OUT / "05_discount_depth_bins.csv")
fp_rr  = float(dd[dd["discount_bin"]=="0% (full price)"]["repeat_rate"].iloc[0])
h_rr   = float(dd[dd["discount_bin"]=="51%+"]["repeat_rate"].iloc[0])
chk("Full-price RR > heavy-discount RR", fp_rr > h_rr,
    f"Full price {fp_rr:.1%} vs 51%+ {h_rr:.1%}")

# 3h. RFM segments sum = total customers
rfm = pd.read_csv(OUT / "03_rfm_segments.csv")
chk("RFM segment rows = all customers", len(rfm) == len(cust),
    f"RFM rows {len(rfm):,} vs customers {len(cust):,}")

# 3i. Revenue by country — MY + SG dominate
ctry = pd.read_csv(OUT / "02_orders_by_country.csv")
top2_orders = ctry[ctry["Shipping: Country"].isin(["Malaysia","Singapore"])]["orders"].sum()
total_orders_ctry = ctry["orders"].sum()
chk("MY+SG orders > 90% of total", top2_orders / total_orders_ctry > 0.90,
    f"{top2_orders/total_orders_ctry:.1%}")

# 3j. disc_pct_orders in 2024 should be >60%
yr2 = yr[yr["year"]==2024]
if not yr2.empty:
    dp24 = float(yr2["disc_pct_orders"].iloc[0])
    chk("2024 disc_pct_orders > 60%", dp24 > 0.60, f"{dp24:.1%}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. VISUALIZATION SCRIPT HARDCODING AUDIT
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4] VISUALIZATION HARDCODING AUDIT")
import re
VIZ = BASE / "visualizations"
EXEMPT_PATTERNS = [
    r"figsize=",     # plot dimensions
    r"fontsize=",    # font
    r"linewidth=",   # line width
    r"markersize=",  # marker
    r"width=0\.",    # bar width
    r"height=0\.",   # bar height
    r"alpha=",       # transparency
    r"dpi=",         # save DPI
    r"zorder=",      # z-order
    r"lw=",          # line width alias
    r"pad=",         # padding
    r"ncol=",        # legend cols
    r"ylim\(0",      # axis limits
    r"xlim\(0",
    r"set_ylim\(0",
    r"set_xlim\(0",
    r"bbox_to_anchor",
    r"axhline\(",
    r"axvline\(",
    r"startangle=",
    r"pctdistance=",
    r"MARGIN",
    r"#",            # comments
    r'TEAL|NAVY|ORANGE|RED|SLATE|GOLD|LIGHT_BG|LILAC|GRID_LINE',
    r">= \d{2,3}",   # color thresholds
    r"> \d{2,4}",
    r"<= \d{2,3}",
    r"< \d{4}",
    r"\* 100",
    r"\* 10",
    r"/ 10",
    r"/ 1000",
    r"\+ 0\.",
    r"range\(",
    r"np\.",
    r"= 100",        # index = 100
    r"\"100\"",
    r"'100'",
]

data_list_pattern = re.compile(r"^\s*\w+\s*=\s*\[[\d\.,\s]+\]")
large_num_pattern  = re.compile(r"=\s*\d{4,}")

for py in sorted(VIZ.glob("*.py")):
    if py.name == "style.py":
        continue
    hardcoded = []
    for lineno, line in enumerate(py.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if data_list_pattern.match(line):
            exempt = any(re.search(p, line) for p in EXEMPT_PATTERNS)
            if not exempt:
                hardcoded.append(f"    L{lineno}: {stripped[:80]}")
        elif large_num_pattern.search(line):
            exempt = any(re.search(p, line) for p in EXEMPT_PATTERNS)
            if not exempt:
                hardcoded.append(f"    L{lineno}: {stripped[:80]}")
    if hardcoded:
        print(f"  [WARN] {py.name} — possible hardcoded data:")
        for h in hardcoded[:5]:
            print(h)
    else:
        print(f"  [PASS] {py.name}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. CHARTS EXIST CHECK
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5] CHART FILES")
charts = sorted((VIZ / "charts").glob("*.png"))
print(f"  Total charts: {len(charts)}")
expected = [
    "01a_revenue_discount_trend.png","01b_monthly_revenue_2024_2026.png",
    "01c_orders_customers_by_year.png","02a_retention_by_channel.png",
    "02b_retention_by_product.png","02c_time_to_second_purchase.png",
    "02d_cohort_60d_retention.png","03a_cross_product_ltv.png",
    "03b_product_revenue_mix.png","03c_sku_loyalty.png","03d_top_product_combos.png",
    "04a_subscriber_vs_onetime.png","04b_churn_by_cycle.png",
    "04c_cancellation_reasons.png","04d_churn_tenure_distribution.png",
    "05a_discount_depth_impact.png","05b_marketplace_vs_website.png",
    "05c_rfm_segments.png","05d_discount_code_taxonomy.png",
    "06a_channel_quality_dual.png",
]
for c in expected:
    chk(c, (VIZ/"charts"/c).exists())

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
if issues:
    print(f"ISSUES FOUND ({len(issues)}):  " + " | ".join(issues))
else:
    print("ALL CHECKS PASSED — pipeline is clean and numbers are consistent")
print("="*70)
