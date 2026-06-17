"""
00_config.py  -  Paths, constants, and shared helpers for LushProtein EDA.

All other scripts import from here.  Adjust BASE_DIR if you move the EDA folder.
"""

from pathlib import Path
import pandas as pd

# -- Root of the data drop ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent   # LushProtein_Project_Data_*

# -- Medallion Data Lake (Bronze / Silver / Gold) --------------------------------
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
GOLD_REFERENCE_DIR = GOLD_DIR / "reference"       # DQ-only snapshots (was do_not_use_these)
GOLD_ANALYTICS_DIR = GOLD_DIR / "analytics"
GOLD_ANALYTICS_DECILE = GOLD_ANALYTICS_DIR / "decile"
GOLD_ANALYTICS_CATEGORY = GOLD_ANALYTICS_DIR / "category"
GOLD_ANALYTICS_FINDINGS = GOLD_ANALYTICS_DIR / "findings"

# Bronze raw sources (immutable — never write here from pipeline scripts)
BRONZE_ORDERS_DIR = BASE_DIR / "1.customer_transaction"
BRONZE_PRODUCTS_DIR = BASE_DIR / "2.product_master"
BRONZE_DISCOUNTS_DIR = BASE_DIR / "3.Discounts"
BRONZE_CAMPAIGNS_DIR = BASE_DIR / "4.Campaigns"
BRONZE_RECHARGE_DIR = BASE_DIR / "5.Recharge_data"
BRONZE_SUPPLEMENTAL_DIR = BRONZE_DIR / "supplemental"

# Legacy raw path aliases (backward compatible)
ORDER_FILES = sorted(BRONZE_ORDERS_DIR.glob("1_*.xlsx"))
PRODUCTS_FILE   = BRONZE_PRODUCTS_DIR / "2_1.products_master_20260505.xlsx"
DISCOUNTS_FILE  = BRONZE_DISCOUNTS_DIR / "3_1.discounts_export_20260505 - Copy - Copy - Copy.csv"
CAMPAIGNS_FILE  = BRONZE_CAMPAIGNS_DIR / "4_1.Sessions by referrer_20260505.csv"
RECHARGE_ORDERS     = BRONZE_RECHARGE_DIR / "5_1.orders_combined_20260505.xlsx"
RECHARGE_CHECKOUT   = BRONZE_RECHARGE_DIR / "5_2.order_items_checkout_20260505.xlsx"
RECHARGE_REACTIVATED= BRONZE_RECHARGE_DIR / "5_3.subscribers_reactivated_20260505.xlsx"
RECHARGE_CHURNED    = BRONZE_RECHARGE_DIR / "5_4.subscriptions_churned_20260505.xlsx"
RECHARGE_RECURRING  = BRONZE_RECHARGE_DIR / "5_5.order_items_recurring_20260505.xlsx"

# Silver / Gold output dirs (canonical medallion locations)
OUTPUT_DIR = SILVER_DIR          # Silver: cleaned merged tables + lens CSV exports
FINALS_DIR = GOLD_DIR          # Gold: finals-filtered parquets + enrichment

# Legacy junction targets (EDA/outputs, EDA/outputs_finals → medallion dirs)
LEGACY_SILVER_JUNCTION = BASE_DIR / "EDA" / "outputs"
LEGACY_GOLD_JUNCTION = BASE_DIR / "EDA" / "outputs_finals"
LEGACY_DECILE_JUNCTION = BASE_DIR / "EDA" / "decile_analysis" / "outputs"
LEGACY_CATEGORY_JUNCTION = BASE_DIR / "EDA" / "category_analysis" / "outputs"

# Ensure medallion dirs exist
for _medallion_dir in (
    BRONZE_DIR, BRONZE_SUPPLEMENTAL_DIR,
    SILVER_DIR, GOLD_DIR, GOLD_REFERENCE_DIR,
    GOLD_ANALYTICS_DIR, GOLD_ANALYTICS_DECILE,
    GOLD_ANALYTICS_CATEGORY, GOLD_ANALYTICS_FINDINGS,
):
    _medallion_dir.mkdir(parents=True, exist_ok=True)


# -- Hero product classification ------------------------------------------------
# Map product handle keywords -> clean category label
PRODUCT_MAP = {
    "lean-protein":    "Lean Protein",
    "lean_protein":    "Lean Protein",
    "clear-protein":   "Clear Protein",
    "clear_protein":   "Clear Protein",
    "collagen":        "Collagen Glow",
    "soy-protein":     "Soy Protein",       # older SKU
    "protein-bar":     "Protein Bar",
    "shaker":          "Accessories",
    "starter-kit":     "Accessories",
}

def classify_product(handle: str) -> str:
    if pd.isna(handle):
        return "Unknown"
    h = str(handle).lower()
    for kw, label in PRODUCT_MAP.items():
        if kw in h:
            return label
    return "Other"

# -- Channel classification from order tags + UTM source -----------------------
# Tags can contain: 'shopee', 'lazada', 'tokopedia', 'Subscription Order',
#                   'FIRST_ORDER', marketplace names
MARKETPLACE_KEYWORDS = ["shopee", "lazada", "tokopedia", "redmart", "grab"]

def classify_channel(row) -> str:
    """
    Returns one of: Subscription | Marketplace | Website (Direct/Paid) | Other
    Uses the Tags column and Browser: UTM Source column.
    """
    tags = str(row.get("Tags", "") or "").lower()
    utm  = str(row.get("Browser: UTM Source", "") or "").lower()
    name = str(row.get("Name", "") or "").lower()

    if any(k in tags for k in MARKETPLACE_KEYWORDS):
        return "Marketplace"
    if "subscription" in tags or "yotpo subscriptions" in tags or "lpsg" in name[:4]:
        return "Subscription"
    if utm in ("facebook", "instagram", "tiktok"):
        return "Paid Social"
    if utm in ("google", "bing"):
        return "Paid Search"
    if utm == "affiliate":
        return "Affiliate"
    if utm in ("shopify_email", "email", "klaviyo"):
        return "Email"
    return "Direct / Organic"

# -- FX conversion rates (5-year average, applied at data load time) -----------
#
# ASSUMPTION: Exchange rates represent the approximate 5-year average (2020-2026).
#   Rates provided by team: 1 SGD = 3.30 MYR  |  1 SGD = 6.10 HKD
#   All revenue (Price: Total, Price: Total Discount, Price: Total Shipping,
#   Line: Price) is multiplied by the relevant rate before saving to Parquet.
#   After conversion the Currency column is set to "SGD" for all orders.
#   This enables combined SG + MY + HK analysis in a single SGD-denominated dataset.
#
#   Limitation: Using a single average rate ignores year-to-year FX movements.
#   For orders spanning 2020-2026, the actual rate at time of transaction may
#   differ from the 5-year average. This introduces a measurement error in
#   absolute revenue figures (estimated <=10% for MY store).
#   Impact is LOW for relative comparisons (retention, repeat rate) but should
#   be noted when citing absolute SGD revenue figures.
#
FX_RATES_TO_SGD = {
    "SG": 1.0,
    "MY": 1.0 / 3.30,   # 1 MYR = 0.3030 SGD  (5-yr avg: 1 SGD = 3.30 MYR)
    "HK": 1.0 / 6.10,   # 1 HKD = 0.1639 SGD  (5-yr avg: 1 SGD = 6.10 HKD)
}

FX_ASSUMPTION_NOTE = (
    "All revenue converted to SGD using 5-year average rates (2020-2026): "
    "1 SGD = 3.30 MYR; 1 SGD = 6.10 HKD. "
    "Applied as fixed rates at data load time."
)

# -- Date helpers ---------------------------------------------------------------
ANALYSIS_DATE = pd.Timestamp("2026-04-30", tz="UTC")   # treat as "today" for RFM calcs

print("[config] BASE_DIR:", BASE_DIR)
print("[config] Order files found:", len(ORDER_FILES))
print("[config] FX NOTE:", FX_ASSUMPTION_NOTE)
