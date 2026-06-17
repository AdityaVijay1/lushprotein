"""
Hierarchical clustering on customer purchase profiles.
Answers: does it make sense for LP? If yes, segment customers for targeted playbooks.

Run: python EDA/aditya_findings/recommendation_systems/hierarchical_clustering.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import (  # noqa: E402
    CHART_STYLE,
    attach_true_profit,
    load_decile_pool,
    load_lines_with_margin,
)

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(CHART_STYLE)
sns.set_theme(style="whitegrid")

CATEGORIES = [
    "Clear Protein", "Lean Protein", "Collagen Glow",
    "Accessories", "Soy Protein", "Other",
]


def main():
    print("=" * 72)
    print("HIERARCHICAL CLUSTERING — Customer purchase profiles")
    print("=" * 72)

    lines = load_lines_with_margin()
    pool = load_decile_pool()
    pool = attach_true_profit(pool, lines)

    # Customer × category spend matrix
    cat_spend = (
        lines.groupby(["customer_id", "product_category"])["line_rev"]
        .sum()
        .unstack(fill_value=0)
    )
    for c in CATEGORIES:
        if c not in cat_spend.columns:
            cat_spend[c] = 0
    cat_spend = cat_spend[CATEGORIES]

    # Also add behavioural features
    beh = pool.set_index("customer_id")[["clean_orders", "clean_revenue", "true_gross_profit"]]
    features = cat_spend.join(beh, how="inner")
    features = features[features["clean_revenue"] > 0]

    # Sample for dendrogram (full 4K too heavy for viz)
    np.random.seed(42)
    sample_n = min(500, len(features))
    sample_idx = features.sample(sample_n, random_state=42).index
    sample = features.loc[sample_idx]

    scaler = StandardScaler()
    X = scaler.fit_transform(sample)

    Z = linkage(X, method="ward")

    # Full clustering on all customers (k=5 clusters — matches LP tiers roughly)
    X_full = scaler.fit_transform(features)
    Z_full = linkage(X_full, method="ward")
    features["cluster"] = fcluster(Z_full, t=5, criterion="maxclust")

    cluster_profile = (
        features.groupby("cluster")
        .agg(
            n_customers=("clean_revenue", "count"),
            avg_revenue=("clean_revenue", "mean"),
            avg_gp=("true_gross_profit", "mean"),
            avg_orders=("clean_orders", "mean"),
            **{f"pct_buy_{c.replace(' ', '_')}": (c, lambda s: (s > 0).mean())
               for c in CATEGORIES},
        )
        .reset_index()
    )
    # Fix aggregation — do category penetration separately
    pen_rows = []
    for cl in sorted(features["cluster"].unique()):
        sub = features[features["cluster"] == cl]
        row = {"cluster": cl, "n_customers": len(sub)}
        for c in CATEGORIES:
            row[f"pct_{c.replace(' ', '_')}"] = (sub[c] > 0).mean()
        row["avg_revenue"] = sub["clean_revenue"].mean()
        row["avg_gp"] = sub["true_gross_profit"].mean()
        row["avg_orders"] = sub["clean_orders"].mean()
        pen_rows.append(row)
    cluster_profile = pd.DataFrame(pen_rows)
    cluster_profile.to_csv(OUT / "hierarchical_cluster_profiles.csv", index=False)

    # Name clusters by dominant behaviour
    names = []
    for _, r in cluster_profile.iterrows():
        pcts = {c: r.get(f"pct_{c.replace(' ', '_')}", 0) for c in CATEGORIES}
        top_cat = max(pcts, key=pcts.get)
        if r["avg_gp"] > cluster_profile["avg_gp"].median():
            names.append(f"Premium_{top_cat.split()[0]}")
        elif r["avg_orders"] > cluster_profile["avg_orders"].median():
            names.append(f"Frequent_{top_cat.split()[0]}")
        else:
            names.append(f"Casual_{top_cat.split()[0]}")
    cluster_profile["cluster_name"] = names
    cluster_profile.to_csv(OUT / "hierarchical_cluster_profiles.csv", index=False)

    # Export customer → cluster mapping
    export = features[["cluster"]].reset_index()
    export = export.merge(cluster_profile[["cluster", "cluster_name"]], on="cluster")
    export.to_csv(OUT / "customer_cluster_assignments.csv", index=False)

    # ── Charts ─────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))
    dendrogram(Z, ax=ax, truncate_mode="lastp", p=20, leaf_rotation=45, leaf_font_size=8)
    ax.set_title("Hierarchical clustering dendrogram (500-customer sample, Ward)")
    ax.set_ylabel("Ward distance")
    plt.tight_layout()
    plt.savefig(OUT / "fig_dendrogram_sample.png", bbox_inches="tight")
    plt.close()

    # Cluster profile heatmap
    heat_cols = [f"pct_{c.replace(' ', '_')}" for c in CATEGORIES]
    hm = cluster_profile.set_index("cluster_name")[heat_cols]
    hm.columns = [c.replace("pct_", "").replace("_", " ") for c in hm.columns]
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(hm, annot=True, fmt=".0%", cmap="YlOrRd", ax=ax)
    ax.set_title("Cluster profiles: category penetration by segment")
    plt.tight_layout()
    plt.savefig(OUT / "fig_cluster_heatmap.png", bbox_inches="tight")
    plt.close()

    # GP by cluster
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(cluster_profile["cluster_name"], cluster_profile["avg_gp"], color="#9b59b6")
    ax.set_ylabel("Avg true gross profit (SGD)")
    ax.set_title("Average GP by hierarchical cluster")
    ax.tick_params(axis="x", rotation=25)
    plt.tight_layout()
    plt.savefig(OUT / "fig_gp_by_cluster.png", bbox_inches="tight")
    plt.close()

    print(f"Customers clustered: {len(features):,}")
    print(f"Clusters: {cluster_profile['cluster'].nunique()}")
    for _, r in cluster_profile.iterrows():
        print(f"  {r['cluster_name']}: n={int(r['n_customers'])}, avg GP=S${r['avg_gp']:.0f}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
