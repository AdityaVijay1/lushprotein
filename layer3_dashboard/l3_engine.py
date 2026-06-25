"""Layer 3 recommendation engine and data layer."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RULES_FILE = DATA_DIR / "cross_sell_rules.csv"
CUSTOMERS_FILE = DATA_DIR / "customers_demo.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions_demo.csv"

DEMO_TODAY = datetime(2026, 6, 26)
LOOKBACK_DAYS = 30
SAMPLE_BUFFER_DAYS = 10

DEFAULT_RULES = pd.DataFrame(
    [
        {
            "first_product_category": "Clear Protein",
            "cross_sell_category": "Lean Protein",
            "sample_product_suggestion": "Lean 40g single-serve (TMT/Taro)",
            "email_cross_sell_day_after_delivery": 14,
            "physical_sample_day_after_delivery": 44,
            "median_reorder_days": 54,
        },
        {
            "first_product_category": "Lean Protein",
            "cross_sell_category": "Clear Protein",
            "sample_product_suggestion": "Clear 25g sachet (Peach or White Grape)",
            "email_cross_sell_day_after_delivery": 14,
            "physical_sample_day_after_delivery": 25,
            "median_reorder_days": 35,
        },
        {
            "first_product_category": "Collagen Glow",
            "cross_sell_category": "Clear Protein",
            "sample_product_suggestion": "Clear 25g sachet OR Lean 40g single-serve",
            "email_cross_sell_day_after_delivery": 21,
            "physical_sample_day_after_delivery": 32,
            "median_reorder_days": 42,
        },
        {
            "first_product_category": "Accessories",
            "cross_sell_category": "Lean Protein",
            "sample_product_suggestion": "Clear 25g sachet - do NOT send another shaker",
            "email_cross_sell_day_after_delivery": 7,
            "physical_sample_day_after_delivery": 25,
            "median_reorder_days": 35,
        },
        {
            "first_product_category": "Soy Protein",
            "cross_sell_category": "Clear Protein",
            "sample_product_suggestion": "Clear or Lean 25g/40g single-serve",
            "email_cross_sell_day_after_delivery": 14,
            "physical_sample_day_after_delivery": 74,
            "median_reorder_days": 84,
        },
        {
            "first_product_category": "Other",
            "cross_sell_category": "Clear Protein",
            "sample_product_suggestion": "Discovery sampler OR Clear 25g sachet",
            "email_cross_sell_day_after_delivery": 14,
            "physical_sample_day_after_delivery": 40,
            "median_reorder_days": 50,
        },
        {
            "first_product_category": "Unknown",
            "cross_sell_category": "Clear Protein",
            "sample_product_suggestion": "Clear 25g sachet Peach",
            "email_cross_sell_day_after_delivery": 14,
            "physical_sample_day_after_delivery": 40,
            "median_reorder_days": 50,
        },
    ]
)


def normalize_customer_id(value: Any) -> str | None:
    """Normalize Shopify customer IDs across Excel / scientific notation formats."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value).strip().lstrip("'").replace(",", "")
    if not s or s.lower() in {"nan", "none"}:
        return None
    if "e" in s.lower():
        try:
            # Scientific notation loses precision for 13-digit Shopify IDs.
            # Match against known demo IDs by prefix when possible.
            approx = str(int(float(s)))
            return approx
        except ValueError:
            return None
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        return s
    try:
        return str(int(float(s)))
    except ValueError:
        return None


def format_customer_id_display(customer_id: str) -> str:
    """Format ID for display without losing precision."""
    return f"{int(customer_id):,}"


def load_rules() -> pd.DataFrame:
    if RULES_FILE.exists():
        rules = pd.read_csv(RULES_FILE)
        rules = rules.rename(
            columns={
                "first_product_category": "first_product_category",
                "cross_sell_category": "cross_sell_category",
                "sample_product_suggestion": "sample_product_suggestion",
                "email_cross_sell_day_after_delivery": "email_cross_sell_day_after_delivery",
                "physical_sample_day_after_delivery": "physical_sample_day_after_delivery",
                "median_reorder_days": "median_reorder_days",
            }
        )
        return rules
    return DEFAULT_RULES.copy()


def load_customers() -> pd.DataFrame:
    df = pd.read_csv(CUSTOMERS_FILE, dtype=str)
    df["customer_id"] = df["customer_id"].apply(normalize_customer_id)
    return df.dropna(subset=["customer_id"])


def load_transactions(reference_date: datetime | None = None) -> pd.DataFrame:
    ref = reference_date or DEMO_TODAY
    cutoff = ref - timedelta(days=LOOKBACK_DAYS)

    df = pd.read_csv(TRANSACTIONS_FILE)
    df["customer_id"] = df["customer_id"].apply(normalize_customer_id)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.tz_localize(None)
    df = df.dropna(subset=["customer_id"])
    df = df[(df["order_date"] >= cutoff) & (df["order_date"] <= ref)]
    return df.sort_values("order_date", ascending=False)


def get_eligible_customer_ids(reference_date: datetime | None = None) -> list[str]:
    tx = load_transactions(reference_date)
    one_order = tx.groupby("customer_id").filter(lambda g: len(g) == 1)
    return sorted(one_order["customer_id"].unique().tolist())


def lookup_customer(
    customer_id_input: str,
    reference_date: datetime | None = None,
) -> dict[str, Any]:
    """Return customer profile + Layer 3 recommendation or an error message."""
    cid = normalize_customer_id(customer_id_input)
    customers = load_customers()
    transactions = load_transactions(reference_date)
    rules = load_rules()

    # Resolve scientific-notation input against known demo IDs (precision-safe)
    if cid and customers["customer_id"].eq(cid).sum() == 0 and "e" in str(customer_id_input).lower():
        prefix = str(int(float(str(customer_id_input).strip().lstrip("'"))))[:6]
        matches = customers[customers["customer_id"].str.startswith(prefix)]
        if len(matches) == 1:
            cid = matches.iloc[0]["customer_id"]
        elif len(matches) > 1:
            return {
                "found": False,
                "error": (
                    "Scientific notation matched multiple customers. "
                    "Use the full Customer ID from the sidebar list."
                ),
            }

    if not cid:
        return {"found": False, "error": "Invalid Customer ID format."}

    cust_row = customers[customers["customer_id"] == cid]
    if cust_row.empty:
        return {
            "found": False,
            "error": "Customer ID not found in demo dataset.",
        }

    tx_rows = transactions[transactions["customer_id"] == cid]
    if tx_rows.empty:
        return {
            "found": False,
            "error": (
                "Customer found, but not eligible for Layer 3 demo. "
                f"Must have exactly 1 order in the last {LOOKBACK_DAYS} days."
            ),
        }

    if len(tx_rows) > 1:
        return {
            "found": False,
            "error": "Customer has multiple recent orders. Layer 3 demo targets first-time buyers only.",
        }

    tx = tx_rows.iloc[0]
    category = tx.get("product_category") or "Unknown"
    rule = rules[rules["first_product_category"] == category]
    if rule.empty:
        rule = rules[rules["first_product_category"] == "Unknown"]
    rule = rule.iloc[0]

    order_date = tx["order_date"].to_pydatetime()
    median_reorder = int(rule["median_reorder_days"])
    sample_day = int(rule["physical_sample_day_after_delivery"])
    email_day = int(rule["email_cross_sell_day_after_delivery"])
    sample_date = order_date + timedelta(days=sample_day)
    reorder_date = order_date + timedelta(days=median_reorder)
    email_date = order_date + timedelta(days=email_day)

    ref = reference_date or DEMO_TODAY
    days_until_sample = max(0, (sample_date - ref).days)
    days_until_reorder = max(0, (reorder_date - ref).days)

    cust = cust_row.iloc[0]
    return {
        "found": True,
        "customer_id": cid,
        "customer_id_display": format_customer_id_display(cid),
        "name": cust.get("name", "Demo Customer"),
        "address_area": cust.get("address_area", "Singapore"),
        "last_product": tx.get("product_name") or category,
        "last_product_category": category,
        "transaction_date": order_date.strftime("%d/%m/%Y"),
        "recommended_product": rule["cross_sell_category"],
        "sample_to_ship": rule["sample_product_suggestion"],
        "time_to_send_sample_days": sample_day,
        "estimated_reorder_days": median_reorder,
        "email_day": email_day,
        "sample_date": sample_date.strftime("%d/%m/%Y"),
        "reorder_date": reorder_date.strftime("%d/%m/%Y"),
        "email_date": email_date.strftime("%d/%m/%Y"),
        "days_until_sample": days_until_sample,
        "days_until_reorder": days_until_reorder,
        "co_purchase_note": f"Rule derived from D1 co-purchase behaviour for {category} first buyers.",
        "order_count": 1,
    }
