"""
Enrich outputs_finals parquets with true COGS margin fields.

Adds to lines.parquet:  unit_cost, cogs, gross_profit, margin_pct, has_cogs
Adds to orders.parquet: order_gp, order_cogs, order_margin_pct
Adds to customers.parquet: true_gross_profit, avg_margin_pct, cogs_coverage_pct,
                           profit_decile_true, crm_tier, n_categories_ever
Updates products.parquet with merged COGS from LP Excel

Run: python EDA/aditya_findings/enrich_finals_with_margin.py
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FINDINGS_DIR = Path(__file__).resolve().parent
EDA_DIR = FINDINGS_DIR.parent
FINALS_DIR = EDA_DIR / "outputs_finals"
sys.path.insert(0, str(FINDINGS_DIR))

from _shared import (  # noqa: E402
    MARGIN_PROXY,
    assign_decile,
    crm_tier,
    load_cogs_map,
)

DECILE_CHART_ORDER = [f"D{i}" for i in range(10, 0, -1)]


def main():
    print("=" * 72)
    print("ENRICH FINALS PARQUETS WITH LP COGS")
    print("=" * 72)

    cost_map = load_cogs_map()
    lines = pd.read_parquet(FINALS_DIR / "lines.parquet")
    orders = pd.read_parquet(FINALS_DIR / "orders.parquet")
    customers = pd.read_parquet(FINALS_DIR / "customers.parquet")
    products = pd.read_parquet(FINALS_DIR / "products.parquet")

    # ── lines.parquet ──────────────────────────────────────────────────────────
    lines["sku_key"] = lines["Line: SKU"].astype(str).str.strip()
    lines["unit_cost"] = lines["sku_key"].map(cost_map)
    lines["line_rev"] = pd.to_numeric(lines["Line: Total"], errors="coerce").fillna(0)
    lines["qty"] = pd.to_numeric(lines["Line: Quantity"], errors="coerce").fillna(1).clip(lower=1)
    lines["cogs"] = lines["unit_cost"] * lines["qty"]
    lines["gross_profit"] = np.where(
        lines["unit_cost"].notna(),
        lines["line_rev"] - lines["cogs"],
        lines["line_rev"] * MARGIN_PROXY,
    )
    lines["has_cogs"] = lines["unit_cost"].notna()
    lines["margin_pct"] = np.where(
        lines["line_rev"] > 0,
        lines["gross_profit"] / lines["line_rev"],
        np.nan,
    )
    lines["gp_method"] = np.where(lines["has_cogs"], "true_cogs", "proxy_40pct")

    # Pack size flag for product analysis
    variant = lines["Line: Variant Title"].astype(str).fillna("")
    lines["pack_size"] = np.where(
        variant.str.contains("1kg|1 kg", case=False, na=False), "1kg",
        np.where(variant.str.contains("500g|500 g", case=False, na=False), "500g", "other"),
    )

    # ── orders.parquet ─────────────────────────────────────────────────────────
    order_gp = lines.groupby("order_id").agg(
        order_gp=("gross_profit", "sum"),
        order_cogs=("cogs", "sum"),
        order_rev=("line_rev", "sum"),
        n_line_items=("order_id", "count"),
        n_categories=("product_category", "nunique"),
        has_full_cogs=("has_cogs", "all"),
    ).reset_index()
    order_gp["order_margin_pct"] = np.where(
        order_gp["order_rev"] > 0,
        order_gp["order_gp"] / order_gp["order_rev"],
        np.nan,
    )
    orders = orders.merge(order_gp, on="order_id", how="left")
    orders["order_gp"] = orders["order_gp"].fillna(
        pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0) * MARGIN_PROXY
    )

    # ── customers.parquet ────────────────────────────────────────────────────
    covered = lines[lines["has_cogs"]]
    cust_gp = covered.groupby("customer_id").agg(
        true_gp_covered=("gross_profit", "sum"),
        rev_covered=("line_rev", "sum"),
    ).reset_index()
    rev_all = lines.groupby("customer_id")["line_rev"].sum().reset_index(name="rev_total_lines")
    cust_gp = rev_all.merge(cust_gp, on="customer_id", how="left")
    cust_gp["true_gp_covered"] = cust_gp["true_gp_covered"].fillna(0)
    cust_gp["rev_covered"] = cust_gp["rev_covered"].fillna(0)
    cust_gp["cogs_coverage_pct"] = np.where(
        cust_gp["rev_total_lines"] > 0,
        cust_gp["rev_covered"] / cust_gp["rev_total_lines"],
        0,
    )

    cat_ever = lines.groupby("customer_id")["product_category"].nunique().reset_index(name="n_categories_ever")
    cust_rev = orders.groupby("customer_id").agg(
        finals_revenue=("Price: Total", lambda s: pd.to_numeric(s, errors="coerce").sum()),
        finals_orders=("order_id", "count"),
        true_gross_profit=("order_gp", "sum"),
    ).reset_index()

    customers = customers.merge(cust_gp, on="customer_id", how="left")
    customers = customers.merge(cat_ever, on="customer_id", how="left")
    customers = customers.merge(cust_rev, on="customer_id", how="left")
    customers["true_gross_profit"] = customers["true_gross_profit"].fillna(
        pd.to_numeric(customers["total_revenue"], errors="coerce").fillna(0) * MARGIN_PROXY
    )
    customers["avg_margin_pct"] = np.where(
        customers["finals_revenue"] > 0,
        customers["true_gross_profit"] / customers["finals_revenue"],
        np.nan,
    )
    customers["n_categories_ever"] = customers["n_categories_ever"].fillna(1).astype(int)

    # Deciles on finals-eligible non-marketplace pool
    pool_mask = customers["finals_eligible"].fillna(False)
    pool = customers[pool_mask].copy()
    pool["profit_decile_true"] = assign_decile(pool["true_gross_profit"])
    pool["freq_decile_true"] = assign_decile(pool["finals_orders"].fillna(pool["total_orders"]))
    pool["is_top_profit"] = pool["profit_decile_true"] == "D1"
    pool["is_top_freq"] = pool["freq_decile_true"] == "D1"
    pool["is_top_both"] = pool["is_top_profit"] & pool["is_top_freq"]
    pool["crm_tier"] = pool.apply(crm_tier, axis=1)

    decile_cols = pool[["customer_id", "profit_decile_true", "freq_decile_true",
                         "is_top_profit", "is_top_freq", "is_top_both", "crm_tier"]]
    customers = customers.merge(decile_cols, on="customer_id", how="left")

    # ── products.parquet ───────────────────────────────────────────────────────
    products["Variant SKU key"] = products["Variant SKU"].astype(str).str.strip()
    products["unit_cost_lp"] = products["Variant SKU key"].map(cost_map)
    products["has_lp_cogs"] = products["unit_cost_lp"].notna()

    # ── Save ───────────────────────────────────────────────────────────────────
    lines.to_parquet(FINALS_DIR / "lines.parquet", index=False)
    orders.to_parquet(FINALS_DIR / "orders.parquet", index=False)
    customers.to_parquet(FINALS_DIR / "customers.parquet", index=False)
    products.to_parquet(FINALS_DIR / "products.parquet", index=False)

    # Summary manifest
    summary = {
        "n_lines": len(lines),
        "pct_lines_with_cogs": round(lines["has_cogs"].mean() * 100, 1),
        "pct_revenue_with_cogs": round(
            lines.loc[lines["has_cogs"], "line_rev"].sum() / lines["line_rev"].sum() * 100, 1
        ),
        "weighted_margin_pct": round(
            lines.loc[lines["has_cogs"], "gross_profit"].sum()
            / lines.loc[lines["has_cogs"], "line_rev"].sum() * 100, 1
        ),
        "n_customers_with_decile": int(customers["profit_decile_true"].notna().sum()),
        "columns_added_lines": ["unit_cost", "cogs", "gross_profit", "margin_pct", "has_cogs", "gp_method", "pack_size"],
        "columns_added_orders": ["order_gp", "order_cogs", "order_rev", "order_margin_pct", "n_categories"],
        "columns_added_customers": ["true_gross_profit", "avg_margin_pct", "cogs_coverage_pct",
                                     "n_categories_ever", "profit_decile_true", "crm_tier"],
    }
    import json
    (FINALS_DIR / "margin_enrichment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print(f"Lines: {summary['pct_lines_with_cogs']}% with COGS, "
          f"{summary['weighted_margin_pct']}% weighted margin")
    print(f"Customers with decile: {summary['n_customers_with_decile']:,}")
    print(f"Saved -> {FINALS_DIR}")


if __name__ == "__main__":
    main()
