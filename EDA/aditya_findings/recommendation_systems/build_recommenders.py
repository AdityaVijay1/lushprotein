"""
Four recommendation systems + comparison export.
1. Rule-based (category T3 rules)
2. Association rules (same-order SKU pairs)
3. Sequential next-best (1st → 2nd order)
4. Item-based collaborative filtering (cosine similarity on user-item matrix)

Run: python EDA/aditya_findings/recommendation_systems/build_recommenders.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import CHART_STYLE, load_lines_with_margin, sku_label  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(CHART_STYLE)
sns.set_theme(style="whitegrid")

# ── 1. Rule-based recommender ──────────────────────────────────────────────────
RULES = [
    {"if_bought": "Clear Protein", "recommend": "Lean Protein", "rule": "D1 T3: 25-62% also buy Lean"},
    {"if_bought": "Lean Protein", "recommend": "Clear Protein", "rule": "D1 T3: 61.7% also buy Clear"},
    {"if_bought": "Lean Protein", "recommend": "Accessories", "rule": "Cohort T3: 29% also Accessories"},
    {"if_bought": "Clear Protein", "recommend": "Accessories", "rule": "Cart add-on, not acquisition"},
    {"if_bought": "Collagen Glow", "recommend": "Clear Protein", "rule": "Collagen repeat 30.5%, protein cross-sell"},
    {"if_bought": "Accessories", "recommend": "Lean Protein", "rule": "Accessories→Lean 41% cohort"},
    {"if_bought": "Accessories", "recommend": "Clear Protein", "rule": "Shaker buyers need protein trial"},
]


def rule_based_recommend(bought_category: str) -> list[dict]:
    return [r for r in RULES if r["if_bought"] == bought_category]


# ── 2. Association rules (load from MBA output) ───────────────────────────────
def association_recommend(sku: str, rules_df: pd.DataFrame, top_n: int = 3) -> list[str]:
    matches = rules_df[rules_df["antecedent"] == sku].nlargest(top_n, "confidence")
    return matches["consequent"].tolist()


# ── 3. Sequential next-best ────────────────────────────────────────────────────
def sequential_recommend(first_sku: str, seq_df: pd.DataFrame) -> str | None:
    row = seq_df[seq_df["first_order_sku"] == first_sku]
    if row.empty:
        return None
    return row.iloc[0]["second_order_sku"]


# ── 4. Item-based CF ─────────────────────────────────────────────────────────
def build_item_cf_matrix(lines: pd.DataFrame, min_customers: int = 5) -> tuple[pd.DataFrame, list]:
    """Customer × SKU binary matrix; return item-item cosine similarity."""
    lines = lines.copy()
    lines["sku_display"] = lines.apply(sku_label, axis=1)
    cust_sku = lines.groupby(["customer_id", "sku_display"]).size().unstack(fill_value=0)
    cust_sku = (cust_sku > 0).astype(int)

    # Keep SKUs bought by >= min_customers
    sku_counts = cust_sku.sum(axis=0)
    keep = sku_counts[sku_counts >= min_customers].index.tolist()
    mat = cust_sku[keep]

    item_sim = pd.DataFrame(
        cosine_similarity(mat.T),
        index=keep,
        columns=keep,
    )
    return item_sim, keep


def cf_recommend(bought_skus: list[str], item_sim: pd.DataFrame, top_n: int = 3) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for sku in bought_skus:
        if sku not in item_sim.index:
            continue
        sims = item_sim.loc[sku].drop(bought_skus, errors="ignore")
        for other, score in sims.items():
            scores[other] = scores.get(other, 0) + score
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
    return ranked


def main():
    print("=" * 72)
    print("RECOMMENDATION SYSTEMS — 4 types")
    print("=" * 72)

    lines = load_lines_with_margin()
    lines["sku_display"] = lines.apply(sku_label, axis=1)

    mba_dir = OUT
    rules_path = mba_dir / "sku_association_rules.csv"
    seq_path = mba_dir / "first_to_second_sku_matrix.csv"

    if not rules_path.exists():
        print("Running SKU MBA first...")
        import sku_market_basket  # noqa: F401
        exec(open(Path(__file__).parent / "sku_market_basket.py").read())

    rules_df = pd.read_csv(rules_path)
    seq_df = pd.read_csv(seq_path)

    # Export rule-based
    pd.DataFrame(RULES).to_csv(OUT / "recommender_01_rule_based.csv", index=False)

    # Item-CF
    item_sim, keep_skus = build_item_cf_matrix(lines, min_customers=10)
    item_sim.to_csv(OUT / "recommender_04_item_similarity_matrix.csv")

    # ── Demo recommendations for hero SKUs ─────────────────────────────────────
    hero_skus = [
        "clear-protein|Peach",
        "clear-protein|White Grape",
        "lean-protein|Thai Milk Tea",
        "lean-protein|Taro",
        "collagen-glow|Unflavoured",
    ]
    # Find closest matching sku_display in data
    all_skus = lines["sku_display"].unique()
    demo_rows = []
    for hero in hero_skus:
        match = next((s for s in all_skus if hero.split("|")[0] in s and hero.split("|")[1] in s), None)
        if not match:
            continue
        cat = lines.loc[lines["sku_display"] == match, "product_category"].iloc[0]
        rb = rule_based_recommend(cat)
        ar = association_recommend(match, rules_df)
        seq = sequential_recommend(match, seq_df)
        cf = cf_recommend([match], item_sim)
        demo_rows.append({
            "input_sku": match,
            "input_category": cat,
            "rule_based": "; ".join(r["recommend"] for r in rb),
            "association_rules": "; ".join(ar[:3]),
            "sequential_next": seq or "",
            "item_cf_top3": "; ".join(f"{s}({sc:.2f})" for s, sc in cf),
        })

    demo_df = pd.DataFrame(demo_rows)
    demo_df.to_csv(OUT / "recommender_comparison_demo.csv", index=False)

    # System comparison summary
    comparison = pd.DataFrame([
        {
            "system": "1. Rule-based",
            "data_needed": "Category T3 cross-sell table",
            "cold_start": "Excellent — works on 1st purchase",
            "personalisation": "Low — same rules for all",
            "best_use": "Klaviyo flows, post-purchase emails",
            "build_effort": "Low (1 day)",
            "expected_attach_lift": "5-8%",
        },
        {
            "system": "2. Association rules",
            "data_needed": "Same-order SKU pairs (lines.parquet)",
            "cold_start": "Good — needs basket history",
            "personalisation": "Medium — SKU-specific",
            "best_use": "PDP 'Frequently bought together'",
            "build_effort": "Low-Medium (MBA script)",
            "expected_attach_lift": "2-4% on PDP",
        },
        {
            "system": "3. Sequential next-best",
            "data_needed": "1st → 2nd order transitions",
            "cold_start": "Medium — needs 1 prior order",
            "personalisation": "High — order-sequence aware",
            "best_use": "Post-purchase email at order 2",
            "build_effort": "Medium",
            "expected_attach_lift": "3-5% on repeat orders",
        },
        {
            "system": "4. Item-based CF",
            "data_needed": "Customer × SKU purchase matrix",
            "cold_start": "Poor for new SKUs/customers",
            "personalisation": "High — similarity-based",
            "best_use": "Logged-in 'You may also like'",
            "build_effort": "Medium-High",
            "expected_attach_lift": "2-3% incremental vs rules",
        },
    ])
    comparison.to_csv(OUT / "recommender_system_comparison.csv", index=False)

    # ── Charts ─────────────────────────────────────────────────────────────────
    # Chart: Top association rules
    top_rules = rules_df.head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [
        f"{r['antecedent'][:25]}→{r['consequent'][:25]}"
        for _, r in top_rules.iterrows()
    ]
    ax.barh(labels[::-1], top_rules["confidence"].values[::-1], color="#3498db")
    ax.set_xlabel("Confidence")
    ax.set_title("Top 10 SKU association rules (same-order)")
    plt.tight_layout()
    plt.savefig(OUT / "fig_top_association_rules.png", bbox_inches="tight")
    plt.close()

    # Chart: Recommender effort vs impact
    fig, ax = plt.subplots(figsize=(7, 5))
    effort_map = {"Low (1 day)": 1, "Low-Medium (MBA script)": 2, "Medium": 3, "Medium-High": 4}
    lift_map = {"5-8%": 6.5, "2-4% on PDP": 3, "3-5% on repeat orders": 4, "2-3% incremental vs rules": 2.5}
    for _, row in comparison.iterrows():
        ax.scatter(
            effort_map.get(row["build_effort"], 2),
            lift_map.get(row["expected_attach_lift"], 3),
            s=200, alpha=0.7,
        )
        ax.annotate(row["system"], (effort_map.get(row["build_effort"], 2),
                                    lift_map.get(row["expected_attach_lift"], 3)),
                    fontsize=8, ha="center")
    ax.set_xlabel("Build effort →")
    ax.set_ylabel("Expected attach lift (%) →")
    ax.set_title("Recommender systems: effort vs impact")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["Low", "Low-Med", "Medium", "Med-High"])
    plt.tight_layout()
    plt.savefig(OUT / "fig_recommender_effort_impact.png", bbox_inches="tight")
    plt.close()

    print(f"Rule-based rules: {len(RULES)}")
    print(f"Association rules: {len(rules_df)}")
    print(f"Sequential transitions: {len(seq_df)}")
    print(f"Item-CF SKUs: {len(keep_skus)}")
    print(f"Demo comparisons: {len(demo_df)}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
