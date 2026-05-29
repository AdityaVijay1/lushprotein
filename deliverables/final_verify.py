"""Final submission verification: ERD + STTM cross-check."""
import re
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root = Path(__file__).resolve().parent.parent
issues = []
warnings = []
passed = []

# --- Load STTM ---
xlsx = root / "LushProtein_Source_to_Target_Mapping_Exercise.xlsx"
team = pd.read_excel(xlsx, sheet_name="1.orders", header=1)
team = team[team["target_column"].notna()].copy()
raw_cols = list(
    pd.read_excel(sorted((root / "1.customer_transaction").glob("**/*.xlsx"))[0], nrows=0).columns
)

# --- Load ERD ---
text = (root / "Group1_ERD.drawio").read_text(encoding="utf-8")
cells = re.findall(
    r'<mxCell id="([^"]+)" parent="([^"]+)"[^>]*value="([^"]*)" vertex="1"',
    text,
)
by_parent = {}
for cid, parent, val in cells:
    by_parent.setdefault(parent, []).append((cid, val))

table_id_map = {}
for m in re.finditer(
    r'id="([^"]+)"[^>]*style="[^"]*shape=table;[^"]*"[^>]*value="([^"]+)"',
    text,
):
    table_id_map[m.group(1)] = m.group(2).replace("&#xa;", " / ")


def descendants(rid):
    out = []
    for cid, val in by_parent.get(rid, []):
        out.append(val)
        out.extend(descendants(cid))
    return out


def entity_pk_fk(table_id):
    desc = descendants(table_id)
    rows = []
    i = 0
    while i < len(desc):
        v = desc[i]
        if v in ("PK", "FK"):
            field = desc[i + 1] if i + 1 < len(desc) else "?"
            rows.append((v, field.split()[0].lower()))
            i += 2
        elif v and any(t in v for t in ("VARCHAR", "BIGINT", "DECIMAL", "INT", "BOOL", "DATE", "TEXT")):
            rows.append(("", v.split()[0].lower()))
            i += 1
        else:
            i += 1
    return rows


def count_fields(table_id):
    return len([r for r in entity_pk_fk(table_id) if r[1] and r[1] not in ("pk", "fk")])


print("=" * 70)
print("FINAL SUBMISSION VERIFICATION")
print("=" * 70)

# REQ: file formats
if (root / "Group1_ERD.drawio").suffix == ".drawio":
    passed.append("ERD submitted as .drawio")
else:
    issues.append("ERD must be .drawio")

if "1.orders" in pd.ExcelFile(xlsx).sheet_names:
    passed.append("STTM has 1.orders sheet (customer transactions)")
else:
    issues.append("STTM missing 1.orders sheet")

req_headers = [
    "target_column", "target_data_type", "pk_fk", "source_file(s)",
    "source_column", "source_data_type", "transformation", "notes / business rule",
]
if list(team.columns) == req_headers:
    passed.append("STTM 8-column format matches example")
else:
    issues.append(f"STTM headers mismatch: {list(team.columns)}")

# STTM: all raw columns
missing_raw = [c for c in raw_cols if c not in team["source_column"].values]
if not missing_raw:
    passed.append(f"STTM maps all {len(raw_cols)} raw order columns")
else:
    issues.append(f"STTM missing raw columns: {missing_raw}")

# STTM PK/FK rules (cross-check ERD)
sttm_rules = {
    "order_id": "PK",
    "customer_id": "FK",
    "checkout_id": "",
    "line_id": "PK",
    "line_product_handle": "FK",
    "line_sku": "FK",
    "line_variant_sku": "FK",
    "line_product_id": "",
    "line_variant_id": "",
}
for col, exp in sttm_rules.items():
    row = team[team["target_column"] == col]
    if row.empty:
        issues.append(f"STTM missing row: {col}")
        continue
    val = "" if pd.isna(row.iloc[0]["pk_fk"]) else str(row.iloc[0]["pk_fk"]).strip()
    if exp == "" and val:
        issues.append(f"STTM {col}: should have blank pk_fk, got {val!r}")
    elif exp == "PK" and "PK" not in val:
        issues.append(f"STTM {col}: expected PK, got {val!r}")
    elif exp == "FK" and "FK" not in val:
        issues.append(f"STTM {col}: expected FK, got {val!r}")
    elif exp == "FK" and "FK" in val:
        passed.append(f"STTM {col}: FK OK")
    elif exp == "PK" and "PK" in val:
        passed.append(f"STTM {col}: PK OK")
    elif exp == "":
        passed.append(f"STTM {col}: not FK OK")

# ERD column counts
expected = {
    "ORDERS": 69,
    "PRODUCT MASTER": 24,
    "DISCOUNTS": 17,
    "SESSIONS BY REFERRER": 10,
}
recharge_exp = {
    "RECHARGE ORDERS": 10,
    "ORDER ITEMS CHECKOUT": 14,
    "ORDER ITEMS RECURRING": 14,
    "SUBSCRIBERS REACTIVATED": 4,
    "SUBSCRIPTIONS CHURNED": 12,
}
for tid, name in table_id_map.items():
    base = name.split(" / ")[0]
    n = count_fields(tid)
    if base in expected:
        if n >= expected[base]:
            passed.append(f"ERD {base}: {n}/{expected[base]} columns")
        else:
            issues.append(f"ERD {base}: {n} fields, need {expected[base]}")
    elif base in recharge_exp:
        if n >= recharge_exp[base] - 1:  # PK row may reduce count
            passed.append(f"ERD {base}: {n} fields (incl. PK)")
        else:
            warnings.append(f"ERD {base}: {n} fields, raw has {recharge_exp[base]}")

# ERD ORDERS PK/FK cross-check with STTM
orders_tid = next((t for t, n in table_id_map.items() if n.startswith("ORDERS")), None)
if orders_tid:
    erd_pf = {name: key for key, name in entity_pk_fk(orders_tid) if name}
    erd_sttm_map = {
        "id": ("order_id", "PK"),
        "checkout_id": ("checkout_id", ""),
        "customer_id": ("customer_id", "FK"),
        "line_id": ("line_id", "PK"),
        "line_product_handle": ("line_product_handle", "FK"),
        "line_product_id": ("line_product_id", ""),
        "line_variant_id": ("line_variant_id", ""),
        "line_sku": ("line_sku", "FK"),
        "line_variant_sku": ("line_variant_sku", "FK"),
    }
    for erd_col, (sttm_col, want) in erd_sttm_map.items():
        erd_key = erd_pf.get(erd_col, "MISSING")
        if want == "PK" and erd_key != "PK":
            issues.append(f"ERD {erd_col}: expected PK, key={erd_key!r}")
        elif want == "FK" and erd_key != "FK":
            issues.append(f"ERD {erd_col}: expected FK, key={erd_key!r}")
        elif want == "" and erd_key == "FK":
            issues.append(f"ERD {erd_col}: should not be FK")
        else:
            passed.append(f"ERD-STTM align: {erd_col} ({erd_key or 'attr'})")

# ERD structural checks
if "SHOPIFY_CHECKOUT" in text:
    issues.append("ERD still contains SHOPIFY_CHECKOUT (should be removed)")
else:
    passed.append("ERD: no SHOPIFY_CHECKOUT box")

if "source VARCHAR" in text or "source VARCHAR(50)" in text:
    passed.append("ERD: source is VARCHAR")
elif "source BIGINT" in text:
    issues.append("ERD: source still BIGINT")

if "shipping_province_code" in text:
    passed.append("ERD: shipping_province_code spelling OK")
elif "shipping province_code" in text:
    issues.append("ERD: shipping province_code typo remains")

if "line_variant_SKU" in text and 'value="FK"' in text:
    # check FK on variant sku row - grep nearby
    if re.search(r'449[^>]*value="FK"', text) or re.search(r'line_variant_SKU[^"]*" vertex="1"[^>]*fontStyle=1', text):
        passed.append("ERD: line_variant_SKU marked FK")
    else:
        warnings.append("ERD: verify line_variant_SKU FK marker manually")

if "dashed=1" in text and "DQ-10" in text:
    passed.append("ERD: DISCOUNTS conceptual (dashed)")
if "shopify_order_id" in text and "DQ-11" in text:
    passed.append("ERD: Recharge join note present")

if "CUSTOMERS (derived)" in text:
    passed.append("ERD: CUSTOMERS (derived) present")

# STTM empty rows
hdr = team[team["target_column"].astype(str).str.contains("Derived", na=False)]
if len(hdr) == 1 and pd.isna(hdr.iloc[0]["transformation"]):
    warnings.append("STTM section header row has empty transformation (acceptable)")

empty_trans = team[team["transformation"].isna() & ~team["target_column"].astype(str).str.contains("Derived", na=False)]
if len(empty_trans):
    issues.append(f"STTM rows missing transformation: {empty_trans['target_column'].tolist()}")

# store derived must exist
if team[team["target_column"] == "store"].empty:
    issues.append("STTM missing store derived column")
else:
    passed.append("STTM: store derived column present")

print("\n--- PASSED (%d) ---" % len(passed))
for p in passed:
    print(f"  [OK] {p}")

if warnings:
    print("\n--- WARNINGS (%d) ---" % len(warnings))
    for w in warnings:
        print(f"  [WARN] {w}")

print("\n--- ISSUES (%d) ---" % len(issues))
for i in issues:
    print(f"  [FAIL] {i}")

print("\n" + "=" * 70)
if not issues:
    print("VERDICT: READY TO SUBMIT")
elif len(issues) <= 2:
    print("VERDICT: FIX ISSUES BEFORE SUBMIT")
else:
    print("VERDICT: NOT READY — address issues above")
print("=" * 70)
