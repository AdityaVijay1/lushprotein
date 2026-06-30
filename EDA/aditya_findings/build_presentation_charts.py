"""
build_presentation_charts.py — Deck-ready charts for Recommendations 1 & 2.
v2: improved storytelling, fixed broken charts, better annotations.

Run: python EDA/aditya_findings/build_presentation_charts.py
Output: EDA/aditya_findings/outputs/charts/
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
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
    "text.parse_math": False,   # treat $ as literal in all text labels
})


def _save(fig, name: str):
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {path.name}")


# ── REC 1 CHARTS ─────────────────────────────────────────────────────────────

def chart_r1_tier_overview():
    """Rec 1: T1–T5 customer counts + avg profit margin — with value labels on both charts."""
    tier = pd.read_csv(FINDINGS / "outputs" / "crm_tier_incentive_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    colors = [PALETTE[t] for t in tier["crm_treatment_tier"]]

    # --- left: customer count ---
    ax = axes[0]
    bars = ax.bar(tier["crm_treatment_tier"], tier["n_customers"], color=colors, edgecolor="white", linewidth=1.2)
    ax.set_title("CRM Tiers — Customer Count", fontweight="bold", pad=12)
    ax.set_xlabel("Treatment tier")
    ax.set_ylabel("Customers")
    for b, n in zip(bars, tier["n_customers"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 30, f"{int(n):,}",
                ha="center", fontsize=10, fontweight="bold")
    # annotate VIP
    ax.annotate("VIP Core\n(top PM + Freq)",
                xy=(bars[0].get_x() + bars[0].get_width() / 2, tier["n_customers"].iloc[0]),
                xytext=(0.8, 900), fontsize=9, color=PALETTE["T1"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["T1"], lw=1.3))

    # --- right: avg profit margin ---
    ax = axes[1]
    bars2 = ax.bar(tier["crm_treatment_tier"], tier["avg_cm"], color=colors, edgecolor="white", linewidth=1.2)
    ax.set_title("Avg Profit Margin (hybrid COGS) by Tier", fontweight="bold", pad=12)
    ax.set_xlabel("Treatment tier")
    ax.set_ylabel("Avg profit margin (SGD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"S${x:,.0f}"))
    for b, v in zip(bars2, tier["avg_cm"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 3, f"S${v:.0f}",
                ha="center", fontsize=10, fontweight="bold")
    # add T1 vs T5 gap annotation
    ax.annotate("", xy=(4, tier["avg_cm"].iloc[4] + 5),
                xytext=(0, tier["avg_cm"].iloc[0] - 10),
                arrowprops=dict(arrowstyle="<->", color=PALETTE["accent"], lw=1.5))
    ax.text(2, 140, f"29× gap\n(T1 vs T5)", ha="center", fontsize=9,
            color=PALETTE["accent"], fontweight="bold")

    fig.suptitle("Recommendation 1 — Stop Treating Every Customer the Same",
                 fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, "r1_crm_tier_overview.png")


def chart_r1_incentive_budgets():
    """Rec 1: Dollar incentives allowed per profit margin decile — with what the budgets buy."""
    dec = pd.read_csv(FINDINGS / "outputs" / "cm_decile_incentive_budgets.csv")
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(dec))
    w = 0.35
    b1 = ax.bar(x - w / 2, dec["budget_5pct"], w, label="5% of profit margin", color=PALETTE["T3"])
    b2 = ax.bar(x + w / 2, dec["budget_10pct"], w, label="10% of profit margin", color=PALETTE["T2"])
    ax.set_xticks(x)
    ax.set_xticklabels(dec["contribution_margin_decile"])
    ax.set_xlabel("Profit margin decile (D1 = highest)")
    ax.set_ylabel("Avg incentive budget (SGD / customer)")
    ax.set_title("Max Incentive Per Customer = X% × Profit Margin\n(Founder decides X — never a blanket % discount)",
                 fontweight="bold", pad=14)
    ax.legend(frameon=True, loc="upper right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"S${x:.0f}"))
    for i, row in dec.iterrows():
        ax.text(i - w / 2, row["budget_5pct"] + 0.3, f"S${row['budget_5pct']:.0f}",
                ha="center", fontsize=9)
        ax.text(i + w / 2, row["budget_10pct"] + 0.3, f"S${row['budget_10pct']:.0f}",
                ha="center", fontsize=9)
    # add interpretation labels
    ax.text(0 + w / 2 + 0.05, dec["budget_10pct"].iloc[0] + 0.8,
            "→ shaker/\nsample pack", ha="center", fontsize=8, color=PALETTE["T2"])
    ax.text(3 + w / 2 + 0.05, dec["budget_10pct"].iloc[3] + 0.5,
            "→ sachet\nonly", ha="center", fontsize=8, color=PALETTE["T2"])
    ax.text(4 + w / 2 + 0.05, dec["budget_10pct"].iloc[4] + 0.5,
            "→ email\nonly", ha="center", fontsize=8, color="#888")
    # highlight D1 region
    ax.axvspan(-0.5, 0.5, alpha=0.06, color=PALETTE["T1"], zorder=0)
    ax.text(0, -3.5, "VIP\n(T1)", ha="center", fontsize=9, color=PALETTE["T1"], fontweight="bold")
    fig.tight_layout()
    _save(fig, "r1_incentive_budget_by_decile.png")


def chart_r1_pm_concentration():
    """Rec 1: D1 profit margin concentration — fixed cumulative x-axis labels."""
    dec = pd.read_csv(FINALS / "decile_customer_table.csv")
    gp = dec.groupby("contribution_margin_decile")["true_gross_profit"].sum()
    gp = gp.reindex([f"D{i}" for i in range(1, 6)])
    pct = gp / gp.sum() * 100

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    colors = sns.color_palette("Blues_r", 5)

    # left: bar chart
    ax = axes[0]
    bars = ax.bar(pct.index, pct.values, color=colors, edgecolor="white", linewidth=1.2)
    ax.set_title("% of Total Profit Margin by Decile", fontweight="bold")
    ax.set_ylabel("% of pool profit margin")
    ax.text(0, pct.iloc[0] + 1, f"{pct.iloc[0]:.1f}%", ha="center",
            fontweight="bold", fontsize=13, color=PALETTE["T1"])
    for b, v in zip(bars[1:], pct.values[1:]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, f"{v:.1f}%",
                ha="center", fontsize=9, color="#555")
    ax.set_ylim(0, 70)
    # highlight D1
    bars[0].set_edgecolor(PALETTE["accent"])
    bars[0].set_linewidth(2.5)

    # right: cumulative curve — fix x-axis labels
    ax = axes[1]
    cum = pct.cumsum()
    x_pos = range(len(cum))
    ax.plot(x_pos, cum.values, marker="o", linewidth=2.5, color=PALETTE["T2"],
            markersize=10, zorder=3)
    ax.fill_between(x_pos, cum.values, alpha=0.15, color=PALETTE["T2"])
    ax.axhline(80, color=PALETTE["accent"], linestyle="--", alpha=0.7, label="80% line")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(cum.index)   # D1, D2, D3, D4, D5
    ax.set_title("Cumulative Profit Margin Concentration", fontweight="bold")
    ax.set_ylabel("Cumulative %")
    ax.set_ylim(0, 105)
    ax.legend()
    # annotate: D1+D2 already = 79%
    ax.annotate(f"D1+D2 = {cum.iloc[1]:.0f}%", xy=(1, cum.iloc[1]),
                xytext=(2.2, cum.iloc[1] - 12), fontsize=9, color=PALETTE["T2"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["T2"], lw=1.2))
    for i, (xi, yi) in enumerate(zip(x_pos, cum.values)):
        ax.text(xi, yi + 2, f"{yi:.0f}%", ha="center", fontsize=8.5, color=PALETTE["T1"])

    fig.suptitle("Top 20% (D1) Hold 57.7% of Profit Margin — 2 Tiers = 80%",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, "r1_profit_margin_concentration.png")


def chart_r1_incentives_not_discounts():
    """Rec 1: Incentive types by tier — NO % discounts banner for T1."""
    data = {
        "Tier": ["T1 VIP", "T2 High-Value", "T3 Growth", "T4 First-tx", "T5 Low"],
        "Merch/Shaker": [35, 25, 15, 10, 0],
        "Partner/Event": [40, 5, 0, 0, 0],
        "Samples/Sachet": [10, 20, 40, 45, 5],
        "Early Access": [15, 10, 5, 5, 0],
        "Email Only": [0, 40, 40, 40, 95],
    }
    df = pd.DataFrame(data).set_index("Tier")
    fig, ax = plt.subplots(figsize=(11, 5.5))
    df.plot(kind="barh", stacked=True, ax=ax,
            color=["#E9C46A", "#2A9D8F", "#E76F51", "#264653", "#CAD2C5"])
    ax.set_title("Incentive Mix by Tier — Experiences & Merch, Not % Discounts",
                 fontweight="bold", pad=12)
    ax.set_xlabel("% of retention budget allocation (illustrative)")
    ax.legend(title="Incentive type", bbox_to_anchor=(1.02, 1), loc="upper left")
    # Add "NO % DISCOUNTS" annotation for T1
    ax.annotate("NO % DISCOUNTS\nfor T1 & T2",
                xy=(0, 4), xytext=(40, 3.5),
                fontsize=9, fontweight="bold", color=PALETTE["accent"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff3f0", edgecolor=PALETTE["accent"]))
    # Add per-tier max budget annotation
    budgets = {"T1 VIP": "≤S$26", "T2 High-Value": "≤S$12", "T3 Growth": "≤S$4",
               "T4 First-tx": "≤S$5", "T5 Low": "≤S$1"}
    for i, (tier, budget) in enumerate(budgets.items()):
        ax.text(101, 4 - i, budget, va="center", fontsize=9, color="#555", fontweight="bold")
    ax.text(101, 4.55, "10% cap", va="center", fontsize=8, color="#777", style="italic")
    ax.set_xlim(0, 115)
    fig.tight_layout()
    _save(fig, "r1_incentive_mix_no_discounts.png")


# ── REC 2 CHARTS ─────────────────────────────────────────────────────────────

def chart_r2_category_ladder():
    """Rec 2: Category ladder — focus on 1→3 cats story with strong annotations."""
    cl = pd.read_csv(FINDINGS / "pitch_analysis" / "outputs" / "category_ladder_gp.csv")
    # Focus on 1-4 categories (story lives here)
    cl = cl[cl["n_categories"] <= 4].copy()
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    x_labels = cl["n_categories"].astype(str) + " cat"
    bar_colors = [PALETTE["accent"], PALETTE["T3"], PALETTE["T2"], PALETTE["T1"]]
    bars = ax1.bar(x_labels, cl["avg_gp"], color=bar_colors, alpha=0.88, label="Avg profit margin",
                   edgecolor="white", linewidth=1.5)
    ax1.set_ylabel("Avg profit margin (SGD)", color=PALETTE["T1"])
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"S${v:.0f}"))
    ax1.set_ylim(0, 310)

    ax2 = ax1.twinx()
    ax2.plot(x_labels, cl["repeat_rate"] * 100, color=PALETTE["accent"],
             marker="o", linewidth=2.5, markersize=10, label="Repeat rate", zorder=5)
    ax2.set_ylabel("Repeat rate (%)", color=PALETTE["accent"])
    ax2.set_ylim(0, 100)

    ax1.set_title("Cross-Sell Goal: Move Customers Up the Category Ladder",
                  fontweight="bold", pad=14)
    ax1.set_xlabel("Categories ever purchased")

    # Add n_customers labels on bars
    for i, row in cl.iterrows():
        ax1.text(i, row["avg_gp"] + 6, f"n={int(row['n_customers']):,}",
                 ha="center", fontsize=9, color="#333")

    # Key insight annotations
    rr = cl["repeat_rate"].values * 100
    ax2.annotate(f"{rr[0]:.0f}%\nrepeat", xy=(0, rr[0]), xytext=(0.4, rr[0] + 15),
                 fontsize=10, fontweight="bold", color=PALETTE["accent"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.2))
    ax2.annotate(f"{rr[2]:.0f}%\nrepeat", xy=(2, rr[2]), xytext=(1.6, rr[2] + 10),
                 fontsize=10, fontweight="bold", color=PALETTE["T1"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["T1"], lw=1.2))
    ax2.text(1, 5, "→ 3× repeat rate with 3 categories", ha="center",
             fontsize=9, style="italic", color="#444")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    fig.tight_layout()
    _save(fig, "r2_category_ladder.png")


def chart_r2_cross_sell_timeline():
    """Rec 2: Clear Protein buyer — full timeline including Day 48 Sub offer."""
    days = [0, 14, 44, 54, 62]
    events = [
        "Order 1\n(delivered)",
        "Day 14\nEmail:\nLean Protein",
        "Day 44\nShip sachet\n(Collagen/Lean)",
        "Day 54\nMedian\nreorder",
        "Day 48*\nSub offer\n(after ord 2)",
    ]
    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.set_xlim(-4, 70)
    ax.set_ylim(0, 3.5)
    ax.axhline(1.5, color="#ddd", linewidth=2, zorder=0)
    colors = [PALETTE["T2"], PALETTE["accent"], PALETTE["vip"], PALETTE["T1"], PALETTE["sub"]]

    # plot all 5 events
    for d, ev, c in zip(days, events, colors):
        ax.scatter(d, 1.5, s=280, c=c, zorder=3, edgecolors="white", linewidth=2)
        # alternate label heights to avoid overlap
        y_offset = 32 if days.index(d) % 2 == 0 else -48
        va = "bottom" if y_offset > 0 else "top"
        ax.annotate(ev, (d, 1.5), textcoords="offset points",
                    xytext=(0, y_offset), ha="center", fontsize=9,
                    fontweight="bold", va=va)
        # vertical tick line
        y_sign = 1 if y_offset > 0 else -1
        ax.annotate("", xy=(d, 1.5 + y_sign * 0.12),
                    xytext=(d, 1.5 + y_sign * 0.28),
                    arrowprops=dict(arrowstyle="-", color="#bbb", lw=1))

    ax.annotate("*After 2nd\norder ships", (62, 1.5), textcoords="offset points",
                xytext=(0, -50), ha="center", fontsize=8, color="#666")

    ax.set_yticks([])
    ax.set_xlabel("Days after first delivery", fontsize=11)
    ax.set_title("Clear Protein Buyer — Full Cross-Sell + Subscription Journey",
                 fontweight="bold", pad=16)
    ax.spines[["top", "right", "left"]].set_visible(False)
    note = ("Email cross-sell at day 14  ·  Physical sachet at day 44 (10d before 54d reorder)"
            "  ·  Sub offer after order 2 + 48d  ·  NOT in first order box")
    ax.text(0.5, 0.02, note, transform=ax.transAxes, ha="center",
            fontsize=9, style="italic", color="#444")
    fig.tight_layout()
    _save(fig, "r2_cross_sell_timeline_clear.png")


def chart_r2_four_layers():
    """Rec 2: 4-layer architecture — fixed layout with proper column headers and spacing."""
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Column headers
    ax.text(2.0, 7.2, "Layer", ha="center", fontsize=11, fontweight="bold", color="#333")
    ax.text(5.8, 7.2, "Customer Moment", ha="center", fontsize=11, fontweight="bold", color="#333")
    ax.text(9.2, 7.2, "How Deployed", ha="center", fontsize=11, fontweight="bold", color="#333")
    ax.axhline(7.0, xmin=0.03, xmax=0.97, color="#ccc", linewidth=1)

    layers = [
        ("L1  Rule-based", "1st purchase\n(cold start — 67% one-and-done)", "Post-purchase email\n+ order confirm page", PALETTE["T4"]),
        ("L2  MBA", "Same cart / on PDP", "Shopify 'Frequently Bought\nTogether' widget", PALETTE["T3"]),
        ("L3  Sequential", "Between orders\n(day 14 email, day 44 sachet)", "Automated email flows\nCS-01 to CS-04", PALETTE["accent"]),
        ("L4  Item-CF", "Logged in — 3+ orders\n(proven repeater)", "Account page\n'Recommended for you'", PALETTE["T2"]),
    ]

    y_start = 6.3
    y_step = 1.1
    for i, (title, stage, deploy, col) in enumerate(layers):
        y = y_start - i * y_step
        # layer box
        rect = mpatches.FancyBboxPatch((0.3, y - 0.38), 3.5, 0.82,
                                       boxstyle="round,pad=0.06",
                                       facecolor=col, edgecolor="white", linewidth=2)
        ax.add_patch(rect)
        ax.text(2.05, y + 0.03, title, ha="center", va="center",
                fontweight="bold", color="white", fontsize=11)
        # stage column
        ax.text(5.8, y + 0.03, stage, ha="center", va="center", fontsize=9.5, color="#333")
        # deploy column
        ax.text(9.2, y + 0.03, deploy, ha="center", va="center",
                fontsize=9.5, color="#555")

    # Subscription bar — separate block below layers with clear gap
    sub_y = y_start - 4 * y_step - 0.05
    rect_sub = mpatches.FancyBboxPatch((0.3, sub_y - 0.4), 10.3, 0.82,
                                       boxstyle="round,pad=0.06",
                                       facecolor=PALETTE["sub"], edgecolor="white", linewidth=2)
    ax.add_patch(rect_sub)
    ax.text(5.45, sub_y + 0.02,
            "Subscription Engine  —  SUB-01 fires after order 2 + 48 days  (689 eligible customers)",
            ha="center", va="center", fontweight="bold", color="white", fontsize=11)

    ax.set_title("Recommendation 2 — 4-Layer Engine + Subscription\n"
                 "(One algorithm per lifecycle moment — not one generic Shopify widget)",
                 fontweight="bold", fontsize=13, pad=18)
    fig.tight_layout()
    _save(fig, "r2_four_layer_architecture.png")


def chart_r2_shopify_vs_custom():
    """Rec 2: Capability comparison — with tick/cross annotations."""
    caps = ["Category\ncross-sell", "Timed\njourneys", "PM tier\ntreatment",
            "Sample\ntiming", "Subscription\ntrigger", "VIP\nexperiences"]
    shopify = [2, 1, 1, 0, 2, 1]
    custom = [5, 5, 5, 5, 5, 5]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(caps))
    w = 0.35
    b1 = ax.bar(x - w / 2, shopify, w, label="Shopify recommended products", color="#CAD2C5")
    b2 = ax.bar(x + w / 2, custom, w, label="Lush Protein 4-layer engine", color=PALETTE["T2"])
    ax.set_xticks(x)
    ax.set_xticklabels(caps)
    ax.set_ylabel("Capability score (1–5)")
    ax.set_ylim(0, 7)
    ax.set_title("Why Custom Engine — Data-Proven Patterns Shopify Cannot Use",
                 fontweight="bold", pad=14)
    ax.legend(loc="upper right")
    # add ✓/✗ labels
    check = ["✗", "✗", "✗", "✗", "~", "✗"]
    for i, (s, c, ck) in enumerate(zip(shopify, check, check)):
        ax.text(i - w / 2, shopify[i] + 0.15, ck, ha="center", fontsize=13,
                color="#E76F51", fontweight="bold")
        ax.text(i + w / 2, 5.15, "✓", ha="center", fontsize=13,
                color=PALETTE["sub"], fontweight="bold")
    ax.text(0.5, -0.14,
            "Shopify 'Recommended products' works for Layer 2 (same-cart). "
            "Layers 1, 3, 4 + Sub timing require custom automated email rules from this analysis.",
            transform=ax.transAxes, ha="center", fontsize=9, style="italic", color="#444")
    fig.tight_layout()
    _save(fig, "r2_shopify_vs_custom_engine.png")


def chart_r2_subscription_decile():
    """Rec 2: Subscription rate by profit margin decile — with sub rate labels and VIP note."""
    dec = pd.read_csv(FINALS / "decile_customer_table.csv")
    sub = dec.groupby("contribution_margin_decile").agg(
        sub_rate=("ever_subscribed", "mean"),
        n=("customer_id", "count"),
        avg_pm=("true_gross_profit", "mean"),
    ).reindex([f"D{i}" for i in range(1, 6)])

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(sub))
    x_labels = sub.index.tolist()
    bars = ax1.bar(x_labels, sub["sub_rate"] * 100, color=PALETTE["sub"],
                   alpha=0.8, label="Ever subscribed %", edgecolor="white", linewidth=1.2)
    ax1.set_ylabel("Subscription rate (%)")
    ax1.set_xlabel("Profit margin decile")
    ax1.set_ylim(0, 45)

    # Sub rate labels on bars
    for bar, rate in zip(bars, sub["sub_rate"] * 100):
        ax1.text(bar.get_x() + bar.get_width() / 2, rate + 0.5,
                 f"{rate:.0f}%", ha="center", fontsize=10, fontweight="bold", color=PALETTE["T1"])

    ax2 = ax1.twinx()
    ax2.plot(x_labels, sub["avg_pm"], color=PALETTE["T2"], marker="s",
             linewidth=2, markersize=8, label="Avg profit margin")
    ax2.set_ylabel("Avg profit margin (SGD)")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"S${v:.0f}"))

    ax1.set_title("Subscribers Are Your Best Customers — Sub Rate Tracks Profit Margin",
                  fontweight="bold", pad=14)

    # VIP note
    ax1.annotate("51% of Top 500 VIPs\nalready subscribe",
                 xy=(0, sub["sub_rate"].iloc[0] * 100),
                 xytext=(1.2, sub["sub_rate"].iloc[0] * 100 + 8),
                 fontsize=9, fontweight="bold", color=PALETTE["T1"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["T1"], lw=1.2))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    fig.tight_layout()
    _save(fig, "r2_subscription_by_profit_decile.png")


def chart_r2_sample_by_purchase_stage():
    """Rec 2: Who gets single-serve samples — with tier labels and action notes."""
    stages = ["1st purchase\n(T4 — trial)", "2nd purchase\n(T3 — growing)", "3rd+ / VIP\n(T1 — loyal)"]
    email_day = [14, 7, 0]
    sample_day = [44, 7, 0]
    merch = [0, 0, 1]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(3)
    w = 0.25
    b1 = ax.bar(x - w, email_day, w, label="Email cross-sell (day after delivery)",
                color=PALETTE["accent"])
    b2 = ax.bar(x, sample_day, w, label="Physical sachet (day after delivery)",
                color=PALETTE["vip"])
    b3 = ax.bar(x + w, [0, 0, 1], w, label="Merch/partner gift (T1 only)",
                color=PALETTE["T1"])

    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_ylabel("Days after delivery (email/sachet) or relative unit (merch)")
    ax.set_title("Single-Serve Strategy — Right Intervention at Each Purchase Stage",
                 fontweight="bold", pad=14)
    ax.legend()

    # Action labels
    ax.text(0 - w, email_day[0] + 1.5, "CS-01", ha="center", fontsize=8.5,
            fontweight="bold", color=PALETTE["accent"])
    ax.text(0, sample_day[0] + 1.5, "Collagen\nor Lean", ha="center",
            fontsize=8, color="#555")
    ax.text(1 - w, email_day[1] + 1.5, "CS-04", ha="center", fontsize=8.5,
            fontweight="bold", color=PALETTE["accent"])
    ax.text(2 + w, 0.8, "HYROX\nor event", ha="center", fontsize=8,
            color=PALETTE["T1"], fontweight="bold")

    ax.text(0.5, -0.17,
            "T5 (one-and-done) → email re-activation only  |  No product gifts for T5",
            transform=ax.transAxes, ha="center", fontsize=9,
            style="italic", color="#444")
    fig.tight_layout()
    _save(fig, "r2_sample_by_purchase_stage.png")


def chart_rec2_problem_retention_gap():
    """Rec 2 story: retention gap — all bars annotated, key callout added."""
    cl = pd.read_csv(FINDINGS / "pitch_analysis" / "outputs" / "category_ladder_gp.csv")
    cl = cl[cl["n_categories"] <= 3]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # left: % of pool
    ax = axes[0]
    cats = cl["n_categories"].astype(str) + " cat"
    bars = ax.bar(cats, cl["pct_of_pool"] * 100,
                  color=[PALETTE["accent"], PALETTE["T3"], PALETTE["T2"]],
                  edgecolor="white", linewidth=1.5)
    ax.set_ylabel("% of customer pool")
    ax.set_title("59% of Customers Stuck at 1 Category", fontweight="bold")
    for bar, row in zip(bars, cl.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2, row.pct_of_pool * 100 + 1.5,
                f"{int(row.n_customers):,}\ncustomers",
                ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, 72)
    ax.annotate("67.6% buy\nonce and leave", xy=(0, cl.iloc[0]["pct_of_pool"] * 100),
                xytext=(1.0, 50),
                fontsize=9, color=PALETTE["accent"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.2))

    # right: repeat rate (all three bars annotated)
    ax = axes[1]
    bars2 = ax.bar(cats, cl["repeat_rate"] * 100,
                   color=[PALETTE["accent"], PALETTE["T3"], PALETTE["T2"]],
                   edgecolor="white", linewidth=1.5)
    ax.set_ylabel("Repeat rate (%)")
    ax.set_title("Repeat Rate Triples from 1 → 3 Categories", fontweight="bold")
    ax.set_ylim(0, 68)
    for bar, (_, row) in zip(bars2, cl.iterrows()):
        pct_val = row["repeat_rate"] * 100
        ax.text(bar.get_x() + bar.get_width() / 2, pct_val + 1.5,
                f"{pct_val:.0f}%", ha="center", fontsize=11, fontweight="bold")
    # arrow callout
    ax.annotate("", xy=(2, cl.iloc[2]["repeat_rate"] * 100),
                xytext=(0, cl.iloc[0]["repeat_rate"] * 100),
                arrowprops=dict(arrowstyle="->", color=PALETTE["T1"], lw=2.0))
    ax.text(1, 45, "3.2× higher\nrepeat rate", ha="center", fontsize=10,
            fontweight="bold", color=PALETTE["T1"],
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#eef6fb", edgecolor=PALETTE["T2"]))

    fig.suptitle("The Problem — Customers Don't Discover the Next Category on Their Own",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, "rec2_problem_retention_gap.png")


def chart_rec2_conservative_prize():
    """Rec 2: conservative / base / upside annual GP scenarios."""
    scenarios = [
        ("Conservative\n(3% attach, 3% sub)", 1508 + 1364),
        ("Base case\n(8% 2nd cat, 5% sub)", 3970 + 2262),
        ("Upside\n(5% → 3 cats, 5% sub)", 10693 + 2262),
    ]
    labels = [s[0] for s in scenarios]
    values = [s[1] for s in scenarios]
    colors = [PALETTE["T4"], PALETTE["T2"], PALETTE["sub"]]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels, values, color=colors, edgecolor="white", height=0.55)
    ax.set_xlabel("Modeled annual gross profit uplift (SGD)")
    ax.set_title("Rec 2 Prize — Conservative to Upside (Year 1)\n"
                 "(Cross-sell ladder + subscription — excludes S$14K VIP guardrail)",
                 fontweight="bold", pad=14)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"S${x:,.0f}"))
    for b, v in zip(bars, values):
        ax.text(v + 150, b.get_y() + b.get_height() / 2, f"S${v:,.0f}",
                va="center", fontweight="bold", fontsize=11)
    ax.set_xlim(0, 15500)
    note = ("Conservative: 3% of 2,514 add 2nd cat (S$20 GP uplift) + 3% of 689 subscribe (S$66 GP)\n"
            "Base: H1 8% 2nd category attach + H2 5% sub convert  |  "
            "Upside: H1 5% reach 3 categories + H2 5% sub")
    ax.text(0.5, -0.18, note, transform=ax.transAxes, ha="center",
            fontsize=9, style="italic", color="#444")
    fig.tight_layout()
    _save(fig, "rec2_conservative_prize.png")


def chart_rec2_lifecycle_implementation():
    """Rec 2: one customer journey through layers + subscription — improved circle labels."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(0, 4)
    ax.axis("off")

    stages = [
        (0.5,  "Order 1\n(T4 buyer)",    PALETTE["T4"],    "L1 welcome email\nLean Protein",   "L1"),
        (2.7,  "Browsing\nPDP",          PALETTE["T3"],    "L2 bundle\nPeach + W.Grape",        "L2"),
        (5.0,  "Day 14",                 PALETTE["accent"], "L3 CS-01\nCross-category email",   "L3e"),
        (7.3,  "Day 44",                 PALETTE["vip"],   "L3 sample ship\nCollagen sachet",   "L3s"),
        (9.5,  "Order 2 +\n48 days",     PALETTE["sub"],   "SUB-01\nSubscribe & Save",          "SUB"),
        (11.5, "Order 3+\nlogged in",    PALETTE["T1"],    "L4 account\nPersonalised SKUs",     "L4"),
    ]

    # connecting line
    ax.plot([s[0] for s in stages], [2.1] * len(stages),
            color="#ddd", linewidth=2.5, zorder=0)

    # Layer circles with short tags
    for x, title, col, detail, tag in stages:
        ax.scatter(x, 2.1, s=700, c=col, zorder=3, edgecolors="white", linewidth=2.5)
        ax.text(x, 2.1, tag, ha="center", va="center", fontsize=7.5,
                fontweight="bold", color="white", zorder=4)
        ax.text(x, 2.82, title, ha="center", fontsize=9, fontweight="bold", color="#222",
                linespacing=1.3)
        ax.text(x, 1.28, detail, ha="center", fontsize=8, color="#444", linespacing=1.3)

    # Deployment week callout
    weeks = ["Wk 1–2", "Wk 2–3", "Wk 1–2", "Wk 3–4", "Wk 4–5", "Wk 6+"]
    for (x, _, _, _, _), wk in zip(stages, weeks):
        ax.text(x, 0.65, wk, ha="center", fontsize=7.5, color="#888",
                style="italic")
    ax.text(-0.4, 0.65, "Deploy:", ha="right", fontsize=8, color="#888", style="italic")

    ax.set_title("One Customer Journey — 4 Layers + Subscription (Clear Protein Buyer)",
                 fontweight="bold", fontsize=13, pad=16)
    ax.text(0.5, 0.07,
            "Rec 1 CRM tier determines which layer fires and what incentive is available",
            transform=ax.transAxes, fontsize=9, style="italic", color="#555", ha="center")
    fig.tight_layout()
    _save(fig, "rec2_lifecycle_implementation.png")


def chart_rec2_one_sku_four_layers():
    """Rec 2: same SKU, four valid recommendations — improved with context."""
    demo = pd.read_csv(FINDINGS / "recommendation_systems" / "outputs" / "recommender_comparison_demo.csv")
    row = demo[demo["input_sku"] == "clear-protein|Peach"].iloc[0]

    layers = ["L1 Rule-based\n(welcome email)", "L2 MBA\n(same cart)", "L3 Sequential\n(day 14 email)", "L4 Item-CF\n(account page)"]
    answers = [
        "→ Lean Protein",
        "→ White Grape\n(36% conf.)",
        "→ Lean Protein\n(replenish order 2)",
        "→ W.Grape · Shaker\n· TMT",
    ]
    colors = [PALETTE["T4"], PALETTE["T3"], PALETTE["accent"], PALETTE["T2"]]
    moment = ["At Order 1", "In Cart Now", "Day 14 Email", "Logged-in Account"]

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(4)
    bars = ax.bar(x, [1, 1, 1, 1], color=colors, edgecolor="white", width=0.72)
    ax.set_xticks(x)
    ax.set_xticklabels(layers, fontsize=10)
    ax.set_yticks([])
    ax.set_ylim(0, 1.9)

    for i, (ans, mom) in enumerate(zip(answers, moment)):
        ax.text(i, 0.52, ans, ha="center", va="center",
                fontweight="bold", fontsize=10, color="white", linespacing=1.3)
        ax.text(i, 1.12, mom, ha="center", fontsize=9, color="#333", style="italic")

    ax.set_title("Clear Peach 500g — Four Different Recommendations, All Correct\n"
                 "(Different moments = different algorithms = different answers)",
                 fontweight="bold", pad=14)
    ax.text(0.5, -0.17,
            "Source: recommender_comparison_demo.csv  —  This is why one Shopify widget is not enough",
            transform=ax.transAxes, ha="center", fontsize=9, style="italic", color="#444")
    fig.tight_layout()
    _save(fig, "rec2_one_sku_four_layers.png")


def chart_rec2_v2_entry_repeat():
    """Why L1 rules differ: repeat rate by first-purchase category — improved."""
    cats = ["Collagen Glow", "Lean Protein", "Clear Protein", "Accessories"]
    n = [209, 616, 887, 371]
    repeat = [36.8, 20.8, 19.6, 20.5]
    colors = [PALETTE["sub"], PALETTE["T2"], PALETTE["T3"], PALETTE["accent"]]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(cats, repeat, color=colors, edgecolor="white", linewidth=1.2, width=0.6)
    ax.set_ylabel("Repeat rate (% with 2+ orders)")
    ax.set_title("Layer 1 Insight — First Purchase Category Predicts Repeat Potential",
                 fontweight="bold", pad=14)
    ax.set_ylim(0, 50)
    for b, r, c in zip(bars, repeat, n):
        ax.text(b.get_x() + b.get_width() / 2, r + 1.2,
                f"{r:.0f}%\n(n={c:,})", ha="center", fontsize=10, fontweight="bold")
    ax.axhline(20, color="#999", linestyle="--", linewidth=1,
               label="Protein / accessories baseline ~20%")
    ax.legend(loc="upper right")
    # Collagen insight
    ax.annotate("Collagen-first\nnearby 2× protein rate\n→ recommend protein attach",
                xy=(0, 36.8), xytext=(1.8, 42),
                fontsize=9, color=PALETTE["sub"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=PALETTE["sub"], lw=1.3))
    # Accessories warning
    ax.annotate("Shaker-first = lowest\nretention → recommend\nprotein immediately",
                xy=(3, 20.5), xytext=(2.05, 10),
                fontsize=8.5, color=PALETTE["accent"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.2))
    fig.tight_layout()
    _save(fig, "rec2_v2_entry_category_repeat.png")


def chart_rec2_v2_gantt_clear_journey():
    """Gantt-style Clear Protein buyer journey — REDESIGNED for legibility.

    Fix: original bars (1–4 day widths on 62-day axis) were too narrow to read.
    New approach: labels live LEFT of timeline; bars show WHEN action fires + minimum width.
    """
    fig, ax = plt.subplots(figsize=(14, 6.5))

    # Timeline axis (x = days), row axis (y = action rows)
    DAY_MAX = 64
    LEFT_MARGIN = 0   # days axis starts at 0
    Y_TOP = 7.5
    BAR_H = 0.55
    MIN_BAR_W = 5     # minimum visual bar width in day units

    ax.set_xlim(-22, DAY_MAX + 2)
    ax.set_ylim(0.2, Y_TOP)
    ax.axis("off")

    # Action rows: (row_label, start_day, end_day_for_display, color, right_detail)
    rows = [
        ("Order 1\nDelivered",          0,  MIN_BAR_W,      PALETTE["T4"],    "Customer buys Clear Protein 500g (Peach)"),
        ("L2 — PDP Bundle\n(optional)",  0,  MIN_BAR_W,      PALETTE["T3"],    "Same cart: add White Grape (36% conf.)"),
        ("L1 + L3\nEmail CS-01",        14,  14 + MIN_BAR_W, PALETTE["accent"],"Recommend Lean Protein for order 2"),
        ("L3 Physical\nSachet",         44,  44 + MIN_BAR_W, PALETTE["vip"],   "Collagen/Lean 40g — 10 days before reorder"),
        ("Order 2\n+ SUB-01",           48,  48 + MIN_BAR_W, PALETTE["sub"],   "Subscribe & Save offer"),
        ("Median\nReorder Window",       54,  54 + MIN_BAR_W, "#888888",        "Customer decides to repurchase"),
    ]

    y_positions = [Y_TOP - 0.85 * (i + 1) for i in range(len(rows))]

    for (row_label, start, end, col, detail), y in zip(rows, y_positions):
        # Row label on the LEFT (outside axis)
        ax.text(-1, y, row_label, ha="right", va="center", fontsize=9,
                fontweight="bold", color="#222", linespacing=1.3)

        # Bar
        ax.barh(y, end - start, left=start, height=BAR_H, color=col,
                edgecolor="white", linewidth=1.5, zorder=2, alpha=0.92)

        # Day marker inside/next to bar
        ax.text(start + (end - start) / 2, y, f"Day {start}",
                ha="center", va="center", fontsize=8, color="white",
                fontweight="bold", zorder=3)

        # Detail text on RIGHT
        ax.text(DAY_MAX + 1, y, detail, ha="left", va="center",
                fontsize=8.5, color="#333")

    # Day-marker vertical lines
    for d, dlabel in [(0, "Day 0"), (14, "Day 14"), (44, "Day 44"), (54, "Day 54")]:
        ax.axvline(d, color="#e0e0e0", linewidth=1.0,
                   ymin=0.04, ymax=0.97, zorder=1)
        ax.text(d, 0.55, dlabel, ha="center", fontsize=9,
                color="#666", fontweight="bold")

    ax.set_title("Clear Protein Buyer — When Each Layer Fires (500g, 54-day median reorder)",
                 fontweight="bold", fontsize=13, pad=12,
                 x=0.5, y=0.97, transform=ax.transAxes)

    ax.text(0.5, 0.015,
            "L1+L3 email (Day 14) · Sachet ships Day 44 (10d before reorder) · "
            "SUB-01 fires after Order 2 · L2 optional same-session bundle",
            transform=ax.transAxes, ha="center",
            fontsize=8.5, style="italic", color="#555")

    fig.tight_layout()
    _save(fig, "rec2_v2_gantt_clear_journey.png")


def chart_rec2_v2_pack_reorder_compare():
    """Observed reorder cadence by hero SKU — Layer 3 timing from data."""
    products = ["Clear Protein\n500g hero SKU", "Lean Protein\n1kg hero SKU", "Collagen\n300g hero SKU"]
    median_days = [54, 35, 42]
    sample_day = [44, 25, 32]
    email_day = [14, 14, 21]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(3)
    w = 0.25
    b1 = ax.bar(x - w, median_days, w, label="Median reorder (days)", color=PALETTE["T2"])
    b2 = ax.bar(x, email_day, w, label="Cross-sell email (day)", color=PALETTE["accent"])
    b3 = ax.bar(x + w, sample_day, w, label="Sample ship (day)", color=PALETTE["vip"])
    ax.set_xticks(x)
    ax.set_xticklabels(products)
    ax.set_ylabel("Days after delivery")
    ax.set_title("Layer 3 Timing — Derived from Observed Reorder Cadence\n"
                 "(Email and sample ship BEFORE median reorder to influence decision)",
                 fontweight="bold", pad=14)
    ax.legend(loc="upper right")
    for i, (m, s, e) in enumerate(zip(median_days, sample_day, email_day)):
        gap = m - s
        ax.text(i + w, s + 1.5, f"{gap}d before\nreorder",
                ha="center", fontsize=8, color="#555", fontweight="bold")
        ax.text(i - w, m + 1.5, f"{m}d", ha="center", fontsize=9, color=PALETTE["T2"])
        ax.text(i, e + 1.5, f"Day {e}", ha="center", fontsize=9, color=PALETTE["accent"])
    ax.set_ylim(0, 68)
    fig.tight_layout()
    _save(fig, "rec2_v2_pack_reorder_compare.png")


def chart_rec2_v2_pdp_mockup():
    """Simple PDP widget explainer — what Layer 2 looks like on site."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # outer card
    rect = mpatches.FancyBboxPatch((0.4, 0.8), 9.2, 8.5,
                                   boxstyle="round,pad=0.10",
                                   facecolor="#f8f9fa", edgecolor="#ccc", linewidth=2)
    ax.add_patch(rect)

    # header bar
    hdr = mpatches.FancyBboxPatch((0.4, 8.3), 9.2, 1.05,
                                   boxstyle="round,pad=0.05",
                                   facecolor=PALETTE["T2"], edgecolor="none")
    ax.add_patch(hdr)
    ax.text(5, 8.85, "Product Page (PDP) — Clear Peach 500g",
            ha="center", fontsize=12, fontweight="bold", color="white")

    ax.text(5, 7.8, "Layer 2: Frequently Bought Together widget",
            ha="center", fontsize=10, color=PALETTE["T2"], fontweight="bold")

    lines = [
        ("[✓] Clear Protein — Peach 500g                S$59.90",  "#1B4965"),
        ("[✓] Clear Protein — White Grape 500g          S$54.90",  "#2E86AB"),
        ("[  ] Clear Shaker                             S$12.90",  "#888"),
        ("",                                                        "#888"),
        ("Bundle total:  S$109.70          [Add bundle to cart]",  "#E76F51"),
    ]
    y = 7.15
    for line, col in lines:
        ax.text(1.1, y, line, fontsize=9.5, family="monospace", color=col)
        y -= 0.58

    ax.text(5, 1.5,
            "36% of Clear Peach buyers add White Grape (same order)  —  sku_association_rules.csv",
            ha="center", fontsize=8.5, style="italic", color="#555")
    ax.text(5, 1.05,
            "Same-category bundle only at checkout  ·  Cross-category (Lean/Collagen) = Day 14 email (L3)",
            ha="center", fontsize=8.5, color="#777")

    ax.set_title("What Is a PDP Widget? — Layer 2 in Action on Shopify",
                 fontweight="bold", fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "rec2_v2_pdp_mockup.png")


def chart_combined_impact():
    """NEW: Combined S$30–35K annual GP impact across all sources — waterfall-style."""
    sources = [
        ("VIP guardrail\n(S$14K protected)", 14000, PALETTE["T1"], True),
        ("Category ladder\n→ 2nd category\n(8% attach)", 3969, PALETTE["T3"], False),
        ("Category ladder\n→ 3 categories\n(5% lift)", 10693, PALETTE["T2"], False),
        ("Subscription\n(repeat non-subs)", 2262, PALETTE["sub"], False),
        ("Sub Freq D1\ntier", 1497, PALETTE["sub"], False),
        ("Acquisition\nmix fix (Rec E)", 4389, PALETTE["accent"], False),
    ]

    labels = [s[0] for s in sources]
    values = [s[1] for s in sources]
    colors = [s[2] for s in sources]
    is_protected = [s[3] for s in sources]

    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.bar(range(len(labels)), values, color=colors,
                  edgecolor="white", linewidth=1.5, width=0.65)

    for i, (bar, val, protected) in enumerate(zip(bars, values, is_protected)):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 180,
                f"S${val:,.0f}", ha="center", fontsize=10, fontweight="bold")
        if protected:
            ax.text(bar.get_x() + bar.get_width() / 2, val / 2,
                    "PROTECTED\nNOT earned",
                    ha="center", va="center", fontsize=9,
                    color="white", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="none",
                              edgecolor="white", linewidth=1.5, alpha=0.6))

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("Annual gross profit (SGD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"S${x:,.0f}"))
    ax.set_title("Combined Annual Impact — ~S$30–35K GP/yr\n"
                 "(Conservative conversion assumptions; VIP guardrail = margin protected, not new revenue)",
                 fontweight="bold", pad=14)

    total = sum(values)
    ax.axhline(total / len(values), color="#ccc", linestyle=":", linewidth=1)
    ax.text(len(labels) - 0.5, max(values) * 0.97,
            f"Combined total\nS${total:,.0f}/yr",
            ha="right", fontsize=11, fontweight="bold",
            color=PALETTE["T1"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#eef6fb",
                      edgecolor=PALETTE["T2"], linewidth=1.5))

    # Rec 1 vs Rec 2 bracket (use clip_on=False for text, annotation_clip for annotate)
    ax.annotate("", xy=(0, -1800), xytext=(1, -1800),
                annotation_clip=False,
                arrowprops=dict(arrowstyle="|-|,widthA=0.5,widthB=0.5",
                                color=PALETTE["T1"], lw=1.5))
    ax.text(0.5, -2400, "Rec 1", ha="center", fontsize=9,
            color=PALETTE["T1"], fontweight="bold", clip_on=False)
    ax.annotate("", xy=(1.5, -1800), xytext=(5.5, -1800),
                annotation_clip=False,
                arrowprops=dict(arrowstyle="|-|,widthA=0.5,widthB=0.5",
                                color=PALETTE["T2"], lw=1.5))
    ax.text(3.5, -2400, "Rec 2", ha="center", fontsize=9,
            color=PALETTE["T2"], fontweight="bold", clip_on=False)

    ax.set_ylim(-800, 17000)
    fig.tight_layout()
    _save(fig, "combined_annual_impact.png")


def main():
    print("Building presentation charts ->", OUT)
    # Rec 1
    chart_r1_tier_overview()
    chart_r1_incentive_budgets()
    chart_r1_pm_concentration()
    chart_r1_incentives_not_discounts()
    # Rec 2 — problem + architecture
    chart_r2_category_ladder()
    chart_r2_cross_sell_timeline()
    chart_r2_four_layers()
    chart_r2_shopify_vs_custom()
    chart_r2_subscription_decile()
    chart_r2_sample_by_purchase_stage()
    # Rec 2 — story arc
    chart_rec2_problem_retention_gap()
    chart_rec2_conservative_prize()
    chart_rec2_lifecycle_implementation()
    chart_rec2_one_sku_four_layers()
    # Rec 2 — v2 detail
    chart_rec2_v2_entry_repeat()
    chart_rec2_v2_gantt_clear_journey()
    chart_rec2_v2_pack_reorder_compare()
    chart_rec2_v2_pdp_mockup()
    # Combined impact
    chart_combined_impact()
    print("Done -", len(list(OUT.glob("*.png"))), "charts in outputs/charts/")


if __name__ == "__main__":
    main()
