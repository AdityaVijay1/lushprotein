"""Verify ERD + STTM against course requirements."""
import re
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root = Path(__file__).resolve().parent.parent

# --- ERD column coverage ---
text = (root / "Group1_ERD.drawio").read_text(encoding="utf-8")
tables = re.findall(
    r'id="[^"]+"[^>]*style="[^"]*shape=table;[^"]*"[^>]*value="([^"]+)"',
    text,
)
print("=" * 60)
print("REQ 3: ERD (Group1_ERD.drawio)")
print("=" * 60)
print(f"File format: .drawio — OK ({(root/'Group1_ERD.drawio').exists()})")
print(f"Entities ({len(tables)}):")
for t in tables:
    print(f"  - {t.replace(chr(10), ' / ')}")

datasets = {
    "ORDERS": ("1.customer_transaction", 69),
    "PRODUCT MASTER": ("2.product_master", 24),
    "DISCOUNTS": ("3.Discounts", 17),
    "SESSIONS BY REFERRER": ("4.Campaigns", 10),
}
# recharge files
recharge = [
    ("RECHARGE ORDERS", 10),
    ("ORDER ITEMS CHECKOUT", 14),
    ("SUBSCRIBERS REACTIVATED", 4),
    ("SUBSCRIPTIONS CHURNED", 12),
    ("ORDER ITEMS RECURRING", 14),
]

# run audit_erd logic inline
cells = re.findall(
    r'<mxCell id="([^"]+)" parent="([^"]+)"[^>]*value="([^"]*)" vertex="1"',
    text,
)
by_parent = {}
for cid, parent, val in cells:
    by_parent.setdefault(parent, []).append(val)


def descendants(rid):
    out = []
    for val in by_parent.get(rid, []):
        out.append(val)
        out.extend(descendants(val))
    return out


table_id_map = {}
for m in re.finditer(
    r'id="([^"]+)"[^>]*style="[^"]*shape=table;[^"]*"[^>]*value="([^"]+)"',
    text,
):
    table_id_map[m.group(1)] = m.group(2)


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
        elif v and any(x in v for x in ("VARCHAR", "BIGINT", "DECIMAL", "INT", "BOOL", "DATE", "TEXT")):
            fields.append(v)
            i += 1
        else:
            i += 1
    return fields


erd_ok = True
for tid, name in table_id_map.items():
    if name in ("CUSTOMERS (derived)",):
        print(f"  [extra logical] {name}: {len(entity_fields(tid))} fields")
        continue
    n = len(entity_fields(tid))
    expected = None
    for k, (_, exp) in datasets.items():
        if k in name or name in k:
            expected = exp
    for k, exp in recharge:
        if k == name:
            expected = exp
    if expected:
        status = "OK" if n >= expected else f"GAP ({n} vs {expected})"
        if n < expected:
            erd_ok = False
        print(f"  {name}: ERD={n}, required={expected} -> {status}")

# PK/FK sanity
print("\nORDERS key markers:")
for tid, name in table_id_map.items():
    if name == "ORDERS":
        for f in entity_fields(tid):
            fn = f.split()[0].lower()
            if fn in (
                "checkout_id",
                "customer_id",
                "line_product_handle",
                "line_sku",
                "line_variant_id",
                "line_product_id",
                "id",
                "line_id",
            ):
                print(f"  {f}")

# edges
edges = len(re.findall(r'edge="1"', text))
print(f"\nRelationship edges: {edges}")
print("SHOPIFY_CHECKOUT present:", "SHOPIFY_CHECKOUT" in text)

# --- STTM ---
print("\n" + "=" * 60)
print("REQ 4: STTM (Customer Transactions / 1.orders only)")
print("=" * 60)
xlsx = root / "LushProtein_Source_to_Target_Mapping_Exercise.xlsx"
xl = pd.ExcelFile(xlsx)
print(f"Sheets: {xl.sheet_names}")
print("Scope: 1.orders sheet only required — OK" if "1.orders" in xl.sheet_names else "MISSING 1.orders")

team = pd.read_excel(xlsx, sheet_name="1.orders", header=1)
team = team[team["target_column"].notna()].copy()
raw_cols = list(
    pd.read_excel(
        sorted((root / "1.customer_transaction").glob("**/*.xlsx"))[0], nrows=0
    ).columns
)

req_headers = [
    "target_column",
    "target_data_type",
    "pk_fk",
    "source_file(s)",
    "source_column",
    "source_data_type",
    "transformation",
    "notes / business rule",
]
headers_ok = list(team.columns) == req_headers
print(f"8-column format matches example: {headers_ok}")

missing = [c for c in raw_cols if c not in team["source_column"].values]
print(f"All 69 raw columns mapped: {len(missing) == 0} ({len(missing)} missing)")
for c in missing:
    print(f"  MISSING: {c}")

derived = team[~team["source_column"].isin(raw_cols)]
print(f"Pipeline-derived rows (allowed): {len(derived)}")
for _, r in derived.iterrows():
    print(f"  + {r['target_column']}")

# PK/FK rules
rules = {
    "id": "PK",
    "customer_id": "FK -> customer",
    "checkout_id": "",  # blank
    "line_id": "PK",
    "line_product_handle": "FK -> products.Handle",
    "line_sku": "FK -> products.Variant SKU",
    "line_variant_id": "",
    "line_product_id": "",
}
sttm_ok = True
for col, exp in rules.items():
    row = team[team["target_column"] == col]
    if row.empty:
        print(f"  STTM missing row: {col}")
        sttm_ok = False
        continue
    val = row.iloc[0]["pk_fk"]
    val_s = "" if pd.isna(val) else str(val).strip()
    ok = val_s == exp or (exp and exp in val_s)
    if not ok:
        sttm_ok = False
    print(f"  {col}: pk_fk={val_s!r} expected={exp!r} -> {'OK' if ok else 'FAIL'}")

# Example comparison
ex = pd.read_excel(root / "LushProtein_Source_to_Target_Mapping_Example.xlsx", header=1)
print(f"\nExample STTM rows: {len(ex)} (products reference)")
print(f"Team STTM rows: {len(team)} (69 raw + {len(derived)} derived)")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"ERD column coverage: {'PASS' if erd_ok else 'REVIEW'}")
print(f"ERD file type .drawio: PASS")
print(f"STTM format + orders scope: {'PASS' if headers_ok and len(missing)==0 else 'REVIEW'}")
print(f"STTM PK/FK rules: {'PASS' if sttm_ok else 'REVIEW'}")
