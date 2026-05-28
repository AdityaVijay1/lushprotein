"""Audit Group1_ERD.drawio column coverage vs raw datasets."""
import re
from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent
text = (root / "Group1_ERD.drawio").read_text(encoding="utf-8")

# Entity -> list of column names from ERD (field cells only)
tables = re.findall(
    r'id="([^"]+)"[^>]*style="[^"]*shape=table;[^"]*"[^>]*value="([^"]+)"',
    text,
)
table_ids = {tid: name for tid, name in tables}

cells = re.findall(
    r'<mxCell id="([^"]+)" parent="([^"]+)"[^>]*value="([^"]*)" vertex="1"',
    text,
)
by_parent = {}
for cid, parent, val in cells:
    by_parent.setdefault(parent, []).append((cid, val))


def descendants(root_id):
    out = []
    for cid, val in by_parent.get(root_id, []):
        out.append(val)
        out.extend(descendants(cid))
    return out


def entity_fields(table_id):
    desc = descendants(table_id)
    fields = []
    i = 0
    while i < len(desc):
        v = desc[i]
        if v in ("PK", "FK"):
            if i + 1 < len(desc):
                fields.append(desc[i + 1])
            i += 2
        elif v and v not in ("",):
            # attribute row: may be empty key col then field
            if " " in v and any(t in v for t in ("VARCHAR", "BIGINT", "DECIMAL", "INT", "BOOL", "DATETIME", "TEXT")):
                fields.append(v)
            i += 1
        else:
            i += 1
    return fields


print("=== ERD ENTITY FIELD COUNTS ===\n")
entity_counts = {}
for tid, name in tables:
    f = entity_fields(tid)
    entity_counts[name] = len(f)
    print(f"{name}: {len(f)} fields")

# Raw datasets
datasets = {
    "ORDERS (expected 69)": list(pd.read_excel(
        sorted((root / "1.customer_transaction").glob("**/*.xlsx"))[0], nrows=0
    ).columns),
    "PRODUCT MASTER (expected 24)": list(pd.read_excel(
        sorted((root / "2.product_master").glob("**/*.xlsx"))[0], nrows=0
    ).columns),
    "DISCOUNTS (expected 17)": list(pd.read_csv(
        sorted((root / "3.Discounts").glob("**/*.csv"))[0], nrows=0
    ).columns),
    "SESSIONS (expected 10)": list(pd.read_csv(
        sorted((root / "4.Campaigns").glob("**/*.csv"))[0], nrows=0
    ).columns),
    "RECHARGE ORDERS (10)": list(pd.read_excel(
        root / "5.Recharge_data" / "5_1.orders_combined_20260505.xlsx", nrows=0
    ).columns),
    "ORDER ITEMS CHECKOUT (14)": list(pd.read_excel(
        root / "5.Recharge_data" / "5_2.order_items_checkout_20260505.xlsx", nrows=0
    ).columns),
    "SUBSCRIBERS REACTIVATED (4)": list(pd.read_excel(
        root / "5.Recharge_data" / "5_3.subscribers_reactivated_20260505.xlsx", nrows=0
    ).columns),
    "SUBSCRIPTIONS CHURNED (12)": list(pd.read_excel(
        root / "5.Recharge_data" / "5_4.subscriptions_churned_20260505.xlsx", nrows=0
    ).columns),
    "ORDER ITEMS RECURRING (14)": list(pd.read_excel(
        root / "5.Recharge_data" / "5_5.order_items_recurring_20260505.xlsx", nrows=0
    ).columns),
}

print("\n=== RAW DATASET COLUMN COUNTS ===\n")
for k, cols in datasets.items():
    print(f"{k}: {len(cols)}")

print("\n=== COVERAGE GAP SUMMARY ===\n")
mapping = [
    ("ORDERS", "ORDERS (expected 69)", 69),
    ("PRODUCT MASTER", "PRODUCT MASTER (expected 24)", 24),
    ("DISCOUNTS", "DISCOUNTS (expected 17)", 17),
    ("SESSIONS BY REFERRER", "SESSIONS (expected 10)", 10),
    ("RECHARGE ORDERS", "RECHARGE ORDERS (10)", 10),
    ("ORDER ITEMS CHECKOUT", "ORDER ITEMS CHECKOUT (14)", 14),
    ("SUBSCRIBERS REACTIVATED", "SUBSCRIBERS REACTIVATED (4)", 4),
    ("SUBSCRIPTIONS CHURNED", "SUBSCRIPTIONS CHURNED (12)", 12),
    ("ORDER ITEMS RECURRING", "ORDER ITEMS RECURRING (14)", 14),
]
for erd_name, raw_key, expected in mapping:
    erd_n = entity_counts.get(erd_name, 0)
    raw_n = len(datasets[raw_key])
    status = "OK" if erd_n >= expected else f"GAP ({erd_n} vs {expected})"
    print(f"  {erd_name}: ERD={erd_n}, Raw={raw_n} -> {status}")
