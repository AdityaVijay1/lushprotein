"""
Shared helpers for aditya_findings analyses.
Loads COGS from LP Excel, finals parquets, and decile pool.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

FINDINGS_DIR = Path(__file__).resolve().parent
EDA_DIR = FINDINGS_DIR.parent
FINALS_DIR = EDA_DIR / "outputs_finals"
DECILE_OUT = EDA_DIR / "decile_analysis" / "outputs"
COGS_FILE = FINDINGS_DIR / "20260616-COGS_Data_Request_LushProtein (1).xlsx"

MARGIN_PROXY = 0.40
DECILE_BEST_FIRST = [f"D{i}" for i in range(1, 11)]
DECILE_CHART_ORDER = [f"D{i}" for i in range(10, 0, -1)]

CHART_STYLE = {
    "figure.dpi": 150,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
}


def load_config():
    spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_cogs_map() -> dict[str, float]:
    """Merge product-master unit_cost + LP-filled COGS sheet."""
    xl = pd.ExcelFile(COGS_FILE)
    all_skus = pd.read_excel(COGS_FILE, "All Sold SKUs")
    missing = pd.read_excel(COGS_FILE, xl.sheet_names[0])

    cost_map: dict[str, float] = {}
    for _, r in all_skus[all_skus["unit_cost"].notna()].iterrows():
        cost_map[str(r["Line: SKU"]).strip()] = float(r["unit_cost"])
    for _, r in missing[missing["COGS"].notna()].iterrows():
        cost_map[str(r["Line: SKU"]).strip()] = float(r["COGS"])
    return cost_map


def load_lines_with_margin() -> pd.DataFrame:
    cost_map = load_cogs_map()
    lines = pd.read_parquet(FINALS_DIR / "lines.parquet").copy()
    lines["sku_key"] = lines["Line: SKU"].astype(str).str.strip()
    lines["unit_cost"] = lines["sku_key"].map(cost_map)
    lines["line_rev"] = pd.to_numeric(lines["Line: Total"], errors="coerce").fillna(0)
    lines["qty"] = pd.to_numeric(lines["Line: Quantity"], errors="coerce").fillna(1).clip(lower=1)
    lines["cogs"] = lines["unit_cost"] * lines["qty"]
    lines["gross_profit"] = lines["line_rev"] - lines["cogs"]
    lines["has_cogs"] = lines["unit_cost"].notna()
    lines["margin_pct"] = np.where(
        lines["line_rev"] > 0,
        lines["gross_profit"] / lines["line_rev"],
        np.nan,
    )
    lines["order_date"] = pd.to_datetime(lines["order_date"], utc=True)
    return lines


def load_decile_pool() -> pd.DataFrame:
    """4,290-customer pool matching run_decile_analysis.py."""
    orders = pd.read_parquet(FINALS_DIR / "orders.parquet")
    cust = pd.read_parquet(FINALS_DIR / "customers.parquet")
    orders["price_total"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)

    mix = orders.groupby("customer_id")["channel"].value_counts(normalize=True).unstack(fill_value=0)
    all_mkt = (
        set(mix[mix["Marketplace"] == 1.0].index.astype(str))
        if "Marketplace" in mix.columns
        else set()
    )
    cust = cust[~cust["customer_id"].astype(str).isin(all_mkt) & (cust["total_orders"] > 0)].copy()
    orders = orders[orders["customer_id"].isin(cust["customer_id"])]

    rebuild = orders.groupby("customer_id").agg(
        clean_orders=("order_id", "count"),
        clean_revenue=("price_total", "sum"),
    ).reset_index()
    df = cust.merge(rebuild, on="customer_id", how="inner")
    df["aov"] = df["clean_revenue"] / df["clean_orders"].clip(lower=1)
    df["profit_proxy"] = df["clean_revenue"] * MARGIN_PROXY
    return df


def assign_decile(series: pd.Series) -> pd.Series:
    ranks = series.rank(method="first", ascending=True)
    return pd.qcut(ranks, q=10, labels=DECILE_CHART_ORDER)


def attach_true_profit(df: pd.DataFrame, lines: pd.DataFrame) -> pd.DataFrame:
    """Add true_gross_profit from COGS-covered line items per customer."""
    covered = lines[lines["has_cogs"]]
    cust_gp = covered.groupby("customer_id").agg(
        true_gp_covered=("gross_profit", "sum"),
        rev_covered=("line_rev", "sum"),
    ).reset_index()
    rev_all = lines.groupby("customer_id")["line_rev"].sum().reset_index(name="rev_total_lines")
    cust_gp = cust_gp.merge(rev_all, on="customer_id", how="outer")
    cust_gp["cogs_coverage_pct"] = np.where(
        cust_gp["rev_total_lines"] > 0,
        cust_gp["rev_covered"].fillna(0) / cust_gp["rev_total_lines"],
        0,
    )

    out = df.merge(cust_gp, on="customer_id", how="left")
    out["true_gp_covered"] = out["true_gp_covered"].fillna(0)
    out["rev_covered"] = out["rev_covered"].fillna(0)
    out["cogs_coverage_pct"] = out["cogs_coverage_pct"].fillna(0)

    # Hybrid: use true GP where covered, proxy for remainder
    out["gp_remainder"] = (out["clean_revenue"] - out["rev_covered"]).clip(lower=0)
    out["true_gross_profit"] = out["true_gp_covered"] + out["gp_remainder"] * MARGIN_PROXY
    out["avg_margin_pct"] = np.where(
        out["clean_revenue"] > 0,
        out["true_gross_profit"] / out["clean_revenue"],
        np.nan,
    )
    return out


def crm_tier(row) -> str:
    if row.get("is_top_both"):
        return "VIP"
    if row.get("is_top_profit") or row.get("profit_decile") == "D1":
        return "Profit_D1"
    if row.get("is_top_freq") or row.get("freq_decile") == "D1":
        return "Freq_D1"
    return "Standard"


def sku_label(row) -> str:
    handle = str(row.get("Line: Product Handle", "") or "unknown")
    if handle in ("nan", "None", ""):
        handle = str(row.get("Line: SKU", "unknown"))
    variant = str(row.get("Line: Variant Title", "") or "")
    if "/" in variant:
        flavour = variant.split("/")[-1].strip()
    else:
        flavour = variant[:30] if variant not in ("nan", "") else "default"
    return f"{handle}|{flavour}"[:80]
