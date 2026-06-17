"""
True-margin analysis using LP COGS data.
Re-ranks profit deciles, quantifies margin leakage, exports coverage stats.

Run: python EDA/aditya_findings/margin_analysis/run_margin_analysis.py
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
    DECILE_BEST_FIRST,
    DECILE_CHART_ORDER,
    MARGIN_PROXY,
    assign_decile,
    attach_true_profit,
    load_cogs_map,
    load_decile_pool,
    load_lines_with_margin,
)

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(CHART_STYLE)
sns.set_theme(style="whitegrid", palette="muted")


def main():
    print("=" * 72)
    print("TRUE MARGIN ANALYSIS — LP COGS")
    print("=" * 72)

    lines = load_lines_with_margin()
    pool = load_decile_pool()
    pool = attach_true_profit(pool, lines)

    # ── Coverage summary ───────────────────────────────────────────────────────
    total_rev = lines["line_rev"].sum()
    covered_rev = lines.loc[lines["has_cogs"], "line_rev"].sum()
    true_gp = lines.loc[lines["has_cogs"], "gross_profit"].sum()
    proxy_gp = total_rev * MARGIN_PROXY

    coverage = pd.DataFrame([{
        "n_skus_with_cost": len(load_cogs_map()),
        "n_lines": len(lines),
        "lines_with_cogs": int(lines["has_cogs"].sum()),
        "pct_lines_covered": round(lines["has_cogs"].mean() * 100, 1),
        "total_revenue_sgd": round(total_rev, 2),
        "revenue_with_cogs_sgd": round(covered_rev, 2),
        "pct_revenue_covered": round(covered_rev / total_rev * 100, 1),
        "true_gp_covered_sgd": round(true_gp, 2),
        "proxy_gp_40pct_sgd": round(proxy_gp, 2),
        "avg_margin_covered_pct": round(
            true_gp / covered_rev * 100 if covered_rev > 0 else 0, 1
        ),
        "method_note": (
            "Hybrid customer GP = true COGS on covered lines + 40% proxy on remainder"
        ),
    }])
    coverage.to_csv(OUT / "cogs_coverage_summary.csv", index=False)

    # SKU-level margin table
    sku_margin = (
        lines.groupby(["sku_key", "Line: Product Handle", "Line: Variant Title", "product_category"])
        .agg(
            line_items=("order_id", "count"),
            revenue=("line_rev", "sum"),
            cogs=("cogs", "sum"),
            gross_profit=("gross_profit", "sum"),
            avg_unit_cost=("unit_cost", "first"),
            has_cogs=("has_cogs", "first"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    sku_margin["margin_pct"] = np.where(
        sku_margin["revenue"] > 0,
        sku_margin["gross_profit"] / sku_margin["revenue"],
        np.nan,
    )
    sku_margin.to_csv(OUT / "sku_true_margin.csv", index=False)

    # ── True profit deciles ────────────────────────────────────────────────────
    pool["profit_decile_proxy"] = assign_decile(pool["profit_proxy"])
    pool["profit_decile_true"] = assign_decile(pool["true_gross_profit"])
    pool["freq_decile"] = assign_decile(pool["clean_orders"])
    pool["is_top_profit"] = pool["profit_decile_true"] == "D1"
    pool["is_top_freq"] = pool["freq_decile"] == "D1"
    pool["is_top_both"] = pool["is_top_profit"] & pool["is_top_freq"]

    total_gp = pool["true_gross_profit"].sum()
    true_summary = (
        pool.groupby("profit_decile_true", observed=False)
        .agg(
            n_customers=("customer_id", "count"),
            total_revenue=("clean_revenue", "sum"),
            total_gp=("true_gross_profit", "sum"),
            avg_gp=("true_gross_profit", "mean"),
            avg_margin_pct=("avg_margin_pct", "mean"),
            avg_revenue=("clean_revenue", "mean"),
            avg_orders=("clean_orders", "mean"),
        )
        .reset_index()
        .rename(columns={"profit_decile_true": "profit_decile"})
    )
    true_summary = true_summary.set_index("profit_decile").reindex(DECILE_BEST_FIRST).reset_index()
    true_summary["pct_gp"] = true_summary["total_gp"] / total_gp
    true_summary["pct_revenue"] = true_summary["total_revenue"] / pool["clean_revenue"].sum()
    true_summary.to_csv(OUT / "true_profit_decile_summary.csv", index=False)

    # Decile rank stability (proxy vs true)
    rank_compare = pool[["customer_id", "profit_decile_proxy", "profit_decile_true"]].copy()
    rank_compare["same_decile"] = rank_compare["profit_decile_proxy"] == rank_compare["profit_decile_true"]
    stability = pd.DataFrame([{
        "n_customers": len(rank_compare),
        "pct_same_decile": round(rank_compare["same_decile"].mean() * 100, 1),
        "pct_d1_both": round(
            ((rank_compare["profit_decile_proxy"] == "D1") &
             (rank_compare["profit_decile_true"] == "D1")).mean() * 100, 1
        ),
        "n_moved_into_d1": int(
            ((rank_compare["profit_decile_proxy"] != "D1") &
             (rank_compare["profit_decile_true"] == "D1")).sum()
        ),
        "n_moved_out_of_d1": int(
            ((rank_compare["profit_decile_proxy"] == "D1") &
             (rank_compare["profit_decile_true"] != "D1")).sum()
        ),
    }])
    stability.to_csv(OUT / "decile_rank_stability.csv", index=False)
    rank_compare.to_csv(OUT / "customer_decile_rank_compare.csv", index=False)

    # Margin leakage scenario
    d1 = pool[pool["profit_decile_true"] == "D1"]
    leakage = pd.DataFrame([
        {
            "scenario": "10pct_site_discount_on_D1",
            "n_customers": len(d1),
            "d1_revenue_sgd": round(d1["clean_revenue"].sum(), 0),
            "d1_gp_sgd": round(d1["true_gross_profit"].sum(), 0),
            "gp_lost_if_10pct_discount_sgd": round(d1["true_gross_profit"].sum() * 0.10, 0),
            "note": "Assumes discount erodes GP proportionally on D1 base",
        },
        {
            "scenario": "10pct_site_discount_on_VIP_only",
            "n_customers": int(d1["is_top_both"].sum()),
            "d1_revenue_sgd": round(d1.loc[d1["is_top_both"], "clean_revenue"].sum(), 0),
            "d1_gp_sgd": round(d1.loc[d1["is_top_both"], "true_gross_profit"].sum(), 0),
            "gp_lost_if_10pct_discount_sgd": round(
                d1.loc[d1["is_top_both"], "true_gross_profit"].sum() * 0.10, 0
            ),
            "note": "VIP = profit D1 AND frequency D1",
        },
        {
            "scenario": "exclude_D1_from_blanket_promo",
            "n_customers": len(d1),
            "d1_revenue_sgd": round(d1["clean_revenue"].sum(), 0),
            "d1_gp_sgd": round(d1["true_gross_profit"].sum(), 0),
            "gp_lost_if_10pct_discount_sgd": 0,
            "note": "Protective action — GP preserved vs blanket promo",
        },
    ])
    leakage.to_csv(OUT / "margin_leakage_scenarios.csv", index=False)

    pool.to_csv(OUT / "customers_with_true_gp.csv", index=False)

    # ── Charts ─────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Chart 1: Proxy vs True GP by decile
    proxy_sum = (
        pool.groupby("profit_decile_proxy", observed=False)["profit_proxy"]
        .sum().reindex(DECILE_CHART_ORDER)
    )
    true_sum = (
        pool.groupby("profit_decile_true", observed=False)["true_gross_profit"]
        .sum().reindex(DECILE_CHART_ORDER)
    )
    x = np.arange(10)
    w = 0.35
    axes[0].bar(x - w / 2, proxy_sum.values / 1000, w, label="40% proxy", color="#95a5a6")
    axes[0].bar(x + w / 2, true_sum.values / 1000, w, label="True COGS (hybrid)", color="#2ecc71")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(DECILE_CHART_ORDER)
    axes[0].set_xlabel("Profit decile (D1 = best)")
    axes[0].set_ylabel("Total GP (S$ thousands)")
    axes[0].set_title("Proxy vs true gross profit by decile")
    axes[0].legend()

    # Chart 2: Avg margin % by decile (true)
    margin_by_dec = (
        pool.groupby("profit_decile_true", observed=False)["avg_margin_pct"]
        .mean().reindex(DECILE_CHART_ORDER) * 100
    )
    colors = ["#27ae60" if d == "D1" else "#3498db" for d in DECILE_CHART_ORDER]
    axes[1].bar(DECILE_CHART_ORDER, margin_by_dec.values, color=colors)
    axes[1].axhline(MARGIN_PROXY * 100, color="red", linestyle="--", label="40% proxy assumption")
    axes[1].set_xlabel("Profit decile (true COGS)")
    axes[1].set_ylabel("Avg gross margin %")
    axes[1].set_title("True margin % by customer decile")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(OUT / "fig_proxy_vs_true_gp.png", bbox_inches="tight")
    plt.close()

    # Chart 3: COGS coverage
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Lines with COGS", "Lines without COGS"]
    sizes = [lines["has_cogs"].sum(), (~lines["has_cogs"]).sum()]
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#2ecc71", "#e74c3c"])
    ax.set_title(f"COGS coverage: {coverage['pct_revenue_covered'].iloc[0]:.1f}% of revenue")
    plt.savefig(OUT / "fig_cogs_coverage.png", bbox_inches="tight")
    plt.close()

    # Chart 4: Margin leakage
    fig, ax = plt.subplots(figsize=(7, 4))
    leak_plot = leakage[leakage["scenario"] != "exclude_D1_from_blanket_promo"]
    ax.barh(leak_plot["scenario"], leak_plot["gp_lost_if_10pct_discount_sgd"] / 1000, color="#e74c3c")
    ax.set_xlabel("GP at risk (S$ thousands) if 10% discount applied")
    ax.set_title("Margin leakage — why D1 needs separate promo rules")
    plt.tight_layout()
    plt.savefig(OUT / "fig_margin_leakage.png", bbox_inches="tight")
    plt.close()

    # Chart 5: Top SKUs by true GP
    top_gp = sku_margin[sku_margin["has_cogs"]].nlargest(12, "gross_profit")
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = [
        f"{r['Line: Product Handle'][:15]}…" if len(str(r["Line: Product Handle"])) > 15
        else r["Line: Product Handle"]
        for _, r in top_gp.iterrows()
    ]
    ax.barh(labels[::-1], (top_gp["gross_profit"] / 1000).values[::-1], color="#3498db")
    ax.set_xlabel("True gross profit (S$ thousands)")
    ax.set_title("Top 12 SKUs by true gross profit (COGS-backed)")
    plt.tight_layout()
    plt.savefig(OUT / "fig_top_skus_true_gp.png", bbox_inches="tight")
    plt.close()

    print(f"\nCoverage: {coverage['pct_revenue_covered'].iloc[0]:.1f}% revenue, "
          f"{coverage['pct_lines_covered'].iloc[0]:.1f}% lines")
    print(f"True GP (covered lines): S${true_gp:,.0f}")
    print(f"Avg margin on covered SKUs: {coverage['avg_margin_covered_pct'].iloc[0]:.1f}%")
    print(f"D1 rank stability: {stability['pct_same_decile'].iloc[0]:.1f}% same decile proxy vs true")
    print(f"Margin leakage (10% on D1): S${leakage.iloc[0]['gp_lost_if_10pct_discount_sgd']:,.0f}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
