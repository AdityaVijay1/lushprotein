"""
02_data_quality.py    “  Data quality audit and descriptive overview.

Outputs
-------
outputs/02_data_quality_report.txt    “  full text report
outputs/02_orders_by_year.csv
outputs/02_orders_by_country.csv
outputs/02_orders_by_channel.csv
outputs/02_revenue_by_month.csv

Run AFTER 01_load_and_merge.py
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import importlib.util
from pathlib import Path

def _load_config():
    spec = importlib.util.spec_from_file_location(
        "lp_config", Path(__file__).parent / "00_config.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg = _load_config()
OUTPUT_DIR = cfg.OUTPUT_DIR

#      Load cached tables                                                                                                                   
print("Loading cached tables...")
orders = pd.read_parquet(OUTPUT_DIR / "orders.parquet")
lines  = pd.read_parquet(OUTPUT_DIR / "lines.parquet")
cust   = pd.read_parquet(OUTPUT_DIR / "customers.parquet")
disc   = pd.read_parquet(OUTPUT_DIR / "discounts.parquet")
prod   = pd.read_parquet(OUTPUT_DIR / "products.parquet")

lines["order_date"] = pd.to_datetime(lines["order_date"], utc=True)
orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
cust["first_order_date"] = pd.to_datetime(cust["first_order_date"], utc=True)

report_lines = []
def p(msg=""):
    print(msg)
    report_lines.append(msg)

p("=" * 70)
p("LUSHPROTEIN EDA    “  DATA QUALITY & OVERVIEW REPORT")
p("=" * 70)

#      1. Table dimensions                                                                                                               
p("\n[1] TABLE DIMENSIONS")
p(f"  Orders (order-level):    {len(orders):>8,}")
p(f"  Line items:              {len(lines):>8,}")
p(f"  Customers:               {len(cust):>8,}")
p(f"  Products:                {len(prod):>8,}")
p(f"  Discount codes:          {len(disc):>8,}")

#      2. Date range                                                                                                                           
p("\n[2] DATE RANGE")
p(f"  Earliest order: {orders['order_date'].min().date()}")
p(f"  Latest order:   {orders['order_date'].max().date()}")
p(f"  Cohort span:    {orders['order_date'].dt.year.min()}   “ {orders['order_date'].dt.year.max()}")

#      3. Orders by year                                                                                                                   
p("\n[3] ORDERS BY YEAR")
by_year = (
    orders.assign(year=orders["order_date"].dt.year)
    .groupby("year")
    .agg(
        orders      = ("order_id",       "count"),
        customers   = ("customer_id",    "nunique"),
        revenue_sgd = ("Price: Total",   "sum"),
        disc_amt    = ("Price: Total Discount", "sum"),
    )
    .assign(avg_order_value=lambda d: d["revenue_sgd"] / d["orders"],
            disc_rate      =lambda d: d["disc_amt"]    / d["revenue_sgd"])
)
p(by_year.to_string())
by_year.to_csv(OUTPUT_DIR / "02_orders_by_year.csv")

#      4. Orders by country                                                                                                             
p("\n[4] ORDERS BY COUNTRY")
by_country = (
    orders.groupby("Shipping: Country")
    .agg(orders=("order_id","count"), revenue=("Price: Total","sum"))
    .sort_values("orders", ascending=False)
    .head(10)
)
p(by_country.to_string())
by_country.to_csv(OUTPUT_DIR / "02_orders_by_country.csv")

#      5. Orders by channel                                                                                                             
p("\n[5] ORDERS BY CHANNEL")
by_channel = (
    orders.groupby("channel")
    .agg(
        orders    = ("order_id",   "count"),
        customers = ("customer_id","nunique"),
        revenue   = ("Price: Total","sum"),
        disc_amt  = ("Price: Total Discount","sum"),
    )
    .assign(aov       =lambda d: d["revenue"]  / d["orders"],
            disc_rate =lambda d: d["disc_amt"] / d["revenue"].replace(0,1))
    .sort_values("orders", ascending=False)
)
p(by_channel.to_string())
by_channel.to_csv(OUTPUT_DIR / "02_orders_by_channel.csv")

#      6. Monthly revenue trend                                                                                                     
p("\n[6] MONTHLY REVENUE TREND (SGD)")
monthly = (
    orders.assign(month=orders["order_date"].dt.to_period("M"))
    .groupby("month")
    .agg(orders=("order_id","count"), revenue=("Price: Total","sum"))
)
# Show only last 24 months for brevity
p(monthly.tail(24).to_string())
monthly.to_csv(OUTPUT_DIR / "02_revenue_by_month.csv")

#      7. Null-rate audit on key columns                                                                                   
p("\n[7] NULL-RATE AUDIT (order-level key columns)")
key_cols = [
    "customer_id", "order_date", "Price: Total", "Price: Total Discount",
    "channel", "product_category", "Shipping: Country",
    "Browser: UTM Source", "Tags",
]
for col in key_cols:
    if col in orders.columns:
        null_pct = orders[col].isna().mean()
        p(f"  {col:<35}  {null_pct:>6.1%} null")

#      8. Payment & fulfilment status breakdown                                                                     
p("\n[8] PAYMENT STATUS")
p(orders["Payment: Status"].value_counts(dropna=False).to_string())

p("\n[9] FULFILMENT STATUS")
p(orders["Order Fulfillment Status"].value_counts(dropna=False).to_string())

#      10. Product master: hero SKU coverage                                                                           
p("\n[10] PRODUCT MASTER   “ active SKUs by category")
if "Status" in prod.columns:
    active_prod = prod[prod["Status"] == "active"].copy()
else:
    active_prod = prod.copy()

# Tag with product category using Handle
from importlib.util import spec_from_file_location, module_from_spec
spec2 = spec_from_file_location("lp_config2", Path(__file__).parent / "00_config.py")
cfg2  = module_from_spec(spec2); spec2.loader.exec_module(cfg2)
active_prod["category"] = active_prod["Handle"].apply(cfg2.classify_product)
p(active_prod["category"].value_counts().to_string())

#      11. Discount code overview                                                                                                 
p("\n[11] DISCOUNT CODE OVERVIEW")
p(f"  Total codes:          {len(disc):,}")
p(f"  Active codes:         {(disc['Status']=='Active').sum():,}")
p(f"  Codes with >0 uses:   {(disc['Times Used In Total'] > 0).sum():,}")
p(f"  Total redemptions:    {disc['Times Used In Total'].sum():,.0f}")
p("\n  By Value Type:")
p(disc.groupby("Value Type")["Times Used In Total"].sum().to_string())
p("\n  By Type:")
p(disc.groupby("Type")["Times Used In Total"].sum().sort_values(ascending=False).to_string())

#      Save report                                                                                                                                 
report_path = OUTPUT_DIR / "02_data_quality_report.txt"
report_path.write_text("\n".join(report_lines), encoding="utf-8")
p(f"\nReport saved to {report_path}")

