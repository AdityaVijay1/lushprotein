"""
00_config.py  -  Paths, constants, and shared helpers for LushProtein EDA.

All other scripts import from here.  Adjust BASE_DIR if you move the EDA folder.
"""

from pathlib import Path
import pandas as pd

# -- Root of the data drop ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent   # LushProtein_Project_Data_*

# -- Raw file paths -------------------------------------------------------------
ORDER_FILES = sorted(
    (BASE_DIR / "1.customer_transaction").glob("1_*.xlsx")
)

PRODUCTS_FILE   = BASE_DIR / "2.product_master"   / "2_1.products_master_20260505.xlsx"
DISCOUNTS_FILE  = BASE_DIR / "3.Discounts"        / "3_1.discounts_export_20260505.csv"
CAMPAIGNS_FILE  = BASE_DIR / "4.Campaigns"        / "4_1.Sessions by referrer_20260505.csv"

RECHARGE_ORDERS     = BASE_DIR / "5.Recharge_data" / "5_1.orders_combined_20260505.xlsx"
RECHARGE_CHECKOUT   = BASE_DIR / "5.Recharge_data" / "5_2.order_items_checkout_20260505.xlsx"
RECHARGE_REACTIVATED= BASE_DIR / "5.Recharge_data" / "5_3.subscribers_reactivated_20260505.xlsx"
RECHARGE_CHURNED    = BASE_DIR / "5.Recharge_data" / "5_4.subscriptions_churned_20260505.xlsx"
RECHARGE_RECURRING  = BASE_DIR / "5.Recharge_data" / "5_5.order_items_recurring_20260505.xlsx"

# -- Output dir -----------------------------------------------------------------
OUTPUT_DIR = BASE_DIR / "EDA" / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

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
