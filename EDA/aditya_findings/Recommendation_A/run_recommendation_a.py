"""
Recommendation A — Stop treating your best customers like strangers.
CRM tiering, margin leakage proof, Klaviyo-ready export.

Run: python EDA/aditya_findings/Recommendation_A/run_recommendation_a.py
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
    DECILE_CHART_ORDER,
    MARGIN_PROXY,
    assign_decile,
    attach_true_profit,
    crm_tier,
    load_decile_pool,
    load_lines_with_margin,
)

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(CHART_STYLE)
sns.set_theme(style="whitegrid")


def main():
    print("=" * 72)
    print("RECOMMENDATION A — Protect the profit core")
    print("=" * 72)

    lines = load_lines_with_margin()
    pool = load_decile_pool()
    pool = attach_true_profit(pool, lines)
    pool["profit_decile"] = assign_decile(pool["true_gross_profit"])
    pool["freq_decile"] = assign_decile(pool["clean_orders"])
    pool["is_top_profit"] = pool["profit_decile"] == "D1"
    pool["is_top_freq"] = pool["freq_decile"] == "D1"
    pool["is_top_both"] = pool["is_top_profit"] & pool["is_top_freq"]
    pool["crm_tier"] = pool.apply(crm_tier, axis=1)

    # ── Tier summary ───────────────────────────────────────────────────────────
    tier_summary = (
        pool.groupby("crm_tier")
        .agg(
            n_customers=("customer_id", "count"),
            total_revenue=("clean_revenue", "sum"),
            total_gp=("true_gross_profit", "sum"),
            avg_revenue=("clean_revenue", "mean"),
            avg_gp=("true_gross_profit", "mean"),
            avg_orders=("clean_orders", "mean"),
            avg_margin_pct=("avg_margin_pct", "mean"),
            avg_aov=("aov", "mean"),
        )
        .reset_index()
        .sort_values("total_gp", ascending=False)
    )
    tier_summary["pct_customers"] = tier_summary["n_customers"] / len(pool)
    tier_summary["pct_gp"] = tier_summary["total_gp"] / pool["true_gross_profit"].sum()
    tier_summary["pct_revenue"] = tier_summary["total_revenue"] / pool["clean_revenue"].sum()
    tier_summary.to_csv(OUT / "crm_tier_summary.csv", index=False)

    # Klaviyo / Shopify export
    export_cols = [
        "customer_id", "crm_tier", "profit_decile", "freq_decile",
        "is_top_both", "is_top_profit", "is_top_freq",
        "clean_revenue", "true_gross_profit", "avg_margin_pct",
        "clean_orders", "aov", "first_channel", "first_product_cat",
    ]
    if "first_channel" not in pool.columns:
        decile_tbl = pd.read_csv(
            Path(__file__).resolve().parents[2] / "decile_analysis" / "outputs" / "customers_decile_table.csv"
        )
        pool = pool.merge(
            decile_tbl[["customer_id", "first_channel", "first_product_cat", "ever_subscribed"]],
            on="customer_id", how="left",
        )
        export_cols += ["ever_subscribed"]

    klaviyo = pool[export_cols].copy()
    klaviyo["promo_policy"] = klaviyo["crm_tier"].map({
        "VIP": "NO_SITE_WIDE_DISCOUNT — early access, bundles, subscription",
        "Profit_D1": "NO_BLANKET_PROMO — premium upsell, multi-category bundles",
        "Freq_D1": "REPLENISHMENT_ONLY — subscribe-and-save, no % off",
        "Standard": "STANDARD_ACQUISITION — win-back only if recent",
    })
    klaviyo.to_csv(OUT / "klaviyo_crm_tiers.csv", index=False)

    # Profit D1 vs Freq D1 comparison
    d1_compare = pd.DataFrame([
        {
            "segment": "Profit D1 (true COGS)",
            "n": int(pool["is_top_profit"].sum()),
            "avg_gp": pool.loc[pool["is_top_profit"], "true_gross_profit"].mean(),
            "avg_revenue": pool.loc[pool["is_top_profit"], "clean_revenue"].mean(),
            "avg_orders": pool.loc[pool["is_top_profit"], "clean_orders"].mean(),
            "avg_margin_pct": pool.loc[pool["is_top_profit"], "avg_margin_pct"].mean(),
        },
        {
            "segment": "Frequency D1",
            "n": int(pool["is_top_freq"].sum()),
            "avg_gp": pool.loc[pool["is_top_freq"], "true_gross_profit"].mean(),
            "avg_revenue": pool.loc[pool["is_top_freq"], "clean_revenue"].mean(),
            "avg_orders": pool.loc[pool["is_top_freq"], "clean_orders"].mean(),
            "avg_margin_pct": pool.loc[pool["is_top_freq"], "avg_margin_pct"].mean(),
        },
        {
            "segment": "VIP (both D1)",
            "n": int(pool["is_top_both"].sum()),
            "avg_gp": pool.loc[pool["is_top_both"], "true_gross_profit"].mean(),
            "avg_revenue": pool.loc[pool["is_top_both"], "clean_revenue"].mean(),
            "avg_orders": pool.loc[pool["is_top_both"], "clean_orders"].mean(),
            "avg_margin_pct": pool.loc[pool["is_top_both"], "avg_margin_pct"].mean(),
        },
        {
            "segment": "D10 (worst)",
            "n": int((pool["profit_decile"] == "D10").sum()),
            "avg_gp": pool.loc[pool["profit_decile"] == "D10", "true_gross_profit"].mean(),
            "avg_revenue": pool.loc[pool["profit_decile"] == "D10", "clean_revenue"].mean(),
            "avg_orders": pool.loc[pool["profit_decile"] == "D10", "clean_orders"].mean(),
            "avg_margin_pct": pool.loc[pool["profit_decile"] == "D10", "avg_margin_pct"].mean(),
        },
    ])
    d1_compare.to_csv(OUT / "d1_profit_vs_frequency.csv", index=False)

    # Discount erosion scenario
    d1_gp = pool.loc[pool["is_top_profit"], "true_gross_profit"].sum()
    scenarios = pd.DataFrame([
        {"discount_pct": 0, "gp_impact_sgd": 0, "label": "No discount"},
        {"discount_pct": 5, "gp_impact_sgd": d1_gp * 0.05, "label": "5% site-wide on D1"},
        {"discount_pct": 10, "gp_impact_sgd": d1_gp * 0.10, "label": "10% site-wide on D1"},
        {"discount_pct": 15, "gp_impact_sgd": d1_gp * 0.15, "label": "15% site-wide on D1"},
        {"discount_pct": 10, "gp_impact_sgd": 0, "label": "Exclude D1 from promo (Rec A)"},
    ])
    scenarios.to_csv(OUT / "discount_erosion_scenarios.csv", index=False)

    # ── Charts ─────────────────────────────────────────────────────────────────
    # Chart 1: CRM tier sizes + GP share
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    tier_order = ["VIP", "Profit_D1", "Freq_D1", "Standard"]
    ts = tier_summary.set_index("crm_tier").reindex(tier_order).reset_index()
    axes[0].bar(ts["crm_tier"], ts["n_customers"], color=["#e74c3c", "#3498db", "#9b59b6", "#95a5a6"])
    axes[0].set_ylabel("Customers")
    axes[0].set_title("CRM tier sizes")
    axes[0].tick_params(axis="x", rotation=15)

    axes[1].bar(ts["crm_tier"], ts["pct_gp"] * 100, color=["#e74c3c", "#3498db", "#9b59b6", "#95a5a6"])
    axes[1].set_ylabel("% of total gross profit")
    axes[1].set_title("GP concentration by tier (true COGS)")
    axes[1].tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(OUT / "fig_crm_tier_summary.png", bbox_inches="tight")
    plt.close()

    # Chart 2: D1 profit vs freq comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = ["avg_gp", "avg_revenue", "avg_orders"]
    x = np.arange(len(metrics))
    w = 0.2
    for i, seg in enumerate(["Profit D1 (true COGS)", "Frequency D1", "VIP (both D1)", "D10 (worst)"]):
        row = d1_compare[d1_compare["segment"] == seg].iloc[0]
        vals = [row["avg_gp"], row["avg_revenue"], row["avg_orders"]]
        ax.bar(x + i * w, vals, w, label=seg)
    ax.set_xticks(x + 1.5 * w)
    ax.set_xticklabels(["Avg GP (SGD)", "Avg Revenue (SGD)", "Avg Orders"])
    ax.set_title("Profit D1 ≠ Frequency D1 — different playbooks needed")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT / "fig_d1_profit_vs_frequency.png", bbox_inches="tight")
    plt.close()

    # Chart 3: GP by profit decile (true COGS) — the "61× gap" proof
    dec_gp = (
        pool.groupby("profit_decile", observed=False)
        .agg(avg_gp=("true_gross_profit", "mean"))
        .reindex(DECILE_CHART_ORDER)
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#27ae60" if d == "D1" else "#bdc3c7" for d in DECILE_CHART_ORDER]
    ax.bar(DECILE_CHART_ORDER, dec_gp["avg_gp"], color=colors)
    d1_avg = dec_gp.loc["D1", "avg_gp"]
    d10_avg = dec_gp.loc["D10", "avg_gp"]
    ratio = d1_avg / d10_avg if d10_avg > 0 else 0
    ax.set_ylabel("Avg true gross profit (SGD)")
    ax.set_title(f"D1 avg GP S${d1_avg:.0f} vs D10 S${d10_avg:.0f} ({ratio:.0f}× gap)")
    plt.tight_layout()
    plt.savefig(OUT / "fig_gp_by_decile_true.png", bbox_inches="tight")
    plt.close()

    # Chart 4: Discount erosion waterfall
    fig, ax = plt.subplots(figsize=(7, 4))
    erosion = scenarios[scenarios["label"] != "Exclude D1 from promo (Rec A)"]
    ax.bar(erosion["label"], erosion["gp_impact_sgd"] / 1000, color="#e74c3c")
    ax.set_ylabel("GP lost (S$ thousands)")
    ax.set_title("Cost of blanket discounts on profit D1")
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(OUT / "fig_discount_erosion.png", bbox_inches="tight")
    plt.close()

    # Chart 5: Margin % by tier
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(ts["crm_tier"], ts["avg_margin_pct"] * 100, color=["#e74c3c", "#3498db", "#9b59b6", "#95a5a6"])
    ax.axhline(MARGIN_PROXY * 100, color="red", linestyle="--", label="40% proxy")
    ax.set_ylabel("Avg gross margin %")
    ax.set_title("True margin by CRM tier — VIPs earn more per dollar")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "fig_margin_by_tier.png", bbox_inches="tight")
    plt.close()

    vip_n = int(pool["is_top_both"].sum())
    profit_d1_n = int(pool["is_top_profit"].sum())
    print(f"\nCRM tiers exported: {len(klaviyo):,} customers")
    print(f"  VIP (both D1): {vip_n}")
    print(f"  Profit D1: {profit_d1_n}")
    print(f"  GP at risk (10% discount on D1): S${d1_gp * 0.10:,.0f}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
