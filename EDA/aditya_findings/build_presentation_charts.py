"""
build_presentation_charts.py — Deck-ready charts for Recommendations 1 & 2.

Run: python EDA/aditya_findings/build_presentation_charts.py
Output: EDA/aditya_findings/outputs/charts/
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

FINDINGS = Path(__file__).resolve().parent
OUT = FINDINGS / "outputs" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
FINALS = FINDINGS.parent / "outputs_finals"

PALETTE = {
    "T1": "#1B4965",
    "T2": "#2E86AB",
    "T3": "#5FA8D3",
    "T4": "#A8DADC",
    "T5": "#CAD2C5",
    "accent": "#E76F51",
    "sub": "#2A9D8F",
    "vip": "#E9C46A",
}
plt.rcParams.update({
    "figure.dpi": 150,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "figure.facecolor": "white",
})


def _save(fig, name: str):
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {path.name}")


def chart_r1_tier_overview():
    """Rec 1: T1–T5 customer counts + avg profit margin."""
    tier = pd.read_csv(FINDINGS / "outputs" / "crm_tier_incentive_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    colors = [PALETTE[t] for t in tier["crm_treatment_tier"]]

    ax = axes[0]
    bars = ax.bar(tier["crm_treatment_tier"], tier["n_customers"], color=colors, edgecolor="white", linewidth=1.2)
    ax.set_title("CRM Tiers — Customer Count", fontweight="bold", pad=12)
    ax.set_xlabel("Treatment tier")
    ax.set_ylabel("Customers")
    for b, n in zip(bars, tier["n_customers"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 30, f"{int(n):,}", ha="center", fontsize=10)

    ax = axes[1]
    ax.bar(tier["crm_treatment_tier"], tier["avg_cm"], color=colors, edgecolor="white", linewidth=1.2)
    ax.set_title("Avg Profit Margin (hybrid COGS) by Tier", fontweight="bold", pad=12)
    ax.set_xlabel("Treatment tier")
    ax.set_ylabel("Avg profit margin (SGD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"S${x:,.0f}"))

    fig.suptitle("Recommendation 1 — Treat Customers Differently by Profit Margin", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, "r1_crm_tier_overview.png")


def chart_r1_incentive_budgets():
    """Rec 1: Dollar incentives allowed per profit margin decile."""
    dec = pd.read_csv(FINDINGS / "outputs" / "cm_decile_incentive_budgets.csv")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(dec))
    w = 0.35
    ax.bar(x - w / 2, dec["budget_5pct"], w, label="5% of profit margin", color=PALETTE["T3"])
    ax.bar(x + w / 2, dec["budget_10pct"], w, label="10% of profit margin", color=PALETTE["T2"])
    ax.set_xticks(x)
    ax.set_xticklabels(dec["contribution_margin_decile"])
    ax.set_xlabel("Profit margin decile (D1 = highest)")
    ax.set_ylabel("Avg incentive budget (SGD / customer)")
    ax.set_title("How Much Can LP Give Away? — Profit Margin × 5% / 10%", fontweight="bold", pad=14)
    ax.legend(frameon=True, loc="upper right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"S${x:.0f}"))
    for i, row in dec.iterrows():
        ax.text(i - w / 2, row["budget_5pct"] + 0.3, f"S${row['budget_5pct']:.0f}", ha="center", fontsize=9)
        ax.text(i + w / 2, row["budget_10pct"] + 0.3, f"S${row['budget_10pct']:.0f}", ha="center", fontsize=9)
    fig.tight_layout()
    _save(fig, "r1_incentive_budget_by_decile.png")


def chart_r1_pm_concentration():
    """Rec 1: D1 profit margin concentration."""
    dec = pd.read_csv(FINALS / "decile_customer_table.csv")
    gp = dec.groupby("contribution_margin_decile")["true_gross_profit"].sum()
    gp = gp.reindex([f"D{i}" for i in range(1, 6)])
    pct = gp / gp.sum() * 100

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    colors = sns.color_palette("Blues_r", 5)
    axes[0].bar(pct.index, pct.values, color=colors, edgecolor="white")
    axes[0].set_title("% of Total Profit Margin by Decile", fontweight="bold")
    axes[0].set_ylabel("% of pool profit margin")
    axes[0].text(0, pct.iloc[0] + 1, f"{pct.iloc[0]:.1f}%", ha="center", fontweight="bold", fontsize=12)

    cum = pct.cumsum()
    axes[1].plot(cum.index, cum.values, marker="o", linewidth=2.5, color=PALETTE["T2"], markersize=10)
    axes[1].fill_between(range(5), cum.values, alpha=0.15, color=PALETTE["T2"])
    axes[1].axhline(80, color=PALETTE["accent"], linestyle="--", alpha=0.7, label="80% line")
    axes[1].set_title("Cumulative Profit Margin Concentration", fontweight="bold")
    axes[1].set_ylabel("Cumulative %")
    axes[1].legend()
    fig.suptitle("Top 20% (D1) Hold 57.7% of Profit Margin", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, "r1_profit_margin_concentration.png")


def chart_r1_incentives_not_discounts():
    """Rec 1: Incentive types by tier (founder: NO discounts)."""
    data = {
        "Tier": ["T1 VIP", "T2 High-Value", "T3 Growth", "T4 First-tx", "T5 Low"],
        "Merch/Shaker": [35, 25, 15, 10, 0],
        "Partner/Event": [40, 5, 0, 0, 0],
        "Samples/Sachet": [10, 20, 40, 45, 5],
        "Early Access": [15, 10, 5, 5, 0],
        "Email Only": [0, 40, 40, 40, 95],
    }
    df = pd.DataFrame(data).set_index("Tier")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    df.plot(kind="barh", stacked=True, ax=ax, color=["#E9C46A", "#2A9D8F", "#E76F51", "#264653", "#CAD2C5"])
    ax.set_title("Incentive Mix by Tier — Experiences & Merch, Not % Discounts", fontweight="bold", pad=12)
    ax.set_xlabel("% of retention budget allocation (illustrative)")
    ax.legend(title="Incentive type", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    _save(fig, "r1_incentive_mix_no_discounts.png")


def chart_r2_category_ladder():
    """Rec 2: Category ladder — retention driver."""
    cl = pd.read_csv(FINDINGS / "pitch_analysis" / "outputs" / "category_ladder_gp.csv")
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    x = cl["n_categories"].astype(str) + " cat"
    ax1.bar(x, cl["avg_gp"], color=PALETTE["T2"], alpha=0.85, label="Avg profit margin")
    ax1.set_ylabel("Avg profit margin (SGD)", color=PALETTE["T2"])
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"S${v:.0f}"))
    ax2 = ax1.twinx()
    ax2.plot(x, cl["repeat_rate"] * 100, color=PALETTE["accent"], marker="o", linewidth=2.5, markersize=9, label="Repeat rate")
    ax2.set_ylabel("Repeat rate (%)", color=PALETTE["accent"])
    ax2.set_ylim(0, 100)
    ax1.set_title("Cross-Sell Goal: Move Customers Up the Category Ladder", fontweight="bold", pad=14)
    ax1.set_xlabel("Categories ever purchased")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    for i, row in cl.iterrows():
        ax1.text(i, row["avg_gp"] + 5, f"{int(row['n_customers']):,}", ha="center", fontsize=9)
    fig.tight_layout()
    _save(fig, "r2_category_ladder.png")


def chart_r2_cross_sell_timeline():
    """Rec 2: Clear Protein buyer — when to email vs ship sample."""
    days = [0, 14, 44, 54, 62]
    events = ["Order 1\n(delivered)", "Day 14\nEmail:\nLean Protein", "Day 44\nShip sachet\n(Collagen/Lean)", "Day 54\nMedian\nreorder", "Day 48*\nSub offer\n(after ord 2)"]
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(-2, 68)
    ax.set_ylim(0, 3)
    ax.axhline(1.5, color="#ddd", linewidth=2, zorder=0)
    colors = [PALETTE["T2"], PALETTE["accent"], PALETTE["vip"], PALETTE["T1"], PALETTE["sub"]]
    for d, ev, c in zip(days[:4], events[:4], colors[:4]):
        ax.scatter(d, 1.5, s=280, c=c, zorder=2, edgecolors="white", linewidth=2)
        ax.annotate(ev, (d, 1.5), textcoords="offset points", xytext=(0, 22), ha="center", fontsize=9, fontweight="bold")
    ax.annotate("*After 2nd order", (48, 1.5), textcoords="offset points", xytext=(0, -35), ha="center", fontsize=8, color="#666")
    ax.set_yticks([])
    ax.set_xlabel("Days after first delivery", fontsize=11)
    ax.set_title("Clear Protein Buyer — Sample BEFORE Reorder (Day 44), Not at Checkout", fontweight="bold", pad=16)
    ax.spines[["top", "right", "left"]].set_visible(False)
    note = "Email cross-sell at day 14 · Physical sachet at day 44 (10d before 54d reorder) · NOT in first order box"
    ax.text(0.5, 0.02, note, transform=ax.transAxes, ha="center", fontsize=10, style="italic", color="#444")
    fig.tight_layout()
    _save(fig, "r2_cross_sell_timeline_clear.png")


def chart_r2_four_layers():
    """Rec 2: 4-layer architecture vs lifecycle."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    layers = [
        ("L1 Rule-based", "1st purchase\n(cold start)", "Klaviyo welcome", PALETTE["T4"]),
        ("L2 MBA", "Same cart", "Shopify PDP bundle", PALETTE["T3"]),
        ("L3 Sequential", "Between orders", "Day 14 / 7 emails", PALETTE["accent"]),
        ("L4 Item-CF", "Logged-in 3+ orders", "Account page", PALETTE["T2"]),
    ]
    for i, (title, stage, deploy, col) in enumerate(layers):
        y = 4.5 - i * 1.1
        rect = mpatches.FancyBboxPatch((0.5, y - 0.35), 3.2, 0.9, boxstyle="round,pad=0.05", facecolor=col, edgecolor="white", linewidth=2)
        ax.add_patch(rect)
        ax.text(2.1, y + 0.1, title, ha="center", va="center", fontweight="bold", color="white", fontsize=11)
        ax.text(5.5, y + 0.1, stage, ha="left", va="center", fontsize=10)
        ax.text(7.5, y + 0.1, deploy, ha="left", va="center", fontsize=10, color="#555")
    rect = mpatches.FancyBboxPatch((0.5, 0.4), 9, 0.9, boxstyle="round,pad=0.05", facecolor=PALETTE["sub"], edgecolor="white", linewidth=2)
    ax.add_patch(rect)
    ax.text(5, 0.85, "Subscription Engine — after order 2 + 48 days (SUB-01)", ha="center", va="center", fontweight="bold", color="white", fontsize=12)
    ax.set_title("Recommendation 2 — 4-Layer Engine + Subscription (Not Shopify Default)", fontweight="bold", fontsize=14, pad=20)
    fig.tight_layout()
    _save(fig, "r2_four_layer_architecture.png")


def chart_r2_shopify_vs_custom():
    """Rec 2: Capability comparison."""
    caps = ["Category\ncross-sell", "Timed\njourneys", "PM tier\ntreatment", "Sample\ntiming", "Subscription\ntrigger", "VIP\nexperiences"]
    shopify = [2, 1, 1, 0, 2, 1]
    custom = [5, 5, 5, 5, 5, 5]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(caps))
    w = 0.35
    ax.bar(x - w / 2, shopify, w, label="Shopify recommended products", color="#CAD2C5")
    ax.bar(x + w / 2, custom, w, label="Lush Protein 4-layer engine", color=PALETTE["T2"])
    ax.set_xticks(x)
    ax.set_xticklabels(caps)
    ax.set_ylabel("Capability score (1–5)")
    ax.set_ylim(0, 6)
    ax.set_title("Why Custom Engine — Data-Proven Patterns Shopify Cannot Use", fontweight="bold", pad=14)
    ax.legend(loc="upper right")
    fig.tight_layout()
    _save(fig, "r2_shopify_vs_custom_engine.png")


def chart_r2_subscription_decile():
    """Rec 2: Subscription rate by profit margin decile."""
    dec = pd.read_csv(FINALS / "decile_customer_table.csv")
    sub = dec.groupby("contribution_margin_decile").agg(
        sub_rate=("ever_subscribed", "mean"),
        n=("customer_id", "count"),
        avg_pm=("true_gross_profit", "mean"),
    ).reindex([f"D{i}" for i in range(1, 6)])

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    x = sub.index
    ax1.bar(x, sub["sub_rate"] * 100, color=PALETTE["sub"], alpha=0.8, label="Ever subscribed %")
    ax1.set_ylabel("Subscription rate (%)")
    ax1.set_xlabel("Profit margin decile")
    ax2 = ax1.twinx()
    ax2.plot(x, sub["avg_pm"], color=PALETTE["T2"], marker="s", linewidth=2, markersize=8, label="Avg profit margin")
    ax2.set_ylabel("Avg profit margin (SGD)")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"S${v:.0f}"))
    ax1.set_title("Higher Profit Margin Deciles Subscribe More — Decile Study", fontweight="bold", pad=14)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    fig.tight_layout()
    _save(fig, "r2_subscription_by_profit_decile.png")


def chart_r2_sample_by_purchase_stage():
    """Rec 2: Who gets single-serve samples."""
    stages = ["1st purchase\n(T4)", "2nd purchase\n(T3)", "3rd+ / VIP\n(T1)"]
    email = [14, 7, 0]
    sample = [44, 7, 0]
    merch = [0, 0, 100]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(3)
    w = 0.25
    ax.bar(x - w, email, w, label="Email cross-sell (day)", color=PALETTE["accent"])
    ax.bar(x, sample, w, label="Physical sachet (day)", color=PALETTE["vip"])
    ax.bar(x + w, [0, 0, 1], w, label="Merch/partner gift", color=PALETTE["T1"])
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_ylabel("Days after delivery (email/sachet) or gift type")
    ax.set_title("Single-Serve Strategy — 1st & 2nd Buyers Get Sachets; VIPs Get Merch", fontweight="bold", pad=14)
    ax.legend()
    fig.tight_layout()
    _save(fig, "r2_sample_by_purchase_stage.png")


def main():
    print("Building presentation charts →", OUT)
    chart_r1_tier_overview()
    chart_r1_incentive_budgets()
    chart_r1_pm_concentration()
    chart_r1_incentives_not_discounts()
    chart_r2_category_ladder()
    chart_r2_cross_sell_timeline()
    chart_r2_four_layers()
    chart_r2_shopify_vs_custom()
    chart_r2_subscription_decile()
    chart_r2_sample_by_purchase_stage()
    print("Done —", len(list(OUT.glob("*.png"))), "charts in outputs/charts/")


if __name__ == "__main__":
    main()
