"""
13_build_finals_datasets.py
Build finals-filtered Parquet datasets for downstream analysis.

Does NOT modify Silver layer. Writes to data/gold/ (FINALS_DIR).

Filter logic (customer-cut LP-F03 — matches 12_finals_deep_dive.py):
  Layer 1 — DQ-02/03/04 on all orders
  Layer 2 — LP-F01/F02/F03/F04 customer flags (F03 = lifetime first_order_date >= 2022)
  Layer 0 — order_date >= 2022-01-01 on retained finals-eligible customers
  Layer 3 — exclude Jul/Nov order months; exclude elite handle from lines

Primary outputs (orders.parquet, lines.parquet, customers.parquet) = all layers applied.
Reference DQ snapshots → data/gold/reference/ only.

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
FINALS_OUT = cfg.FINALS_DIR
DO_NOT_USE = cfg.GOLD_REFERENCE_DIR
ORDER_FILES = cfg.ORDER_FILES

EXCLUDE_HANDLE = "better-whey-protein-elite"
EXCLUDE_MONTHS = {7, 11}
ANALYSIS_START = pd.Timestamp("2022-01-01", tz="Asia/Singapore")

FINALS_OUT.mkdir(exist_ok=True)
DO_NOT_USE.mkdir(exist_ok=True)

print("=" * 70)
print("BUILD FINALS DATASETS — 13_build_finals_datasets.py")
print("=" * 70)
print(f"Source:  {OUT}")
print(f"Output:  {FINALS_OUT}")
print(f"Reference DQ files -> {DO_NOT_USE}")

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

cust_base["first_order_date"] = pd.to_datetime(cust_base["first_order_date"], utc=True)
cust_base["last_order_date"] = pd.to_datetime(cust_base["last_order_date"], utc=True)

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
# LAYER 1 — DQ-02 / DQ-03 / DQ-04 (all order dates)
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


def _rebuild_customers(orders_df, lines_df, cust_seed, *, preserve_lifetime_acq=True):
    """
    Rebuild order/revenue stats from orders_df.
    When preserve_lifetime_acq=True, keep lifetime first_order_date from cust_seed
    (required for LP-F03 customer cut and LP-F02 acquisition month).
    """
    orders_df = orders_df.copy()
    orders_df["_rev_sgd"] = pd.to_numeric(orders_df["Price: Total"], errors="coerce").fillna(0)

    agg = (
        orders_df.groupby("customer_id")
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("_rev_sgd", "sum"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    orders_df.drop(columns=["_rev_sgd"], inplace=True, errors="ignore")

    active_ids = set(agg["customer_id"])
    cust = cust_seed[cust_seed["customer_id"].isin(active_ids)].copy()

    drop_cols = [
        "total_orders", "total_revenue", "first_order_date", "last_order_date",
        "is_repeat", "acq_year", "acq_month", "lifespan_days", "recency_days", "days_to_second",
        "second_order_date", "first_disc_depth", "first_disc_bin", "first_order_source", "first_order_pos",
        "exclude_elite_buyer", "exclude_51pct", "exclude_promo_month", "finals_eligible",
        "unique_handles", "unique_flavor_skus", "loyal_repeater", "profit_proxy", "vtd_decile",
    ]
    cust = cust.drop(columns=[c for c in drop_cols if c in cust.columns])
    cust = cust.merge(agg, on="customer_id", how="inner")

    if preserve_lifetime_acq:
        acq_cols = cust_seed[["customer_id", "first_order_date"]].drop_duplicates("customer_id")
        cust = cust.merge(acq_cols, on="customer_id", how="left", suffixes=("_drop", ""))
        if "first_order_date_drop" in cust.columns:
            cust = cust.drop(columns=["first_order_date_drop"])
    else:
        first_dt = (
            orders_df.groupby("customer_id")["order_date"]
            .min()
            .reset_index()
            .rename(columns={"order_date": "first_order_date"})
        )
        cust = cust.merge(first_dt, on="customer_id", how="left")

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

    for col in ["first_channel", "ever_subscribed", "ever_discounted", "first_product_cat"]:
        if col not in cust.columns and col in cust_seed.columns:
            cust = cust.merge(cust_seed[["customer_id", col]].drop_duplicates("customer_id"), on="customer_id", how="left")

    elite_customers = set(
        lines_df[lines_df["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)]["customer_id"]
    )
    cust["exclude_elite_buyer"] = cust["customer_id"].isin(elite_customers)
    cust["exclude_51pct"] = cust["first_disc_bin"].astype(str) == "51%+"
    cust["exclude_promo_month"] = cust["acq_month"].isin(EXCLUDE_MONTHS)
    cust["finals_eligible"] = (
        (cust["first_order_date"] >= ANALYSIS_START)   # LP-F03: customer cut (lifetime acq)
        & ~cust["exclude_elite_buyer"]
        & ~cust["exclude_51pct"]
        & ~cust["exclude_promo_month"]
    )
    return cust


cust_dq = _rebuild_customers(orders_dq, lines_dq, cust_base, preserve_lifetime_acq=True)
print(f"  Active customers after DQ: {len(cust_dq):,}")

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — LP customer filters (F03 = exclude pre-2022 acquisitions entirely)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Layer 2 — LushProtein feedback filters...")
_pre2022 = (cust_dq["first_order_date"] < ANALYSIS_START).sum()
print(f"  LP-F03 pre-2022 acquisitions (excluded):  {_pre2022:,}")
print(f"  LP-F01 elite buyers flagged:              {cust_dq['exclude_elite_buyer'].sum():,}")
print(f"  LP-F02 Jul/Nov acquisitions flagged:      {cust_dq['exclude_promo_month'].sum():,}")
print(f"  LP-F04 51%+ first-order disc flagged:     {cust_dq['exclude_51pct'].sum():,}")
print(f"  Finals-eligible customers:                {cust_dq['finals_eligible'].sum():,}")

finals_ids = set(cust_dq[cust_dq["finals_eligible"]]["customer_id"])
orders_l2 = orders_dq[orders_dq["customer_id"].isin(finals_ids)].copy()
lines_l2 = lines_dq[lines_dq["customer_id"].isin(finals_ids)].copy()
cust_l2 = cust_dq[cust_dq["finals_eligible"]].copy()

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 0 — 2022+ order window (on finals-eligible customers only)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] Layer 0 — 2022+ order window...")
_n_pre_window = len(orders_l2)
orders_l2 = orders_l2[orders_l2["order_date"] >= ANALYSIS_START].copy()
lines_l2 = lines_l2[lines_l2["order_id"].isin(set(orders_l2["order_id"]))].copy()
print(f"  Pre-2022 orders dropped: {_n_pre_window - len(orders_l2):,}")
print(f"  Retained 2022+ orders:     {len(orders_l2):,}")

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

cust_finals = _rebuild_customers(orders_finals, lines_finals, cust_l2, preserve_lifetime_acq=True)
cust_finals = cust_finals[cust_finals["customer_id"].isin(finals_ids)].copy()
cust_finals["finals_eligible"] = True

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

lines_sku = lines_no_elite.copy()

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

# Reference snapshots only — not for downstream analysis
orders_dq.to_parquet(DO_NOT_USE / "orders_dq_clean.parquet", index=False)
lines_dq.to_parquet(DO_NOT_USE / "lines_dq_clean.parquet", index=False)
cust_dq.to_parquet(DO_NOT_USE / "customers_dq_clean.parquet", index=False)

# Remove legacy dq_clean copies from outputs_finals root if present
for legacy in ["orders_dq_clean.parquet", "lines_dq_clean.parquet", "customers_dq_clean.parquet"]:
    legacy_path = FINALS_OUT / legacy
    if legacy_path.exists():
        legacy_path.unlink()
        print(f"  Removed legacy root file: {legacy}")

# Primary: all layers applied
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
    "approach": (
        "Customer-cut LP-F03: exclude customers whose lifetime first_order_date < 2022-01-01. "
        "Retained customers keep all 2022+ orders. Order window + Jul/Nov order-month filter applied at order level."
    ),
    "filters_applied": {
        "layer1_dq": {
            "DQ-02": "Price: Total = 0 AND Price: Total Discount = 0",
            "DQ-03": "Price: Total = 0 AND Price: Total Discount > 0",
            "DQ-04": "Tags contains wholesale-sale OR Price: Total > 5000 SGD",
        },
        "layer2_lp_customer": {
            "LP-F03": f"lifetime first_order_date >= {ANALYSIS_START.date()} — entire customer excluded if acquired pre-2022",
            "LP-F01": f"Exclude customers who bought {EXCLUDE_HANDLE}",
            "LP-F02": "Exclude customers acquired in July or November (lifetime acq month)",
            "LP-F04": "Exclude first retained order with discount depth 51%+",
        },
        "layer0_order_window": {
            "rule": f"order_date >= {ANALYSIS_START.date()} on finals-eligible customers",
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
    "reference_files_dir": str(DO_NOT_USE),
    "row_counts": {
        "base_midterm": base_counts,
        "reference_dq_only_in_do_not_use_these": {
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

## LP-F03 — customer cut (reverted from order cut)

**Rule:** If a customer's *lifetime* `first_order_date` is before 2022-01-01, drop the **entire customer** — none of their orders appear, even from 2024.

**Example:** Customer acquired March 2022 → keeps 2022, 2023, 2024, and 2025 orders.  
Customer acquired in 2021 → excluded completely.

**Additional order-level filters:**
- `order_date >= 2022-01-01` on retained customers
- Drop orders in **July & November** (order month)
- Drop elite-whey line items from `lines.parquet`

## Filter layers (primary files)

### Layer 1 — DQ drops
| ID | Rule |
|----|------|
| DQ-02 | Zero revenue + zero discount |
| DQ-03 | 100%-discount free fulfilments |
| DQ-04 | wholesale-sale tag OR > S$5,000 |

### Layer 2 — LP feedback (customer-level)
| ID | Rule |
|----|------|
| LP-F03 | Lifetime `first_order_date >= 2022-01-01` |
| LP-F01 | Exclude `{EXCLUDE_HANDLE}` buyers |
| LP-F02 | Exclude Jul/Nov **acquisition** months |
| LP-F04 | Exclude 51%+ discounted first retained order |

### Layer 0 — order window
- `order_date >= 2022-01-01` (on finals-eligible customers)

### Layer 3 — order-month + product
- Drop Jul/Nov order months
- Drop elite handle from lines

## Files

| File | Description | Rows |
|------|-------------|------|
| `orders.parquet` | Primary — all layers | {len(orders_finals):,} |
| `lines.parquet` | Primary — all layers | {len(lines_finals):,} |
| `customers.parquet` | Primary — all layers | {len(cust_finals):,} |
| `lines_sku_analysis.parquet` | Primary + flavor_sku | {len(lines_sku):,} |
| `discounts.parquet` | Reference (unchanged) | {len(discounts_out):,} |
| `products.parquet` | Reference | {len(products_out):,} |

**Do not use for analysis:** `do_not_use_these/*_dq_clean.parquet` (DQ-only reference snapshots).

Re-run: `python EDA/13_build_finals_datasets.py`
"""

(FINALS_OUT / "README.md").write_text(readme, encoding="utf-8")

(DO_NOT_USE / "README.md").write_text(
    """# do_not_use_these — reference snapshots only

These `*_dq_clean.parquet` files are **DQ-only** reference outputs from `13_build_finals_datasets.py`.
They still contain all order dates and have **not** had LP-F03 customer exclusion applied.

For all analysis (deciles, deep dives, finals report), use the primary files in the parent folder:
- `orders.parquet`
- `customers.parquet`
- `lines.parquet`
""",
    encoding="utf-8",
)

print("\n" + "=" * 70)
print("DONE — finals datasets saved to EDA/outputs_finals/")
print(f"  orders.parquet (all layers): {len(orders_finals):,}")
print(f"  lines.parquet:             {len(lines_finals):,}")
print(f"  customers.parquet:         {len(cust_finals):,}")
print(f"  DQ reference -> do_not_use_these/")
print("=" * 70)
