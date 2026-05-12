"""
01_load_and_merge.py  –  Load all raw sources and build the two canonical tables:

    orders_df   : one row per ORDER  (Top Row == 1 filter)
    lines_df    : one row per LINE ITEM  (Line: Type == 'Line Item' filter)

These are saved as Parquet to OUTPUT_DIR so downstream scripts can load them
instantly without re-reading all the Excel files.

Run this script once; subsequent scripts use the cached Parquet files.
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import importlib.util
from pathlib import Path

# ── load 00_config.py via importlib (leading digit prevents normal import) ─────
def _load_config():
    spec = importlib.util.spec_from_file_location(
        "lp_config", Path(__file__).parent / "00_config.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg = _load_config()
ORDER_FILES      = cfg.ORDER_FILES
PRODUCTS_FILE    = cfg.PRODUCTS_FILE
DISCOUNTS_FILE   = cfg.DISCOUNTS_FILE
RECHARGE_ORDERS      = cfg.RECHARGE_ORDERS
RECHARGE_CHECKOUT    = cfg.RECHARGE_CHECKOUT
RECHARGE_REACTIVATED = cfg.RECHARGE_REACTIVATED
RECHARGE_CHURNED     = cfg.RECHARGE_CHURNED
RECHARGE_RECURRING   = cfg.RECHARGE_RECURRING
OUTPUT_DIR       = cfg.OUTPUT_DIR
classify_product = cfg.classify_product
classify_channel = cfg.classify_channel
ANALYSIS_DATE    = cfg.ANALYSIS_DATE

# ── 1. Load all Shopify order files ───────────────────────────────────────────
print("Loading Shopify order files...")
raw_chunks = []
for f in ORDER_FILES:
    print(f"  {f.name} ...", end=" ", flush=True)
    df = pd.read_excel(f, dtype={"ID": str, "Customer: ID": str})
    print(f"{len(df):,} rows")
    raw_chunks.append(df)

raw = pd.concat(raw_chunks, ignore_index=True)
print(f"  Total rows (all line types): {len(raw):,}\n")

# ── 2. Parse dates ─────────────────────────────────────────────────────────────
raw["Processed At"] = pd.to_datetime(raw["Processed At"], utc=True, errors="coerce")
raw["order_date"]   = raw["Processed At"].dt.tz_convert("Asia/Singapore").dt.normalize()

# ── 3. Derive store / country prefix from order Name ──────────────────────────
def store_prefix(name: str) -> str:
    if pd.isna(name):
        return "Unknown"
    n = str(name).upper().replace("#", "")
    if n.startswith("LPMY"):  return "MY"
    if n.startswith("LPHK"):  return "HK"
    if n.startswith("LPSG"):  return "SG"
    if n.startswith("LP"):    return "SG"
    return "Other"

raw["store"] = raw["Name"].apply(store_prefix)

# ── 4. Order-level table (one row per order) ───────────────────────────────────
print("Building order-level table (Top Row == 1)...")
orders_cols = [
    "ID", "Name", "Tags", "order_date", "store",
    "Customer: ID", "Currency",
    "Price: Total", "Price: Total Discount", "Price: Total Shipping",
    "Payment: Status", "Order Fulfillment Status",
    "Shipping: Country", "Shipping: Country Code",
    "Browser: UTM Source", "Browser: UTM Medium", "Browser: UTM Campaign",
    "Browser: Referrer Domain",
    "Cancelled At",
    # First line-item product (present on Top Row)
    "Line: Product Handle", "Line: Title", "Line: Variant Title", "Line: SKU",
    "Line: Price", "Line: Quantity",
]
existing_cols = [c for c in orders_cols if c in raw.columns]
orders_df = raw[raw["Top Row"] == 1][existing_cols].copy()
orders_df = orders_df.rename(columns={"ID": "order_id", "Customer: ID": "customer_id"})

# Drop rows with no customer_id or no order_date (cancellations before fulfilment)
orders_df = orders_df.dropna(subset=["customer_id", "order_date"])
# Keep only paid/fulfilled orders
if "Payment: Status" in orders_df.columns:
    orders_df = orders_df[
        orders_df["Payment: Status"].isin(["paid", "partially_refunded"]) |
        orders_df["Payment: Status"].isna()
    ]
orders_df = orders_df[orders_df["Order Fulfillment Status"].fillna("") != "restocked"]

# Channel label
orders_df["channel"] = orders_df.apply(classify_channel, axis=1)
# Product category of first line item
orders_df["product_category"] = orders_df["Line: Product Handle"].apply(classify_product)
# Discount flag
orders_df["has_discount"] = orders_df["Price: Total Discount"].fillna(0) > 0
# Subscription flag from tags
orders_df["is_subscription"] = orders_df["Tags"].fillna("").str.lower().str.contains(
    "subscription|yotpo subscriptions"
)
# First-order flag from tags
orders_df["is_first_order_tag"] = orders_df["Tags"].fillna("").str.upper().str.contains("FIRST_ORDER")

print(f"  Order-level rows: {len(orders_df):,}")
print(f"  Unique customers: {orders_df['customer_id'].nunique():,}")
print(f"  Date range: {orders_df['order_date'].min().date()} to {orders_df['order_date'].max().date()}\n")

# ── 5. Line-item table ─────────────────────────────────────────────────────────
print("Building line-item table (Line: Type == 'Line Item')...")
line_cols = [
    "ID", "Customer: ID", "order_date", "store",
    "Line: Product Handle", "Line: Title", "Line: Variant Title",
    "Line: SKU", "Line: Quantity", "Line: Price", "Line: Discount", "Line: Total",
]
existing_line_cols = [c for c in line_cols if c in raw.columns]
lines_df = raw[raw["Line: Type"] == "Line Item"][existing_line_cols].copy()
lines_df = lines_df.rename(columns={"ID": "order_id", "Customer: ID": "customer_id"})
lines_df = lines_df.dropna(subset=["customer_id", "order_date"])
lines_df["product_category"] = lines_df["Line: Product Handle"].apply(classify_product)

print(f"  Line-item rows: {len(lines_df):,}\n")

# ── 6. Customer-level summary ──────────────────────────────────────────────────
print("Building customer summary table...")
cust = (
    orders_df.sort_values("order_date")
    .groupby("customer_id")
    .agg(
        first_order_date   = ("order_date", "min"),
        last_order_date    = ("order_date", "max"),
        total_orders       = ("order_id",   "count"),
        total_revenue      = ("Price: Total", "sum"),
        total_discount     = ("Price: Total Discount", "sum"),
        ever_subscribed    = ("is_subscription", "any"),
        ever_discounted    = ("has_discount",    "any"),
        first_channel      = ("channel",          "first"),
        first_product_cat  = ("product_category", "first"),
        first_store        = ("store",             "first"),
    )
    .reset_index()
)

# Cohort month
cust["cohort_month"] = cust["first_order_date"].dt.to_period("M")

# Days to second purchase (NaN if only 1 order)
second_orders = (
    orders_df.sort_values("order_date")
    .groupby("customer_id", as_index=False)
    .nth(1)
    [["customer_id", "order_date"]]
    .rename(columns={"order_date": "second_order_date"})
)
cust = cust.merge(second_orders, on="customer_id", how="left")
cust["days_to_second"] = (
    cust["second_order_date"] - cust["first_order_date"]
).dt.days

# Repeat flag (2+ orders)
cust["is_repeat"] = cust["total_orders"] >= 2

# Customer lifespan in days
cust["lifespan_days"] = (
    cust["last_order_date"] - cust["first_order_date"]
).dt.days

# Days since last order (recency for RFM)
cust["recency_days"] = (ANALYSIS_DATE - cust["last_order_date"]).dt.days

print(f"  Customer rows: {len(cust):,}")
print(f"  Overall repeat rate: {cust['is_repeat'].mean():.1%}\n")

# ── 7. Load ancillary tables ───────────────────────────────────────────────────
print("Loading ancillary tables...")
products_df   = pd.read_excel(PRODUCTS_FILE)
discounts_df  = pd.read_csv(DISCOUNTS_FILE, encoding="utf-8", encoding_errors="replace")

rc_orders     = pd.read_excel(RECHARGE_ORDERS)
rc_checkout   = pd.read_excel(RECHARGE_CHECKOUT)
rc_reactivated= pd.read_excel(RECHARGE_REACTIVATED)
rc_churned    = pd.read_excel(RECHARGE_CHURNED)
rc_recurring  = pd.read_excel(RECHARGE_RECURRING)

for tbl, name in [
    (products_df,"products"), (discounts_df,"discounts"),
    (rc_orders,"rc_orders"), (rc_checkout,"rc_checkout"),
    (rc_reactivated,"rc_reactivated"), (rc_churned,"rc_churned"),
    (rc_recurring,"rc_recurring"),
]:
    print(f"  {name}: {len(tbl):,} rows")

# ── 8. Coerce mixed-type object columns → clean strings before saving ─────────
def clean_object_cols(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].where(df[col].notna(), other=pd.NA)
        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else pd.NA)
    return df

orders_df = clean_object_cols(orders_df)
lines_df  = clean_object_cols(lines_df)
cust      = clean_object_cols(cust)

# ── 9. Save Parquet ────────────────────────────────────────────────────────────
print("\nSaving Parquet files to", OUTPUT_DIR)
orders_df.to_parquet(OUTPUT_DIR / "orders.parquet", index=False)
lines_df .to_parquet(OUTPUT_DIR / "lines.parquet",  index=False)
cust     .to_parquet(OUTPUT_DIR / "customers.parquet", index=False)
products_df  .to_parquet(OUTPUT_DIR / "products.parquet",   index=False)
discounts_df .to_parquet(OUTPUT_DIR / "discounts.parquet",  index=False)
rc_orders    .to_parquet(OUTPUT_DIR / "rc_orders.parquet",     index=False)
rc_checkout  .to_parquet(OUTPUT_DIR / "rc_checkout.parquet",   index=False)
rc_reactivated.to_parquet(OUTPUT_DIR / "rc_reactivated.parquet", index=False)
rc_churned   .to_parquet(OUTPUT_DIR / "rc_churned.parquet",    index=False)
rc_recurring .to_parquet(OUTPUT_DIR / "rc_recurring.parquet",  index=False)

print("Done.  All tables cached.\n")
print("="*60)
print("QUICK SUMMARY")
print("="*60)
print(f"Orders (all years):        {len(orders_df):>8,}")
print(f"Line items:                {len(lines_df):>8,}")
print(f"Unique customers:          {cust['customer_id'].nunique():>8,}")
print(f"Repeat customers (2+ ord): {cust['is_repeat'].sum():>8,}")
print(f"Overall repeat rate:       {cust['is_repeat'].mean():>8.1%}")
print(f"Median days to 2nd order:  {cust['days_to_second'].median():>8.0f} days")
print(f"Ever-subscribed customers: {cust['ever_subscribed'].sum():>8,}")
