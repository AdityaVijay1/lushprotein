"""
build_orders_sttm.py
Combine all Shopify order exports and generate full Source-to-Target Mapping (STTM).

Outputs:
  deliverables/LushProtein_Orders_Combined_20260505.csv
  deliverables/LushProtein_Orders_STTM.csv
"""
import re
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parent.parent
ORDER_DIR = BASE / "1.customer_transaction"
ORDER_GLOB = "1_*.orders-*_20260505.xlsx"
SOURCE_FILES = "1.customer_transaction/1_*.orders-YYYY_20260505.xlsx"
COMBINED_OUT = BASE / "deliverables" / "LushProtein_Orders_Combined_20260505.csv"
STTM_OUT = BASE / "deliverables" / "LushProtein_Orders_STTM.csv"

ID_COLS = {
    "ID", "Customer: ID", "Checkout ID", "Line: ID",
    "Line: Product ID", "Line: Variant ID", "Line: SKU", "Line: Variant Barcode",
}
DATETIME_COLS = {"Processed At", "Cancelled At"}
BOOL_COLS = {"Top Row", "Line: Requires Shipping", "Line: Gift Card"}
INT_COLS = {
    "Line: Quantity", "Line: Grams", "Line: Variant Inventory Qty", "Weight Total",
}
DECIMAL_PREFIXES = ("Price:", "Line: Price", "Line: Total", "Line: Discount", "Line: Variant")


def _snake(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[:/]", " ", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def _source_dtype(col: str, series: pd.Series) -> str:
    if col in ID_COLS:
        return "id (13-digit)" if col in {"ID", "Customer: ID", "Line: ID", "Checkout ID", "Line: Product ID", "Line: Variant ID"} else "text"
    if col in DATETIME_COLS:
        return "datetime+tz"
    if col in BOOL_COLS:
        return "bool/int flag"
    if col in INT_COLS:
        return "int"
    if col.startswith(DECIMAL_PREFIXES) or col in {"Line: Variant Compare At Price", "Line: Variant Cost", "Line: Variant Price"}:
        return "decimal"
    if col in {"Payment: Status", "Order Fulfillment Status", "Currency", "Source", "Shipping: Country Code", "Shipping: Province Code"}:
        return "text (cat)"
    if col == "Tags" or col == "Customer: Tags":
        return "text (comma-list)"
    if pd.api.types.is_numeric_dtype(series):
        return "decimal" if pd.api.types.is_float_dtype(series) else "int"
    return "text"


def _target_dtype(source_dtype: str, col: str) -> str:
    if col in {"ID", "Line: ID"}:
        return "STRING (id)"
    if col == "Customer: ID":
        return "STRING (id)"
    if "id" in source_dtype:
        return "STRING (id)"
    if source_dtype.startswith("datetime"):
        return "DATETIME"
    if source_dtype == "bool/int flag":
        return "BOOL" if col in BOOL_COLS and col != "Top Row" else "INT"
    if source_dtype == "int":
        return "INT"
    if source_dtype == "decimal":
        return "DECIMAL"
    if source_dtype == "text (cat)":
        return "STRING (cat)"
    return "STRING"


def _pk_fk(col: str) -> str:
    if col == "ID":
        return "PK (order-level when Top Row = 1)"
    if col == "Line: ID":
        return "PK (line-level when Line: Type = Line Item)"
    if col == "Customer: ID":
        return "FK -> customer"
    if col == "Line: Product Handle":
        return "FK -> products.Handle"
    if col in {"Line: SKU", "Line: Variant SKU"}:
        return "FK -> products.Variant SKU"
    if col == "Checkout ID":
        return ""
    return ""


def _grain(col: str) -> str:
    if col in {"Top Row", "Line: Type"}:
        return "structural"
    if col.startswith("Line:") or col in {"Line: Name"}:
        return "line-level (Line: Type = Line Item)"
    return "order-level (Top Row = 1)"


# Column-specific transformation + notes (pipeline-aware)
COLUMN_META = {
    "ID": (
        "Direct copy; cast STRING; filter Top Row = 1 for order grain.",
        "Shopify order PK. Same ID repeats on line rows - use Top Row = 1 for one row per order.",
    ),
    "Name": (
        "Direct copy; filter Top Row = 1.",
        "Human-readable order number. Prefix encodes store: LP/LPSG=SG, LPMY=MY, LPHK=HK.",
    ),
    "Processed At": (
        "Parse UTC; convert to Asia/Singapore; stored as order_date in pipeline.",
        "Payment/process timestamp (SGT). Raw export column; pipeline also builds normalized order_date from this field (see derived order_date row). Not Created At.",
    ),
    "Top Row": (
        "Direct copy; filter Top Row = 1 for order-level table.",
        "Shopify export flag: 1 = order header row, 0 = additional line/shipping rows.",
    ),
    "Customer: ID": (
        "Direct copy; cast STRING; drop null customer_id in pipeline.",
        "Links to customer entity. Required for all analytical joins.",
    ),
    "Currency": (
        "Direct copy at load; post-FX pipeline sets all rows to SGD.",
        "Raw values: SGD/MYR/HKD. Never sum across currencies before FX conversion.",
    ),
    "Price: Total": (
        "Numeric cast; multiply by FX_RATES_TO_SGD[store] in 01_load_and_merge.py.",
        "Net order revenue. Loaded to orders.parquet as Price: Total (SGD).",
    ),
    "Price: Total Discount": (
        "Numeric cast; fill null->0; multiply by FX rate.",
        "Order-level discount amount. Used for discount depth analysis.",
    ),
    "Price: Total Shipping": (
        "Numeric cast; fill null->0; multiply by FX rate.",
        "Shipping charged on order.",
    ),
    "Payment: Status": (
        "Direct copy; pipeline keeps paid and partially_refunded only.",
        "Exclude unpaid/cancelled before payment.",
    ),
    "Order Fulfillment Status": (
        "Direct copy; pipeline excludes restocked.",
        "Fulfillment state. restocked rows removed in 01_load_and_merge.py.",
    ),
    "Tags": (
        "Direct copy; parse for subscription/marketplace signals.",
        "~38% populated. Key values: Subscription Order, FIRST_ORDER, shopee, lazada.",
    ),
    "Source": (
        "Direct copy; lower-case in finals POS analysis.",
        "Shopify order source: web, pos, subscription_contract, shopify_draft_order, etc. POS = on-site.",
    ),
    "Browser: UTM Source": (
        "Direct copy; used in classify_channel() when present.",
        "~5% populated. Primary paid/organic attribution when available.",
    ),
    "Browser: UTM Medium": ("Direct copy.", "Companion to Browser: UTM Source."),
    "Browser: UTM Campaign": ("Direct copy.", "Campaign name string."),
    "Browser: UTM Content": ("Direct copy.", "Ad/content variant within campaign."),
    "Browser: Referrer Domain": ("Direct copy.", "Loaded to orders.parquet when present."),
    "Browser: Referrer": ("Direct copy.", "Full referrer URL. Often null."),
    "Browser: Landing Page": ("Direct copy.", "First page URL in session. Often null."),
    "Browser: Ad URL": ("Direct copy.", "Click/ad destination URL. Often null."),
    "Browser: User Agent": ("Direct copy.", "Device/browser string. POS orders show Shopify POS user agent."),
    "Shipping: Country": ("Direct copy.", "Top countries: Malaysia ~52%, Singapore ~41%."),
    "Shipping: Country Code": ("Direct copy.", "ISO country code companion to Shipping: Country."),
    "Cancelled At": ("Parse datetime; null = not cancelled.", "~89% null."),
    "Cancel: Reason": ("Direct copy.", "Populated only when order cancelled."),
    "Line: Type": (
        "Direct copy; filter Line: Type = Line Item for line-item table.",
        "Values include Line Item, Shipping, Discount, etc.",
    ),
    "Line: ID": (
        "Direct copy; cast STRING; filter Line: Type = Line Item.",
        "Line-level PK for product analysis.",
    ),
    "Line: Product Handle": (
        "Direct copy; filter Line: Type = Line Item.",
        "Product slug; join key to products_master.Handle. Used for product_category derivation.",
    ),
    "Line: SKU": (
        "Direct copy; cast STRING preserve leading zeros.",
        "Variant SKU; join key to products_master.Variant SKU.",
    ),
    "Line: Variant SKU": (
        "Direct copy; cast STRING.",
        "Duplicate/alternate SKU field on some rows; prefer Line: SKU when both present.",
    ),
    "Line: Title": ("Direct copy.", "Product display name on line row."),
    "Line: Variant Title": ("Direct copy.", "Flavor/pack-size label - use for SKU/flavor-level analysis."),
    "Line: Quantity": ("Cast INT.", "Units purchased on line."),
    "Line: Price": (
        "Numeric cast; multiply by FX rate in pipeline.",
        "Unit price before line discount (SGD in parquet).",
    ),
    "Line: Discount": (
        "Numeric cast; fill null->0; multiply by FX rate.",
        "Line-level discount amount (SGD in lines.parquet).",
    ),
    "Line: Total": (
        "Numeric cast; multiply by FX rate.",
        "Line revenue after discount (SGD in lines.parquet). Primary revenue field for SKU analysis.",
    ),
}


def _transformation_and_notes(col: str, null_pct: float, in_orders: bool, in_lines: bool) -> tuple[str, str]:
    if col in COLUMN_META:
        return COLUMN_META[col]

    grain = _grain(col)
    null_note = f"~{null_pct:.0f}% null in combined export." if null_pct >= 5 else "Mostly populated in combined export."

    if in_orders or in_lines:
        load = []
        if in_orders:
            load.append("orders.parquet")
        if in_lines:
            load.append("lines.parquet")
        return (
            f"Direct copy; retained in combined export. Partially loaded to {' + '.join(load)} in current pipeline.",
            f"{grain}. {null_note}",
        )

    return (
        "Direct copy to combined export; not loaded to analytical parquet in current pipeline.",
        f"{grain}. {null_note} Included in STTM for completeness (may be empty).",
    )


def main():
    order_files = sorted(ORDER_DIR.glob(ORDER_GLOB))
    if not order_files:
        raise FileNotFoundError(f"No order files matching {ORDER_GLOB} in {ORDER_DIR}")

    dtype_map = {
        "ID": str, "Customer: ID": str, "Line: ID": str,
        "Checkout ID": str, "Line: Product ID": str, "Line: Variant ID": str,
    }
    chunks = []
    print("Combining order files...")
    for f in order_files:
        print(f"  {f.name}")
        chunks.append(pd.read_excel(f, dtype=dtype_map))
    raw = pd.concat(chunks, ignore_index=True)
    columns = list(raw.columns)
    print(f"Combined rows: {len(raw):,} | columns: {len(columns)}")

    print(f"Writing {COMBINED_OUT.name} ...")
    raw.to_csv(COMBINED_OUT, index=False)

    orders_cols = {
        "ID", "Name", "Tags", "Customer: ID", "Currency",
        "Price: Total", "Price: Total Discount", "Price: Total Shipping",
        "Payment: Status", "Order Fulfillment Status",
        "Shipping: Country", "Shipping: Country Code",
        "Browser: UTM Source", "Browser: UTM Medium", "Browser: UTM Campaign",
        "Browser: Referrer Domain", "Cancelled At", "Source",
        "Line: Product Handle", "Line: Title", "Line: Variant Title", "Line: SKU", "Line: Price", "Line: Quantity",
    }
    lines_cols = {
        "ID", "Customer: ID",
        "Line: Product Handle", "Line: Title", "Line: Variant Title",
        "Line: SKU", "Line: Quantity", "Line: Price", "Line: Discount", "Line: Total",
    }

    rows = []
    for col in columns:
        series = raw[col]
        null_pct = series.isna().mean() * 100
        src_dtype = _source_dtype(col, series)
        tgt_dtype = _target_dtype(src_dtype, col)
        transform, notes = _transformation_and_notes(
            col, null_pct,
            col in orders_cols,
            col in lines_cols,
        )
        rows.append({
            "target_column": _snake(col),
            "target_data_type": tgt_dtype,
            "pk_fk": _pk_fk(col),
            "source_file(s)": SOURCE_FILES,
            "source_column": col,
            "source_data_type": src_dtype,
            "transformation": transform,
            "notes / business rule": notes,
        })

    sttm = pd.DataFrame(rows)

    derived_rows = [
        {
            "target_column": "order_date",
            "target_data_type": "DATETIME",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Processed At (derived)",
            "source_data_type": "datetime+tz",
            "transformation": "Parse UTC; convert to Asia/Singapore; normalize to date.",
            "notes / business rule": "Derived in 01_load_and_merge.py from Processed At: same source as processed_at, normalized to date-only in Asia/Singapore. Not a separate raw export column.",
        },
        {
            "target_column": "store",
            "target_data_type": "STRING (cat)",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Name (derived)",
            "source_data_type": "text",
            "transformation": "CASE WHEN Name starts LPMY->MY, LPHK->HK, LPSG/LP->SG ELSE Other.",
            "notes / business rule": "Derived market code - not in raw export. Required for FX conversion.",
        },
        {
            "target_column": "channel",
            "target_data_type": "STRING (cat)",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Tags + Browser: UTM Source + Name (derived)",
            "source_data_type": "text",
            "transformation": "classify_channel() in 00_config.py.",
            "notes / business rule": "Derived acquisition channel: Subscription | Marketplace | Direct/Organic | Paid Social | Email | Affiliate | Paid Search.",
        },
        {
            "target_column": "product_category",
            "target_data_type": "STRING (cat)",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Line: Product Handle (derived)",
            "source_data_type": "text",
            "transformation": "classify_product() keyword map in 00_config.py.",
            "notes / business rule": "Derived product family - not a product-master join. Order grain (Top Row=1): first line item handle. Line grain (Line Item): each line handle.",
        },
        {
            "target_column": "has_discount",
            "target_data_type": "BOOL",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Price: Total Discount (derived)",
            "source_data_type": "decimal",
            "transformation": "total_discount > 0.",
            "notes / business rule": "Derived flag for discounted orders.",
        },
        {
            "target_column": "is_subscription",
            "target_data_type": "BOOL",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Tags (derived)",
            "source_data_type": "text (comma-list)",
            "transformation": "Tags contains subscription|yotpo subscriptions (case-insensitive).",
            "notes / business rule": "Shopify-trackable subscription orders only.",
        },
        {
            "target_column": "is_first_order_tag",
            "target_data_type": "BOOL",
            "pk_fk": "",
            "source_file(s)": SOURCE_FILES,
            "source_column": "Tags (derived)",
            "source_data_type": "text (comma-list)",
            "transformation": "Tags contains FIRST_ORDER.",
            "notes / business rule": "Tag-based first-order indicator from Shopify.",
        },
        {
            "target_column": "total_revenue",
            "target_data_type": "DECIMAL",
            "pk_fk": "",
            "source_file(s)": f"{SOURCE_FILES} -> orders.parquet -> customers.parquet",
            "source_column": "Price: Total",
            "source_data_type": "decimal",
            "transformation": "SUM(Price: Total) GROUP BY customer_id.",
            "notes / business rule": "Customer-level derived (customers.parquet). Customer LTV = SUM(Price: Total SGD) per customer_id. Used in finals analysis.",
        },
        {
            "target_column": "is_repeat",
            "target_data_type": "BOOL",
            "pk_fk": "",
            "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
            "source_column": "order count (derived)",
            "source_data_type": "bool",
            "transformation": "total_orders >= 2.",
            "notes / business rule": "Customer-level derived (customers.parquet). Repeat customer flag.",
        },
        {
            "target_column": "ever_subscribed",
            "target_data_type": "BOOL",
            "pk_fk": "",
            "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
            "source_column": "is_subscription (derived)",
            "source_data_type": "bool",
            "transformation": "ANY(is_subscription) GROUP BY customer_id.",
            "notes / business rule": "Customer-level derived (customers.parquet). Ever had a Shopify subscription order.",
        },
        {
            "target_column": "first_channel",
            "target_data_type": "STRING (cat)",
            "pk_fk": "",
            "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
            "source_column": "channel (derived)",
            "source_data_type": "text",
            "transformation": "FIRST channel by order_date per customer.",
            "notes / business rule": "Customer-level derived (customers.parquet). Acquisition channel for LTV-by-channel analysis.",
        },
        {
            "target_column": "cohort_month",
            "target_data_type": "PERIOD",
            "pk_fk": "",
            "source_file(s)": f"{SOURCE_FILES} -> customers.parquet (derived)",
            "source_column": "first_order_date (derived)",
            "source_data_type": "period",
            "transformation": "first_order_date.to_period(M).",
            "notes / business rule": "Customer-level derived (customers.parquet). Monthly acquisition cohort key.",
        },
    ]
    sttm = pd.concat([sttm, pd.DataFrame(derived_rows)], ignore_index=True)

    print(f"Writing {STTM_OUT.name} ({len(sttm)} rows) ...")
    sttm.to_csv(STTM_OUT, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
