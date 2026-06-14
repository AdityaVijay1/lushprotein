"""
13_build_finals_datasets.py
Build finals-filtered Parquet datasets for downstream analysis.

Does NOT modify EDA/outputs/ (midterm base). Writes to EDA/outputs_finals/.

Filter logic (order-window approach):
  Layer 0 — LP-F03: drop all orders before 2022-01-01 (forget pre-2022 history)
  Layer 1 — DQ-02/03/04 order drops, customer stats rebuilt from 2022+ clean pool
  Layer 2 — LP-F01/F02/F04 → finals_eligible (acq = first order in 2022+ window)
  Layer 3 — exclude Jul/Nov order months; exclude elite handle from lines

Primary outputs (orders.parquet, lines.parquet, customers.parquet) = all layers applied.

Run after: python EDA/01_load_and_merge.py  (or full run_eda.py)
"""
import warnings
warnings.filterwarnings("ignore")

import importlib.util
import json
import numpy as np
import pandas as pd
from pathlib import Path

def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", Path(__file__).parent / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg = _load_config()
OUT = cfg.OUTPUT_DIR
FINALS_OUT = cfg.BASE_DIR / "EDA" / "outputs_finals"
ORDER_FILES = cfg.ORDER_FILES

EXCLUDE_HANDLE = "better-whey-protein-elite"
EXCLUDE_MONTHS = {7, 11}
ANALYSIS_START = pd.Timestamp("2022-01-01", tz="Asia/Singapore")

FINALS_OUT.mkdir(exist_ok=True)

print("=" * 70)
print("BUILD FINALS DATASETS — 13_build_finals_datasets.py")
print("=" * 70)
print(f"Source:  {OUT}")
print(f"Output:  {FINALS_OUT}")

# ── Load base tables ─────────────────────────────────────────────────────────
orders = pd.read_parquet(OUT / "orders.parquet")
lines = pd.read_parquet(OUT / "lines.parquet")
cust_base = pd.read_parquet(OUT / "customers.parquet")
products = pd.read_parquet(OUT / "products.parquet")
discounts = pd.read_parquet(OUT / "discounts.parquet")

rc_tables = {
    "rc_orders": pd.read_parquet(OUT / "rc_orders.parquet"),
    "rc_checkout": pd.read_parquet(OUT / "rc_checkout.parquet"),
    "rc_churned": pd.read_parquet(OUT / "rc_churned.parquet"),
    "rc_reactivated": pd.read_parquet(OUT / "rc_reactivated.parquet"),
    "rc_recurring": pd.read_parquet(OUT / "rc_recurring.parquet"),
}

base_counts = {
    "orders": len(orders),
    "lines": len(lines),
    "customers": len(cust_base),
    "products": len(products),
    "discounts": len(discounts),
    **{k: len(v) for k, v in rc_tables.items()},
}

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
lines["order_date"] = pd.to_datetime(lines["order_date"], utc=True)
orders["order_id"] = orders["order_id"].astype(str)
lines["order_id"] = lines["order_id"].astype(str)

# ── Enrich orders with Source (POS vs web) ───────────────────────────────────
print("\n[1] Loading Source column from raw order files...")
src_chunks = []
for f in ORDER_FILES:
    if f.stat().st_size < 1000:
        continue
    df = pd.read_excel(f, usecols=["ID", "Top Row", "Source"], dtype=str, engine="openpyxl")
    df = df[df["Top Row"] == "1"].rename(columns={"ID": "order_id"})
    src_chunks.append(df[["order_id", "Source"]])
src_df = pd.concat(src_chunks, ignore_index=True).drop_duplicates("order_id")
src_df["order_id"] = src_df["order_id"].astype(str)
orders = orders.merge(src_df, on="order_id", how="left")
orders["order_source"] = orders["Source"].fillna("unknown").str.lower()
orders["is_pos"] = orders["order_source"] == "pos"
orders["is_web"] = orders["order_source"] == "web"

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 0 — LP-F03: order window from 2022-01-01 (drop pre-2022 orders only)
# Customers who joined before 2022 are KEPT if they have 2022+ orders.
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Layer 0 — 2022+ order window (LP-F03 as order-date cut)...")
_n_all = len(orders)
orders = orders[orders["order_date"] >= ANALYSIS_START].copy()
lines = lines[lines["order_id"].isin(set(orders["order_id"]))].copy()
print(f"  Pre-2022 orders dropped: {_n_all - len(orders):,}")
print(f"  Retained 2022+ orders:     {len(orders):,}")

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — DQ-02 / DQ-03 / DQ-04
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Layer 1 — DQ order drops...")
_n_start = len(orders)

_rev = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
_disc = pd.to_numeric(orders["Price: Total Discount"], errors="coerce").fillna(0)

_dq02 = (_rev == 0) & (_disc == 0)
_dq03 = (_rev == 0) & (_disc > 0)
_dq04 = orders["Tags"].fillna("").str.lower().str.contains("wholesale") | (_rev > 5000)
_drop_mask = _dq02 | _dq03 | _dq04

print(f"  DQ-02 (zero rev + zero disc):            {_dq02.sum():>5,}")
print(f"  DQ-03 (100%-discount / free fulfilment): {_dq03.sum():>5,}")
print(f"  DQ-04 (wholesale OR > S$5,000):          {_dq04.sum():>5,}")

orders_dq = orders[~_drop_mask].copy()
lines_dq = lines[lines["order_id"].isin(set(orders_dq["order_id"]))].copy()
print(f"  Retained orders: {len(orders_dq):,} / {_n_start:,}")

# ── Rebuild customer table from 2022+ DQ-clean orders only ───────────────────
def _rebuild_customers(orders_df, lines_df, cust_seed):
    """Build customer stats from a specific order pool (2022+ window)."""
    orders_df = orders_df.copy()
    orders_df["_rev_sgd"] = pd.to_numeric(orders_df["Price: Total"], errors="coerce").fillna(0)

    agg = (
        orders_df.groupby("customer_id")
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("_rev_sgd", "sum"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    orders_df.drop(columns=["_rev_sgd"], inplace=True, errors="ignore")

    active_ids = set(agg["customer_id"])
    cust = cust_seed[cust_seed["customer_id"].isin(active_ids)].copy()
    drop_cols = ["total_orders", "total_revenue", "first_order_date", "last_order_date",
                 "is_repeat", "acq_year", "acq_month", "lifespan_days", "recency_days", "days_to_second",
                 "second_order_date", "first_disc_depth", "first_disc_bin", "first_order_source", "first_order_pos",
                 "exclude_elite_buyer", "exclude_51pct", "exclude_promo_month", "finals_eligible"]
    cust = cust.drop(columns=[c for c in drop_cols if c in cust.columns])

    cust = cust.merge(agg, on="customer_id", how="inner")
    cust["is_repeat"] = cust["total_orders"] >= 2
    cust["acq_year"] = cust["first_order_date"].dt.year
    cust["acq_month"] = cust["first_order_date"].dt.month
    cust["lifespan_days"] = (cust["last_order_date"] - cust["first_order_date"]).dt.days
    cust["recency_days"] = (cfg.ANALYSIS_DATE - cust["last_order_date"]).dt.days

    first_ord = orders_df.sort_values("order_date").groupby("customer_id").first().reset_index()
    first_ord["first_rev"] = pd.to_numeric(first_ord["Price: Total"], errors="coerce").fillna(0)
    first_ord["first_disc"] = pd.to_numeric(first_ord["Price: Total Discount"], errors="coerce").fillna(0)
    first_ord["first_disc_depth"] = np.where(
        (first_ord["first_rev"] + first_ord["first_disc"]) > 0,
        first_ord["first_disc"] / (first_ord["first_rev"] + first_ord["first_disc"]),
        0,
    )
    first_ord["first_disc_bin"] = pd.cut(
        first_ord["first_disc_depth"],
        bins=[-0.001, 0.001, 0.05, 0.10, 0.20, 0.30, 0.50, 1.01],
        labels=["0%", "1-5%", "6-10%", "11-20%", "21-30%", "31-50%", "51%+"],
    )
    first_ord["first_order_source"] = first_ord["Source"].fillna("unknown").str.lower()

    second_ord = (
        orders_df.sort_values("order_date")
        .groupby("customer_id", as_index=False)
        .nth(1)[["customer_id", "order_date"]]
        .rename(columns={"order_date": "second_order_date"})
    )
    cust = cust.merge(
        first_ord[["customer_id", "first_disc_depth", "first_disc_bin", "first_order_source"]],
        on="customer_id", how="left",
    )
    cust = cust.merge(second_ord, on="customer_id", how="left")
    if "second_order_date" not in cust.columns:
        cust["second_order_date"] = pd.NaT
    cust["days_to_second"] = (cust["second_order_date"] - cust["first_order_date"]).dt.days
    cust["first_order_pos"] = cust["first_order_source"] == "pos"

    # Carry over channel / subscription fields from seed where available
    for col in ["first_channel", "ever_subscribed", "ever_discounted", "first_product_cat"]:
        if col not in cust.columns and col in cust_seed.columns:
            cust = cust.merge(cust_seed[["customer_id", col]], on="customer_id", how="left")

    # LP flags evaluated on 2022+ window
    elite_customers = set(
        lines_df[lines_df["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)]["customer_id"]
    )
    cust["exclude_elite_buyer"] = cust["customer_id"].isin(elite_customers)
    cust["exclude_51pct"] = cust["first_disc_bin"].astype(str) == "51%+"
    cust["exclude_promo_month"] = cust["acq_month"].isin(EXCLUDE_MONTHS)
    cust["finals_eligible"] = (
        ~cust["exclude_elite_buyer"]
        & ~cust["exclude_51pct"]
        & ~cust["exclude_promo_month"]
    )
    return cust

cust_dq = _rebuild_customers(orders_dq, lines_dq, cust_base)
print(f"  Active customers (2022+ DQ-clean): {len(cust_dq):,}")

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — LP-F01 / F02 / F04 (F03 already applied as 2022+ order cut)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] Layer 2 — LushProtein feedback filters (on 2022+ window)...")
print(f"  LP-F01 elite buyers flagged:         {cust_dq['exclude_elite_buyer'].sum():,}")
print(f"  LP-F02 Jul/Nov acquisitions flagged: {cust_dq['exclude_promo_month'].sum():,}")
print(f"  LP-F04 51%+ first-order disc:        {cust_dq['exclude_51pct'].sum():,}")
print(f"  Finals-eligible customers:             {cust_dq['finals_eligible'].sum():,}")

finals_ids = set(cust_dq[cust_dq["finals_eligible"]]["customer_id"])
orders_l2 = orders_dq[orders_dq["customer_id"].isin(finals_ids)].copy()
lines_l2 = lines_dq[lines_dq["customer_id"].isin(finals_ids)].copy()
cust_l2 = cust_dq[cust_dq["finals_eligible"]].copy()

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — exclude Jul/Nov order months; exclude elite handle from lines
# ══════════════════════════════════════════════════════════════════════════════
print("\n[5] Layer 3 — SKU/order-month filters...")
_jul_nov_mask = orders_l2["order_date"].dt.month.isin(EXCLUDE_MONTHS)
orders_finals = orders_l2[~_jul_nov_mask].copy()
lines_finals = lines_l2[
    lines_l2["order_id"].isin(set(orders_finals["order_id"]))
    & ~lines_l2["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)
].copy()
print(f"  Jul/Nov orders dropped:  {_jul_nov_mask.sum():,}")
print(f"  Elite line items dropped: {len(lines_l2) - len(lines_finals):,} (incl. jul/nov overlap)")

# Rebuild customer stats from layer-3 orders; keep LP eligibility from layer 2
cust_finals = _rebuild_customers(orders_finals, lines_finals, cust_dq)
cust_finals = cust_finals[cust_finals["customer_id"].isin(finals_ids)].copy()

# Enrichment on finals customers
lines_no_elite = lines_finals.copy()
breadth = lines_no_elite.groupby("customer_id")["Line: Product Handle"].nunique().reset_index(name="unique_handles")
lines_no_elite["flavor_sku"] = (
    lines_no_elite["Line: Product Handle"].fillna("unknown")
    + " | "
    + lines_no_elite["Line: Variant Title"].fillna("Default")
)
flavor_breadth = lines_no_elite.groupby("customer_id")["flavor_sku"].nunique().reset_index(name="unique_flavor_skus")
cust_finals = cust_finals.merge(breadth, on="customer_id", how="left").merge(flavor_breadth, on="customer_id", how="left")
cust_finals["unique_handles"] = cust_finals["unique_handles"].fillna(0).astype(int)
cust_finals["unique_flavor_skus"] = cust_finals["unique_flavor_skus"].fillna(0).astype(int)
cust_finals["loyal_repeater"] = cust_finals["is_repeat"] & (cust_finals["total_orders"] >= 3)
cust_finals["profit_proxy"] = cust_finals["total_revenue"] * 0.40
if len(cust_finals) >= 10:
    cust_finals["vtd_decile"] = pd.qcut(
        cust_finals["total_revenue"].rank(method="first"), 10, labels=[f"D{i}" for i in range(1, 11)]
    )
else:
    cust_finals["vtd_decile"] = pd.NA

lines_sku = lines_no_elite.copy()  # same as lines.parquet + flavor_sku already present

# ── Products & discounts ───────────────────────────────────────────────────────
products_out = products.copy()
products_out["is_excluded_elite"] = products_out["Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)
discounts_out = discounts.copy()

# ── Recharge tables — join + filter to finals cohort + 2022+ where possible ──
print("\n[6] Filtering Recharge tables...")
order_cust_map = orders_dq[["order_id", "customer_id"]].drop_duplicates()
order_cust_map["order_id"] = order_cust_map["order_id"].astype(str)

rc_orders_map = rc_tables["rc_orders"].copy()
rc_orders_map["shopify_order_id"] = rc_orders_map["shopify_order_id"].astype(str)
rc_cust_map = (
    rc_orders_map
    .merge(
        order_cust_map.rename(columns={"order_id": "shopify_order_id", "customer_id": "shopify_customer_id"}),
        on="shopify_order_id",
        how="left",
    )
    .dropna(subset=["customer_id", "shopify_customer_id"])
    .drop_duplicates("customer_id")
    .rename(columns={"customer_id": "rc_customer_id"})[["rc_customer_id", "shopify_customer_id"]]
)

rc_finals = {}
for name, rc in rc_tables.items():
    rc = rc.copy()
    orig_cols = list(rc.columns)

    if "shopify_order_id" in rc.columns:
        rc["shopify_order_id"] = rc["shopify_order_id"].astype(str)
        rc = rc.merge(
            order_cust_map.rename(columns={"order_id": "shopify_order_id", "customer_id": "shopify_customer_id"}),
            on="shopify_order_id",
            how="left",
        )
        rc = rc[rc["shopify_customer_id"].isin(finals_ids)]
        if "metric_date" in rc.columns:
            rc["metric_date"] = pd.to_datetime(rc["metric_date"], errors="coerce")
            rc = rc[rc["metric_date"] >= ANALYSIS_START.tz_localize(None)]
    elif "customer_id" in rc.columns:
        rc = rc.merge(rc_cust_map, left_on="customer_id", right_on="rc_customer_id", how="left")
        rc = rc[rc["shopify_customer_id"].isin(finals_ids)]
        if "metric_date" in rc.columns:
            rc["metric_date"] = pd.to_datetime(rc["metric_date"], errors="coerce")
            rc = rc[rc["metric_date"] >= ANALYSIS_START.tz_localize(None)]

    keep = orig_cols + (["shopify_customer_id"] if "shopify_customer_id" in rc.columns else [])
    rc_finals[name] = rc[[c for c in keep if c in rc.columns]].copy()
    print(f"  {name}: {len(rc_finals[name]):,} / {len(rc_tables[name]):,} rows")

# ── Save Parquet files ───────────────────────────────────────────────────────
print("\n[7] Saving Parquet files...")

# Reference: 2022+ with Layer 1 only
orders_dq.to_parquet(FINALS_OUT / "orders_dq_clean.parquet", index=False)
lines_dq.to_parquet(FINALS_OUT / "lines_dq_clean.parquet", index=False)
cust_dq.to_parquet(FINALS_OUT / "customers_dq_clean.parquet", index=False)

# Primary: all 3 layers applied
orders_finals.to_parquet(FINALS_OUT / "orders.parquet", index=False)
lines_finals.to_parquet(FINALS_OUT / "lines.parquet", index=False)
cust_finals.to_parquet(FINALS_OUT / "customers.parquet", index=False)
lines_sku.to_parquet(FINALS_OUT / "lines_sku_analysis.parquet", index=False)

products_out.to_parquet(FINALS_OUT / "products.parquet", index=False)
discounts_out.to_parquet(FINALS_OUT / "discounts.parquet", index=False)
for name, df in rc_finals.items():
    df.to_parquet(FINALS_OUT / f"{name}.parquet", index=False)

manifest = {
    "generated_by": "EDA/13_build_finals_datasets.py",
    "source_dir": str(OUT),
    "output_dir": str(FINALS_OUT),
    "approach": "Order-window: LP-F03 drops pre-2022 ORDERS (not customers). Pre-2022 joiners kept if they have 2022+ activity.",
    "filters_applied": {
        "layer0_window": {
            "LP-F03": f"order_date >= {ANALYSIS_START.date()} — pre-2022 orders discarded, not customers",
        },
        "layer1_dq": {
            "DQ-02": "Price: Total = 0 AND Price: Total Discount = 0",
            "DQ-03": "Price: Total = 0 AND Price: Total Discount > 0",
            "DQ-04": "Tags contains wholesale-sale OR Price: Total > 5000 SGD",
        },
        "layer2_lp": {
            "LP-F01": f"Exclude customers who bought {EXCLUDE_HANDLE} (in 2022+ window)",
            "LP-F02": "Exclude customers whose first 2022+ order was in July or November",
            "LP-F04": "Exclude first 2022+ order with discount depth 51%+",
        },
        "layer3": {
            "rules": [
                "finals_eligible customers only",
                "exclude order months July and November",
                f"exclude product handle {EXCLUDE_HANDLE} from lines",
            ],
            "primary_files": ["orders.parquet", "lines.parquet", "customers.parquet", "lines_sku_analysis.parquet"],
        },
    },
    "row_counts": {
        "base_midterm": base_counts,
        "layer1_dq_clean_2022plus": {
            "orders_dq_clean.parquet": len(orders_dq),
            "lines_dq_clean.parquet": len(lines_dq),
            "customers_dq_clean.parquet": len(cust_dq),
        },
        "primary_all_layers": {
            "orders.parquet": len(orders_finals),
            "lines.parquet": len(lines_finals),
            "customers.parquet": len(cust_finals),
            "lines_sku_analysis.parquet": len(lines_sku),
        },
        "reference": {
            "products.parquet": len(products_out),
            "discounts.parquet": len(discounts_out),
            **{f"{k}.parquet": len(v) for k, v in rc_finals.items()},
        },
    },
}

with open(FINALS_OUT / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, default=str)

readme = f"""# Finals-Filtered Datasets

Generated by `EDA/13_build_finals_datasets.py`.

## Key logic change — 2022+ is an ORDER cut, not a customer cut

**Old approach:** If a customer's *first-ever* order was before 2022, drop the entire customer — even their 2024 orders.

**This folder:** Drop all *orders* before 2022-01-01. Customers who joined in 2020 but ordered again in 2024 are **kept** — only their 2022+ history counts.

## Filter layers (all applied to primary files)

### Layer 0 — 2022+ order window (LP-F03)
- Drop orders where `order_date < 2022-01-01`
- Pre-2022 history is ignored, not used to exclude customers

### Layer 1 — DQ drops (order-level, on 2022+ pool)
| ID | Rule |
|----|------|
| DQ-02 | Zero revenue + zero discount |
| DQ-03 | 100%-discount free fulfilments |
| DQ-04 | wholesale-sale tag OR > S$5,000 |

### Layer 2 — LP feedback (customer-level, on 2022+ rebuilt stats)
| ID | Rule |
|----|------|
| LP-F01 | Exclude `{EXCLUDE_HANDLE}` buyers |
| LP-F02 | Exclude if first **2022+** order was in Jul/Nov |
| LP-F04 | Exclude if first **2022+** order was 51%+ discounted |

### Layer 3 — order-month + product (primary outputs)
- Finals-eligible customers only
- Drop orders in July & November (order month, not acquisition)
- Drop elite-whey line items from `lines.parquet`

## Files

| File | Layers | Rows |
|------|--------|------|
| `orders.parquet` | 0+1+2+3 | {len(orders_finals):,} |
| `lines.parquet` | 0+1+2+3 | {len(lines_finals):,} |
| `customers.parquet` | 0+1+2+3 (stats from L3 orders) | {len(cust_finals):,} |
| `lines_sku_analysis.parquet` | same as lines + `flavor_sku` | {len(lines_sku):,} |
| `orders_dq_clean.parquet` | 0+1 reference | {len(orders_dq):,} |
| `lines_dq_clean.parquet` | 0+1 reference | {len(lines_dq):,} |
| `customers_dq_clean.parquet` | 0+1 reference + LP flags | {len(cust_dq):,} |

Re-run: `python EDA/13_build_finals_datasets.py`
"""

(FINALS_OUT / "README.md").write_text(readme, encoding="utf-8")

print("\n" + "=" * 70)
print("DONE — finals datasets saved to EDA/outputs_finals/")
print(f"  orders.parquet (L0+L1+L2+L3): {len(orders_finals):,}")
print(f"  lines.parquet:                {len(lines_finals):,}")
print(f"  customers.parquet:            {len(cust_finals):,}")
print(f"  lines_sku_analysis.parquet:   {len(lines_sku):,}")
print("=" * 70)
