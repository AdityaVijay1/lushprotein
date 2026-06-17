"""
SKU-level market basket analysis (Phase 2).
Outputs: sku_association_rules.csv, first_to_second_sku_matrix.csv

Run: python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
"""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import load_lines_with_margin, sku_label  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

MIN_SUPPORT = 0.005  # 0.5% of orders
MIN_CONFIDENCE = 0.05


def main():
    print("=" * 72)
    print("SKU MARKET BASKET — Phase 2")
    print("=" * 72)

    lines = load_lines_with_margin()
    lines["sku_display"] = lines.apply(sku_label, axis=1)

    # ── Same-order association rules ─────────────────────────────────────────────
    baskets = (
        lines.groupby("order_id")["sku_display"]
        .apply(lambda s: sorted(set(s)))
        .reset_index()
    )
    n_orders = len(baskets)
    item_counts = lines.groupby("sku_display")["order_id"].nunique()
    pair_counts: dict[tuple[str, str], int] = {}

    for items in baskets["sku_display"]:
        if len(items) < 2:
            continue
        for a, b in combinations(items, 2):
            key = (a, b) if a < b else (b, a)
            pair_counts[key] = pair_counts.get(key, 0) + 1

    rules = []
    for (a, b), cnt in pair_counts.items():
        support = cnt / n_orders
        if support < MIN_SUPPORT:
            continue
        conf_ab = cnt / item_counts.get(a, 1)
        conf_ba = cnt / item_counts.get(b, 1)
        if conf_ab >= MIN_CONFIDENCE:
            rules.append({
                "antecedent": a,
                "consequent": b,
                "support": round(support, 4),
                "confidence": round(conf_ab, 4),
                "lift": round(conf_ab / (item_counts.get(b, 1) / n_orders), 2)
                if item_counts.get(b, 0) > 0 else np.nan,
                "pair_orders": cnt,
            })
        if conf_ba >= MIN_CONFIDENCE:
            rules.append({
                "antecedent": b,
                "consequent": a,
                "support": round(support, 4),
                "confidence": round(conf_ba, 4),
                "lift": round(conf_ba / (item_counts.get(a, 1) / n_orders), 2)
                if item_counts.get(a, 0) > 0 else np.nan,
                "pair_orders": cnt,
            })

    rules_df = (
        pd.DataFrame(rules)
        .sort_values(["confidence", "support"], ascending=False)
        .drop_duplicates(subset=["antecedent", "consequent"])
    )
    top20 = rules_df.head(20)
    top20.to_csv(OUT / "sku_association_rules.csv", index=False)
    rules_df.to_csv(OUT / "sku_association_rules_full.csv", index=False)

    # ── Sequential: 1st order SKU → 2nd order SKU ─────────────────────────────
    cust_orders = (
        lines.sort_values(["customer_id", "order_date"])
        .groupby(["customer_id", "order_id"])
        .agg(
            order_date=("order_date", "first"),
            skus=("sku_display", lambda s: sorted(set(s))),
        )
        .reset_index()
    )
    cust_orders["order_seq"] = cust_orders.groupby("customer_id").cumcount() + 1
    repeaters = cust_orders[cust_orders.groupby("customer_id")["customer_id"].transform("count") >= 2]

    first_orders = repeaters[repeaters["order_seq"] == 1].set_index("customer_id")
    second_orders = repeaters[repeaters["order_seq"] == 2].set_index("customer_id")
    common = first_orders.index.intersection(second_orders.index)

    transitions: dict[tuple[str, str], int] = {}
    first_counts: dict[str, int] = {}
    for cid in common:
        for fsku in first_orders.loc[cid, "skus"]:
            first_counts[fsku] = first_counts.get(fsku, 0) + 1
            for ssku in second_orders.loc[cid, "skus"]:
                key = (fsku, ssku)
                transitions[key] = transitions.get(key, 0) + 1

    seq_rows = []
    for (fsku, ssku), cnt in transitions.items():
        prob = cnt / first_counts.get(fsku, 1)
        if first_counts.get(fsku, 0) < 10:
            continue
        seq_rows.append({
            "first_order_sku": fsku,
            "second_order_sku": ssku,
            "transition_count": cnt,
            "first_sku_customers": first_counts[fsku],
            "p_second_given_first": round(prob, 4),
        })

    seq_df = pd.DataFrame(seq_rows).sort_values(
        ["first_order_sku", "p_second_given_first"], ascending=[True, False]
    )
    seq_df.to_csv(OUT / "first_to_second_sku_matrix.csv", index=False)

    # Top recommendation per first SKU
    top_next = (
        seq_df.groupby("first_order_sku")
        .first()
        .reset_index()
        .rename(columns={"second_order_sku": "recommended_next_sku"})
    )
    top_next.to_csv(OUT / "next_best_sku_per_first.csv", index=False)

    print(f"Orders analysed: {n_orders:,}")
    print(f"Association rules (full): {len(rules_df):,} | top 20 exported")
    print(f"Sequential transitions: {len(seq_df):,}")
    if len(top20):
        print(f"Top rule: {top20.iloc[0]['antecedent'][:40]} -> "
              f"{top20.iloc[0]['consequent'][:40]} "
              f"(conf={top20.iloc[0]['confidence']:.2f})")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
