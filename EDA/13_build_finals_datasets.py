"""
13_build_finals_datasets.py
Build finals-filtered Parquet datasets for downstream analysis.

Does NOT modify EDA/outputs/ (midterm base). Writes to EDA/outputs_finals/.

Filter layers (same as 12_finals_deep_dive.py):
  Layer 1 — DQ-02/03/04 order drops, customer stats rebuilt
  Layer 2 — LP-F01..F04 → finals_eligible cohort
  Layer 3 — SKU analysis lines: 2022+ orders, exclude Jul/Nov order months, no elite handle

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
cust = pd.read_parquet(OUT / "customers.parquet")
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
    "customers": len(cust),
    "products": len(products),
    "discounts": len(discounts),
    **{k: len(v) for k, v in rc_tables.items()},
}

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
lines["order_date"] = pd.to_datetime(lines["order_date"], utc=True)
cust["first_order_date"] = pd.to_datetime(cust["first_order_date"], utc=True)
cust["last_order_date"] = pd.to_datetime(cust["last_order_date"], utc=True)
cust["acq_year"] = cust["first_order_date"].dt.year
cust["acq_month"] = cust["first_order_date"].dt.month

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
orders["order_id"] = orders["order_id"].astype(str)
lines["order_id"] = lines["order_id"].astype(str)
orders = orders.merge(src_df, on="order_id", how="left")
orders["order_source"] = orders["Source"].fillna("unknown").str.lower()
orders["is_pos"] = orders["order_source"] == "pos"
orders["is_web"] = orders["order_source"] == "web"

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — DQ-02 / DQ-03 / DQ-04
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Layer 1 — DQ order drops...")
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

# Rebuild customer stats from DQ-clean orders
orders_dq["_rev_sgd"] = pd.to_numeric(orders_dq["Price: Total"], errors="coerce").fillna(0)
_cust_rebuild = (
    orders_dq.groupby("customer_id")
    .agg(
        _total_orders=("order_id", "count"),
        _total_revenue=("_rev_sgd", "sum"),
    )
    .reset_index()
)
orders_dq.drop(columns=["_rev_sgd"], inplace=True)

cust_dq = cust.merge(_cust_rebuild, on="customer_id", how="left")
cust_dq["total_orders"] = cust_dq["_total_orders"].fillna(0).astype(int)
cust_dq["total_revenue"] = cust_dq["_total_revenue"].fillna(0)
cust_dq["is_repeat"] = cust_dq["total_orders"] >= 2
cust_dq.drop(columns=["_total_orders", "_total_revenue"], inplace=True)
# Keep original first_order_date / acq_month from midterm base (matches 12_finals_deep_dive.py)

# First-order discount depth (for LP-F04)
first_ord = orders_dq.sort_values("order_date").groupby("customer_id").first().reset_index()
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
cust_dq = cust_dq.merge(
    first_ord[["customer_id", "first_disc_depth", "first_disc_bin", "first_order_source"]],
    on="customer_id",
    how="left",
)
cust_dq["first_order_pos"] = cust_dq["first_order_source"] == "pos"

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — LP-F01..F04
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Layer 2 — LushProtein feedback filters...")

elite_customers = set(
    lines_dq[lines_dq["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)]["customer_id"]
)
cust_dq["exclude_elite_buyer"] = cust_dq["customer_id"].isin(elite_customers)
cust_dq["exclude_51pct"] = cust_dq["first_disc_bin"].astype(str) == "51%+"
cust_dq["exclude_promo_month"] = cust_dq["acq_month"].isin(EXCLUDE_MONTHS)
cust_dq["finals_eligible"] = (
    (cust_dq["first_order_date"] >= ANALYSIS_START)
    & ~cust_dq["exclude_elite_buyer"]
    & ~cust_dq["exclude_51pct"]
    & ~cust_dq["exclude_promo_month"]
)

print(f"  LP-F01 elite buyers flagged:        {cust_dq['exclude_elite_buyer'].sum():,}")
print(f"  LP-F02 Jul/Nov acquisitions flagged: {cust_dq['exclude_promo_month'].sum():,}")
print(f"  LP-F03 pre-2022 acquisitions:        {(cust_dq['first_order_date'] < ANALYSIS_START).sum():,}")
print(f"  LP-F04 51%+ first-order disc:       {cust_dq['exclude_51pct'].sum():,}")
print(f"  Finals-eligible customers:            {cust_dq['finals_eligible'].sum():,}")

# Finals cohort: all finals_eligible customers (matches 12_finals_deep_dive flag count)
cust_finals = cust_dq[cust_dq["finals_eligible"]].copy()
finals_ids = set(cust_finals["customer_id"])

orders_finals = orders_dq[orders_dq["customer_id"].isin(finals_ids)].copy()
lines_finals = lines_dq[lines_dq["customer_id"].isin(finals_ids)].copy()

# Product breadth (elite handle excluded from line items)
lines_no_elite = lines_dq[
    ~lines_dq["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)
].copy()
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
cust_finals["vtd_decile"] = pd.qcut(
    cust_finals["total_revenue"].rank(method="first"), 10, labels=[f"D{i}" for i in range(1, 11)]
)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — SKU analysis lines
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] Layer 3 — SKU analysis subset...")
lines_sku = lines_no_elite[lines_no_elite["customer_id"].isin(finals_ids)].copy()
lines_sku = lines_sku[lines_sku["order_date"] >= ANALYSIS_START]
lines_sku = lines_sku[~lines_sku["order_date"].dt.month.isin(EXCLUDE_MONTHS)]
print(f"  lines_sku_analysis rows: {len(lines_sku):,}")

# ── Products & discounts (reference copies) ──────────────────────────────────
products_out = products.copy()
products_out["is_excluded_elite"] = products_out["Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)
discounts_out = discounts.copy()

# ── Recharge tables — join to Shopify customer via shopify_order_id ──────────
print("\n[5] Filtering Recharge tables to finals-eligible customers...")
order_cust_map = orders_dq[["order_id", "customer_id"]].drop_duplicates()
order_cust_map["order_id"] = order_cust_map["order_id"].astype(str)

rc_finals = {}
for name, rc in rc_tables.items():
    rc = rc.copy()
    if "shopify_order_id" in rc.columns:
        rc["shopify_order_id"] = rc["shopify_order_id"].astype(str)
        rc = rc.merge(
            order_cust_map.rename(columns={"order_id": "shopify_order_id", "customer_id": "shopify_customer_id"}),
            on="shopify_order_id",
            how="left",
        )
        rc_finals[name] = rc[rc["shopify_customer_id"].isin(finals_ids)].copy()
        print(f"  {name}: {len(rc_finals[name]):,} / {len(rc):,} rows (order-join filter)")
    elif "customer_id" in rc.columns:
        # rc_churned / rc_reactivated use Recharge customer_id — map via any rc order join
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
            .rename(columns={"customer_id": "rc_customer_id"})
        )
        rc = rc.merge(rc_cust_map, left_on="customer_id", right_on="rc_customer_id", how="left")
        rc_finals[name] = rc[rc["shopify_customer_id"].isin(finals_ids)].copy()
        print(f"  {name}: {len(rc_finals[name]):,} / {len(rc):,} rows (customer-map filter)")
    else:
        rc_finals[name] = rc.copy()
        print(f"  {name}: copied unchanged ({len(rc):,} rows)")

# ── Save Parquet files ───────────────────────────────────────────────────────
print("\n[6] Saving Parquet files...")

# Layer 1 reference (DQ-clean full customer base)
orders_dq.to_parquet(FINALS_OUT / "orders_dq_clean.parquet", index=False)
lines_dq.to_parquet(FINALS_OUT / "lines_dq_clean.parquet", index=False)
cust_dq.to_parquet(FINALS_OUT / "customers_dq_clean.parquet", index=False)

# Primary finals cohort (Layer 1 + Layer 2) — default names for analysis
orders_finals.to_parquet(FINALS_OUT / "orders.parquet", index=False)
lines_finals.to_parquet(FINALS_OUT / "lines.parquet", index=False)
cust_finals.to_parquet(FINALS_OUT / "customers.parquet", index=False)

# Layer 3 SKU subset
lines_sku.to_parquet(FINALS_OUT / "lines_sku_analysis.parquet", index=False)

# Reference tables
products_out.to_parquet(FINALS_OUT / "products.parquet", index=False)
discounts_out.to_parquet(FINALS_OUT / "discounts.parquet", index=False)
for name, df in rc_finals.items():
    df.to_parquet(FINALS_OUT / f"{name}.parquet", index=False)

# ── Manifest ─────────────────────────────────────────────────────────────────
manifest = {
    "generated_by": "EDA/13_build_finals_datasets.py",
    "source_dir": str(OUT),
    "output_dir": str(FINALS_OUT),
    "filters_applied": {
        "layer1_dq": {
            "DQ-02": "Price: Total = 0 AND Price: Total Discount = 0",
            "DQ-03": "Price: Total = 0 AND Price: Total Discount > 0",
            "DQ-04": "Tags contains wholesale-sale OR Price: Total > 5000 SGD",
        },
        "layer2_lp": {
            "LP-F01": f"Exclude customers who bought {EXCLUDE_HANDLE}",
            "LP-F02": "Exclude customers acquired in July or November",
            "LP-F03": "first_order_date >= 2022-01-01",
            "LP-F04": "Exclude first-order discount depth 51%+",
        },
        "layer3_sku": {
            "rules": [
                "finals_eligible customers only",
                f"order_date >= {ANALYSIS_START.date()}",
                "exclude order months July and November",
                f"exclude product handle {EXCLUDE_HANDLE}",
            ],
            "file": "lines_sku_analysis.parquet",
        },
    },
    "row_counts": {
        "base_midterm": base_counts,
        "layer1_dq_clean": {
            "orders_dq_clean.parquet": len(orders_dq),
            "lines_dq_clean.parquet": len(lines_dq),
            "customers_dq_clean.parquet": len(cust_dq),
        },
        "layer2_finals_primary": {
            "orders.parquet": len(orders_finals),
            "lines.parquet": len(lines_finals),
            "customers.parquet": len(cust_finals),
        },
        "layer3_sku": {
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

**Source (unchanged midterm base):** `EDA/outputs/`
**This folder:** post-presentation clean analysis pool.

## Filter layers

### Layer 1 — DQ drops (order-level)
| ID | Rule | Dropped |
|----|------|---------|
| DQ-02 | Zero revenue + zero discount | {_dq02.sum():,} orders |
| DQ-03 | 100%-discount free fulfilments | {_dq03.sum():,} orders |
| DQ-04 | wholesale-sale tag OR > S$5,000 | {_dq04.sum():,} orders |
| **Retained** | | **{len(orders_dq):,} orders** |

### Layer 2 — LP feedback (customer-level → `finals_eligible`)
| ID | Rule | Flagged |
|----|------|---------|
| LP-F01 | Exclude `{EXCLUDE_HANDLE}` buyers | {cust_dq['exclude_elite_buyer'].sum():,} |
| LP-F02 | Exclude Jul/Nov acquisitions | {cust_dq['exclude_promo_month'].sum():,} |
| LP-F03 | first_order_date >= 2022-01-01 | {(cust_dq['first_order_date'] < ANALYSIS_START).sum():,} pre-2022 |
| LP-F04 | First order 51%+ discount | {cust_dq['exclude_51pct'].sum():,} |
| **Finals-eligible** | all four LP filters pass | **{len(cust_finals):,} customers** |

### Layer 3 — SKU analysis (`lines_sku_analysis.parquet`)
- Finals-eligible customers
- Orders from 2022-01-01 onwards
- Exclude July & November **order months**
- Exclude `{EXCLUDE_HANDLE}` line items

## Files

| File | Description | Rows |
|------|-------------|------|
| `orders.parquet` | Primary — finals cohort orders (L1+L2) | {len(orders_finals):,} |
| `lines.parquet` | Primary — finals cohort line items (L1+L2) | {len(lines_finals):,} |
| `customers.parquet` | Primary — finals-eligible customers with flags | {len(cust_finals):,} |
| `lines_sku_analysis.parquet` | SKU analysis subset (L1+L2+L3) | {len(lines_sku):,} |
| `orders_dq_clean.parquet` | Reference — DQ-clean only (all customers) | {len(orders_dq):,} |
| `lines_dq_clean.parquet` | Reference — DQ-clean lines | {len(lines_dq):,} |
| `customers_dq_clean.parquet` | Reference — DQ-clean customers + filter flags | {len(cust_dq):,} |
| `products.parquet` | Product master (+ `is_excluded_elite` flag) | {len(products_out):,} |
| `discounts.parquet` | Discount codes (standalone reference) | {len(discounts_out):,} |
| `rc_*.parquet` | Recharge data filtered to finals cohort | see manifest.json |

## Usage

```python
import pandas as pd
from pathlib import Path
FINALS = Path("EDA/outputs_finals")

orders = pd.read_parquet(FINALS / "orders.parquet")
customers = pd.read_parquet(FINALS / "customers.parquet")
lines_sku = pd.read_parquet(FINALS / "lines_sku_analysis.parquet")
```

Re-run after any filter change:
```bash
python EDA/13_build_finals_datasets.py
```
"""

(FINALS_OUT / "README.md").write_text(readme, encoding="utf-8")

print("\n" + "=" * 70)
print("DONE — finals datasets saved to EDA/outputs_finals/")
print(f"  orders.parquet:           {len(orders_finals):,}")
print(f"  lines.parquet:            {len(lines_finals):,}")
print(f"  customers.parquet:        {len(cust_finals):,}")
print(f"  lines_sku_analysis.parquet: {len(lines_sku):,}")
print("=" * 70)
