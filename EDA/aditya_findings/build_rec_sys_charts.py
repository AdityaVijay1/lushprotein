"""
build_rec_sys_charts.py — Recommendation-system deep-dive charts.
No platform-brand references (email automation = generic CRM).

Run: python EDA/aditya_findings/build_rec_sys_charts.py
Output: EDA/aditya_findings/outputs/charts/
"""
from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import seaborn as sns

FINDINGS = Path(__file__).resolve().parent
OUT = FINDINGS / "outputs" / "charts"
OUT.mkdir(parents=True, exist_ok=True)
FINALS = FINDINGS.parent / "outputs_finals"
REC_OUT = FINDINGS / "recommendation_systems" / "outputs"

PALETTE = {
    "T1": "#1B4965", "T2": "#2E86AB", "T3": "#5FA8D3", "T4": "#A8DADC", "T5": "#CAD2C5",
    "accent": "#E76F51", "sub": "#2A9D8F", "vip": "#E9C46A",
    "L1": "#A8DADC", "L2": "#5FA8D3", "L3": "#E76F51", "L4": "#1B4965",
}
plt.rcParams.update({
    "figure.dpi": 150, "font.size": 11, "axes.titlesize": 14,
    "axes.labelsize": 11, "figure.facecolor": "white",
    "text.parse_math": False,
})


def _save(fig, name: str):
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {path.name}")


# ── CHART 1: IMPROVED 4-LAYER ARCHITECTURE ───────────────────────────────────

def chart_rec_sys_architecture():
    """Improved 4-layer architecture — lifecycle bar + data proof column, no platform names."""
    fig = plt.figure(figsize=(15, 9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # ── Title ──
    ax.text(7.5, 9.6, "Recommendation 2 — 4-Layer Engine + Subscription",
            ha="center", fontsize=14, fontweight="bold", color="#111")
    ax.text(7.5, 9.2, "One algorithm per customer lifecycle moment  ·  not one generic product widget",
            ha="center", fontsize=10, color="#555", style="italic")

    # ── Lifecycle arrow bar at top ──
    stages = [(0.4, 2.5, "1st Purchase\n(Cold Start)"),
              (3.1, 2.5, "Active Session\n(Browsing)"),
              (5.8, 5.0, "Post-Purchase\n(Between Orders)"),
              (11.1, 2.8, "Logged-in\nRepeat Buyer")]
    arrow_y = 8.5
    ax.annotate("", xy=(14.6, arrow_y), xytext=(0.3, arrow_y),
                arrowprops=dict(arrowstyle="->", color="#aaa", lw=2.5))
    ax.text(0.3, arrow_y + 0.25, "Customer lifecycle", fontsize=9, color="#888")
    stage_x = [1.5, 4.3, 8.3, 12.5]
    stage_col = [PALETTE["L1"], PALETTE["L2"], PALETTE["L3"], PALETTE["L4"]]
    stage_label = ["1st Purchase\n(Cold Start)", "Active Session\n(Browsing)",
                   "Post-Purchase\n(Between Orders)", "Logged-in\nRepeat Buyer"]
    for sx, sc, sl in zip(stage_x, stage_col, stage_label):
        ax.scatter(sx, arrow_y, s=220, c=sc, zorder=3, edgecolors="white", linewidth=2)
        ax.text(sx, arrow_y - 0.45, sl, ha="center", fontsize=8, color="#333", linespacing=1.3)

    # ── Column headers ──
    header_y = 7.0
    ax.axhline(header_y - 0.1, xmin=0.02, xmax=0.98, color="#ccc", lw=1)
    ax.text(1.5, header_y + 0.15, "Layer", ha="center", fontsize=10.5,
            fontweight="bold", color="#333")
    ax.text(5.2, header_y + 0.15, "Customer Moment", ha="center", fontsize=10.5,
            fontweight="bold", color="#333")
    ax.text(9.5, header_y + 0.15, "How Deployed", ha="center", fontsize=10.5,
            fontweight="bold", color="#333")
    ax.text(13.0, header_y + 0.15, "Data Proof", ha="center", fontsize=10.5,
            fontweight="bold", color="#333")

    # ── Layer rows ──
    layers = [
        # (name, moment, deploy, proof, color)
        ("L1  Rule-based\n(Cold Start)",
         "First purchase — no history\n67% of customers are one-and-done",
         "Post-purchase email\n(sent day 1–3 after order)",
         "53% Clear buyers also buy Lean\n65% Lean buyers also buy Clear\n(D1 co-purchase data)",
         PALETTE["L1"]),
        ("L2  Association Rules\n(Market Basket)",
         "Active session — cart or\nproduct page (same order)",
         "Product page bundle widget\nCart drawer 'add both'",
         "36% Peach buyers add White Grape\n93% TMT buyers add Shaker\n(8,955 actual orders)",
         PALETTE["L2"]),
        ("L3  Sequential\n(Timed Journey)",
         "Between orders — before they\ndecide whether to reorder",
         "Post-purchase email flow\nDay 14 (email) + Day 44 (sample)",
         "739 measured 1st→2nd SKU transitions\nClear 54d reorder · Lean 35d reorder\n(order sequence data)",
         PALETTE["L3"]),
        ("L4  Item-Item CF\n(Personalised)",
         "Logged-in repeat buyer\n3+ purchases, proven product fit",
         "Account page module\n'Recommended for you'",
         "83-SKU similarity matrix\nTMT-Taro sim 0.86 · Peach-Grape 0.41\n(cosine similarity, all 4,290 buyers)",
         PALETTE["L4"]),
    ]

    row_y = 6.15
    row_h = 0.95
    for name, moment, deploy, proof, col in layers:
        # layer box
        rect = mpatches.FancyBboxPatch((0.2, row_y - row_h * 0.45), 2.7, row_h * 0.9,
                                       boxstyle="round,pad=0.05",
                                       facecolor=col, edgecolor="white", lw=2)
        ax.add_patch(rect)
        ax.text(1.55, row_y, name, ha="center", va="center",
                fontweight="bold", color="white", fontsize=9.5, linespacing=1.3)
        # moment
        ax.text(5.2, row_y, moment, ha="center", va="center",
                fontsize=9, color="#222", linespacing=1.35)
        # deploy
        ax.text(9.5, row_y, deploy, ha="center", va="center",
                fontsize=9, color="#444", linespacing=1.35)
        # proof (data backed)
        ax.text(13.0, row_y, proof, ha="center", va="center",
                fontsize=8.5, color=PALETTE["T1"], linespacing=1.3)
        # divider
        ax.axhline(row_y - row_h * 0.5, xmin=0.02, xmax=0.98, color="#f0f0f0", lw=0.8)
        row_y -= row_h * 1.05

    # ── Subscription bar — placed below L4 with clear gap ──
    sub_y = row_y - 0.25   # row_y is already decremented past L4
    rect_sub = mpatches.FancyBboxPatch((0.2, sub_y - 0.4), 14.6, 0.82,
                                       boxstyle="round,pad=0.06",
                                       facecolor=PALETTE["sub"], edgecolor="white", lw=2)
    ax.add_patch(rect_sub)
    ax.text(7.5, sub_y + 0.02,
            "Subscribe & Save Engine  —  triggered after 2nd purchase + 48 days  "
            "(689 eligible customers  ·  62% repeat vs 19% for non-subs)",
            ha="center", va="center", fontweight="bold", color="white", fontsize=10.5)

    _save(fig, "r2_four_layer_architecture.png")
    _save(fig, "rec_sys_architecture_v2.png")


# ── CHART 2: WHY 4 LAYERS — COVERAGE PYRAMID ─────────────────────────────────

def chart_rec_sys_why_4_layers():
    """Why 4 layers: coverage + single-model failure modes — two-panel."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ── LEFT: coverage funnel ──
    ax = axes[0]
    layers = ["L1 Rule-based\n(1st purchase)", "L2 MBA\n(browsing session)",
              "L3 Sequential\n(post-purchase)", "L4 Item-CF\n(3+ orders)"]
    pct_reach = [100, 100, 32.4, 17.0]
    n_reach   = [4290, 4290, 1390, 730]
    colors    = [PALETTE["L1"], PALETTE["L2"], PALETTE["L3"], PALETTE["L4"]]
    bars = ax.barh(layers[::-1], pct_reach[::-1], color=colors[::-1],
                   edgecolor="white", height=0.6)
    for b, pct, n in zip(bars, pct_reach[::-1], n_reach[::-1]):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
                f"{pct:.0f}% of customers (~{n:,})",
                va="center", fontsize=9.5, fontweight="bold")
    ax.set_xlim(0, 130)
    ax.set_xlabel("% of 4,290-customer pool reached")
    ax.set_title("Coverage: Why You Need All 4 Layers", fontweight="bold")
    ax.text(0.5, -0.12,
            "L4 alone (CF) would miss 83% of customers — cold-start problem",
            transform=ax.transAxes, ha="center", fontsize=9,
            style="italic", color=PALETTE["accent"])
    ax.spines[["top", "right"]].set_visible(False)

    # ── RIGHT: failure modes if you use only one model ──
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 5.5)
    ax.axis("off")
    ax.set_title("What Breaks If You Use Only One Model", fontweight="bold")

    rows = [
        ("Only collaborative\nfiltering (CF/ML)", PALETTE["accent"],
         "67% have NO history  →  cold-start fail for majority of customers"),
        ("Only association\nrules", PALETTE["T3"],
         "Works for same cart, but completely misses post-order\ncross-sell timing (day 14 email, day 44 sachet)"),
        ("Only rule-based\n(L1 forever)", PALETTE["T4"],
         "Works for first purchase, but never personalises\nrepeat buyers (ignores their actual purchase history)"),
        ("Only post-purchase\nemail", PALETTE["L3"],
         "Misses basket expansion during active session\n(no PDP widget  =  no same-cart upsell)"),
    ]
    y = 4.8
    for label, col, desc in rows:
        rect = mpatches.FancyBboxPatch((0.1, y - 0.42), 3.0, 0.78,
                                       boxstyle="round,pad=0.05",
                                       facecolor=col, edgecolor="white", lw=1.5)
        ax.add_patch(rect)
        ax.text(1.6, y, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="white")
        ax.text(3.4, y, "→", ha="center", va="center",
                fontsize=14, color=PALETTE["accent"], fontweight="bold")
        ax.text(3.8, y, desc, ha="left", va="center",
                fontsize=8.5, color="#333", linespacing=1.3)
        y -= 1.2

    ax.text(5, -0.3, "Solution: match one algorithm to one customer moment",
            ha="center", fontsize=9, fontweight="bold",
            color=PALETTE["T1"],
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#eef6fb",
                      edgecolor=PALETTE["T2"], lw=1.5))

    fig.suptitle("Why a 4-Layer Architecture — Not One Universal Algorithm",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    _save(fig, "rec_sys_why_4_layers.png")


# ── CHART 3: L1 COLD-START PROOF ─────────────────────────────────────────────

def chart_rec_sys_l1_cold_start():
    """L1: co-purchase confidence rates + 'what rules say' visual."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # left: confidence bar chart
    ax = axes[0]
    pairs = [
        ("Clear  →  Lean Protein", 53, PALETTE["L3"]),
        ("Lean  →  Clear Protein", 65, PALETTE["L2"]),
        ("Lean  →  Accessories", 35, PALETTE["T3"]),
        ("Collagen  →  Clear/Lean", 31, PALETTE["T4"]),
        ("Accessories  →  Protein", 21, PALETTE["T5"]),
    ]
    labels = [p[0] for p in pairs]
    values = [p[1] for p in pairs]
    colors = [p[2] for p in pairs]
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1],
                   edgecolor="white", height=0.55)
    for b, v in zip(bars, values[::-1]):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
                f"{v}% co-purchase\n(D1 buyers)", va="center", fontsize=9)
    ax.set_xlim(0, 88)
    ax.set_xlabel("Co-purchase rate among D1 (best) customers")
    ax.set_title("L1 Rules — Built from YOUR Best Customers' Behaviour", fontweight="bold")
    ax.axvline(50, color="#ccc", linestyle="--", lw=1, label="50% threshold")
    ax.legend(loc="lower right", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)

    # right: what the rule card looks like
    ax = axes[1]
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title("What L1 Looks Like in Practice", fontweight="bold")

    # rule cards
    cards = [
        (1.0, 8.0, PALETTE["L2"], "IF: first purchase = Clear Protein",
         "THEN: recommend Lean Protein (TMT or Taro 1kg)",
         "WHY: 53% of top CM buyers bought both  |  WHEN: day 1-3 email"),
        (1.0, 5.0, PALETTE["L3"], "IF: first purchase = Lean Protein",
         "THEN: recommend Clear Protein (Peach or White Grape 500g)",
         "WHY: 65% of top CM buyers bought both  |  WHEN: day 1-3 email"),
        (1.0, 2.0, PALETTE["T4"], "IF: first purchase = Accessories (shaker)",
         "THEN: recommend Protein starter — not another accessory",
         "WHY: protein-first repeats 2x higher than shaker-first  |  WHEN: welcome email"),
    ]
    for cx, cy, col, line1, line2, line3 in cards:
        rect = mpatches.FancyBboxPatch((cx, cy - 1.2), 8, 2.2,
                                       boxstyle="round,pad=0.1",
                                       facecolor="#f8f9fa", edgecolor=col, lw=2)
        ax.add_patch(rect)
        ax.text(cx + 0.3, cy + 0.75, line1, fontsize=9.5, fontweight="bold", color=col)
        ax.text(cx + 0.3, cy + 0.2, line2, fontsize=9, color="#222")
        ax.text(cx + 0.3, cy - 0.4, line3, fontsize=8, color="#666", style="italic")

    fig.suptitle("Layer 1: Rule-Based Cold Start — No History Needed, Evidence-Backed",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    _save(fig, "rec_sys_l1_cold_start.png")


# ── CHART 4: L2 MBA RULES ────────────────────────────────────────────────────

def chart_rec_sys_l2_mba():
    """L2: top MBA rules — confidence, lift, order count bubble chart + deploy context."""
    rules = pd.read_csv(REC_OUT / "sku_association_rules.csv")
    rules["orders"] = rules["support"] * 8955

    # Clean names
    name_map = {
        "0724999810463|Thai Milk Tea": "Lean TMT 1kg",
        "0724999810470|Taro": "Lean Taro 1kg",
        "lushprotein-clear-shaker|White": "Clear Shaker",
        "clear-protein-25g-single-sachet|Peach": "Clear Sachet Peach",
        "clear-protein-25g-single-sachet|White Grape": "Clear Sachet WGrape",
        "lushprotein-lean-protein-40g-single-serve|Taro": "Lean Sachet Taro",
        "lushprotein-lean-protein-40g-single-serve|Thai Milk Tea": "Lean Sachet TMT",
        "clear-protein|Peach": "Clear Peach 500g",
        "clear-protein|White Grape": "Clear WGrape 500g",
    }
    rules["ant_clean"] = rules["antecedent"].map(name_map).fillna(rules["antecedent"])
    rules["con_clean"] = rules["consequent"].map(name_map).fillna(rules["consequent"])
    rules["rule_label"] = rules["ant_clean"] + "\n  → " + rules["con_clean"]

    top = rules.nlargest(8, "confidence")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # left: horizontal bar sorted by confidence
    ax = axes[0]
    colors = [PALETTE["L2"]] * len(top)
    bars = ax.barh(top["rule_label"], top["confidence"] * 100,
                   color=colors, edgecolor="white", height=0.6)
    for b, row in zip(bars, top.itertuples()):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
                f"{row.confidence*100:.0f}%  ({int(row.pair_orders)} orders, lift {row.lift:.1f}x)",
                va="center", fontsize=8.5)
    ax.set_xlim(0, 125)
    ax.set_xlabel("Confidence (% of antecedent buyers who also bought consequent)")
    ax.set_title("L2 Top Association Rules — Same-Cart Co-Purchase", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.5, -0.12,
            "Source: sku_association_rules.csv  —  8,955 actual purchase orders (not views)",
            transform=ax.transAxes, ha="center", fontsize=8.5, style="italic", color="#555")

    # right: bubble chart confidence × lift, sized by orders
    ax = axes[1]
    scatter = ax.scatter(top["confidence"] * 100, top["lift"],
                         s=top["pair_orders"] * 2.5,
                         c=[PALETTE["L2"], PALETTE["L3"], PALETTE["L4"], PALETTE["T1"],
                            PALETTE["T3"], PALETTE["T4"], PALETTE["sub"], PALETTE["vip"]],
                         alpha=0.8, edgecolors="white", linewidth=1.5)
    for _, row in top.iterrows():
        ax.text(row["confidence"] * 100 + 0.5, row["lift"] + 0.5,
                f"{row['ant_clean'][:12]}", fontsize=7.5, color="#444")
    ax.set_xlabel("Confidence (%)")
    ax.set_ylabel("Lift (how much more likely vs random)")
    ax.set_title("Confidence vs Lift — Bubble Size = Order Count", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    # size legend
    for size_val, label in [(100, "~40 orders"), (300, "~120 orders"), (380, "~152 orders")]:
        ax.scatter([], [], s=size_val * 2.5, c="gray", alpha=0.5, label=label)
    ax.legend(title="Order count", loc="upper right", fontsize=8)

    fig.suptitle("Layer 2: Market Basket Analysis — What Goes Together in the Same Cart",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    _save(fig, "rec_sys_l2_mba_rules.png")


# ── CHART 5: L3 TIMING DETAIL ─────────────────────────────────────────────────

def chart_rec_sys_l3_timing():
    """L3: timed journey — reorder windows per SKU + trigger timing matrix."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # left: reorder windows with email/sample timing
    ax = axes[0]
    products = ["Clear Protein\n500g", "Lean Protein\n1kg", "Collagen Glow\n300g", "Creatine\n250g"]
    reorder = [54, 35, 42, 66]
    email_day = [14, 14, 21, 21]
    sample_day = [44, 25, 32, 55]

    x = np.arange(4)
    w = 0.26
    b1 = ax.bar(x - w, reorder, w, label="Median reorder (days)", color=PALETTE["T1"], alpha=0.9)
    b2 = ax.bar(x, email_day, w, label="Email cross-sell fires (day)", color=PALETTE["accent"])
    b3 = ax.bar(x + w, sample_day, w, label="Physical sample ships (day)", color=PALETTE["vip"])

    ax.set_xticks(x)
    ax.set_xticklabels(products)
    ax.set_ylabel("Days after delivery")
    ax.set_title("L3 Timing — From Observed Reorder Data\n(Email and sample fire BEFORE reorder window)",
                 fontweight="bold")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    for i, (r, s) in enumerate(zip(reorder, sample_day)):
        gap = r - s
        ax.text(i + w, s + 1.5, f"{gap}d gap", ha="center", fontsize=8, fontweight="bold",
                color=PALETTE["T1"])

    # right: trigger table as visual grid
    ax = axes[1]
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title("L3 Trigger Rules — What Fires When", fontweight="bold")

    headers = ["Trigger", "Day", "Action", "Goal"]
    col_x = [0.3, 3.2, 4.8, 8.2]
    header_y = 9.3
    for hx, ht in zip(col_x, headers):
        ax.text(hx, header_y, ht, fontsize=9.5, fontweight="bold", color="#333")
    ax.axhline(9.1, xmin=0.02, xmax=0.98, color="#ccc", lw=1)

    rows = [
        ("Order 1\nfulfilled", "Day 14", "Email: recommend\ncross-category\n(CS-01/02/03)", PALETTE["L3"],
         "Drive 2nd category\non order 2"),
        ("Order 2\nfulfilled", "Day 7", "Email: recommend\n3rd category\n(Collagen, new flavour)", PALETTE["L4"],
         "Drive 3rd category\nby order 3"),
        ("Order 2 +\n48 days", "Day 48", "Subscribe & Save\ntrigger email\n(SUB-01)", PALETTE["sub"],
         "Lock replenishment\nafter proven fit"),
        ("Pre-reorder\nwindow", "-10d", "Physical sample\nshipped (sachet)", PALETTE["vip"],
         "Introduce new category\nbefore decision point"),
    ]
    ry = 8.3
    for trigger, day, action, col, goal in rows:
        rect = mpatches.FancyBboxPatch((0.1, ry - 0.85), 2.8, 0.95,
                                       boxstyle="round,pad=0.05",
                                       facecolor=col, edgecolor="white", lw=1.5)
        ax.add_patch(rect)
        ax.text(1.5, ry - 0.35, trigger, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="white")
        ax.text(3.3, ry - 0.35, day, ha="center", va="center",
                fontsize=9, color="#333", fontweight="bold")
        ax.text(4.9, ry - 0.35, action, ha="left", va="center",
                fontsize=8.5, color="#333", linespacing=1.3)
        ax.text(8.3, ry - 0.35, goal, ha="left", va="center",
                fontsize=8.5, color=PALETTE["T1"], linespacing=1.3)
        ax.axhline(ry - 0.95, xmin=0.02, xmax=0.98, color="#f0f0f0", lw=0.7)
        ry -= 1.85

    fig.suptitle("Layer 3: Sequential Timing — Cross-Sell BEFORE the Reorder Window, Not At Checkout",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    _save(fig, "rec_sys_l3_timing_detail.png")


# ── CHART 6: L4 ITEM-CF HEATMAP ───────────────────────────────────────────────

def chart_rec_sys_l4_item_cf():
    """L4: Item-CF similarity heatmap + how it works explanation."""
    cf = pd.read_csv(REC_OUT / "recommender_04_item_similarity_matrix.csv", index_col=0)

    key_skus = [
        "clear-protein|Peach",
        "clear-protein|White Grape",
        "0724999810463|Thai Milk Tea",
        "0724999810470|Taro",
        "collagen-glow|Natural (Unflavoured)",
        "lushprotein-clear-shaker|White",
        "micronized-creatine-monohydrate|250g (50 servings)",
        "clear-protein-25g-single-sachet|Peach",
        "clear-protein-25g-single-sachet|White Grape",
    ]
    name_map = {
        "clear-protein|Peach": "Clear Peach 500g",
        "clear-protein|White Grape": "Clear WGrape 500g",
        "0724999810463|Thai Milk Tea": "Lean TMT 1kg",
        "0724999810470|Taro": "Lean Taro 1kg",
        "collagen-glow|Natural (Unflavoured)": "Collagen Natural",
        "lushprotein-clear-shaker|White": "Clear Shaker",
        "micronized-creatine-monohydrate|250g (50 servings)": "Creatine 250g",
        "clear-protein-25g-single-sachet|Peach": "Sachet Peach 25g",
        "clear-protein-25g-single-sachet|White Grape": "Sachet WGrape 25g",
    }
    available = [s for s in key_skus if s in cf.index]
    sub = cf.loc[available, available].rename(index=name_map, columns=name_map)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # left: heatmap
    ax = axes[0]
    mask = np.eye(len(sub), dtype=bool)
    sns.heatmap(sub, ax=ax, mask=mask, annot=True, fmt=".2f",
                cmap="Blues", vmin=0, vmax=0.5,
                linewidths=0.5, linecolor="#f0f0f0",
                annot_kws={"size": 8})
    ax.set_title("Item-Item CF Similarity Matrix\n(key product SKUs — cosine similarity)",
                 fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=8)

    # right: explanation of how CF works
    ax = axes[1]
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title("How Item-Item CF Works\n(conceptual explanation)", fontweight="bold")

    # Step-by-step boxes
    steps = [
        (PALETTE["T4"], "Step 1 — Build Purchase Matrix",
         "4,290 customers × 83 SKUs\nEach cell = 1 if customer bought that SKU, 0 if not\n"
         "Result: a 4,290-row binary matrix"),
        (PALETTE["T3"], "Step 2 — Compute Cosine Similarity",
         "For each pair of SKUs, compare their purchase vectors\n"
         "Similarity = how often the same customers bought both\n"
         "TMT + Taro: similarity 0.86 (very often bought together)"),
        (PALETTE["L3"], "Step 3 — Build Recommendation Table",
         "For each SKU, rank all other SKUs by similarity score\n"
         "Top-3 most similar = recommendations\n"
         "Clear Peach 500g  →  WGrape (0.41), Shaker (0.22), TMT (0.16)"),
        (PALETTE["T2"], "Step 4 — Deploy on Account Page",
         "When a logged-in customer visits their account:\n"
         "Find their purchase history  →  look up similar items\n"
         "Show top 3-5 'Recommended for you' SKUs"),
    ]
    y = 9.0
    for col, title, body in steps:
        ax.text(0.3, y, title, fontsize=9.5, fontweight="bold", color=col)
        ax.text(0.3, y - 0.5, body, fontsize=8.5, color="#333", linespacing=1.35)
        ax.axhline(y - 1.55, xmin=0.02, xmax=0.98, color="#eee", lw=0.8)
        y -= 2.3

    ax.text(0.3, 0.5,
            "Why item-item not user-user CF:\n"
            "67% of customers only buy once  →  user vectors too sparse for user-user CF\n"
            "Item vectors have enough density (83 active SKUs, 10+ buyers each)",
            fontsize=8.5, color=PALETTE["T1"], linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#eef6fb",
                      edgecolor=PALETTE["T2"], lw=1.2))

    fig.suptitle("Layer 4: Item-Item Collaborative Filtering — Personalised for Repeat Buyers",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    _save(fig, "rec_sys_l4_item_cf_heatmap.png")


# ── CHART 7: IMPLEMENTATION ROADMAP ──────────────────────────────────────────

def chart_rec_sys_roadmap():
    """Phased implementation roadmap — week-by-week Gantt with layer + measure."""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(-2, 11)
    ax.set_ylim(-0.5, 9.5)
    ax.axis("off")

    ax.set_title("Recommendation Engine — 6-Week Implementation Roadmap\n"
                 "(Sequenced by ease of execution and dependency order)",
                 fontweight="bold", fontsize=13, pad=14)

    # Columns: Action | Wk1-2 | Wk2-3 | Wk3-4 | Wk4-5 | Wk5-6+
    col_x = [-1.8, 1.0, 3.0, 5.0, 7.0, 9.0]
    headers = ["Action", "Wk 1–2", "Wk 2–3", "Wk 3–4", "Wk 4–5", "Wk 6+"]
    header_y = 9.1
    for cx, ht in zip(col_x, headers):
        ax.text(cx, header_y, ht, ha="left" if cx < 0 else "center",
                fontsize=10, fontweight="bold", color="#333")
    ax.axhline(8.9, xmin=0.01, xmax=0.99, color="#ccc", lw=1)

    # Rows: (label, start_col, end_col, color, measure)
    # col positions: 1.0=wk1, 3.0=wk2, 5.0=wk3, 7.0=wk4, 9.0=wk6
    rows_data = [
        ("L1 — Post-purchase email\n(rule-based, T4 first buyers)",
         0, 2, PALETTE["L1"], "Email open rate >30%\nCTR 5-8%"),
        ("L3 — Day-14 cross-sell\n(email after order 1)",
         0, 2, PALETTE["L3"], "2nd category attach\n+5pp vs control"),
        ("L2 — PDP bundle widget\n(top 5 revenue SKUs)",
         2, 4, PALETTE["L2"], "Bundle add-to-cart\nrate >10%"),
        ("L3 — Day-44 sachet logistics\n(sample before reorder window)",
         4, 6, PALETTE["L3"], "Sample-to-purchase\nconversion >15%"),
        ("Subscribe & Save trigger\n(order 2 + 48 days, 689 eligible)",
         6, 8, PALETTE["sub"], "Sub conversion\n5% of eligible pool"),
        ("L4 — Account page CF\n(logged-in 3+ order buyers)",
         8, 10, PALETTE["L4"], "Repeat SKU click\nrate >8%"),
    ]

    # col_x index to x position mapping
    cx_map = {0: 1.0, 2: 3.0, 4: 5.0, 6: 7.0, 8: 9.0, 10: 10.8}
    row_h = 0.7
    row_spacing = 1.2
    start_y = 8.2
    bar_left_labels = [-1.8] * len(rows_data)

    for i, (label, cs, ce, col, measure) in enumerate(rows_data):
        y = start_y - i * row_spacing
        # row label on left
        ax.text(-1.8, y, label, ha="left", va="center",
                fontsize=8.5, color="#222", linespacing=1.3)
        # bar spanning columns
        x_start = cx_map[cs]
        x_end = cx_map[ce]
        rect = mpatches.FancyBboxPatch((x_start - 0.85, y - row_h * 0.45),
                                       (x_end - x_start) + 0.85, row_h * 0.88,
                                       boxstyle="round,pad=0.05",
                                       facecolor=col, edgecolor="white", lw=2, alpha=0.85)
        ax.add_patch(rect)
        # measure on right
        ax.text(10.95, y, measure, ha="left", va="center",
                fontsize=7.5, color=PALETTE["T1"], linespacing=1.3)

    # Week column dividers
    for cx in [1.0, 3.0, 5.0, 7.0, 9.0]:
        ax.axvline(cx - 0.95, color="#f0f0f0", lw=1,
                   ymin=0.03, ymax=0.93)

    # Dependency note at bottom
    ax.text(4.5, -0.3,
            "L1+L3 email first (week 1)  →  L2 PDP (week 2)  →  samples + SUB-01 (week 4)  →  L4 personalisation (week 6+)",
            ha="center", fontsize=9, style="italic", color="#555")

    fig.tight_layout()
    _save(fig, "rec_sys_implementation_roadmap.png")


# ── CHART 8: CRM TIER × LAYER MATRIX ─────────────────────────────────────────

def chart_rec_sys_tier_layer_matrix():
    """CRM tier × layer deployment matrix — who gets which recommendation system."""
    tiers = ["T1 VIP\n(500 customers)", "T2 High-Value\n(744 customers)",
             "T3 Growth\n(63 customers)", "T4 First Buyer\n(2,120 customers)",
             "T5 Low Value\n(831 customers)"]
    layers_names = ["L1\nRule", "L2\nMBA", "L3\nSequential", "L4\nItem-CF", "Subscribe\n& Save"]

    # 1 = active, 0.4 = partial/future, 0 = not deployed
    matrix = np.array([
        [0.4, 1.0, 1.0, 1.0, 0.6],   # T1 - has history, L1 if new, L4 main
        [0.4, 1.0, 1.0, 0.8, 1.0],   # T2 - L3 primary, sub conversion target
        [1.0, 1.0, 1.0, 0.4, 0.6],   # T3 - L1+L3 primary, building history
        [1.0, 1.0, 1.0, 0,   0],     # T4 - L1+L3 only, prove fit first
        [0.4, 0,   0.4, 0,   0],     # T5 - win-back email only
    ])

    fig, ax = plt.subplots(figsize=(12, 6.5))

    # Custom colormap: 0=white, 0.4=light, 1=dark
    custom_cmap = plt.cm.get_cmap("Blues")
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1.2, aspect="auto")

    # Cell annotations
    annotations = [
        ["L4 is primary", "PDP widget", "Day-14 email\n+day-44 sample", "Account page\nrecs", "No % discount\nVIP track"],
        ["L3 most important", "PDP widget", "Day-14 email\n+day-44 sample\n+day-7 order 2", "Deploy wk 6+", "SUB-01 primary\nconversion"],
        ["L1 critical", "PDP widget", "CS-04/05\nDay-7 after ord 2", "Future (wk 6+)", "After order 3"],
        ["L1 critical", "PDP widget", "CS-01/02/03\nDay 14", "Not yet\n(no history)", "Not yet\n(prove fit first)"],
        ["Win-back only", "Not deployed", "Light\nre-activation", "Not deployed", "Not deployed"],
    ]

    for i in range(5):
        for j in range(5):
            val = matrix[i, j]
            text_col = "white" if val > 0.7 else ("#333" if val > 0 else "#ccc")
            ax.text(j, i, annotations[i][j], ha="center", va="center",
                    fontsize=7.5, color=text_col, linespacing=1.3,
                    fontweight="bold" if val > 0.8 else "normal")

    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.set_xticklabels(layers_names, fontsize=10)
    ax.set_yticklabels(tiers, fontsize=9.5)
    ax.set_title("CRM Tier × Recommendation Layer — Who Gets Which System",
                 fontweight="bold", pad=14, fontsize=13)
    ax.tick_params(axis="both", which="both", length=0)
    ax.spines[:].set_visible(False)

    # Color legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=custom_cmap(0.85), label="Primary layer for this tier"),
        Patch(facecolor=custom_cmap(0.45), label="Deployed / future deployment"),
        Patch(facecolor="#f0f0f0", edgecolor="#ccc", label="Not deployed for this tier"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.25, 1),
              fontsize=8.5, title="Deployment level")

    fig.tight_layout()
    _save(fig, "rec_sys_tier_layer_matrix.png")


def main():
    print("Building rec-sys charts ->", OUT)
    chart_rec_sys_architecture()     # also updates r2_four_layer_architecture.png
    chart_rec_sys_why_4_layers()
    chart_rec_sys_l1_cold_start()
    chart_rec_sys_l2_mba()
    chart_rec_sys_l3_timing()
    chart_rec_sys_l4_item_cf()
    chart_rec_sys_roadmap()
    chart_rec_sys_tier_layer_matrix()
    print("Done -", len(list(OUT.glob("rec_sys_*.png"))) + 1, "new charts")


if __name__ == "__main__":
    main()
