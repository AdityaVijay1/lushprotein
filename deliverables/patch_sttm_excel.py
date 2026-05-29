"""Patch derived-row refinements in LushProtein_Source_to_Target_Mapping_Exercise.xlsx (sheet 1.orders)."""
from pathlib import Path

from openpyxl import load_workbook

BASE = Path(__file__).resolve().parent.parent
XLSX = BASE / "LushProtein_Source_to_Target_Mapping_Exercise.xlsx"
SOURCE_FILES = "1.customer_transaction/1_*.orders-YYYY_20260505.xlsx"

PATCHES = {
    "processed_at": {
        "notes / business rule": (
            "Payment/process timestamp (SGT). Raw export column; pipeline also builds "
            "normalized order_date from this field (see derived order_date row). Not Created At."
        ),
    },
    "order_date": {
        "notes / business rule": (
            "Derived in 01_load_and_merge.py from Processed At: same source as processed_at, "
            "normalized to date-only in Asia/Singapore. Not a separate raw export column."
        ),
    },
    "store": {
        "notes / business rule": "Derived market code - not in raw export. Required for FX conversion.",
    },
    "checkout_id": {
        "notes / business rule": "order-level attribute only (Top Row = 1). ~65% null. No FK - no checkout table in project.",
    },
    "line_variant_title": {
        "notes / business rule": "Flavor/pack-size label - use for SKU/flavor-level analysis.",
    },
    "product_category": {
        "notes / business rule": (
            "Derived product family - not a product-master join. "
            "Order grain (Top Row=1): first line item handle. "
            "Line grain (Line Item): each line handle."
        ),
    },
    "total_revenue": {
        "source_file(s)": f"{SOURCE_FILES} -> orders.parquet -> customers.parquet",
        "notes / business rule": (
            "Customer-level derived (customers.parquet). "
            "Customer LTV = SUM(Price: Total SGD) per customer_id. Used in finals analysis."
        ),
    },
    "is_repeat": {
        "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
        "notes / business rule": "Customer-level derived (customers.parquet). Repeat customer flag.",
    },
    "ever_subscribed": {
        "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
        "notes / business rule": (
            "Customer-level derived (customers.parquet). Ever had a Shopify subscription order."
        ),
    },
    "first_channel": {
        "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
        "notes / business rule": (
            "Customer-level derived (customers.parquet). Acquisition channel for LTV-by-channel analysis."
        ),
    },
    "cohort_month": {
        "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
        "notes / business rule": (
            "Customer-level derived (customers.parquet). Monthly acquisition cohort key."
        ),
    },
}

COL_MAP = {
    "target_column": 1,
    "source_file(s)": 4,
    "notes / business rule": 8,
}


def _fix_encoding(value: str) -> str:
    # Common UTF-8 dash misreads in Excel exports
    replacements = (
        ("\u2014", "-"),  # em dash
        ("—", "-"),
        (bytes([0xE2, 0x80, 0x94]).decode("latin-1"), "-"),  # E2 80 94 -> â€"
        ("\u00e2\u20ac\u201d", "-"),  # E2 80 94 mis-decoded as â + € + "
    )
    out = value
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def main() -> None:
    wb = load_workbook(XLSX)
    ws = wb["1.orders"]
    header_row = 2
    headers = {ws.cell(header_row, c).value: c for c in range(1, 9) if ws.cell(header_row, c).value}
    updated = []
    encoding_fixes = 0
    for row in range(header_row + 1, ws.max_row + 1):
        for col in range(1, 9):
            val = ws.cell(row, col).value
            if isinstance(val, str):
                fixed = _fix_encoding(val)
                if fixed != val:
                    ws.cell(row, col, fixed)
                    encoding_fixes += 1
        target = ws.cell(row, headers["target_column"]).value
        if target not in PATCHES:
            continue
        for field, value in PATCHES[target].items():
            col = headers.get(field) or COL_MAP.get(field)
            if col:
                ws.cell(row, col, value)
        updated.append(target)
    wb.save(XLSX)
    print(f"Patched {len(updated)} rows in {XLSX.name}: {', '.join(updated)}")
    print(f"Fixed {encoding_fixes} cells with em-dash/mojibake encoding.")


if __name__ == "__main__":
    main()
