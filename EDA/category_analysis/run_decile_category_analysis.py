"""
run_decile_category_analysis.py — T1–T9 category × decile analysis.

Uses:
  - EDA/decile_analysis/outputs/customers_decile_table.csv (4,290 pool)
  - EDA/outputs_finals/ orders + lines
  - 40% gross-margin profit proxy (until LP provides COGS)

Produces outputs in:
  EDA/category_analysis/outputs/by_profit_decile/
  EDA/category_analysis/outputs/by_frequency_decile/

Run: python EDA/category_analysis/run_decile_category_analysis.py
"""
import warnings
warnings.filterwarnings("ignore")

import importlib.util
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

MARGIN_RATE = 0.40
DECILE_BEST_FIRST = [f"D{i}" for i in range(1, 11)]
CALENDAR_YEARS = [2022, 2023, 2024, 2025]

SCRIPT_DIR = Path(__file__).resolve().parent
EDA_DIR = SCRIPT_DIR.parent


def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_cfg = _load_config()
FINALS_DIR = _cfg.FINALS_DIR
DECILE_CUST_PATH = _cfg.GOLD_ANALYTICS_DECILE / "customers_decile_table.csv"
OUT_BASE = _cfg.GOLD_ANALYTICS_CATEGORY


def _load_data():
    cfg = _load_config()
    classify_product = cfg.classify_product

    decile_cust = pd.read_csv(DECILE_CUST_PATH)
    decile_cust["customer_id"] = decile_cust["customer_id"].astype(str)
    pool_ids = set(decile_cust["customer_id"])

    orders = pd.read_parquet(FINALS_DIR / "orders.parquet")
    lines = pd.read_parquet(FINALS_DIR / "lines.parquet")
    orders["customer_id"] = orders["customer_id"].astype(str)
    lines["customer_id"] = lines["customer_id"].astype(str)

    orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True).dt.tz_convert("Asia/Singapore")
    lines["order_date"] = pd.to_datetime(lines["order_date"], utc=True).dt.tz_convert("Asia/Singapore")
    orders["order_id"] = orders["order_id"].astype(str)
    lines["order_id"] = lines["order_id"].astype(str)

    orders = orders[orders["customer_id"].isin(pool_ids)].copy()
    lines = lines[lines["customer_id"].isin(pool_ids)].copy()

    lines["product_category"] = lines["Line: Product Handle"].apply(classify_product)
    lines["line_revenue"] = pd.to_numeric(lines["Line: Total"], errors="coerce").fillna(0)
    lines["line_qty"] = pd.to_numeric(lines["Line: Quantity"], errors="coerce").fillna(1)
    lines["line_profit"] = lines["line_revenue"] * MARGIN_RATE
    lines["order_year"] = lines["order_date"].dt.year

    orders["order_revenue"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
    orders["order_profit"] = orders["order_revenue"] * MARGIN_RATE
    orders["order_year"] = orders["order_date"].dt.year

    cust = decile_cust.copy()
    cust["first_order_date"] = pd.to_datetime(cust["first_order_date"], utc=True, errors="coerce")

    # Per-customer product breadth
    handles = lines.groupby("customer_id")["Line: Product Handle"].apply(lambda s: set(s)).reset_index()
    handles.columns = ["customer_id", "handles_ever"]
    cats = lines.groupby("customer_id")["product_category"].apply(lambda s: set(s)).reset_index()
    cats.columns = ["customer_id", "categories_ever"]
    cust = cust.merge(handles, on="customer_id", how="left").merge(cats, on="customer_id", how="left")
    cust["n_handles_ever"] = cust["handles_ever"].apply(lambda x: len(x) if isinstance(x, set) else 0)
    cust["n_categories_ever"] = cust["categories_ever"].apply(lambda x: len(x) if isinstance(x, set) else 0)

    # Per-order basket metrics
    order_basket = (
        lines.groupby(["customer_id", "order_id", "order_date"])
        .agg(
            n_cats=("product_category", "nunique"),
            n_handles=("Line: Product Handle", "nunique"),
            n_units=("line_qty", "sum"),
            order_revenue=("line_revenue", "sum"),
        )
        .reset_index()
    )
    order_basket["order_year"] = order_basket["order_date"].dt.year

    # First-transaction categories (T9)
    first_oid = orders.sort_values("order_date").groupby("customer_id")["order_id"].first().reset_index()
    first_oid.columns = ["customer_id", "first_order_id"]
    fol = lines.merge(first_oid, on="customer_id")
    fol = fol[fol["order_id"] == fol["first_order_id"]]
    first_tx = (
        fol.groupby("customer_id")["product_category"]
        .apply(lambda s: sorted(set(s)))
        .reset_index()
        .rename(columns={"product_category": "first_tx_categories"})
    )
    cust = cust.merge(first_tx, on="customer_id", how="left")

    return cust, orders, lines, order_basket


# ══════════════════════════════════════════════════════════════════════════════
# T1 — Decile summary with product metrics
# ══════════════════════════════════════════════════════════════════════════════
def build_t1(cust: pd.DataFrame, order_basket: pd.DataFrame, decile_col: str) -> pd.DataFrame:
    ob = order_basket.merge(cust[["customer_id", decile_col]], on="customer_id")
    pool_n = len(cust)

    cust_agg = cust.groupby(decile_col, observed=False).agg(
        n_customers=("customer_id", "count"),
        total_profit=("profit_proxy", "sum"),
        total_revenue=("clean_revenue", "sum"),
        total_orders=("clean_orders", "sum"),
        avg_profit=("profit_proxy", "mean"),
        avg_orders=("clean_orders", "mean"),
        avg_revenue=("clean_revenue", "mean"),
        avg_aov=("aov", "mean"),
        avg_cats_ever=("n_categories_ever", "mean"),
        avg_handles_ever=("n_handles_ever", "mean"),
    ).reset_index()

    basket_agg = ob.groupby(decile_col, observed=False).agg(
        avg_units_per_tx=("n_units", "mean"),
        avg_cats_per_tx=("n_cats", "mean"),
        avg_handles_per_tx=("n_handles", "mean"),
        total_units=("n_units", "sum"),
        total_tx=("order_id", "count"),
        total_line_revenue=("order_revenue", "sum"),
    ).reset_index()

    t1 = cust_agg.merge(basket_agg, on=decile_col, how="left")
    t1["pct_customers"] = t1["n_customers"] / pool_n
    t1["aov_decile"] = t1["total_revenue"] / t1["total_orders"]
    t1["dollars_per_unit"] = t1["total_line_revenue"] / t1["total_units"]
    t1["units_per_cat_per_tx"] = np.where(
        t1["avg_cats_per_tx"] > 0, t1["avg_units_per_tx"] / t1["avg_cats_per_tx"], np.nan
    )
    t1 = t1.rename(columns={decile_col: "decile"})
    t1 = t1.set_index("decile").reindex(DECILE_BEST_FIRST).reset_index()

    out_cols = [
        "decile", "n_customers", "pct_customers", "avg_profit", "avg_orders",
        "aov_decile", "avg_cats_ever", "avg_handles_ever",
        "avg_units_per_tx", "dollars_per_unit", "units_per_cat_per_tx", "avg_cats_per_tx",
        "total_profit", "total_revenue", "total_orders",
    ]
    return t1[[c for c in out_cols if c in t1.columns]]


# ══════════════════════════════════════════════════════════════════════════════
# T3 — Cross-category buying behavior
# ══════════════════════════════════════════════════════════════════════════════
def build_t3(cust: pd.DataFrame, lines: pd.DataFrame, segment_label: str,
             *, customer_filter=None) -> pd.DataFrame:
    if customer_filter is not None:
        c = cust[cust["customer_id"].isin(customer_filter)].copy()
        ln = lines[lines["customer_id"].isin(customer_filter)].copy()
    else:
        c, ln = cust, lines

    cust_cat_profit = ln.groupby(["customer_id", "product_category"])["line_profit"].sum().reset_index()
    cust_total_profit = cust_cat_profit.groupby("customer_id")["line_profit"].sum()

    rows = []
    for focal in sorted(ln["product_category"].unique()):
        buyers = set(ln.loc[ln["product_category"] == focal, "customer_id"])
        n_buyers = len(buyers)
        if n_buyers == 0:
            continue
        buyer_c = c[c["customer_id"].isin(buyers)]
        n_sole = int((buyer_c["n_categories_ever"] == 1).sum())
        focal_profit = cust_cat_profit[cust_cat_profit["product_category"] == focal].set_index("customer_id")["line_profit"]
        buyer_profit = cust_total_profit.reindex(buyers).fillna(0)
        focal_profit_b = focal_profit.reindex(buyers).fillna(0)
        cat_share = focal_profit_b.sum() / buyer_profit.sum() if buyer_profit.sum() > 0 else np.nan

        addl = Counter()
        for cid in buyers:
            cats = c.loc[c["customer_id"] == cid, "categories_ever"].iloc[0]
            if isinstance(cats, set):
                for cat in cats - {focal}:
                    addl[cat] += 1
        if addl:
            mc, n_also = addl.most_common(1)[0]
            pct_also = n_also / n_buyers
        else:
            mc, pct_also = "", 0.0

        rows.append({
            "segment": segment_label,
            "category": focal,
            "n_category_buyers": n_buyers,
            "pct_sole_cat_buyers": round(n_sole / n_buyers, 4),
            "avg_n_categories": round(buyer_c["n_categories_ever"].mean(), 2),
            "cat_share_of_buyers_profit": round(cat_share, 4) if pd.notna(cat_share) else np.nan,
            "most_common_additional_cat": mc,
            "pct_also_buying": round(pct_also, 4),
        })
    if not rows:
        return pd.DataFrame(columns=[
            "segment", "category", "n_category_buyers", "pct_sole_cat_buyers",
            "avg_n_categories", "cat_share_of_buyers_profit",
            "most_common_additional_cat", "pct_also_buying",
        ])
    return pd.DataFrame(rows).sort_values("n_category_buyers", ascending=False)


# ══════════════════════════════════════════════════════════════════════════════
# T4 — D1 vs All category decomposition
# ══════════════════════════════════════════════════════════════════════════════
def build_t4(cust: pd.DataFrame, lines: pd.DataFrame, orders: pd.DataFrame,
             decile_col: str, d1_value: str = "D1") -> pd.DataFrame:
    span_years = max(1, orders["order_year"].max() - orders["order_year"].min() + 1)
    all_ids = set(cust["customer_id"])
    d1_ids = set(cust.loc[cust[decile_col] == d1_value, "customer_id"])

    # Category orders per customer
    cat_orders = (
        lines.groupby(["customer_id", "product_category", "order_id"])
        .agg(units=("line_qty", "sum"), revenue=("line_revenue", "sum"), profit=("line_profit", "sum"))
        .reset_index()
    )
    cat_cust = (
        cat_orders.groupby(["customer_id", "product_category"])
        .agg(
            cat_orders=("order_id", "nunique"),
            cat_units=("units", "sum"),
            cat_revenue=("revenue", "sum"),
            cat_profit=("profit", "sum"),
        )
        .reset_index()
    )

    rows = []
    for cat in sorted(lines["product_category"].unique()):
        for seg, ids, seg_label in [("All", all_ids, "All"), ("D1", d1_ids, f"D1_{decile_col}")]:
            seg_n = len(ids)
            buyers = cat_cust[(cat_cust["product_category"] == cat) & (cat_cust["customer_id"].isin(ids))]
            n_buyers = buyers["customer_id"].nunique()
            pct_active = n_buyers / seg_n if seg_n else 0

            if n_buyers == 0:
                rows.append({
                    "category": cat, "segment": seg_label, "pct_active": 0,
                    "acof": np.nan, "acov": np.nan, "units_per_order": np.nan,
                    "dollars_per_unit": np.nan, "margin_pct": MARGIN_RATE,
                    "profit_per_customer": 0, "n_buyers": 0,
                })
                continue

            acof = buyers["cat_orders"].sum() / n_buyers / span_years
            acov = buyers["cat_revenue"].sum() / buyers["cat_orders"].sum()
            units_per_order = buyers["cat_units"].sum() / buyers["cat_orders"].sum()
            dollars_per_unit = buyers["cat_revenue"].sum() / buyers["cat_units"].sum()
            profit_per_customer = buyers["cat_profit"].sum() / n_buyers

            rows.append({
                "category": cat,
                "segment": seg_label,
                "pct_active": round(pct_active, 4),
                "acof": round(acof, 2),
                "acov": round(acov, 2),
                "units_per_order": round(units_per_order, 2),
                "dollars_per_unit": round(dollars_per_unit, 2),
                "margin_pct": MARGIN_RATE,
                "profit_per_customer": round(profit_per_customer, 2),
                "n_buyers": n_buyers,
            })

    df = pd.DataFrame(rows)
    # Pivot-style index: compare D1 vs All
    index_rows = []
    for cat in df["category"].unique():
        all_row = df[(df["category"] == cat) & (df["segment"] == "All")]
        d1_row = df[(df["category"] == cat) & (df["segment"].str.startswith("D1"))]
        if all_row.empty or d1_row.empty:
            continue
        all_ppc = all_row["profit_per_customer"].iloc[0]
        d1_ppc = d1_row["profit_per_customer"].iloc[0]
        idx = (d1_ppc / all_ppc * 100) if all_ppc > 0 else np.nan
        all_share = all_row["profit_per_customer"].iloc[0] * all_row["n_buyers"].iloc[0]
        d1_share = d1_row["profit_per_customer"].iloc[0] * d1_row["n_buyers"].iloc[0]
        index_rows.append({
            "category": cat,
            "pct_active_all": all_row["pct_active"].iloc[0],
            "pct_active_d1": d1_row["pct_active"].iloc[0],
            "acof_all": all_row["acof"].iloc[0],
            "acof_d1": d1_row["acof"].iloc[0],
            "acov_all": all_row["acov"].iloc[0],
            "acov_d1": d1_row["acov"].iloc[0],
            "units_per_order_all": all_row["units_per_order"].iloc[0],
            "units_per_order_d1": d1_row["units_per_order"].iloc[0],
            "dollars_per_unit_all": all_row["dollars_per_unit"].iloc[0],
            "dollars_per_unit_d1": d1_row["dollars_per_unit"].iloc[0],
            "margin_pct": MARGIN_RATE,
            "profit_per_customer_all": all_ppc,
            "profit_per_customer_d1": d1_ppc,
            "d1_index": round(idx, 1) if pd.notna(idx) else np.nan,
            "profit_share_all": round(all_share, 2),
            "profit_share_d1": round(d1_share, 2),
        })
    return pd.DataFrame(index_rows).sort_values("d1_index", ascending=False, na_position="last")


# ══════════════════════════════════════════════════════════════════════════════
# T5 — Cumulative categories by decile × calendar year
# ══════════════════════════════════════════════════════════════════════════════
def build_t5(lines: pd.DataFrame, cust: pd.DataFrame, decile_col: str) -> pd.DataFrame:
    rows = []
    for year in CALENDAR_YEARS:
        yr_lines = lines[lines["order_year"] <= year]
        for dec in DECILE_BEST_FIRST:
            ids = set(cust.loc[cust[decile_col] == dec, "customer_id"])
            active = yr_lines[yr_lines["customer_id"].isin(ids)]
            # customers with at least one order by end of year
            cust_with_orders = active.groupby("customer_id")["product_category"].apply(
                lambda s: s.nunique()
            )
            if len(cust_with_orders) == 0:
                avg_cats = np.nan
                n_cust = 0
            else:
                avg_cats = cust_with_orders.mean()
                n_cust = len(cust_with_orders)
            rows.append({
                "decile": dec,
                "calendar_year": year,
                "avg_cumulative_categories": round(avg_cats, 2) if pd.notna(avg_cats) else np.nan,
                "n_customers_with_orders": n_cust,
            })

    df = pd.DataFrame(rows)
    # Add change Yr1 -> Yr4
    pivot = df.pivot(index="decile", columns="calendar_year", values="avg_cumulative_categories")
    if 2022 in pivot.columns and 2025 in pivot.columns:
        pivot["change_yr2022_to_yr2025"] = pivot[2025] - pivot[2022]
    return df, pivot.reset_index()


# ══════════════════════════════════════════════════════════════════════════════
# T6 — Active categories per year (in-year only)
# ══════════════════════════════════════════════════════════════════════════════
def build_t6(lines: pd.DataFrame, cust: pd.DataFrame, decile_col: str) -> pd.DataFrame:
    rows = []
    for year in CALENDAR_YEARS:
        yr_lines = lines[lines["order_year"] == year]
        for dec in DECILE_BEST_FIRST:
            ids = set(cust.loc[cust[decile_col] == dec, "customer_id"])
            active_ids = set(yr_lines[yr_lines["customer_id"].isin(ids)]["customer_id"])
            if not active_ids:
                rows.append({"decile": dec, "calendar_year": year, "avg_active_categories": np.nan, "n_active_customers": 0})
                continue
            sub = yr_lines[yr_lines["customer_id"].isin(active_ids)]
            per_cust = sub.groupby("customer_id")["product_category"].nunique()
            rows.append({
                "decile": dec,
                "calendar_year": year,
                "avg_active_categories": round(per_cust.mean(), 2),
                "n_active_customers": len(per_cust),
            })
    df = pd.DataFrame(rows)
    pivot = df.pivot(index="decile", columns="calendar_year", values="avg_active_categories")
    if 2022 in pivot.columns and 2025 in pivot.columns:
        pivot["trend_yr2022_to_yr2025"] = pivot[2025] - pivot[2022]
    return df, pivot.reset_index()


# ══════════════════════════════════════════════════════════════════════════════
# T7 — D1 cumulative category adoption (% ever bought) by year
# ══════════════════════════════════════════════════════════════════════════════
def build_t7(lines: pd.DataFrame, cust: pd.DataFrame, decile_col: str, d1_value: str = "D1") -> pd.DataFrame:
    d1_ids = set(cust.loc[cust[decile_col] == d1_value, "customer_id"])
    d1_n = len(d1_ids)
    rows = []
    for year in CALENDAR_YEARS:
        yr_lines = lines[(lines["order_year"] <= year) & (lines["customer_id"].isin(d1_ids))]
        for cat in sorted(lines["product_category"].unique()):
            buyers = yr_lines.loc[yr_lines["product_category"] == cat, "customer_id"].nunique()
            rows.append({
                "calendar_year": year,
                "category": cat,
                "pct_d1_ever_bought": round(buyers / d1_n, 4) if d1_n else 0,
                "n_d1_buyers": buyers,
                "d1_pool_size": d1_n,
            })
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# T8 — D1 active category % per year (bought in that year)
# ══════════════════════════════════════════════════════════════════════════════
def build_t8(lines: pd.DataFrame, cust: pd.DataFrame, decile_col: str, d1_value: str = "D1") -> pd.DataFrame:
    d1_ids = set(cust.loc[cust[decile_col] == d1_value, "customer_id"])
    d1_n = len(d1_ids)
    all_cats = sorted(lines["product_category"].unique())
    rows = []
    for year in CALENDAR_YEARS:
        yr_lines = lines[(lines["order_year"] == year) & (lines["customer_id"].isin(d1_ids))]
        active_d1 = yr_lines["customer_id"].nunique()
        for cat in all_cats:
            buyers = yr_lines.loc[yr_lines["product_category"] == cat, "customer_id"].nunique()
            rows.append({
                "calendar_year": year,
                "category": cat,
                "pct_d1_active_in_year": round(buyers / d1_n, 4) if d1_n else 0,
                "n_d1_active_buyers": buyers,
                "d1_pool_size": d1_n,
                "n_d1_active_any_order": active_d1,
            })
    long_df = pd.DataFrame(rows)
    wide_rows = []
    for cat in all_cats:
        sub = long_df[long_df["category"] == cat].set_index("calendar_year")["pct_d1_active_in_year"]
        chg = (sub.get(2025, 0) - sub.get(2022, 0)) * 100 if 2022 in sub.index and 2025 in sub.index else np.nan
        wide_rows.append({
            "category": cat,
            "pct_2022": round(sub.get(2022, np.nan) * 100, 1) if 2022 in sub.index else np.nan,
            "pct_2023": round(sub.get(2023, np.nan) * 100, 1) if 2023 in sub.index else np.nan,
            "pct_2024": round(sub.get(2024, np.nan) * 100, 1) if 2024 in sub.index else np.nan,
            "pct_2025": round(sub.get(2025, np.nan) * 100, 1) if 2025 in sub.index else np.nan,
            "change_pp_yr2022_to_yr2025": round(chg, 1) if pd.notna(chg) else np.nan,
        })
    return long_df, pd.DataFrame(wide_rows).sort_values("change_pp_yr2022_to_yr2025")


# ══════════════════════════════════════════════════════════════════════════════
# T9 — First-transaction category index
# ══════════════════════════════════════════════════════════════════════════════
def build_t9(cust: pd.DataFrame, lines: pd.DataFrame, segment_label: str) -> pd.DataFrame:
    n_pool = len(cust)
    pool_ids = set(cust["customer_id"])
    ln = lines[lines["customer_id"].isin(pool_ids)]
    cohort_avg_vtd = cust["profit_proxy"].mean()
    cat_profit = ln.groupby("product_category")["line_profit"].sum()

    rows = []
    for cat in sorted(ln["product_category"].unique()):
        ever_ids = set(ln.loc[ln["product_category"] == cat, "customer_id"])
        n_ever = len(ever_ids)
        pct_ever = n_ever / n_pool

        first_mask = cust["first_tx_categories"].apply(
            lambda xs: cat in xs if isinstance(xs, list) else False
        )
        first_sub = cust[first_mask]
        n_first = len(first_sub)
        pct_first = n_first / n_pool
        pct_ever_on_first = pct_first / pct_ever if pct_ever > 0 else np.nan
        tot_vtd = first_sub["profit_proxy"].sum()
        avg_vtd = tot_vtd / n_first if n_first > 0 else np.nan
        index = avg_vtd / cohort_avg_vtd * 100 if n_first > 0 and cohort_avg_vtd > 0 else np.nan

        rows.append({
            "segment": segment_label,
            "category": cat,
            "category_profit_sgd": round(cat_profit.get(cat, 0), 2),
            "pct_ever_buying_cat": round(pct_ever, 4),
            "pct_buying_cat_on_first_trans": round(pct_first, 4),
            "n_first_tx_buyers": n_first,
            "pct_ever_buyers_on_first_trans": round(pct_ever_on_first, 4) if pd.notna(pct_ever_on_first) else np.nan,
            "tot_vtd_sgd": round(tot_vtd, 2),
            "avg_vtd_sgd": round(avg_vtd, 2) if pd.notna(avg_vtd) else np.nan,
            "vtd_index": round(index, 1) if pd.notna(index) else np.nan,
            "cohort_avg_vtd_sgd": round(cohort_avg_vtd, 2),
        })
    return pd.DataFrame(rows).sort_values("n_first_tx_buyers", ascending=False)


def run_slice(cust, orders, lines, order_basket, decile_col: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    label = "profit" if decile_col == "profit_decile" else "frequency"
    d1_ids = set(cust.loc[cust[decile_col] == "D1", "customer_id"])

    print(f"\n  [{label}] T1 decile product summary...")
    t1 = build_t1(cust, order_basket, decile_col)
    t1.to_csv(out_dir / "t1_decile_product_summary.csv", index=False)

    print(f"  [{label}] T3 cross-category (all + D1)...")
    t3_all = build_t3(cust, lines, f"all_{label}")
    t3_d1 = build_t3(cust, lines, f"d1_{label}", customer_filter=d1_ids)
    pd.concat([t3_all, t3_d1]).to_csv(out_dir / "t3_cross_category_behavior.csv", index=False)

    print(f"  [{label}] T4 D1 vs All decomposition...")
    t4 = build_t4(cust, lines, orders, decile_col)
    t4.to_csv(out_dir / "t4_d1_vs_all_category_decomposition.csv", index=False)

    print(f"  [{label}] T5 cumulative categories by year...")
    t5_long, t5_wide = build_t5(lines, cust, decile_col)
    t5_long.to_csv(out_dir / "t5_cumulative_categories_by_year.csv", index=False)
    t5_wide.to_csv(out_dir / "t5_cumulative_categories_pivot.csv", index=False)

    print(f"  [{label}] T6 active categories per year...")
    t6_long, t6_wide = build_t6(lines, cust, decile_col)
    t6_long.to_csv(out_dir / "t6_active_categories_per_year.csv", index=False)
    t6_wide.to_csv(out_dir / "t6_active_categories_pivot.csv", index=False)

    print(f"  [{label}] T7 D1 category adoption (cumulative)...")
    t7 = build_t7(lines, cust, decile_col)
    t7.to_csv(out_dir / "t7_d1_category_adoption_cumulative.csv", index=False)

    print(f"  [{label}] T8 D1 active category % by year...")
    t8_long, t8_wide = build_t8(lines, cust, decile_col)
    t8_long.to_csv(out_dir / "t8_d1_active_category_by_year.csv", index=False)
    t8_wide.to_csv(out_dir / "t8_d1_active_category_pivot.csv", index=False)

    print(f"  [{label}] T9 first-transaction index...")
    t9_all = build_t9(cust, lines, f"all_{label}")
    t9_d1 = build_t9(cust[cust["customer_id"].isin(d1_ids)], lines, f"d1_{label}")
    pd.concat([t9_all, t9_d1]).to_csv(out_dir / "t9_first_transaction_index.csv", index=False)

    # D1-only T1 row for quick reference
    t1_d1 = t1[t1["decile"] == "D1"]
    t1_d1.to_csv(out_dir / "t1_d1_snapshot.csv", index=False)

    return {
        "t1_d1_avg_profit": float(t1_d1["avg_profit"].iloc[0]) if len(t1_d1) else None,
        "t1_d10_avg_profit": float(t1.loc[t1["decile"] == "D10", "avg_profit"].iloc[0]) if len(t1) else None,
    }


def main():
    print("=" * 72)
    print("DECILE × CATEGORY ANALYSIS — T1 through T9")
    print("=" * 72)
    print(f"Decile pool: {DECILE_CUST_PATH}")
    print(f"Margin proxy: {MARGIN_RATE:.0%}")
    print(f"Calendar years: {CALENDAR_YEARS}")

    cust, orders, lines, order_basket = _load_data()
    print(f"Pool customers: {len(cust):,} | Orders: {len(orders):,} | Lines: {len(lines):,}")

    stats = {}
    for decile_col, folder in [
        ("profit_decile", OUT_BASE / "by_profit_decile"),
        ("freq_decile", OUT_BASE / "by_frequency_decile"),
    ]:
        stats[folder.name] = run_slice(cust, orders, lines, order_basket, decile_col, folder)

    readme = f"""# Decile × Category Analysis (T1–T9)

Generated by `run_decile_category_analysis.py`.

**Pool:** {len(cust):,} customers from `decile_analysis/outputs/customers_decile_table.csv`  
**Profit proxy:** revenue × {MARGIN_RATE:.0%} (uniform until LP provides COGS)  
**Category:** product-level via `classify_product()` (not flavour)  
**Years:** calendar {CALENDAR_YEARS}

## Folders

| Folder | Decile grouping |
|--------|-----------------|
| `by_profit_decile/` | All tables grouped/filtered by **profit_decile** (D1 = highest profit) |
| `by_frequency_decile/` | All tables grouped/filtered by **freq_decile** (D1 = most frequent) |

## Files (in each folder)

| File | Slide | Description |
|------|-------|-------------|
| `t1_decile_product_summary.csv` | T1 | Decile metrics: AOF, AOV, avg categories, $/unit, cats/tx |
| `t1_d1_snapshot.csv` | T1 | D1 row only |
| `t3_cross_category_behavior.csv` | T3 | Sole-buyer %, cross-shop — all pool + D1 segment |
| `t4_d1_vs_all_category_decomposition.csv` | T4 | Per-category D1 vs All: penetration, ACOF, ACOV, index |
| `t5_cumulative_categories_by_year.csv` | T5 | Cumulative categories ever bought by decile × year |
| `t5_cumulative_categories_pivot.csv` | T5 | Wide pivot + change 2022→2025 |
| `t6_active_categories_per_year.csv` | T6 | In-year active categories by decile |
| `t6_active_categories_pivot.csv` | T6 | Wide pivot + trend |
| `t7_d1_category_adoption_cumulative.csv` | T7 | D1 % ever bought each category by year (cumulative) |
| `t8_d1_active_category_by_year.csv` | T8 | D1 % actively buying category in each year |
| `t8_d1_active_category_pivot.csv` | T8 | Wide with pp change 2022→2025 |
| `t9_first_transaction_index.csv` | T9 | First-tx VTD index — all pool + D1 segment |

## Column notes

- **T5 cumulative:** distinct categories ever purchased through end of calendar year
- **T6 active:** distinct categories purchased *within* that calendar year only
- **T7 cumulative:** % of D1 decile who have ever bought category by end of year
- **T8 active:** % of D1 decile who bought category in that specific year
- **T4 index:** D1 profit/customer ÷ All profit/customer × 100 per category

Re-run: `python EDA/category_analysis/run_decile_category_analysis.py`
"""
    (OUT_BASE / "README_decile_category.md").write_text(readme, encoding="utf-8")

    print("\n" + "=" * 72)
    print("DONE — outputs in category_analysis/outputs/by_profit_decile/ and by_frequency_decile/")
    print("=" * 72)


if __name__ == "__main__":
    main()
