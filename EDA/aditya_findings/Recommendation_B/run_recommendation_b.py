"""
Recommendation B — Product-led cross-sell on a schedule.
Phase 1 category MBA, Klaviyo flow specs, bundle ROI with true COGS.

Run: python EDA/aditya_findings/Recommendation_B/run_recommendation_b.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import (  # noqa: E402
    CHART_STYLE,
    assign_decile,
    attach_true_profit,
    load_decile_pool,
    load_lines_with_margin,
)

EDA_DIR = Path(__file__).resolve().parents[2]
CAT_OUT = EDA_DIR / "category_analysis" / "outputs"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(CHART_STYLE)
sns.set_theme(style="whitegrid")

CATEGORIES = [
    "Clear Protein", "Lean Protein", "Collagen Glow",
    "Accessories", "Soy Protein", "Other", "Unknown",
]


def build_co_purchase_matrix(orders_cats: pd.DataFrame) -> pd.DataFrame:
    """% of row-category buyers who also bought column-category (same customer, ever)."""
    cust_cats = orders_cats.groupby("customer_id")["product_category"].apply(set).reset_index()
    matrix = pd.DataFrame(index=CATEGORIES, columns=CATEGORIES, dtype=float)
    for row_cat in CATEGORIES:
        buyers = cust_cats[cust_cats["product_category"].apply(lambda s: row_cat in s)]
        n = len(buyers)
        if n == 0:
            continue
        for col_cat in CATEGORIES:
            if row_cat == col_cat:
                matrix.loc[row_cat, col_cat] = 100.0
            else:
                also = buyers["product_category"].apply(lambda s: col_cat in s).sum()
                matrix.loc[row_cat, col_cat] = round(also / n * 100, 1)
    return matrix


def main():
    print("=" * 72)
    print("RECOMMENDATION B — Product-led cross-sell")
    print("=" * 72)

    lines = load_lines_with_margin()
    orders = pd.read_parquet(EDA_DIR / "outputs_finals" / "orders.parquet")
    pool = load_decile_pool()
    pool = attach_true_profit(pool, lines)
    pool["profit_decile"] = assign_decile(pool["true_gross_profit"])

    # D1 pool for focused analysis
    d1_ids = set(pool.loc[pool["profit_decile"] == "D1", "customer_id"])
    lines_d1 = lines[lines["customer_id"].isin(d1_ids)]

    # ── Phase 1: Category co-purchase ──────────────────────────────────────────
    co_all = build_co_purchase_matrix(lines)
    co_d1 = build_co_purchase_matrix(lines_d1)
    co_all.to_csv(OUT / "co_purchase_matrix_all.csv")
    co_d1.to_csv(OUT / "co_purchase_matrix_d1.csv")

    # Load existing T3 for validation
    t3_d1 = pd.read_csv(CAT_OUT / "by_profit_decile" / "t3_cross_category_behavior.csv")
    t3_d1 = t3_d1[t3_d1["segment"] == "d1_profit"]

    # ── Cross-sell flow specs (3 Klaviyo flows) ────────────────────────────────
    flows = pd.DataFrame([
        {
            "flow_id": "CS-01",
            "name": "Clear → Lean",
            "trigger": "Order 1 fulfilled — customer bought Clear Protein, no Lean yet",
            "delay_days": 14,
            "fires_before": "Order 2",
            "target_for_order": 2,
            "target_product": "Lean Protein (Thai Milk Tea or Taro 1kg)",
            "evidence_pct": co_d1.loc["Clear Protein", "Lean Protein"]
            if "Clear Protein" in co_d1.index else 25.0,
            "evidence_source": "D1 co-purchase matrix + T3 pct_also_buying",
            "expected_attach_rate": 0.08,
            "avg_basket_gp_sgd": 35,
        },
        {
            "flow_id": "CS-02",
            "name": "Lean → Clear",
            "trigger": "Order 1 fulfilled — customer bought Lean Protein, no Clear yet",
            "delay_days": 14,
            "fires_before": "Order 2",
            "target_for_order": 2,
            "target_product": "Clear Protein (Peach or White Grape 500g)",
            "evidence_pct": co_d1.loc["Lean Protein", "Clear Protein"]
            if "Lean Protein" in co_d1.index else 61.7,
            "evidence_source": "D1 T3: 61.7% Lean buyers also Clear",
            "expected_attach_rate": 0.10,
            "avg_basket_gp_sgd": 38,
        },
        {
            "flow_id": "CS-03",
            "name": "Collagen → Protein",
            "trigger": "Order 1 fulfilled — Collagen only, no protein SKU",
            "delay_days": 21,
            "fires_before": "Order 2",
            "target_for_order": 2,
            "target_product": "Clear or Lean starter (500g)",
            "evidence_pct": 30.5,
            "evidence_source": "Collagen first-tx repeat rate 30.5%",
            "expected_attach_rate": 0.12,
            "avg_basket_gp_sgd": 32,
        },
    ])
    flows.to_csv(OUT / "klaviyo_cross_sell_flows.csv", index=False)

    # ── Bundle ROI (Clear + Lean starter) with true COGS ───────────────────────
    clear_lines = lines[lines["product_category"] == "Clear Protein"]
    lean_lines = lines[lines["product_category"] == "Lean Protein"]
    avg_clear_gp = clear_lines.loc[clear_lines["has_cogs"], "gross_profit"].sum() / max(
        clear_lines.loc[clear_lines["has_cogs"], "qty"].sum(), 1
    )
    avg_lean_gp = lean_lines.loc[lean_lines["has_cogs"], "gross_profit"].sum() / max(
        lean_lines.loc[lean_lines["has_cogs"], "qty"].sum(), 1
    )
    bundle_gp = avg_clear_gp + avg_lean_gp

    single_cat = pool[pool["customer_id"].isin(
        lines.groupby("customer_id")["product_category"].nunique().reset_index()
        .query("product_category == 1")["customer_id"]
    )]
    n_single = len(single_cat)
    n_middle = len(pool[pool["profit_decile"].isin([f"D{i}" for i in range(5, 8)])])

    bundle_scenarios = pd.DataFrame([
        {
            "scenario": "5% single-cat buyers convert to Clear+Lean bundle",
            "pool": n_single,
            "conversion_rate": 0.05,
            "bundle_gp_sgd": round(bundle_gp, 2),
            "bundle_discount_pct": 0.05,
            "net_gp_per_conversion": round(bundle_gp * 0.95, 2),
            "annual_gp_uplift_sgd": round(n_single * 0.05 * bundle_gp * 0.95, 0),
        },
        {
            "scenario": "8% middle decile (D5-D7) add 2nd category via bundle",
            "pool": n_middle,
            "conversion_rate": 0.08,
            "bundle_gp_sgd": round(bundle_gp, 2),
            "bundle_discount_pct": 0.05,
            "net_gp_per_conversion": round(bundle_gp * 0.95, 2),
            "annual_gp_uplift_sgd": round(n_middle * 0.08 * bundle_gp * 0.95, 0),
        },
        {
            "scenario": "Conservative total cross-sell GP (flows + bundle)",
            "pool": len(pool),
            "conversion_rate": 0.03,
            "bundle_gp_sgd": round(bundle_gp, 2),
            "bundle_discount_pct": 0,
            "net_gp_per_conversion": 35,
            "annual_gp_uplift_sgd": 15000,
        },
    ])
    bundle_scenarios.to_csv(OUT / "bundle_roi_scenarios.csv", index=False)

    # ── Category breadth by order number ───────────────────────────────────────
    order_cats = orders[["order_id", "customer_id", "order_date", "product_category"]].copy()
    order_cats = order_cats.sort_values(["customer_id", "order_date"])
    order_cats["order_num"] = order_cats.groupby("customer_id").cumcount() + 1
    breadth = (
        order_cats.groupby("order_num")
        .apply(lambda g: g["product_category"].nunique())
        .reset_index(name="avg_categories_in_order")
    )
    # cumulative unique categories per customer up to order N
    cum_rows = []
    for cust, grp in order_cats.groupby("customer_id"):
        seen = set()
        for _, row in grp.sort_values("order_date").iterrows():
            seen.add(row["product_category"])
            cum_rows.append({
                "customer_id": cust,
                "order_num": row["order_num"],
                "cumulative_categories": len(seen),
            })
    cum_df = pd.DataFrame(cum_rows)
    breadth_by_order = (
        cum_df.groupby("order_num")["cumulative_categories"]
        .mean()
        .reset_index()
    )
    breadth_by_order.to_csv(OUT / "category_breadth_by_order.csv", index=False)

    # Sole vs cross for D1
    d1_cust_cats = (
        lines_d1.groupby("customer_id")["product_category"]
        .apply(lambda s: s.nunique())
        .reset_index(name="n_categories")
    )
    sole_pct = (d1_cust_cats["n_categories"] == 1).mean() * 100
    sole_summary = pd.DataFrame([{
        "segment": "Profit D1",
        "n_customers": len(d1_cust_cats),
        "pct_sole_category": round(sole_pct, 1),
        "pct_multi_category": round(100 - sole_pct, 1),
        "avg_categories": round(d1_cust_cats["n_categories"].mean(), 2),
    }])
    sole_summary.to_csv(OUT / "sole_vs_cross_d1.csv", index=False)

    # ── Charts ─────────────────────────────────────────────────────────────────
    # Chart 1: Co-purchase heatmap (D1)
    core_cats = ["Clear Protein", "Lean Protein", "Collagen Glow", "Accessories"]
    hm = co_d1.loc[core_cats, core_cats].astype(float)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(hm, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax, vmin=0, vmax=80)
    ax.set_title("D1 co-purchase rate (%): row buyers who also bought column")
    plt.tight_layout()
    plt.savefig(OUT / "fig_co_purchase_heatmap_d1.png", bbox_inches="tight")
    plt.close()

    # Chart 2: Sole vs cross (D1)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        [sole_pct, 100 - sole_pct],
        labels=["Sole category", "Multi-category"],
        autopct="%1.1f%%",
        colors=["#e74c3c", "#2ecc71"],
    )
    ax.set_title(f"D1 buyers: only {sole_pct:.0f}% stay in one category")
    plt.savefig(OUT / "fig_sole_vs_cross_d1.png", bbox_inches="tight")
    plt.close()

    # Chart 3: Category breadth by order number
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(breadth_by_order["order_num"], breadth_by_order["cumulative_categories"],
            marker="o", color="#3498db", linewidth=2)
    ax.axvline(3, color="red", linestyle="--", label="Target: 2nd category by order 3")
    ax.set_xlabel("Order number")
    ax.set_ylabel("Avg cumulative categories")
    ax.set_title("Category breadth builds after order 2 — cross-sell at order 3")
    ax.legend()
    ax.set_xticks(range(1, min(8, breadth_by_order["order_num"].max() + 1)))
    plt.tight_layout()
    plt.savefig(OUT / "fig_breadth_by_order.png", bbox_inches="tight")
    plt.close()

    # Chart 4: Cross-sell flow evidence
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(flows["name"], flows["evidence_pct"], color="#9b59b6")
    ax.set_xlabel("Co-purchase / repeat evidence (%)")
    ax.set_title("Evidence backing each Klaviyo cross-sell flow")
    plt.tight_layout()
    plt.savefig(OUT / "fig_cross_sell_flows.png", bbox_inches="tight")
    plt.close()

    # Chart 5: Bundle ROI scenarios
    fig, ax = plt.subplots(figsize=(8, 4))
    scenarios_plot = bundle_scenarios[bundle_scenarios["scenario"] != "Conservative total cross-sell GP (flows + bundle)"]
    ax.barh(scenarios_plot["scenario"], scenarios_plot["annual_gp_uplift_sgd"] / 1000, color="#27ae60")
    ax.set_xlabel("Estimated annual GP uplift (S$ thousands)")
    ax.set_title("Clear + Lean bundle ROI (true COGS, 5% bundle discount)")
    plt.tight_layout()
    plt.savefig(OUT / "fig_bundle_roi.png", bbox_inches="tight")
    plt.close()

    print(f"\nD1 sole-category: {sole_pct:.1f}% | multi: {100-sole_pct:.1f}%")
    print(f"Clear->Lean D1 co-purchase: {co_d1.loc['Clear Protein','Lean Protein']:.1f}%")
    print(f"Lean->Clear D1 co-purchase: {co_d1.loc['Lean Protein','Clear Protein']:.1f}%")
    print(f"Bundle GP (Clear+Lean, true COGS): S${bundle_gp:.2f}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
