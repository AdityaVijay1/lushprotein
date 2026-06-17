"""
Validate and quantify Rec F (Gateway Flavor Playbook) and Rec G (Middle Decile Cross-Sell Window).

Outputs -> EDA/aditya_findings/rec_f_g_validation/outputs/
Docs    -> REC_F_G_ANALYSIS.md, REC_F_G_FEEDBACK.md

Run: python EDA/aditya_findings/rec_f_g_validation/run_rec_f_g_analysis.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

FINDINGS = Path(__file__).resolve().parent.parent
EDA = FINDINGS.parent
FINALS = EDA / "outputs_finals"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(FINDINGS))
from _shared import assign_decile  # noqa: E402

plt.rcParams.update({"figure.dpi": 150, "font.size": 9})
sns.set_theme(style="whitegrid")

LOYAL_MIN_ORDERS = 3
POOL_REPEAT_BASELINE = 0.165  # 1-category repeat from category ladder


def load_pool():
    cust = pd.read_parquet(FINALS / "customers.parquet")
    orders = pd.read_parquet(FINALS / "orders.parquet")
    mix = orders.groupby("customer_id")["channel"].value_counts(normalize=True).unstack(fill_value=0)
    all_mkt = set(mix[mix["Marketplace"] == 1.0].index.astype(str)) if "Marketplace" in mix.columns else set()
    pool = cust[
        cust["finals_eligible"].fillna(False)
        & ~cust["customer_id"].astype(str).isin(all_mkt)
        & (cust["total_orders"] > 0)
    ].copy()
    if "profit_decile_true" not in pool.columns:
        pool["true_gross_profit"] = pool.get("true_gross_profit", pool["total_revenue"] * 0.4)
        pool["profit_decile_true"] = assign_decile(pool["true_gross_profit"])
    pool["n_categories"] = pool.get("n_categories_ever", 1).fillna(1)
    pool["is_loyal"] = pool["total_orders"] >= LOYAL_MIN_ORDERS
    return pool


def build_flavor_quadrant():
    """Rec F: first-purchase SKU -> quadrant."""
    flavor = pd.read_csv(EDA / "outputs" / "12_first_flavor_loyalty_min30.csv")
    loyal_top = pd.read_csv(EDA / "outputs" / "12_loyal_repeater_top_first_flavors.csv")
    loyal_set = set(loyal_top["flavor_sku"].str.strip())

    # Revenue rank from finals lines
    lines = pd.read_parquet(FINALS / "lines.parquet")
    if "line_rev" not in lines.columns:
        lines["line_rev"] = pd.to_numeric(lines["Line: Total"], errors="coerce").fillna(0)
    sku_rev = (
        lines.groupby(["Line: SKU", "Line: Product Handle", "Line: Variant Title"])
        .agg(revenue=("line_rev", "sum"), buyers=("customer_id", "nunique"))
        .reset_index()
    )

    flavor = flavor.rename(columns={"first_sku": "Line: SKU"})
    flavor["Line: SKU"] = flavor["Line: SKU"].astype(str).str.strip()
    sku_rev["Line: SKU"] = sku_rev["Line: SKU"].astype(str).str.strip()
    fq = flavor.merge(
        sku_rev[["Line: SKU", "revenue", "buyers"]].groupby("Line: SKU").first().reset_index(),
        on="Line: SKU", how="left",
    )
    fq["in_loyal_top"] = fq["flavor_sku"].isin(loyal_set)
    fq["loyal_rate"] = fq["repeat_rate"]  # proxy: repeat >= 3 orders path
    fq["pct_loyal_among_repeaters"] = fq["repeat_rate"]

    med_vol = fq["customers"].median()
    med_repeat = fq["repeat_rate"].median()

    def quadrant(row):
        hi_vol = row["customers"] >= med_vol
        hi_rep = row["repeat_rate"] >= med_repeat
        if hi_rep and hi_vol:
            return "Gateway Hero"
        if hi_rep and not hi_vol:
            return "Hidden Gem"
        if not hi_rep and hi_vol:
            return "Acquisition Trap"
        return "Laggard"

    fq["quadrant"] = fq.apply(quadrant, axis=1)
    fq["display_name"] = fq["first_handle"] + " / " + fq["first_variant"].str[:40]
    fq = fq.sort_values("customers", ascending=False)

    # Prize scenario Rec F
    traps = fq[fq["quadrant"] == "Acquisition Trap"]
    heroes = fq[fq["quadrant"] == "Gateway Hero"]
    n_new_acq_yr = 4000  # rough annual new customers estimate
    shift_pct = 0.05
    n_shifted = int(n_new_acq_yr * shift_pct)
    trap_repeat = traps["repeat_rate"].mean() if len(traps) else 0.20
    hero_repeat = heroes["repeat_rate"].mean() if len(heroes) else 0.30
    lift_repeat = (hero_repeat - trap_repeat) / 2  # halfway improvement
    tier2_ltv = 119  # from cross_product 2-product avg
    gp_margin = 0.665  # true weighted margin
    prize_direct = n_shifted * lift_repeat * tier2_ltv * gp_margin

    prize_scenario = pd.DataFrame([{
        "scenario": "Rec F: 5% of new acq shifted from trap to hero entry SKU",
        "annual_new_acquirers_assumed": n_new_acq_yr,
        "pct_shifted": shift_pct,
        "n_shifted": n_shifted,
        "trap_avg_repeat": round(trap_repeat, 3),
        "hero_avg_repeat": round(hero_repeat, 3),
        "incremental_repeat_lift_assumed": round(lift_repeat, 3),
        "gp_per_new_repeater_sgd": round(tier2_ltv * gp_margin, 0),
        "annual_gp_uplift_sgd": round(prize_direct, 0),
        "note": "Conservative: halfway between trap and hero repeat rates",
    }])

    return fq, prize_scenario, med_vol, med_repeat


def build_middle_decile_window(pool: pd.DataFrame):
    """Rec G: D5-D7, 1-category, 2+ orders."""
    mid = pool[pool["profit_decile_true"].isin(["D5", "D6", "D7"])].copy()
    ladder = pd.read_csv(FINDINGS / "pitch_analysis" / "outputs" / "category_ladder_gp.csv")
    gp1 = ladder.loc[ladder["n_categories"] == 1, "avg_gp"].iloc[0]
    gp2 = ladder.loc[ladder["n_categories"] == 2, "avg_gp"].iloc[0]
    gp3 = ladder.loc[ladder["n_categories"] == 3, "avg_gp"].iloc[0]
    rep1 = ladder.loc[ladder["n_categories"] == 1, "repeat_rate"].iloc[0]
    rep2 = ladder.loc[ladder["n_categories"] == 2, "repeat_rate"].iloc[0]

    addressable = mid[(mid["n_categories"] == 1) & (mid["total_orders"] >= 2)]
    two_orders_only = mid[(mid["n_categories"] == 1) & (mid["total_orders"] == 2)]
    three_plus_stuck = mid[(mid["n_categories"] == 1) & (mid["total_orders"] >= 3)]

    conv_rate = 0.08
    n_conv = int(len(addressable) * conv_rate)
    gp_uplift_2cat = gp2 - gp1
    year1_gp = n_conv * gp_uplift_2cat
    n_to_3cat = int(n_conv * 0.30)
    year1_gp += n_to_3cat * (gp3 - gp2)

    scenario = pd.DataFrame([
        {
            "segment": "D5-D7 all",
            "n": len(mid),
            "avg_categories": mid["n_categories"].mean(),
            "avg_orders": mid["total_orders"].mean(),
            "pct_1_category": (mid["n_categories"] == 1).mean(),
        },
        {
            "segment": "D5-D7, 1-cat, 2+ orders (Rec G pool)",
            "n": len(addressable),
            "avg_categories": addressable["n_categories"].mean(),
            "avg_orders": addressable["total_orders"].mean(),
            "pct_1_category": 1.0,
        },
        {
            "segment": "D5-D7, 1-cat, exactly 2 orders",
            "n": len(two_orders_only),
            "avg_categories": 1.0,
            "avg_orders": 2.0,
            "pct_1_category": 1.0,
        },
        {
            "segment": "D5-D7, 1-cat, 3+ orders (stuck repeaters)",
            "n": len(three_plus_stuck),
            "avg_categories": 1.0,
            "avg_orders": three_plus_stuck["total_orders"].mean(),
            "pct_1_category": 1.0,
        },
    ])

    prize = pd.DataFrame([{
        "scenario": "Rec G: 8% of addressable middle-decile convert to 2nd category",
        "pool": len(addressable),
        "pool_definition": "D5-D7, 1 category ever, 2+ orders",
        "conversion_rate": conv_rate,
        "n_converted": n_conv,
        "gp_uplift_per_customer_2cat": round(gp_uplift_2cat, 2),
        "year1_gp_sgd": round(year1_gp, 0),
        "repeat_lift_1_to_2_cat": f"{rep1:.0%} -> {rep2:.0%}",
        "follow_on_30pct_reach_3cat": n_to_3cat,
    }])

    return scenario, prize, addressable


def plot_flavor_quadrant(fq, med_vol, med_repeat):
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = {
        "Gateway Hero": "#27ae60",
        "Hidden Gem": "#3498db",
        "Acquisition Trap": "#e74c3c",
        "Laggard": "#95a5a6",
    }
    for q, grp in fq.groupby("quadrant"):
        ax.scatter(
            grp["customers"], grp["repeat_rate"] * 100,
            s=np.clip(grp["revenue"].fillna(0) / 200, 30, 400),
            c=colors.get(q, "#333"), alpha=0.7, label=q, edgecolors="white",
        )
    for _, r in fq.nlargest(8, "customers").iterrows():
        ax.annotate(
            r["display_name"][:28], (r["customers"], r["repeat_rate"] * 100),
            fontsize=7, alpha=0.9,
        )
    ax.axvline(med_vol, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(med_repeat * 100, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("First-purchase customers (volume)")
    ax.set_ylabel("Repeat rate (%)")
    ax.set_title("Rec F: Entry SKU quadrants (bubble = revenue)")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT / "fig_flavor_quadrant.png", bbox_inches="tight")
    plt.close()


def plot_middle_decile(pool):
    mid = pool[pool["profit_decile_true"].isin(["D5", "D6", "D7"])]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    cat_dist = mid["n_categories"].value_counts().sort_index()
    axes[0].bar(cat_dist.index.astype(str), cat_dist.values, color="#9b59b6")
    axes[0].set_xlabel("Categories ever purchased")
    axes[0].set_ylabel("Customers")
    axes[0].set_title("D5-D7: category breadth distribution")

    addr = mid[(mid["n_categories"] == 1) & (mid["total_orders"] >= 2)]
    axes[1].bar(
        ["D5-D7 total", "1-cat only", "Rec G pool\n(1-cat, 2+ orders)"],
        [len(mid), (mid["n_categories"] == 1).sum(), len(addr)],
        color=["#bdc3c7", "#e67e22", "#e74c3c"],
    )
    axes[1].set_ylabel("Customers")
    axes[1].set_title("Rec G addressable pool")
    plt.tight_layout()
    plt.savefig(OUT / "fig_middle_decile_pool.png", bbox_inches="tight")
    plt.close()


def main():
    print("=" * 72)
    print("REC F & G VALIDATION")
    print("=" * 72)

    pool = load_pool()
    fq, prize_f, med_vol, med_repeat = build_flavor_quadrant()
    mid_scenario, prize_g, addressable = build_middle_decile_window(pool)

    fq.to_csv(OUT / "flavor_quadrant.csv", index=False)
    prize_f.to_csv(OUT / "rec_f_prize_scenario.csv", index=False)
    mid_scenario.to_csv(OUT / "rec_g_segment_breakdown.csv", index=False)
    prize_g.to_csv(OUT / "rec_g_prize_scenario.csv", index=False)

    plot_flavor_quadrant(fq, med_vol, med_repeat)
    plot_middle_decile(pool)

    print("\nRec F quadrants:")
    print(fq.groupby("quadrant").agg(n_skus=("flavor_sku", "count"), avg_repeat=("repeat_rate", "mean"),
                                     total_first_buyers=("customers", "sum")))
    print(f"\nRec F prize: S${prize_f['annual_gp_uplift_sgd'].iloc[0]:,.0f}")
    print(f"\nRec G addressable pool: {len(addressable):,}")
    print(f"Rec G prize: S${prize_g['year1_gp_sgd'].iloc[0]:,.0f}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
