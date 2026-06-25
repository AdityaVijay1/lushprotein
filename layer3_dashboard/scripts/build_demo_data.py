"""Build anonymized demo datasets for the Layer 3 dashboard."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
sys.path.insert(0, str(ROOT))

from l3_engine import DEMO_TODAY, LOOKBACK_DAYS, format_customer_id_display, normalize_customer_id

DATA_DIR = ROOT / "data"
CUSTOMERS_SRC = PROJECT / "1.customer_transaction" / "customers_export_20260622.xlsx"
ORDERS_SRC = PROJECT / "EDA" / "outputs_finals" / "orders.parquet"
RULES_SRC = PROJECT / "EDA" / "aditya_findings" / "outputs" / "cross_sell_timing_and_samples.csv"

DEMO_NAMES = [
    ("Aditya Vijay", "Ang Mo Kio"),
    ("Shwe Tin Aung", "Bishan"),
    ("Marcus Tan", "Tampines"),
    ("Priya Sharma", "Jurong West"),
    ("Daniel Koh", "Bedok"),
    ("Emily Wong", "Woodlands"),
    ("Ryan Lim", "Punggol"),
    ("Siti Rahman", "Hougang"),
    ("James Lee", "Clementi"),
    ("Nadia Hassan", "Serangoon"),
    ("Kevin Ng", "Yishun"),
    ("Chloe Tan", "Toa Payoh"),
    ("Arjun Patel", "Bukit Batok"),
    ("Mei Lin Chen", "Queenstown"),
    ("Omar Ibrahim", "Pasir Ris"),
]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    orders = pd.read_parquet(ORDERS_SRC)
    orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.tz_localize(None)
    orders["customer_id"] = orders["customer_id"].apply(normalize_customer_id)

    order_counts = orders.groupby("customer_id").size().reset_index(name="order_count")
    first_orders = (
        orders.sort_values("order_date")
        .groupby("customer_id", as_index=False)
        .first()
        .merge(order_counts, on="customer_id")
    )

    # Use recent first-time buyers; shift dates into demo window around DEMO_TODAY
    ref = DEMO_TODAY
    cutoff = ref - timedelta(days=LOOKBACK_DAYS)
    pool = first_orders[first_orders["order_count"] == 1].copy()
    pool = pool.sort_values("order_date", ascending=False).head(120)

    if pool.empty:
        raise SystemExit("No eligible customers found in order data.")

    # Spread purchase dates across last 30 days for demo realism
    n = len(pool)
    demo_dates = [ref - timedelta(days=int(i * (LOOKBACK_DAYS - 1) / max(n - 1, 1))) for i in range(n)]
    pool = pool.reset_index(drop=True)
    pool["demo_order_date"] = demo_dates

    # Load customer export for join (names anonymized regardless)
    cust_export = pd.read_excel(
        CUSTOMERS_SRC,
        usecols=["Customer ID", "First Name", "Last Name", "Default Address City"],
    )
    cust_export["customer_id"] = cust_export["Customer ID"].apply(normalize_customer_id)

    demo_customers = []
    demo_transactions = []

    for idx, (_, row) in enumerate(pool.iterrows()):
        cid = row["customer_id"]
        name, area = DEMO_NAMES[idx % len(DEMO_NAMES)]
        demo_customers.append(
            {
                "customer_id": cid,
                "customer_id_display": format_customer_id_display(cid),
                "name": name,
                "address_area": area,
            }
        )
        product_name = row.get("Line: Title") or row.get("product_category") or "Unknown"
        demo_transactions.append(
            {
                "customer_id": cid,
                "order_id": row["order_id"],
                "order_date": row["demo_order_date"].strftime("%Y-%m-%d"),
                "product_category": row.get("product_category") or "Unknown",
                "product_name": str(product_name),
                "order_count": 1,
            }
        )

    customers_df = pd.DataFrame(demo_customers)
    customers_df["customer_id"] = customers_df["customer_id"].astype(str)
    customers_df.to_csv(DATA_DIR / "customers_demo.csv", index=False)

    tx_df = pd.DataFrame(demo_transactions)
    tx_df["customer_id"] = tx_df["customer_id"].astype(str)
    tx_df.to_csv(DATA_DIR / "transactions_demo.csv", index=False)

    if RULES_SRC.exists():
        rules = pd.read_csv(RULES_SRC)
        keep = [
            "first_product_category",
            "cross_sell_category",
            "sample_product_suggestion",
            "email_cross_sell_day_after_delivery",
            "physical_sample_day_after_delivery",
            "median_reorder_days",
        ]
        rules[keep].to_csv(DATA_DIR / "cross_sell_rules.csv", index=False)
    else:
        from l3_engine import DEFAULT_RULES

        DEFAULT_RULES.to_csv(DATA_DIR / "cross_sell_rules.csv", index=False)

    print(f"Built {len(demo_customers)} demo customers -> {DATA_DIR / 'customers_demo.csv'}")
    print(f"Built {len(demo_transactions)} transactions -> {DATA_DIR / 'transactions_demo.csv'}")
    print(f"Sample lookup IDs:")
    for c in demo_customers[:5]:
        print(f"  {c['customer_id_display']}  ({c['name']})")


if __name__ == "__main__":
    main()
