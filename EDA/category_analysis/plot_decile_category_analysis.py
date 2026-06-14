"""
plot_decile_category_analysis.py — Charts + actionable insights for T1–T9 decile category analysis.

Reads from:
  EDA/category_analysis/outputs/by_profit_decile/
  EDA/category_analysis/outputs/by_frequency_decile/

Saves PNGs to:
  EDA/category_analysis/outputs/charts/by_profit_decile/
  EDA/category_analysis/outputs/charts/by_frequency_decile/

Also writes: outputs/ACTIONABLE_INSIGHTS.md

Run: python EDA/category_analysis/plot_decile_category_analysis.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

VIZ_DIR = Path(__file__).resolve().parent.parent.parent / "visualizations"
sys.path.insert(0, str(VIZ_DIR))
from style import TEAL, NAVY, ORANGE, RED, SLATE, GOLD, LILAC, LIGHT_BG, CAT_COLORS  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_BASE = SCRIPT_DIR / "outputs"
DECILES = [f"D{i}" for i in range(1, 11)]
HERO_CATS = ["Clear Protein", "Lean Protein", "Collagen Glow", "Soy Protein", "Accessories", "Other"]
CAT_COLOR = {c: CAT_COLORS[i % len(CAT_COLORS)] for i, c in enumerate(HERO_CATS + ["Unknown"])}


def save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=LIGHT_BG)
    plt.close(fig)
    print(f"  Saved: {path.relative_to(OUT_BASE)}")


def _read(data_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(data_dir / name)


def chart_t1(t1: pd.DataFrame, chart_dir: Path, label: str):
    t1 = t1.set_index("decile").reindex(DECILES).reset_index()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"T1 — Decile Product Summary ({label})", fontsize=14, fontweight="bold", y=1.01)
    x = t1["decile"].astype(str)
    colors = [TEAL if d == "D1" else SLATE + "99" for d in x]

    for ax, col, title, fmt, ylab in [
        (axes[0, 0], "avg_profit", "Avg Profit per Customer", "${:,.0f}", "SGD"),
        (axes[0, 1], "avg_orders", "Avg Order Frequency (AOF)", "{:.1f}", "Orders"),
        (axes[1, 0], "avg_cats_ever", "Avg Categories Ever Purchased", "{:.1f}", "Categories"),
        (axes[1, 1], "dollars_per_unit", "$/Unit (AOV driver)", "${:.0f}", "SGD/unit"),
    ]:
        vals = t1[col].tolist()
        bars = ax.bar(x, vals, color=colors, edgecolor="white")
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Decile (D1 = best)")
        ax.set_ylabel(ylab)
        for bar, v in zip(bars, vals):
            if pd.notna(v) and v > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, v, fmt.format(v),
                        ha="center", va="bottom", fontsize=7)
        ax.grid(axis="y", alpha=0.4)
    fig.tight_layout()
    save_fig(fig, chart_dir / "t1_decile_product_summary.png")


def chart_t3(t3: pd.DataFrame, chart_dir: Path, label: str):
    d1 = t3[t3["segment"].str.contains("d1")].copy()
    if d1.empty:
        d1 = t3.head(7)
    d1 = d1.sort_values("n_category_buyers", ascending=True).tail(7)
    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(d1))
    sole = d1["pct_sole_cat_buyers"] * 100
    cross = 100 - sole
    ax.barh(y, sole, color=TEAL, height=0.55, label="Sole-category")
    ax.barh(y, cross, left=sole, color=SLATE + "55", height=0.55, label="Cross-category")
    ax.set_yticks(y)
    ax.set_yticklabels(d1["category"], fontsize=9)
    ax.set_xlabel("% of category buyers")
    ax.set_title(f"T3 — Sole vs Cross-Category Buyers (D1 segment, {label})", fontweight="bold")
    for i, (s, c) in enumerate(zip(sole, cross)):
        ax.text(s / 2, i, f"{s:.0f}%", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    save_fig(fig, chart_dir / "t3_sole_vs_cross_d1.png")


def chart_t4(t4: pd.DataFrame, chart_dir: Path, label: str):
    plot = t4[~t4["category"].isin(["Unknown"])].copy()
    plot = plot.sort_values("d1_index", ascending=True).tail(6)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"T4 — D1 vs All Category Decomposition ({label})", fontweight="bold", y=1.02)

    y = np.arange(len(plot))
    bars = axes[0].barh(y, plot["d1_index"], color=[TEAL if v >= 200 else ORANGE if v >= 100 else SLATE for v in plot["d1_index"]])
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(plot["category"])
    axes[0].axvline(100, color=RED, linestyle="--", linewidth=1.5, label="Index = 100")
    axes[0].set_xlabel("D1 Profit Index (100 = average)")
    axes[0].set_title("D1 Profit per Customer vs All")
    for bar, v in zip(bars, plot["d1_index"]):
        axes[0].text(v + 2, bar.get_y() + bar.get_height() / 2, f"{v:.0f}", va="center", fontsize=9)

    w = 0.35
    x = np.arange(len(plot))
    axes[1].bar(x - w / 2, plot["acov_all"], w, label="All", color=SLATE)
    axes[1].bar(x + w / 2, plot["acov_d1"], w, label="D1", color=TEAL)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(plot["category"], rotation=30, ha="right", fontsize=9)
    axes[1].set_ylabel("ACOV (SGD)")
    axes[1].set_title("Avg Order Value in Category")
    axes[1].legend(fontsize=9)
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"S${v:.0f}"))
    fig.tight_layout()
    save_fig(fig, chart_dir / "t4_d1_index_and_acov.png")


def chart_t5_pivot(pivot: pd.DataFrame, chart_dir: Path, label: str):
    year_cols = [c for c in pivot.columns if str(c).isdigit()]
    if not year_cols:
        return
    fig, ax = plt.subplots(figsize=(10, 7))
    data = pivot.set_index("decile").reindex(DECILES)[year_cols].astype(float)
    im = ax.imshow(data.values, cmap="YlGnBu", aspect="auto", vmin=1, vmax=data.values.max())
    ax.set_xticks(range(len(year_cols)))
    ax.set_xticklabels(year_cols)
    ax.set_yticks(range(len(DECILES)))
    ax.set_yticklabels(DECILES)
    ax.set_title(f"T5 — Cumulative Categories by Decile × Year ({label})", fontweight="bold")
    ax.set_xlabel("Calendar year (cumulative through year-end)")
    ax.set_ylabel("Decile")
    for i in range(len(DECILES)):
        for j in range(len(year_cols)):
            v = data.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8,
                        color="white" if v > data.values.max() * 0.6 else NAVY)
    plt.colorbar(im, ax=ax, label="Avg cumulative categories")
    fig.tight_layout()
    save_fig(fig, chart_dir / "t5_cumulative_categories_heatmap.png")


def chart_t6_pivot(pivot: pd.DataFrame, chart_dir: Path, label: str):
    year_cols = [c for c in pivot.columns if str(c).isdigit()]
    if not year_cols:
        return
    fig, ax = plt.subplots(figsize=(10, 7))
    data = pivot.set_index("decile").reindex(DECILES)[year_cols].astype(float)
    im = ax.imshow(data.values, cmap="OrRd", aspect="auto")
    ax.set_xticks(range(len(year_cols)))
    ax.set_xticklabels(year_cols)
    ax.set_yticks(range(len(DECILES)))
    ax.set_yticklabels(DECILES)
    ax.set_title(f"T6 — Active Categories per Year ({label})", fontweight="bold")
    ax.set_xlabel("Calendar year (in-year only)")
    ax.set_ylabel("Decile")
    for i in range(len(DECILES)):
        for j in range(len(year_cols)):
            v = data.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8,
                        color="white" if v > np.nanmax(data.values) * 0.55 else NAVY)
    plt.colorbar(im, ax=ax, label="Avg active categories")
    fig.tight_layout()
    save_fig(fig, chart_dir / "t6_active_categories_heatmap.png")


def chart_t7(t7: pd.DataFrame, chart_dir: Path, label: str):
    hero = [c for c in HERO_CATS if c in t7["category"].values]
    fig, ax = plt.subplots(figsize=(11, 6))
    for cat in hero:
        sub = t7[t7["category"] == cat].sort_values("calendar_year")
        ax.plot(sub["calendar_year"], sub["pct_d1_ever_bought"] * 100,
                marker="o", linewidth=2, label=cat, color=CAT_COLOR.get(cat, SLATE))
    ax.set_xlabel("Calendar year (cumulative through year-end)")
    ax.set_ylabel("% of D1 customers who ever bought category")
    ax.set_title(f"T7 — D1 Category Adoption Over Time ({label})", fontweight="bold")
    ax.legend(fontsize=8, ncol=2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    save_fig(fig, chart_dir / "t7_d1_adoption_cumulative.png")


def chart_t8(t8: pd.DataFrame, chart_dir: Path, label: str):
    hero = [c for c in HERO_CATS if c in t8["category"].values]
    fig, ax = plt.subplots(figsize=(11, 6))
    for cat in hero:
        sub = t8[t8["category"] == cat].sort_values("calendar_year")
        ax.plot(sub["calendar_year"], sub["pct_d1_active_in_year"] * 100,
                marker="s", linewidth=2, label=cat, color=CAT_COLOR.get(cat, SLATE))
    ax.set_xlabel("Calendar year")
    ax.set_ylabel("% of D1 pool active in category this year")
    ax.set_title(f"T8 — D1 Active Category Rate per Year ({label})", fontweight="bold")
    ax.legend(fontsize=8, ncol=2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    save_fig(fig, chart_dir / "t8_d1_active_category_yoy.png")


def chart_t9(t9: pd.DataFrame, chart_dir: Path, label: str):
    sub = t9[t9["segment"].str.contains("all")].copy()
    sub = sub[~sub["category"].isin(["Unknown"])].sort_values("vtd_index", ascending=True).tail(6)
    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(sub))
    colors = [TEAL if v >= 100 else ORANGE if v >= 85 else SLATE for v in sub["vtd_index"]]
    bars = ax.barh(y, sub["vtd_index"], color=colors, height=0.55)
    ax.axvline(100, color=RED, linestyle="--", linewidth=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels(sub["category"])
    ax.set_xlabel("VTD Index (100 = pool average)")
    ax.set_title(f"T9 — First-Transaction Category VTD Index ({label})", fontweight="bold")
    for bar, v, n in zip(bars, sub["vtd_index"], sub["n_first_tx_buyers"]):
        ax.text(v + 1, bar.get_y() + bar.get_height() / 2, f"{v:.0f}  (n={int(n):,})",
                va="center", fontsize=9)
    fig.tight_layout()
    save_fig(fig, chart_dir / "t9_first_transaction_index.png")


def build_insights(profit_dir: Path, freq_dir: Path) -> str:
    t1p = _read(profit_dir, "t1_decile_product_summary.csv")
    t1f = _read(freq_dir, "t1_decile_product_summary.csv")
    t4p = _read(profit_dir, "t4_d1_vs_all_category_decomposition.csv")
    t5p = _read(profit_dir, "t5_cumulative_categories_pivot.csv")
    t8p = _read(profit_dir, "t8_d1_active_category_pivot.csv")
    t9p = _read(profit_dir, "t9_first_transaction_index.csv")
    t3p = _read(profit_dir, "t3_cross_category_behavior.csv")

    d1p = t1p[t1p["decile"] == "D1"].iloc[0]
    d10p = t1p[t1p["decile"] == "D10"].iloc[0]
    d1f = t1f[t1f["decile"] == "D1"].iloc[0]

    profit_ratio = d1p["avg_profit"] / d10p["avg_profit"]
    unit_ratio = d1p["dollars_per_unit"] / d10p["dollars_per_unit"]

    top_t4 = t4p[~t4p["category"].isin(["Unknown"])].sort_values("d1_index", ascending=False).head(3)
    top_t9 = t9p[t9p["segment"].str.contains("all")].sort_values("vtd_index", ascending=False).head(3)

    d1_cats_2022 = float(t5p[t5p["decile"] == "D1"]["2022"].iloc[0])
    d1_cats_2025 = float(t5p[t5p["decile"] == "D1"]["2025"].iloc[0])

    clear_t8 = t8p[t8p["category"] == "Clear Protein"]
    lean_t8 = t8p[t8p["category"] == "Lean Protein"]

    t3_d1_clear = t3p[(t3p["segment"] == "d1_profit") & (t3p["category"] == "Clear Protein")]
    sole_clear = float(t3_d1_clear["pct_sole_cat_buyers"].iloc[0]) * 100 if len(t3_d1_clear) else 0

    lines = [
        "# Actionable Insights — Decile × Category Analysis",
        "",
        f"**Pool:** 4,290 customers | **Profit proxy:** 40% margin | **Years:** 2022–2025",
        "",
        "---",
        "",
        "## 1. Protect and grow profit D1 — they are a different species (T1)",
        "",
        f"- **D1 profit decile** averages **S${d1p['avg_profit']:,.0f}** profit vs **S${d10p['avg_profit']:,.0f}** for D10 — a **{profit_ratio:.0f}×** gap.",
        f"- D1 buys **{d1p['avg_orders']:.1f}×** more often ({d1p['avg_orders']:.1f} vs {d10p['avg_orders']:.1f} orders) but the bigger lever is **$/unit**: **S${d1p['dollars_per_unit']:.0f}** vs **S${d10p['dollars_per_unit']:.0f}** ({unit_ratio:.0f}×).",
        f"- D1 explores **{d1p['avg_cats_ever']:.1f}** categories vs D10's **{d10p['avg_cats_ever']:.1f}** — breadth AND premium basket composition drive value.",
        "",
        "**Actions:**",
        "- VIP programme for profit D1 (early access, bundles, subscription nudges).",
        "- Upsell to **larger packs / hero proteins** — don't discount D1; they already pay premium $/unit.",
        "- Do NOT treat D10 one-time buyers with the same promo intensity as D1.",
        "",
        "---",
        "",
        "## 2. Frequency D1 ≠ Profit D1 — target both explicitly (T1 compare)",
        "",
        f"- **Frequency D1** averages **{d1f['avg_orders']:.1f} orders** but only **S${d1f['avg_profit']:,.0f}** profit — high engagement without highest spend.",
        f"- **Profit D1** has fewer orders ({d1p['avg_orders']:.1f}) but **higher AOV** (S${d1p['aov_decile']:.0f} vs S${d1f['aov_decile']:.0f}).",
        "",
        "**Actions:**",
        "- **Frequency D1:** subscription conversion, replenishment reminders (54-day reorder window from prior SKU analysis).",
        "- **Profit D1:** premium bundles, multi-category baskets, avoid margin-eroding discounts.",
        "- Use `is_top_both` flag in `customers_decile_table.csv` (~244 customers) as **true VIP** tier.",
        "",
        "---",
        "",
        "## 3. Cross-sell is the retention engine (T3 + T5)",
        "",
        f"- Profit D1 Clear Protein buyers: only **{sole_clear:.0f}%** are sole-category — most cross-shop.",
        f"- D1 cumulative categories grew **{d1_cats_2022:.1f} → {d1_cats_2025:.1f}** ({d1_cats_2025 - d1_cats_2022:+.1f}) from 2022 to 2025 — breadth develops over time, not just at acquisition.",
        "",
        "**Actions:**",
        "- **Year 1→2 cross-sell window:** email lean/clear buyers with complementary category (Collagen, Soy) within 60 days of 2nd order.",
        f"- Post-purchase flows: 'Customers who bought Clear also bought Lean' — only **{sole_clear:.0f}%** stay in one category.",
        "- Incentivise **2nd category by order 3**, not just 2nd order.",
        "",
        "---",
        "",
        "## 4. Prioritise hero proteins in D1 strategy (T4)",
        "",
    ]
    for _, row in top_t4.iterrows():
        lines.append(
            f"- **{row['category']}:** D1 index **{row['d1_index']:.0f}** | "
            f"D1 ACOV S${row['acov_d1']:.0f} vs All S${row['acov_all']:.0f} | "
            f"D1 penetration {row['pct_active_d1']*100:.0f}% vs {row['pct_active_all']*100:.0f}%"
        )
    lines += [
        "",
        "**Actions:**",
        "- Feature **Lean + Clear** in acquisition creative and landing pages (highest D1 profit density).",
        "- Accessories alone are low profit density (index ~127) — use as **cart add-on**, not acquisition lead.",
        "- Bundle Clear + Lean for D1-leaning customers at checkout.",
        "",
        "---",
        "",
        "## 5. Steer acquisition by first-transaction category (T9)",
        "",
    ]
    for _, row in top_t9.iterrows():
        if row["category"] != "Unknown":
            lines.append(
                f"- **{row['category']}** first-tx entrants: VTD index **{row['vtd_index']:.0f}**, "
                f"avg VTD S${row['avg_vtd_sgd']:,.0f}, n={int(row['n_first_tx_buyers']):,}"
            )
    lines += [
        "",
        "**Actions:**",
        "- **Collagen Glow** first-buyers over-index on lifetime value (index ~171) — treat as VIP onboarding despite smaller volume.",
        "- **Accessories-first** entrants index below average (~68) — upsell to protein within 30 days.",
        "- Channel mix: track which acquisition sources produce Collagen/Clear first-tx (personalise welcome series).",
        "",
        "---",
        "",
        "## 6. Retain active protein buyers year-over-year (T7 + T8)",
        "",
    ]
    if len(clear_t8):
        lines.append(
            f"- **Clear Protein** D1 active rate: {clear_t8['pct_2022'].iloc[0]:.0f}% (2022) → "
            f"{clear_t8['pct_2025'].iloc[0]:.0f}% (2025) — "
            f"change {clear_t8['change_pp_yr2022_to_yr2025'].iloc[0]:+.0f}pp"
        )
    if len(lean_t8):
        lines.append(
            f"- **Lean Protein** D1 active rate: {lean_t8['pct_2022'].iloc[0]:.0f}% → "
            f"{lean_t8['pct_2025'].iloc[0]:.0f}% — "
            f"change {lean_t8['change_pp_yr2022_to_yr2025'].iloc[0]:+.0f}pp"
        )
    lines += [
        "- **Unknown** category shows sharp active decline for D1 — fix product handle mapping in `00_config.py` to sharpen targeting.",
        "",
        "**Actions:**",
        "- **Reactivation campaigns** for D1 customers who bought Clear/Lean in 2024 but not 2025.",
        "- Flavour rotation emails for D1 (Peach, White Grape, Thai Milk Tea) to maintain active engagement.",
        "- Monitor **active** not just cumulative — a customer who tried 4 categories but only buys 1 per year still needs stimulation.",
        "",
        "---",
        "",
        "## 7. Data quality actions (enables sharper insights)",
        "",
        "- **~28% Unknown category** distorts T4/T9 — extend `PRODUCT_MAP` in `00_config.py` and request COGS from LP (`deliverables/COGS_Data_Request_LushProtein.xlsx`).",
        "- Once COGS received: re-run profit deciles on **true gross profit** — Accessories margin may differ from 40% assumption.",
        "",
        "---",
        "",
        "## 8. Priority action matrix",
        "",
        "| Priority | Segment | Action | Expected impact |",
        "|----------|---------|--------|-----------------|",
        "| P0 | `is_top_both` (~244) | VIP + subscription + exclusive bundles | Protect highest LTV |",
        "| P0 | Profit D1, not Freq D1 | Premium upsell, limit deep discounts | Raise $/unit |",
        "| P1 | Freq D1 | Replenishment + subscribe-and-save | Raise order frequency |",
        "| P1 | Collagen first-tx | VIP onboarding, cross-sell proteins | Higher VTD index |",
        "| P2 | D5–D7 middle deciles | 2nd-category incentive by order 3 | Move toward D1 breadth |",
        "| P2 | Accessories acquirers | Protein upsell within 30 days | Lift from index ~68 |",
        "| P3 | D10 one-and-done | Low-cost win-back only if recent | Low ROI — deprioritise |",
        "",
        "---",
        "",
        "Regenerate: `python EDA/category_analysis/plot_decile_category_analysis.py`",
    ]
    return "\n".join(lines)


def run_slice(data_dir: Path, chart_dir: Path, label: str):
    print(f"\n--- Charts: {label} ---")
    chart_t1(_read(data_dir, "t1_decile_product_summary.csv"), chart_dir, label)
    chart_t3(_read(data_dir, "t3_cross_category_behavior.csv"), chart_dir, label)
    chart_t4(_read(data_dir, "t4_d1_vs_all_category_decomposition.csv"), chart_dir, label)
    chart_t5_pivot(_read(data_dir, "t5_cumulative_categories_pivot.csv"), chart_dir, label)
    chart_t6_pivot(_read(data_dir, "t6_active_categories_pivot.csv"), chart_dir, label)
    chart_t7(_read(data_dir, "t7_d1_category_adoption_cumulative.csv"), chart_dir, label)
    chart_t8(_read(data_dir, "t8_d1_active_category_by_year.csv"), chart_dir, label)
    chart_t9(_read(data_dir, "t9_first_transaction_index.csv"), chart_dir, label)


def main():
    print("=" * 72)
    print("DECILE CATEGORY CHARTS + INSIGHTS")
    print("=" * 72)

    profit_dir = OUT_BASE / "by_profit_decile"
    freq_dir = OUT_BASE / "by_frequency_decile"

    run_slice(profit_dir, OUT_BASE / "charts" / "by_profit_decile", "Profit Decile")
    run_slice(freq_dir, OUT_BASE / "charts" / "by_frequency_decile", "Frequency Decile")

    # Comparison: D1 profit vs D1 frequency on key metrics
    t1p = _read(profit_dir, "t1_decile_product_summary.csv")
    t1f = _read(freq_dir, "t1_decile_product_summary.csv")
    d1p = t1p[t1p["decile"] == "D1"].iloc[0]
    d1f = t1f[t1f["decile"] == "D1"].iloc[0]
    fig, ax = plt.subplots(figsize=(10, 5))
    metrics = ["avg_profit", "avg_orders", "aov_decile", "avg_cats_ever"]
    labels = ["Avg Profit", "Avg Orders", "AOV", "Avg Categories"]
    x = np.arange(len(metrics))
    w = 0.35
    vp = [d1p[m] for m in metrics]
    vf = [d1f[m] for m in metrics]
    ax.bar(x - w / 2, vp, w, label="D1 Profit Decile", color=TEAL)
    ax.bar(x + w / 2, vf, w, label="D1 Frequency Decile", color=ORANGE)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("D1 Comparison: Profit Decile vs Frequency Decile", fontweight="bold")
    ax.legend()
    for i, (a, b) in enumerate(zip(vp, vf)):
        ax.text(i - w / 2, a, f"{a:,.0f}" if a > 10 else f"{a:.1f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + w / 2, b, f"{b:,.0f}" if b > 10 else f"{b:.1f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    save_fig(fig, OUT_BASE / "charts" / "d1_profit_vs_frequency_comparison.png")

    insights = build_insights(profit_dir, freq_dir)
    (OUT_BASE / "ACTIONABLE_INSIGHTS.md").write_text(insights, encoding="utf-8")
    print(f"\n  Saved: outputs/ACTIONABLE_INSIGHTS.md")

    print("\n" + "=" * 72)
    print("DONE")
    print("=" * 72)


if __name__ == "__main__":
    main()
