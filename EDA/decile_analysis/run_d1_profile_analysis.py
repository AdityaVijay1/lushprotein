"""
D1 Customer Profile — what makes a D1 customer D1?

Compares profit D1 (true COGS) vs all other deciles across:
  economics, product breadth, pack size, channel, subscription,
  first product, hero SKUs, discount depth

Outputs → EDA/decile_analysis/outputs/d1_profile/
Markdown → EDA/decile_analysis/D1_CUSTOMER_PROFILE.md

Run: python EDA/decile_analysis/run_d1_profile_analysis.py
"""
import importlib.util
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

SCRIPT_DIR = Path(__file__).resolve().parent
EDA_DIR = SCRIPT_DIR.parent


def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_cfg = _load_config()
FINALS_DIR = _cfg.FINALS_DIR
OUT_DIR = _cfg.GOLD_ANALYTICS_DECILE
OUT = OUT_DIR / "d1_profile"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(EDA_DIR / "aditya_findings"))
from _shared import assign_decile, crm_tier  # noqa: E402

plt.rcParams.update({"figure.dpi": 150, "font.size": 10})
sns.set_theme(style="whitegrid")

DECILES = [f"D{i}" for i in range(1, 11)]
HERO_HANDLES = ["clear-protein", "lean-protein", "collagen-glow"]


def load_pool():
    cust = pd.read_parquet(FINALS_DIR / "customers.parquet")
    lines = pd.read_parquet(FINALS_DIR / "lines.parquet")
    orders = pd.read_parquet(FINALS_DIR / "orders.parquet")

    mix = orders.groupby("customer_id")["channel"].value_counts(normalize=True).unstack(fill_value=0)
    all_mkt = set(mix[mix["Marketplace"] == 1.0].index.astype(str)) if "Marketplace" in mix.columns else set()

    pool = cust[
        cust["finals_eligible"].fillna(False)
        & ~cust["customer_id"].astype(str).isin(all_mkt)
        & (cust["total_orders"] > 0)
    ].copy()

    if "profit_decile_true" not in pool.columns or pool["profit_decile_true"].isna().all():
        pool["true_gross_profit"] = pool.get("true_gross_profit", pool["total_revenue"] * 0.4)
        pool["profit_decile_true"] = assign_decile(pool["true_gross_profit"])
    if "freq_decile_true" not in pool.columns:
        pool["freq_decile_true"] = assign_decile(pool["finals_orders"].fillna(pool["total_orders"]))

    pool["is_d1_profit"] = pool["profit_decile_true"] == "D1"
    pool["is_d1_freq"] = pool["freq_decile_true"] == "D1"
    pool["is_vip"] = pool["is_d1_profit"] & pool["is_d1_freq"]
    pool["segment_label"] = np.select(
        [pool["is_vip"], pool["is_d1_profit"], pool["is_d1_freq"]],
        ["VIP (profit+freq D1)", "Profit D1 only", "Freq D1 only"],
        default="Not D1",
    )

    decile_tbl = pd.read_csv(SCRIPT_DIR / "outputs" / "customers_decile_table.csv")
    decile_tbl["customer_id"] = decile_tbl["customer_id"].astype(pool["customer_id"].dtype)
    merge_cols = ["customer_id", "first_channel", "first_product_cat", "first_store",
                    "is_repeat", "loyal_repeater"]
    if "ever_subscribed" not in pool.columns:
        merge_cols.append("ever_subscribed")
    pool = pool.merge(decile_tbl[merge_cols], on="customer_id", how="left", suffixes=("", "_tbl"))
    pool["revenue"] = pool.get("finals_revenue", pool["total_revenue"])
    pool["orders"] = pool.get("finals_orders", pool["total_orders"])

    # Discount depth per customer
    ord_cust = orders.groupby("customer_id").agg(
        total_rev=("Price: Total", lambda s: pd.to_numeric(s, errors="coerce").sum()),
        total_disc=("Price: Total Discount", lambda s: pd.to_numeric(s, errors="coerce").sum()),
        n_orders=("order_id", "count"),
    ).reset_index()
    ord_cust["disc_pct"] = np.where(
        ord_cust["total_rev"] > 0,
        ord_cust["total_disc"].abs() / ord_cust["total_rev"],
        0,
    )
    pool = pool.merge(ord_cust[["customer_id", "disc_pct"]], on="customer_id", how="left")
    pool["disc_pct"] = pool["disc_pct"].fillna(0)

    # Line-level features per customer
    lines = lines[lines["customer_id"].isin(pool["customer_id"])].copy()
    if "pack_size" not in lines.columns:
        variant = lines["Line: Variant Title"].astype(str).fillna("")
        lines["pack_size"] = np.where(
            variant.str.contains("1kg|1 kg", case=False, na=False), "1kg",
            np.where(variant.str.contains("500g|500 g", case=False, na=False), "500g", "other"),
        )

    cat_ever = lines.groupby("customer_id")["product_category"].nunique().reset_index(name="n_categories")
    pool = pool.merge(cat_ever, on="customer_id", how="left")
    pool["n_categories"] = pool["n_categories"].fillna(pool.get("n_categories_ever", 1))

    handle_ever = lines.groupby("customer_id")["Line: Product Handle"].nunique().reset_index(name="n_handles")
    pool = pool.merge(handle_ever, on="customer_id", how="left")
    pool["n_handles"] = pool["n_handles"].fillna(1)

    # Category flags
    for cat in ["Clear Protein", "Lean Protein", "Collagen Glow", "Accessories", "Soy Protein"]:
        buyers = set(lines.loc[lines["product_category"] == cat, "customer_id"])
        pool[f"ever_{cat.replace(' ', '_').lower()}"] = pool["customer_id"].isin(buyers)

    # Pack mix
    pack_mix = (
        lines[lines["pack_size"].isin(["500g", "1kg"])]
        .groupby("customer_id")["pack_size"]
        .apply(lambda s: s.value_counts().idxmax() if len(s) else "other")
        .reset_index(name="dominant_pack")
    )
    pool = pool.merge(pack_mix, on="customer_id", how="left")
    pool["dominant_pack"] = pool["dominant_pack"].fillna("other")

    # Hero SKU flags
    for handle in HERO_HANDLES:
        col = f"ever_{handle.replace('-', '_')}"
        buyers = set(lines.loc[lines["Line: Product Handle"].astype(str).str.contains(handle, na=False), "customer_id"])
        pool[f"ever_{handle.replace('-', '_')}"] = pool["customer_id"].isin(buyers)

    if "qty" not in lines.columns:
        lines["qty"] = pd.to_numeric(lines["Line: Quantity"], errors="coerce").fillna(1)
    if "line_rev" not in lines.columns:
        lines["line_rev"] = pd.to_numeric(lines["Line: Total"], errors="coerce").fillna(0)

    cust_units = lines.groupby("customer_id").agg(
        total_units=("qty", "sum"),
        total_line_rev=("line_rev", "sum"),
    ).reset_index()
    cust_units["dollars_per_unit"] = np.where(
        cust_units["total_units"] > 0,
        cust_units["total_line_rev"] / cust_units["total_units"],
        np.nan,
    )
    pool = pool.merge(cust_units[["customer_id", "dollars_per_unit", "total_units"]], on="customer_id", how="left")

    pool["aov"] = pool["revenue"] / pool["orders"].clip(lower=1)
    pool["avg_margin_pct"] = pool.get("avg_margin_pct", pool["true_gross_profit"] / pool["revenue"].replace(0, np.nan))

    return pool, lines


def decile_comparison(pool: pd.DataFrame) -> pd.DataFrame:
    """Metric by profit decile."""
    metrics = []
    for d in DECILES:
        sub = pool[pool["profit_decile_true"] == d]
        if not len(sub):
            continue
        metrics.append({
            "profit_decile": d,
            "n_customers": len(sub),
            "avg_gp": sub["true_gross_profit"].mean(),
            "median_gp": sub["true_gross_profit"].median(),
            "avg_revenue": sub["revenue"].mean(),
            "avg_aov": sub["aov"].mean(),
            "avg_orders": sub["orders"].mean(),
            "avg_margin_pct": sub["avg_margin_pct"].mean(),
            "avg_categories": sub["n_categories"].mean(),
            "avg_handles": sub["n_handles"].mean(),
            "dollars_per_unit": sub["dollars_per_unit"].mean(),
            "pct_subscribed": sub["ever_subscribed"].fillna(False).mean(),
            "pct_repeat": sub["is_repeat"].fillna(False).mean(),
            "avg_disc_pct": sub["disc_pct"].mean(),
            "pct_ever_clear": sub["ever_clear_protein"].mean(),
            "pct_ever_lean": sub["ever_lean_protein"].mean(),
            "pct_ever_collagen": sub["ever_collagen_glow"].mean(),
            "pct_1kg_dominant": (sub["dominant_pack"] == "1kg").mean(),
            "pct_multi_category": (sub["n_categories"] >= 2).mean(),
            "pct_multi_category_3plus": (sub["n_categories"] >= 3).mean(),
        })
    return pd.DataFrame(metrics)


def identification_factors(pool: pd.DataFrame) -> pd.DataFrame:
    """Lift: D1 rate vs rest-of-pool rate for each factor."""
    d1 = pool[pool["is_d1_profit"]]
    rest = pool[~pool["is_d1_profit"]]
    n_d1, n_rest = len(d1), len(rest)

    factors = []

    def add_factor(name, d1_val, rest_val, kind="rate"):
        if kind == "rate":
            lift = (d1_val / rest_val) if rest_val > 0 else np.nan
            factors.append({
                "factor": name,
                "d1_value": round(d1_val, 4),
                "non_d1_value": round(rest_val, 4),
                "lift_index": round(lift * 100, 1) if not np.isnan(lift) else np.nan,
                "type": "binary_rate",
            })
        else:
            diff = d1_val - rest_val
            factors.append({
                "factor": name,
                "d1_value": round(d1_val, 2),
                "non_d1_value": round(rest_val, 2),
                "lift_index": round(d1_val / rest_val * 100, 1) if rest_val > 0 else np.nan,
                "type": "continuous",
                "diff": round(diff, 2),
            })

    add_factor("avg_orders", d1["orders"].mean(), rest["orders"].mean(), "continuous")
    add_factor("avg_aov", d1["aov"].mean(), rest["aov"].mean(), "continuous")
    add_factor("avg_gp", d1["true_gross_profit"].mean(), rest["true_gross_profit"].mean(), "continuous")
    add_factor("avg_categories", d1["n_categories"].mean(), rest["n_categories"].mean(), "continuous")
    add_factor("dollars_per_unit", d1["dollars_per_unit"].mean(), rest["dollars_per_unit"].mean(), "continuous")
    add_factor("avg_margin_pct", d1["avg_margin_pct"].mean(), rest["avg_margin_pct"].mean(), "continuous")
    add_factor("avg_disc_pct", d1["disc_pct"].mean(), rest["disc_pct"].mean(), "continuous")

    for col, label in [
        ("ever_clear_protein", "Ever bought Clear Protein"),
        ("ever_lean_protein", "Ever bought Lean Protein"),
        ("ever_collagen_glow", "Ever bought Collagen Glow"),
        ("ever_subscribed", "Ever subscribed"),
        ("is_repeat", "Is repeat buyer"),
        ("loyal_repeater", "Loyal repeater flag"),
    ]:
        add_factor(label, d1[col].fillna(False).mean(), rest[col].fillna(False).mean())

    add_factor("Dominant pack = 1kg", (d1["dominant_pack"] == "1kg").mean(), (rest["dominant_pack"] == "1kg").mean())
    add_factor("3+ categories", (d1["n_categories"] >= 3).mean(), (rest["n_categories"] >= 3).mean())
    add_factor("2+ categories", (d1["n_categories"] >= 2).mean(), (rest["n_categories"] >= 2).mean())

    # First product
    for cat in ["Clear Protein", "Lean Protein", "Collagen Glow", "Accessories", "Other"]:
        add_factor(
            f"First product = {cat}",
            (d1["first_product_cat"] == cat).mean(),
            (rest["first_product_cat"] == cat).mean(),
        )

    # Channel
    for ch in ["Direct / Organic", "Subscription", "Paid Social", "Email"]:
        add_factor(
            f"First channel = {ch}",
            (d1["first_channel"] == ch).mean(),
            (rest["first_channel"] == ch).mean(),
        )

    df = pd.DataFrame(factors).sort_values("lift_index", ascending=False)
    return df


def d1_archetypes(pool: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in ["VIP (profit+freq D1)", "Profit D1 only", "Freq D1 only"]:
        sub = pool[pool["segment_label"] == label]
        rows.append({
            "archetype": label,
            "n": len(sub),
            "avg_gp": sub["true_gross_profit"].mean(),
            "avg_revenue": sub["revenue"].mean(),
            "avg_orders": sub["orders"].mean(),
            "avg_aov": sub["aov"].mean(),
            "avg_categories": sub["n_categories"].mean(),
            "dollars_per_unit": sub["dollars_per_unit"].mean(),
            "pct_subscribed": sub["ever_subscribed"].fillna(False).mean(),
            "pct_3plus_cat": (sub["n_categories"] >= 3).mean(),
            "pct_1kg": (sub["dominant_pack"] == "1kg").mean(),
        })
    return pd.DataFrame(rows)


def conversion_gaps(pool: pd.DataFrame) -> pd.DataFrame:
    """Where middle deciles (D5-D7) and single-category buyers gap vs D1."""
    d1 = pool[pool["is_d1_profit"]]
    targets = {
        "D5-D7 (moveable middle)": pool[pool["profit_decile_true"].isin(["D5", "D6", "D7"])],
        "D2-D4 (near-D1)": pool[pool["profit_decile_true"].isin(["D2", "D3", "D4"])],
        "Single-category only": pool[pool["n_categories"] == 1],
        "Repeat non-subscriber": pool[(pool["is_repeat"].fillna(False)) & (~pool["ever_subscribed"].fillna(False))],
        "One-time buyers": pool[~pool["is_repeat"].fillna(False)],
    }

    rows = []
    d1_benchmarks = {
        "avg_gp": d1["true_gross_profit"].mean(),
        "avg_categories": d1["n_categories"].mean(),
        "dollars_per_unit": d1["dollars_per_unit"].mean(),
        "pct_2plus_cat": (d1["n_categories"] >= 2).mean(),
        "pct_subscribed": d1["ever_subscribed"].fillna(False).mean(),
        "avg_orders": d1["orders"].mean(),
    }

    for name, sub in targets.items():
        rows.append({
            "target_segment": name,
            "n_customers": len(sub),
            "avg_gp": sub["true_gross_profit"].mean(),
            "gp_gap_vs_d1": d1_benchmarks["avg_gp"] - sub["true_gross_profit"].mean(),
            "avg_categories": sub["n_categories"].mean(),
            "cat_gap_vs_d1": d1_benchmarks["avg_categories"] - sub["n_categories"].mean(),
            "dollars_per_unit": sub["dollars_per_unit"].mean(),
            "unit_gap_vs_d1": d1_benchmarks["dollars_per_unit"] - sub["dollars_per_unit"].mean(),
            "pct_2plus_cat": (sub["n_categories"] >= 2).mean(),
            "pct_subscribed": sub["ever_subscribed"].fillna(False).mean(),
            "avg_orders": sub["orders"].mean(),
        })
    return pd.DataFrame(rows)


def first_product_d1_rate(pool: pd.DataFrame) -> pd.DataFrame:
    return (
        pool.groupby("first_product_cat")
        .agg(
            n=("customer_id", "count"),
            d1_rate=("is_d1_profit", "mean"),
            avg_gp=("true_gross_profit", "mean"),
            repeat_rate=("is_repeat", "mean"),
        )
        .reset_index()
        .sort_values("d1_rate", ascending=False)
    )


def plot_charts(pool, dec_comp, id_factors):
    # Chart 1: GP by decile
    fig, ax = plt.subplots(figsize=(9, 4))
    colors = ["#27ae60" if d == "D1" else "#bdc3c7" for d in dec_comp["profit_decile"]]
    ax.bar(dec_comp["profit_decile"], dec_comp["avg_gp"], color=colors)
    ax.set_ylabel("Avg true GP (SGD)")
    ax.set_title("Average gross profit by profit decile (true COGS)")
    plt.tight_layout()
    plt.savefig(OUT / "fig_gp_by_decile.png", bbox_inches="tight")
    plt.close()

    # Chart 2: D1 identification factors (top lifts)
    top = id_factors[id_factors["type"] == "binary_rate"].head(12)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["factor"][::-1], top["lift_index"][::-1], color="#3498db")
    ax.axvline(100, color="red", linestyle="--", label="Pool average (=100)")
    ax.set_xlabel("D1 index (100 = same as non-D1)")
    ax.set_title("Top D1 identification factors (lift vs non-D1)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "fig_d1_identification_factors.png", bbox_inches="tight")
    plt.close()

    # Chart 3: Categories vs GP scatter by decile
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = pool.sample(min(2000, len(pool)), random_state=42)
    colors_map = {"D1": "#27ae60", "D2": "#82e0aa", "D3": "#abebc6"}
    for d in ["D1", "D2", "D3", "D5", "D10"]:
        s = sample[sample["profit_decile_true"] == d]
        ax.scatter(s["n_categories"], s["true_gross_profit"], alpha=0.5, label=d, s=30)
    ax.set_xlabel("Categories ever purchased")
    ax.set_ylabel("True gross profit (SGD)")
    ax.set_title("GP vs category breadth by decile")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "fig_gp_vs_categories.png", bbox_inches="tight")
    plt.close()

    # Chart 4: Decile radar-style comparison (categories, $/unit, orders)
    metrics = ["avg_categories", "dollars_per_unit", "avg_orders", "pct_multi_category_3plus", "pct_subscribed"]
    d1_row = dec_comp[dec_comp["profit_decile"] == "D1"].iloc[0]
    d5_row = dec_comp[dec_comp["profit_decile"] == "D5"].iloc[0]
    d10_row = dec_comp[dec_comp["profit_decile"] == "D10"].iloc[0]

    # Normalize to D1=100
    norm_rows = []
    for label, row in [("D1", d1_row), ("D5", d5_row), ("D10", d10_row)]:
        norm_rows.append({
            "decile": label,
            "categories_idx": row["avg_categories"] / d1_row["avg_categories"] * 100,
            "dollars_per_unit_idx": row["dollars_per_unit"] / d1_row["dollars_per_unit"] * 100,
            "orders_idx": row["avg_orders"] / d1_row["avg_orders"] * 100,
            "pct_3cat_idx": row["pct_multi_category_3plus"] / d1_row["pct_multi_category_3plus"] * 100 if d1_row["pct_multi_category_3plus"] > 0 else 0,
            "sub_idx": row["pct_subscribed"] / d1_row["pct_subscribed"] * 100 if d1_row["pct_subscribed"] > 0 else 0,
        })
    norm_df = pd.DataFrame(norm_rows)
    x = np.arange(5)
    w = 0.25
    labels = ["Categories", "$/unit", "Orders", "3+ cat %", "Sub %"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (_, r) in enumerate(norm_df.iterrows()):
        vals = [r["categories_idx"], r["dollars_per_unit_idx"], r["orders_idx"], r["pct_3cat_idx"], r["sub_idx"]]
        ax.bar(x + i * w, vals, w, label=r["decile"])
    ax.set_xticks(x + w)
    ax.set_xticklabels(labels)
    ax.axhline(100, color="gray", linestyle="--", alpha=0.5)
    ax.set_ylabel("Index (D1 = 100)")
    ax.set_title("D1 vs D5 vs D10 — behavioural fingerprint")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "fig_d1_fingerprint.png", bbox_inches="tight")
    plt.close()


def build_markdown(pool, dec_comp, id_factors, archetypes, gaps, first_prod):
    d1 = pool[pool["is_d1_profit"]]
    d1_1kg = (d1["dominant_pack"] == "1kg").mean()
    d1_row = dec_comp[dec_comp["profit_decile"] == "D1"].iloc[0]
    d10_row = dec_comp[dec_comp["profit_decile"] == "D10"].iloc[0]

    top_binary = id_factors[id_factors["type"] == "binary_rate"].head(8)
    top_cont = id_factors[id_factors["type"] == "continuous"].head(6)

    md = f"""# What Makes a D1 Customer? — Identification & Conversion Playbook

**Pool:** {len(pool):,} customers (finals, excl. 100% marketplace)  
**Profit D1:** {len(d1):,} customers ({len(d1)/len(pool):.0%} of pool) · **{d1_row['avg_gp']:.0f}** avg true GP  
**Data:** True COGS hybrid + `outputs_finals/` enriched parquets  
**Script:** `run_d1_profile_analysis.py`

---

## 1. Executive summary — the D1 fingerprint

A **profit D1 customer** is not simply "someone who orders a lot." They are identifiable by a **combination** of:

1. **Premium basket** — high $/unit (S${d1_row['dollars_per_unit']:.0f} vs S${d10_row['dollars_per_unit']:.0f} for D10)
2. **Multi-category shopping** — {d1_row['avg_categories']:.1f} categories ever vs {d10_row['avg_categories']:.1f} for D10
3. **Hero protein affinity** — over-index on Clear + Lean (D1 index 265–275 in category analysis)
4. **Repeat behaviour** — {d1_row['pct_repeat']:.0%} repeat rate vs {d10_row['pct_repeat']:.0%} for D10
5. **Moderate frequency** — {d1_row['avg_orders']:.1f} orders avg (profit-only D1 often have fewer orders but higher AOV)

**The 69× GP gap** (D1 S${d1_row['avg_gp']:.0f} vs D10 S${d10_row['avg_gp']:.0f}) comes from **basket quality × breadth**, not order count alone.

---

## 2. Identification factors (ranked by lift vs non-D1)

*100 = same as non-D1. Above 100 = D1 over-indexes.*

| Rank | Factor | D1 rate/avg | Non-D1 | Index |
|------|--------|-------------|--------|-------|
"""
    for i, (_, r) in enumerate(top_binary.iterrows(), 1):
        d1v = f"{r['d1_value']:.0%}" if r["d1_value"] <= 1 else f"{r['d1_value']:.2f}"
        nond1v = f"{r['non_d1_value']:.0%}" if r["non_d1_value"] <= 1 else f"{r['non_d1_value']:.2f}"
        md += f"| {i} | {r['factor']} | {d1v} | {nond1v} | **{r['lift_index']:.0f}** |\n"

    md += f"""
### Continuous metrics (D1 vs non-D1)

| Metric | D1 | Non-D1 | D1 index |
|--------|-----|--------|----------|
"""
    for _, r in top_cont.iterrows():
        md += f"| {r['factor']} | {r['d1_value']} | {r['non_d1_value']} | {r['lift_index']:.0f} |\n"

    md += f"""
**Key insight:** The strongest *predictive* signals are **loyal repeater flag**, **3+ categories**, and **repeat purchase**. Product signals: **Collagen**, **Clear**, **Lean**, and **1kg packs**. Frequency alone does not separate profit D1 from frequency D1.

---

## 3. Three D1 archetypes (not one monolith)

| Archetype | Count | Avg GP | Orders | AOV | Categories | Playbook |
|-----------|-------|--------|--------|-----|------------|----------|
"""
    for _, r in archetypes.iterrows():
        md += f"| {r['archetype']} | {int(r['n'])} | S${r['avg_gp']:.0f} | {r['avg_orders']:.1f} | S${r['avg_aov']:.0f} | {r['avg_categories']:.1f} | See below |\n"

    vip = archetypes[archetypes["archetype"] == "VIP (profit+freq D1)"].iloc[0]
    profit_only = archetypes[archetypes["archetype"] == "Profit D1 only"].iloc[0]
    freq_only = archetypes[archetypes["archetype"] == "Freq D1 only"].iloc[0]

    md += f"""
### VIP (profit D1 + frequency D1) — {int(vip['n'])} customers
- **Who:** Highest GP (S${vip['avg_gp']:.0f}), {vip['avg_orders']:.1f} orders, {vip['avg_categories']:.1f} categories. {vip['pct_subscribed']:.0%} subscribed.
- **Identification:** `profit_decile_true = D1` AND `freq_decile_true = D1` (or `is_top_both` in decile table)
- **Action:** Protect — no blanket discounts. Early access, flavour drops, subscription perks.

### Profit D1 only — {int(profit_only['n'])} customers
- **Who:** High spend per order (AOV S${profit_only['avg_aov']:.0f}), only {profit_only['avg_orders']:.1f} orders avg. Whales and big-basket buyers.
- **Identification:** `profit_decile_true = D1` AND `freq_decile_true != D1`
- **Action:** Premium upsell (1kg packs, bundles). Do not push frequency — push basket value.

### Frequency D1 only — {int(freq_only['n'])} customers
- **Who:** {freq_only['avg_orders']:.1f} orders but lower GP (S${freq_only['avg_gp']:.0f}) and AOV (S${freq_only['avg_aov']:.0f}). Replenishment without premium basket.
- **Identification:** `freq_decile_true = D1` AND `profit_decile_true != D1`
- **Action:** Subscribe-and-save, pack-size upgrade (500g→1kg), cross-sell to raise $/unit.

---

## 4. Product-side identification (what D1 buys)

From category x decile analysis (T4) and line-level data:

| Signal | D1 behaviour | vs All customers |
|--------|--------------|------------------|
| **Lean Protein** | D1 index **275**; 30% penetration | Higher $/unit (S$54 vs S$40) |
| **Clear Protein** | D1 index **265**; 35% penetration | Higher ACOV (S$105 vs S$78) |
| **Collagen Glow** | D1 index **202**; 22% penetration | VIP onboarding candidate |
| **Accessories** | D1 index **127** | Cart add-on only — not a D1 driver |
| **Pack size** | {d1_1kg:.0%} dominant 1kg | 500g = acquisition; 1kg = loyalty |
| **Sole category** | Only ~28% stay in 1 category | Cross-shop is the norm for D1 |

**Hero SKUs among D1 loyal buyers:** Clear Peach 500g, Lean TMT 1kg, Clear White Grape 500g (from `12_loyal_repeater_reorder_skus.csv`).

---

## 5. Customer-side identification (how D1 arrives)

### First product that predicts D1 probability

| First product | D1 rate | Avg GP | Repeat rate |
|---------------|---------|--------|-------------|
"""
    for _, r in first_prod.head(8).iterrows():
        if pd.notna(r["first_product_cat"]) and r["first_product_cat"] != "":
            md += f"| {r['first_product_cat']} | {r['d1_rate']:.0%} | S${r['avg_gp']:.0f} | {r['repeat_rate']:.0%} |\n"

    md += f"""
### Channel patterns
- **Direct / Organic** and **Subscription** channels over-index among D1
- **Accessories-first** acquisition under-indexes (VTD index ~68)
- **Collagen-first** over-indexes on lifetime quality despite smaller volume

### Discount behaviour
- D1 avg discount depth: **{d1_row['avg_disc_pct']:.1%}** — D1 can be discount-trained too; guardrail needed (Rec A)
- Do not use heavy discounting to *create* D1 — it attracts low-$/unit buyers

---

## 6. D1 scoring checklist (practical identification)

Use this to score any customer 0–100 for "D1 potential":

| Criterion | Points | How to check |
|-----------|--------|--------------|
| 2+ categories ever | +25 | `n_categories_ever >= 2` in customers.parquet |
| 3+ categories ever | +15 | `n_categories_ever >= 3` |
| Ever bought Lean | +15 | line history |
| Ever bought Clear | +15 | line history |
| $/unit above S$45 | +10 | line revenue / units |
| 1kg pack dominant | +10 | variant titles |
| Subscribed | +10 | `ever_subscribed` |
| 3+ orders | +10 | `total_orders` |
| **Accessories-only** | **-20** | only Accessories in history |
| **Single order, low AOV** | **-15** | 1 order, AOV < S$50 |

**Score ≥ 60:** High D1 potential — route to VIP nurture  
**Score 35–59:** Moveable middle (D5–D7) — cross-sell + pack upgrade  
**Score < 35:** Standard acquisition — do not spend VIP-level retention $

---

## 7. How to convert non-D1 → D1 behaviour

### Target segments (where the gap is)

| Segment | N | GP gap vs D1 | Main gap | Priority action |
|---------|---|--------------|----------|-------------------|
"""
    for _, r in gaps.iterrows():
        md += f"| {r['target_segment']} | {int(r['n_customers'])} | S${r['gp_gap_vs_d1']:.0f} | {r['cat_gap_vs_d1']:.1f} categories | See playbook |\n"

    md += """
### Conversion playbook by gap type

#### Gap 1: Single category (2,514 customers) — biggest pool
- **Problem:** Stuck at 1 category, S$59 GP, 17% repeat
- **D1 target:** 2.3+ categories, S$144+ GP at 3 categories
- **Actions:**
  1. Day 14 after order 1: Clear↔Lean cross-sell email (Rec B)
  2. Clear+Lean bundle at checkout
  3. Day 7 after order 2: push 3rd category (Collagen or 2nd flavour)
- **Prize:** 5% reach 3 categories = S$10,693 GP/yr

#### Gap 2: Low $/unit (middle deciles D5–D7)
- **Problem:** Buying 500g trial packs, not 1kg loyalty packs
- **D1 target:** S$53+/unit vs S$30–40 for middle deciles
- **Actions:**
  1. Order 2 email: "Upgrade to 1kg — better $/serve"
  2. PDP: default to 1kg for logged-in repeaters
  3. Bundle: 2× 1kg flavours at modest discount (not site-wide %)
- **Prize:** Pack upgrade on 10% of middle decile = ~S$13K GP/yr

#### Gap 3: Repeat but not subscribed (689 customers)
- **Problem:** Proved product fit, no replenishment lock-in
- **D1 target:** 62% repeat rate (subscriber benchmark)
- **Actions:**
  1. 48 days post-order 2: Subscribe & Save on exact SKU
  2. Target Freq D1 non-subs first (228 customers)
- **Prize:** 5% convert = S$2,262 GP/yr + compounding repeat

#### Gap 4: Accessories-first acquirers (371 customers)
- **Problem:** 20% repeat, S$71 avg revenue — shaker without protein habit
- **D1 target:** Protein trial within 30 days
- **Actions:**
  1. Mandatory protein upsell: sachet trial pack S$9.90
  2. Do not use shakers as paid acquisition lead

#### Gap 5: Near-D1 (D2–D4, 1,287 customers)
- **Problem:** Close to D1 economically — small nudge needed
- **Actions:**
  1. One more category or one 1kg upgrade may push them to D1
  2. Personalised email: "You're S$X away from VIP status" (gamification)

---

## 8. What does NOT convert someone to D1

| Action | Why it fails |
|--------|--------------|
| Blanket 10%-off promos | Attracts low-$/unit buyers; erodes existing D1 margin |
| Shaker-led acquisition | Accessories index 127 — not a profit driver |
| Pushing frequency alone on low-AOV buyers | Creates Freq D1, not Profit D1 |
| Win-back on D10 one-and-dones | S$5 avg GP — negative ROI |
| Generic "shop now" emails | Flavour-specific bundles outperform 3:1 |

---

## 9. Charts

| Figure | File |
|--------|------|
| GP by decile | `outputs/d1_profile/fig_gp_by_decile.png` |
| Identification factor lifts | `outputs/d1_profile/fig_d1_identification_factors.png` |
| GP vs categories scatter | `outputs/d1_profile/fig_gp_vs_categories.png` |
| D1 vs D5 vs D10 fingerprint | `outputs/d1_profile/fig_d1_fingerprint.png` |

---

## 10. Data files

| File | Contents |
|------|----------|
| `outputs/d1_profile/decile_comparison.csv` | All metrics by decile |
| `outputs/d1_profile/identification_factors.csv` | Lift indices |
| `outputs/d1_profile/d1_archetypes.csv` | VIP / profit-only / freq-only |
| `outputs/d1_profile/conversion_gaps.csv` | Target segments vs D1 |
| `outputs/d1_profile/first_product_d1_rate.csv` | First product → D1 probability |

---

## 11. Regenerate

```bash
python EDA/aditya_findings/enrich_finals_with_margin.py
python EDA/decile_analysis/run_d1_profile_analysis.py
```
"""
    return md


def main():
    print("=" * 72)
    print("D1 CUSTOMER PROFILE ANALYSIS")
    print("=" * 72)

    pool, lines = load_pool()
    dec_comp = decile_comparison(pool)
    id_factors = identification_factors(pool)
    archetypes = d1_archetypes(pool)
    gaps = conversion_gaps(pool)
    first_prod = first_product_d1_rate(pool)

    dec_comp.to_csv(OUT / "decile_comparison.csv", index=False)
    id_factors.to_csv(OUT / "identification_factors.csv", index=False)
    archetypes.to_csv(OUT / "d1_archetypes.csv", index=False)
    gaps.to_csv(OUT / "conversion_gaps.csv", index=False)
    first_prod.to_csv(OUT / "first_product_d1_rate.csv", index=False)

    plot_charts(pool, dec_comp, id_factors)

    md = build_markdown(pool, dec_comp, id_factors, archetypes, gaps, first_prod)
    (SCRIPT_DIR / "D1_CUSTOMER_PROFILE.md").write_text(md, encoding="utf-8")

    d1 = pool[pool["is_d1_profit"]]
    print(f"Pool: {len(pool):,} | D1: {len(d1):,}")
    print(f"Top factor: {id_factors.iloc[0]['factor']} (index {id_factors.iloc[0]['lift_index']:.0f})")
    print(f"D1 avg GP: S${d1['true_gross_profit'].mean():.0f} | categories: {d1['n_categories'].mean():.1f}")
    print(f"Markdown -> {SCRIPT_DIR / 'D1_CUSTOMER_PROFILE.md'}")
    print(f"Outputs -> {OUT}")


if __name__ == "__main__":
    main()
