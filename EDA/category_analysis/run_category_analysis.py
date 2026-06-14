"""
run_category_analysis.py — Category-level analysis on finals-filtered data.

Data source: EDA/outputs_finals/ (customer-cut LP-F03 cohort)
Category definition: product-level via classify_product() in 00_config.py
  (e.g. clear-protein-chocolate and clear-protein-taro -> "Clear Protein")

Outputs (EDA/category_analysis/outputs/):
  01_category_penetration.csv       — % of customers who ever bought each category
  01_repeat_by_first_product.csv    — repeat rate by first product purchased [A]
  02_t3_cross_category_behavior.csv — sole-buyer & cross-purchase metrics [T3]
  03_t9_first_transaction_index.csv — first-transaction VTD index by category [T9]
  summary.txt                       — console-style report

Run: python EDA/category_analysis/run_category_analysis.py
Charts: python EDA/category_analysis/plot_category_analysis.py
"""
import warnings
warnings.filterwarnings("ignore")

import importlib.util
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

MARGIN_RATE = 0.40  # profit proxy — no SKU-level COGS in source data

SCRIPT_DIR = Path(__file__).resolve().parent
EDA_DIR = SCRIPT_DIR.parent
FINALS_DIR = EDA_DIR / "outputs_finals"
OUT_DIR = SCRIPT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cfg = _load_config()
classify_product = cfg.classify_product

print("=" * 72)
print("CATEGORY ANALYSIS — outputs_finals cohort")
print("=" * 72)
print(f"Data: {FINALS_DIR}")

orders = pd.read_parquet(FINALS_DIR / "orders.parquet")
lines = pd.read_parquet(FINALS_DIR / "lines.parquet")
cust = pd.read_parquet(FINALS_DIR / "customers.parquet")

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True)
lines["order_date"] = pd.to_datetime(lines["order_date"], utc=True)
orders["order_id"] = orders["order_id"].astype(str)
lines["order_id"] = lines["order_id"].astype(str)

# Ensure product_category at product (not flavour) level
lines["product_category"] = lines["Line: Product Handle"].apply(classify_product)
lines["line_revenue"] = pd.to_numeric(lines["Line: Total"], errors="coerce").fillna(0)
lines["line_profit"] = lines["line_revenue"] * MARGIN_RATE

cust["profit_proxy"] = pd.to_numeric(cust["total_revenue"], errors="coerce").fillna(0) * MARGIN_RATE
n_cohort = len(cust)
cohort_avg_vtd = cust["profit_proxy"].mean()

# ── Rebuild first-product & first-order categories from finals window ────────
first_order_id = (
    orders.sort_values("order_date")
    .groupby("customer_id")["order_id"]
    .first()
    .rename("first_order_id")
    .reset_index()
)

first_order_lines = lines.merge(first_order_id, on="customer_id")
first_order_lines = first_order_lines[first_order_lines["order_id"] == first_order_lines["first_order_id"]]

# First product cat = first line on first order (matches 01_load_and_merge Top Row logic)
first_line_cat = (
    first_order_lines.sort_values(["customer_id", "Line: Product Handle"])
    .groupby("customer_id")
    .first()
    .reset_index()[["customer_id", "product_category"]]
    .rename(columns={"product_category": "first_product_cat"})
)

# All categories on first transaction (for T9)
first_tx_cats = (
    first_order_lines.groupby("customer_id")["product_category"]
    .apply(lambda s: sorted(set(s)))
    .reset_index()
    .rename(columns={"product_category": "first_tx_categories"})
)

cust = cust.merge(first_line_cat, on="customer_id", how="left", suffixes=("_legacy", ""))
if "first_product_cat_legacy" in cust.columns:
    cust = cust.drop(columns=["first_product_cat_legacy"])
cust = cust.merge(first_tx_cats, on="customer_id", how="left")

# Per-customer category sets (ever bought)
cust_cats = (
    lines.groupby("customer_id")["product_category"]
    .apply(lambda s: set(s))
    .reset_index()
    .rename(columns={"product_category": "categories_ever"})
)
cust = cust.merge(cust_cats, on="customer_id", how="left")
cust["n_categories_ever"] = cust["categories_ever"].apply(lambda x: len(x) if isinstance(x, set) else 0)

report_lines = []
report_lines.append(f"Cohort size: {n_cohort:,} customers")
report_lines.append(f"Cohort avg VTD (profit proxy): S${cohort_avg_vtd:,.2f}")
report_lines.append("")

# ══════════════════════════════════════════════════════════════════════════════
# TASK 1A — Category penetration & revenue overview
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1A] Category penetration (ever bought)")
print("-" * 60)

cat_pen = (
    lines.groupby("product_category")
    .agg(
        n_customers_ever=("customer_id", "nunique"),
        n_orders=("order_id", "nunique"),
        total_units=("Line: Quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_profit=("line_profit", "sum"),
    )
    .reset_index()
)
cat_pen["pct_customers_ever"] = cat_pen["n_customers_ever"] / n_cohort
cat_pen["pct_revenue"] = cat_pen["total_revenue"] / cat_pen["total_revenue"].sum()
cat_pen["avg_revenue_per_buyer"] = cat_pen["total_revenue"] / cat_pen["n_customers_ever"]
cat_pen = cat_pen.sort_values("pct_customers_ever", ascending=False)
cat_pen.to_csv(OUT_DIR / "01_category_penetration.csv", index=False)
print(cat_pen.to_string(index=False))
report_lines.append("[1A] Category penetration saved -> 01_category_penetration.csv")

# ══════════════════════════════════════════════════════════════════════════════
# TASK 1B — Repeat rate by FIRST product purchased (image A)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1B] Repeat rate by first product purchased")
print("-" * 60)

rep_by_first = (
    cust.groupby("first_product_cat", dropna=False)
    .agg(
        customers=("customer_id", "count"),
        repeaters=("is_repeat", "sum"),
        avg_total_orders=("total_orders", "mean"),
        avg_ltv=("total_revenue", "mean"),
        avg_vtd=("profit_proxy", "mean"),
        median_days_2nd=("days_to_second", "median"),
    )
    .assign(repeat_rate=lambda d: d["repeaters"] / d["customers"])
    .sort_values("repeat_rate", ascending=False)
    .reset_index()
)
rep_by_first.to_csv(OUT_DIR / "01_repeat_by_first_product.csv", index=False)
print(rep_by_first.to_string(index=False))
report_lines.append("[1B] Repeat by first product saved -> 01_repeat_by_first_product.csv")

# ══════════════════════════════════════════════════════════════════════════════
# TASK 2 — T3 Category buying behavior & cross-purchasing
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] T3 — Category cross-purchasing behavior")
print("-" * 60)

# Profit by customer x category
cust_cat_profit = (
    lines.groupby(["customer_id", "product_category"])["line_profit"]
    .sum()
    .reset_index()
)
cust_total_profit = cust_cat_profit.groupby("customer_id")["line_profit"].sum().rename("total_profit")

t3_rows = []
all_categories = sorted(lines["product_category"].unique())

for focal in all_categories:
    buyers = set(lines.loc[lines["product_category"] == focal, "customer_id"])
    n_buyers = len(buyers)
    if n_buyers == 0:
        continue

    buyer_rows = cust[cust["customer_id"].isin(buyers)]

    sole_mask = buyer_rows["n_categories_ever"] == 1
    n_sole = int(sole_mask.sum())
    pct_sole = n_sole / n_buyers
    avg_n_cats = buyer_rows["n_categories_ever"].mean()

    focal_profit = (
        cust_cat_profit[cust_cat_profit["product_category"] == focal]
        .set_index("customer_id")["line_profit"]
    )
    buyer_profit = cust_total_profit.reindex(buyers).fillna(0)
    focal_profit_buyers = focal_profit.reindex(buyers).fillna(0)
    cat_share_profit = (
        focal_profit_buyers.sum() / buyer_profit.sum() if buyer_profit.sum() > 0 else np.nan
    )

    # Most common additional category among focal buyers
    addl_counter = Counter()
    for cid in buyers:
        cats = cust.loc[cust["customer_id"] == cid, "categories_ever"].iloc[0]
        if not isinstance(cats, set):
            continue
        for c in cats - {focal}:
            addl_counter[c] += 1

    if addl_counter:
        most_common_addl, n_also = addl_counter.most_common(1)[0]
        pct_also_buying = n_also / n_buyers
    else:
        most_common_addl, pct_also_buying = "", 0.0

    t3_rows.append({
        "category": focal,
        "n_category_buyers": n_buyers,
        "pct_sole_cat_buyers": round(pct_sole, 4),
        "avg_n_categories": round(avg_n_cats, 2),
        "cat_share_of_buyers_profit": round(cat_share_profit, 4) if pd.notna(cat_share_profit) else np.nan,
        "most_common_additional_cat": most_common_addl,
        "pct_also_buying": round(pct_also_buying, 4),
        "n_sole_cat_buyers": n_sole,
        "n_also_buying_most_common": addl_counter.get(most_common_addl, 0) if most_common_addl else 0,
    })

t3 = pd.DataFrame(t3_rows).sort_values("n_category_buyers", ascending=False)
t3.to_csv(OUT_DIR / "02_t3_cross_category_behavior.csv", index=False)
print(t3.to_string(index=False))
report_lines.append("[2] T3 cross-category saved -> 02_t3_cross_category_behavior.csv")

# ══════════════════════════════════════════════════════════════════════════════
# TASK 3 — T9 First-transaction category analysis
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] T9 — First-transaction category index")
print("-" * 60)

# Category profit in analysis window (2022+ finals)
cat_window_profit = lines.groupby("product_category")["line_profit"].sum()

# Ever buyers per category
ever_buyers = {
    cat: set(lines.loc[lines["product_category"] == cat, "customer_id"])
    for cat in all_categories
}

t9_rows = []
for cat in all_categories:
    n_ever = len(ever_buyers[cat])
    pct_ever = n_ever / n_cohort

    # First-transaction buyers: first order included this category
    first_tx_mask = cust["first_tx_categories"].apply(
        lambda xs: cat in xs if isinstance(xs, list) else False
    )
    first_tx_buyers = cust.loc[first_tx_mask, "customer_id"]
    n_first_tx = len(first_tx_buyers)
    pct_first_tx = n_first_tx / n_cohort

    pct_ever_buyers_on_first = (pct_first_tx / pct_ever) if pct_ever > 0 else np.nan

    tot_vtd = cust.loc[first_tx_mask, "profit_proxy"].sum()
    avg_vtd = tot_vtd / n_first_tx if n_first_tx > 0 else np.nan
    index = (avg_vtd / cohort_avg_vtd * 100) if n_first_tx > 0 and cohort_avg_vtd > 0 else np.nan

    t9_rows.append({
        "category": cat,
        "category_profit_SGD": round(cat_window_profit.get(cat, 0), 2),
        "pct_ever_buying_cat": round(pct_ever, 4),
        "pct_buying_cat_on_first_trans": round(pct_first_tx, 4),
        "n_first_tx_buyers": n_first_tx,
        "pct_ever_buyers_buying_cat_on_first_trans": round(pct_ever_buyers_on_first, 4)
        if pd.notna(pct_ever_buyers_on_first) else np.nan,
        "tot_vtd_SGD": round(tot_vtd, 2),
        "avg_vtd_SGD": round(avg_vtd, 2) if pd.notna(avg_vtd) else np.nan,
        "vtd_index": round(index, 1) if pd.notna(index) else np.nan,
        "n_ever_buyers": n_ever,
    })

t9 = pd.DataFrame(t9_rows).sort_values("n_first_tx_buyers", ascending=False)
t9.to_csv(OUT_DIR / "03_t9_first_transaction_index.csv", index=False)
print(t9.to_string(index=False))
report_lines.append("[3] T9 first-transaction index saved -> 03_t9_first_transaction_index.csv")

# ── Summary file ─────────────────────────────────────────────────────────────
readme = f"""# Category Analysis — outputs_finals

Generated by `run_category_analysis.py`.

**Cohort:** {n_cohort:,} customers (finals-filtered, customer-cut LP-F03)  
**VTD:** profit proxy = revenue x {MARGIN_RATE:.0%} (no SKU COGS in source data)  
**Category:** product-level via `classify_product()` — flavours map to same product family

## Files

| File | Description |
|------|-------------|
| `01_category_penetration.csv` | % of cohort who ever bought each category + revenue/profit |
| `01_repeat_by_first_product.csv` | Repeat rate & LTV by first product on first order [A] |
| `02_t3_cross_category_behavior.csv` | Sole-buyer %, cross-shop, profit share [T3] |
| `03_t9_first_transaction_index.csv` | First-transaction VTD index by category [T9] |

## Column definitions

### T3
- **pct_sole_cat_buyers** — % of category buyers who bought only that category (ever)
- **avg_n_categories** — mean distinct categories purchased by category buyers
- **cat_share_of_buyers_profit** — share of those buyers' total profit from this category
- **most_common_additional_cat** — most frequent co-purchased category
- **pct_also_buying** — % of focal buyers who also bought the most common additional category

### T9
- **pct_ever_buying_cat** — % of cohort who ever bought this category
- **pct_buying_cat_on_first_trans** — % whose first order included this category
- **pct_ever_buyers_buying_cat_on_first_trans** — pct_first_tx / pct_ever (entry-point rate among ever-buyers)
- **tot_vtd_SGD** — total profit proxy of customers whose first order included this category
- **avg_vtd_SGD** — tot_vtd / n_first_tx_buyers
- **vtd_index** — avg_vtd / cohort avg VTD x 100 (100 = average)

Re-run: `python EDA/category_analysis/run_category_analysis.py`
"""
(OUT_DIR / "README.md").write_text(readme, encoding="utf-8")

report_lines.append("")
report_lines.append(f"Outputs written to: {OUT_DIR}")
summary_text = "\n".join(report_lines)
(OUT_DIR / "summary.txt").write_text(summary_text, encoding="utf-8")

print("\n" + "=" * 72)
print("DONE — outputs in EDA/category_analysis/outputs/")
print("=" * 72)
