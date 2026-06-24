"""
Fix for slide3c, slide4a, and slide4b — replaced with cleaner layouts.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "text.parse_math": False,
})

DARK  = "#1C2B3A"
TEAL  = "#2A7F7F"
CORAL = "#E8603C"
GOLD  = "#F0A500"
BLUE  = "#3B6EA5"
GREEN = "#4CAF7D"
LGREY = "#F5F5F5"
MID   = "#94A3B8"
WHITE = "#FFFFFF"
OUT   = "EDA/aditya_findings/outputs/charts"


# =============================================================================
# SLIDE 3C — Data Evidence (clean rewrite)
# =============================================================================
def slide3c_evidence():
    fig, axes = plt.subplots(1, 2, figsize=(16, 9), facecolor=WHITE)
    fig.suptitle("Layer 3 — Data Evidence: Every Design Decision is Grounded in the Numbers",
                 fontsize=14, fontweight="bold", color=DARK, y=1.00)

    # ── LEFT: Why not first box + reorder measurement ──────────────────────
    ax = axes[0]
    ax.set_facecolor(WHITE)
    ax.axis("off")

    # Section 1: Why not in box
    ax.text(0.02, 0.97, "Why does the sample ship separately — not in the first order box?",
            transform=ax.transAxes, fontsize=12, fontweight="bold", color=DARK, va="top")
    ax.plot([0.02, 0.98], [0.935, 0.935], color=CORAL, lw=2, transform=ax.transAxes)

    reasons = [
        ("Sachet in first box = ignored",
         "Customer is excited about their new product. The sachet sits unnoticed.\n"
         "By the time they try it, they've already made their reorder decision."),
        ("Pre-reorder arrival = maximum influence",
         "Day 44 (for Clear Protein buyers): customer is running low on their protein.\n"
         "They're thinking 'what do I reorder?' — then a Lean TMT sachet arrives.\n"
         "They try it. They add it to their next order."),
        ("The sample appears at the decision moment",
         "This is the key insight. The sample doesn't just introduce a product —\n"
         "it shows up at exactly the moment the customer is deciding what to buy next."),
    ]
    y_r = 0.90
    for title, body in reasons:
        ax.text(0.03, y_r, title, transform=ax.transAxes,
                fontsize=10.5, fontweight="bold", color=CORAL, va="top")
        y_r -= 0.04
        ax.text(0.05, y_r, body, transform=ax.transAxes,
                fontsize=9.5, color=DARK, va="top", linespacing=1.5)
        y_r -= 0.095

    # Section 2: How reorder timing was measured
    ax.text(0.02, y_r - 0.01, "How the reorder timing was measured (not assumed)",
            transform=ax.transAxes, fontsize=12, fontweight="bold", color=BLUE, va="top")
    ax.plot([0.02, 0.98], [y_r - 0.048, y_r - 0.048], color=BLUE, lw=2, transform=ax.transAxes)
    y_r -= 0.07

    method = [
        "1.  For each (SKU, customer): collect all order dates for that SKU.",
        "2.  Sort dates. Compute day gaps between consecutive orders using .diff().",
        "3.  Take the MEDIAN gap per customer (handles irregular / bulk buyers).",
        "4.  Take the MEDIAN across all customers for that SKU.",
        "5.  Sample dispatch day = median - 10 days.",
    ]
    for line in method:
        ax.text(0.04, y_r, line, transform=ax.transAxes,
                fontsize=9.5, color=DARK, va="top")
        y_r -= 0.042

    ax.text(0.04, y_r - 0.005,
            "Why median, not mean?  Clear Peach: median=54d vs mean=76d.  "
            "Lean TMT: median=35d vs mean=69d.\n"
            "Mean is skewed by customers who pause or buy in bulk. Median targets the typical buyer.",
            transform=ax.transAxes, fontsize=9, color=MID, va="top", style="italic", linespacing=1.4)
    y_r -= 0.075

    # Cohort table (using regular subplot table via text)
    col_headers = ["SKU", "Buyers", "Median", "Mean", "Sample ships"]
    col_xs_t    = [0.02, 0.32, 0.50, 0.63, 0.77]
    col_ws_t    = [0.27, 0.17, 0.12, 0.12, 0.17]

    row_y = y_r - 0.015
    # Header row
    for hdr, cx in zip(col_headers, col_xs_t):
        ax.text(cx, row_y, hdr, transform=ax.transAxes,
                fontsize=9.5, fontweight="bold", color=WHITE, va="top",
                bbox=dict(boxstyle="round,pad=0.15", facecolor=DARK, edgecolor=DARK))
    row_y -= 0.05

    cohort_data = [
        ("Clear Peach 500g",     "81", "54 days", "76 days", "Day 44", BLUE),
        ("Clear White Grape",    "48", "54 days", "71 days", "Day 44", TEAL),
        ("Collagen Glow 300g",   "40", "42 days", "50 days", "Day 32", CORAL),
        ("Lean TMT 1kg",         "39", "35 days", "69 days", "Day 25", TEAL),
        ("Creatine 250g",        "37", "66 days", "85 days", "Day 55", GOLD),
    ]
    for i, (sku, n, med, mean, ship, col) in enumerate(cohort_data):
        bg = LGREY if i % 2 == 0 else WHITE
        for val, cx, cw in zip([sku, n, med, mean, ship], col_xs_t, col_ws_t):
            is_sku = (val == sku)
            ax.text(cx, row_y, val, transform=ax.transAxes,
                    fontsize=9, color=col if is_sku else DARK, va="top",
                    fontweight="bold" if is_sku else "normal",
                    bbox=dict(boxstyle="square,pad=0.12", facecolor=bg, edgecolor=MID + "55", linewidth=0.5))
        row_y -= 0.042

    # ── RIGHT: Co-purchase rates + Category prize ───────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor(WHITE)
    ax2.axis("off")

    ax2.text(0.02, 0.97, "Co-purchase rates — the source of the routing rules",
             transform=ax2.transAxes, fontsize=12, fontweight="bold", color=TEAL, va="top")
    ax2.plot([0.02, 0.98], [0.935, 0.935], color=TEAL, lw=2, transform=ax2.transAxes)
    ax2.text(0.02, 0.915, "Based on D1 customers (top 10% by profit) — your best customers' actual purchase behaviour.",
             transform=ax2.transAxes, fontsize=9, color=MID, va="top", style="italic")

    co_data = [
        ("Clear Protein", "Lean Protein", "53%", "D1 Clear buyers also buy Lean", BLUE),
        ("Lean Protein",  "Clear Protein", "65%", "D1 Lean buyers also buy Clear", TEAL),
        ("Collagen Glow", "Clear Protein", "24%", "Attach rate — protein cross-sell", CORAL),
        ("Accessories",   "Lean Protein (URGENT)", "41%", "Accessories buyers move to protein", GOLD),
        ("Soy Protein",   "Clear Protein", "10%", "Low co-purchase — push hero gateway SKU", MID),
    ]
    y_c = 0.865
    col_xs_c = [0.02, 0.28, 0.52, 0.60]
    for (bought, reco, pct, note, col) in co_data:
        ax2.text(col_xs_c[0], y_c, f"Bought {bought}", transform=ax2.transAxes,
                 fontsize=10, fontweight="bold", color=col, va="top")
        ax2.text(col_xs_c[1], y_c, f"-> {reco}", transform=ax2.transAxes,
                 fontsize=10, color=DARK, va="top")
        ax2.text(col_xs_c[2], y_c, pct, transform=ax2.transAxes,
                 fontsize=11, fontweight="bold", color=col, va="top")
        ax2.text(col_xs_c[3], y_c, note, transform=ax2.transAxes,
                 fontsize=8.5, color=MID, va="top", style="italic")
        y_c -= 0.065

    # Category prize section
    ax2.text(0.02, y_c - 0.01, "The category ladder prize — what L3 is trying to unlock",
             transform=ax2.transAxes, fontsize=12, fontweight="bold", color=GREEN, va="top")
    ax2.plot([0.02, 0.98], [y_c - 0.048, y_c - 0.048], color=GREEN, lw=2, transform=ax2.transAxes)
    y_c -= 0.07

    # Category table
    cat_col_xs = [0.02, 0.30, 0.50, 0.68]
    cat_headers = ["Categories ever bought", "Customers", "Repeat rate", "Avg GP"]
    for hdr, cx in zip(cat_headers, cat_col_xs):
        ax2.text(cx, y_c, hdr, transform=ax2.transAxes,
                 fontsize=9.5, fontweight="bold", color=WHITE, va="top",
                 bbox=dict(boxstyle="round,pad=0.15", facecolor=DARK, edgecolor=DARK))
    y_c -= 0.05

    cat_rows = [
        ("1 category",    "3,681 (65%)", "13%",  "S$64",  CORAL),
        ("2 categories",  "1,411 (25%)", "30%",  "S$92",  GOLD),
        ("3+ categories", "602 (11%)",   "63%",  "S$223", GREEN),
    ]
    for i, (cat, n, rep, gp, col) in enumerate(cat_rows):
        bg = LGREY if i % 2 == 0 else WHITE
        for val, cx in zip([cat, n, rep, gp], cat_col_xs):
            is_cat = (val == cat)
            ax2.text(cx, y_c, val, transform=ax2.transAxes,
                     fontsize=10, color=col if is_cat else DARK, va="top",
                     fontweight="bold" if is_cat else "normal",
                     bbox=dict(boxstyle="square,pad=0.12", facecolor=bg, edgecolor=MID + "55", linewidth=0.5))
        y_c -= 0.047

    y_c -= 0.02
    ax2.text(0.02, y_c, "What each category step means:", transform=ax2.transAxes,
             fontsize=10, fontweight="bold", color=DARK, va="top")
    y_c -= 0.042
    step_stats = [
        ("+S$28 avg GP per customer", GREEN, "Avg gross profit increase from 1-cat to 2-cat"),
        ("+17 percentage points",     TEAL,  "Repeat rate increase per category added"),
        ("+S$131 avg GP per customer",GREEN, "Avg gross profit increase from 2-cat to 3-cat"),
    ]
    for stat, col, note in step_stats:
        ax2.text(0.04, y_c, stat, transform=ax2.transAxes,
                 fontsize=11, fontweight="bold", color=col, va="top")
        ax2.text(0.38, y_c, note, transform=ax2.transAxes,
                 fontsize=9.5, color=DARK, va="top")
        y_c -= 0.048

    y_c -= 0.015
    prize_entries = [
        ("5% of 3,681 reach 2 categories:", "184 custs x +S$28 = +S$5,152 GP/yr", GOLD),
        ("5% of 3,681 reach 3 categories:", "184 custs x +S$159 = +S$10,693 GP/yr", GREEN),
    ]
    for scenario, result, col in prize_entries:
        ax2.text(0.04, y_c, scenario, transform=ax2.transAxes,
                 fontsize=10, color=DARK, va="top")
        ax2.text(0.55, y_c, result, transform=ax2.transAxes,
                 fontsize=10, fontweight="bold", color=col, va="top")
        y_c -= 0.048

    plt.tight_layout(rect=[0, 0, 1, 0.97], w_pad=3)
    plt.savefig(f"{OUT}/slide3c_evidence.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide3c_evidence.png")


# =============================================================================
# SLIDE 4A — Shopify Pipeline (clean rewrite, no duplicate text in boxes)
# =============================================================================
def slide4a_pipeline():
    fig, ax = plt.subplots(figsize=(12, 11), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.axis("off")
    fig.suptitle("Layer 3 — Shopify Data Pipeline\nPhase 1: Live in 4 Weeks, No Custom App Required",
                 fontsize=14, fontweight="bold", color=DARK, y=1.00)

    # Use transAxes (0-1) coordinates throughout for reliability
    def flow_box(ax, yc, title, body_lines, fc, lpad=0.07, rpad=0.93):
        """Draw a full-width flow step box using axes coordinates."""
        height = 0.055 + len(body_lines) * 0.038
        ytop = yc + height / 2
        ybot = yc - height / 2
        patch = FancyBboxPatch((lpad, ybot), rpad - lpad, height,
                                boxstyle="round,pad=0.01", facecolor=fc,
                                edgecolor=fc, linewidth=0,
                                transform=ax.transAxes, zorder=3, clip_on=False)
        ax.add_patch(patch)
        ax.text(0.5, ytop - 0.018, title, transform=ax.transAxes,
                ha="center", va="top", fontsize=11, fontweight="bold", color=WHITE, zorder=4)
        y_body = ytop - 0.052
        for line in body_lines:
            ax.text(0.5, y_body, line, transform=ax.transAxes,
                    ha="center", va="top", fontsize=9.5, color=WHITE, zorder=4)
            y_body -= 0.036
        return ybot

    def flow_arrow(ax, y):
        ax.annotate("", xy=(0.5, y - 0.014), xytext=(0.5, y + 0.014),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=MID, lw=1.8, mutation_scale=14))

    # Step boxes (top to bottom)
    y = 0.94
    b1 = flow_box(ax, y, "TRIGGER — Shopify orders/fulfilled webhook",
                  ["Fires automatically every time an order ships  |  Free, native to Shopify",
                   "Payload: customer_id, SKUs ordered, order date, store"],
                  DARK)
    flow_arrow(ax, b1)
    y = b1 - 0.055
    b2 = flow_box(ax, y, "STEP 1 — Data Extraction  (nightly batch job)",
                  ["Query Shopify Admin API for all fulfilled orders in the last 24 hours",
                   "For each customer: look up first-ever product category from order history",
                   "Store mapping:  customer_id  ->  first_product_category"],
                  BLUE)
    flow_arrow(ax, b2)
    y = b2 - 0.055
    b3 = flow_box(ax, y, "STEP 2 — Batch Inference  (lookup table — NO machine learning)",
                  ["Input:   first_product_category  (one of 7 values)",
                   "Lookup:  cross_sell_timing_and_samples.csv  (7 rows, already built)",
                   "Output:  email_day  |  sample_day  |  recommended_sku  |  sample_sku"],
                  TEAL)

    # Branch line from STEP 2 to 3 outputs
    y_branch = b3 - 0.03
    ax.plot([0.5, 0.5], [b3, y_branch], color=MID, lw=1.8, transform=ax.transAxes)
    ax.plot([0.17, 0.83], [y_branch, y_branch], color=MID, lw=1.5, transform=ax.transAxes)

    # Three output boxes
    output_specs = [
        (0.17, CORAL, "OUTPUT A\nEmail Schedule",
         ["CS-01 / CS-02 / CS-03 flows",
          "Email fires at Day 14",
          "(Day 21 for Collagen buyers)"]),
        (0.50, GOLD,  "OUTPUT B\nFulfilment Tag",
         ["Shopify customer tag added:",
          "sample_sku + ship_date",
          "Fulfilment dispatches sachet"]),
        (0.83, GREEN, "OUTPUT C\nSubscribe Trigger",
         ["After Order 2 fulfilled:",
          "SUB-01 scheduled Day 48",
          "Subscribe & Save on hero SKU"]),
    ]
    out_top = y_branch - 0.02
    for (cx, col, title, body) in output_specs:
        oh = 0.05 + len(body) * 0.038
        out_bot = out_top - oh
        patch = FancyBboxPatch((cx - 0.15, out_bot), 0.30, oh,
                                boxstyle="round,pad=0.01", facecolor=col,
                                edgecolor=col, linewidth=0,
                                transform=ax.transAxes, zorder=3, clip_on=False)
        ax.add_patch(patch)
        ax.annotate("", xy=(cx, out_top + 0.001), xytext=(cx, y_branch - 0.001),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=MID, lw=1.4, mutation_scale=10))
        # Title (split on newline)
        title_lines = title.split("\n")
        ty = out_top - 0.018
        for tl in title_lines:
            ax.text(cx, ty, tl, transform=ax.transAxes, ha="center", va="top",
                    fontsize=9.5, fontweight="bold", color=WHITE, zorder=4)
            ty -= 0.032
        for bl in body:
            ax.text(cx, ty, bl, transform=ax.transAxes, ha="center", va="top",
                    fontsize=8.5, color=WHITE, zorder=4, linespacing=1.3)
            ty -= 0.030
        out_bottom_y = out_bot

    # Phase roadmap
    y_ph = out_bottom_y - 0.04
    phases = [
        (TEAL,  "Phase 1 (Weeks 1-4):",   "L3 cross-sell emails + physical sample dispatch LIVE"),
        (BLUE,  "Phase 2 (Weeks 4-6):",   "L2 'Frequently Bought Together' widget on product pages"),
        (CORAL, "Phase 3 (Weeks 6-10):",  "L4 Item-CF personalised recs on logged-in account page"),
    ]
    for col, label, desc in phases:
        ax.text(0.07, y_ph, label, transform=ax.transAxes,
                fontsize=10, fontweight="bold", color=col, va="top")
        ax.text(0.32, y_ph, desc, transform=ax.transAxes,
                fontsize=10, color=DARK, va="top")
        y_ph -= 0.042

    # Tech stack box
    y_stack_top = y_ph - 0.02
    stack_items = [
        ("Shopify webhooks / Admin API", "Native — free"),
        ("7-row CSV lookup table",        "cross_sell_timing_and_samples.csv — already built"),
        ("Email automation platform",     "Klaviyo / Omnisend / Mailchimp — trigger-based"),
        ("Shopify customer tags",         "Store first_cat, sample_sku, email_scheduled"),
        ("Shopify Flow (optional)",       "Free Shopify app — automates tag-to-action logic"),
    ]
    stack_height = 0.04 + len(stack_items) * 0.042 + 0.02
    y_stack_bot = y_stack_top - stack_height
    patch_s = FancyBboxPatch((0.05, y_stack_bot), 0.90, stack_height,
                              boxstyle="round,pad=0.01", facecolor=LGREY,
                              edgecolor=BLUE, linewidth=1.5,
                              transform=ax.transAxes, zorder=2)
    ax.add_patch(patch_s)
    ax.text(0.5, y_stack_top - 0.015, "Tech Stack — Phase 1  (no custom Shopify app required)",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=11, fontweight="bold", color=DARK, zorder=4)
    y_si = y_stack_top - 0.055
    for tool, note in stack_items:
        ax.text(0.08, y_si, tool, transform=ax.transAxes,
                fontsize=9.5, fontweight="bold", color=DARK, va="top", zorder=4)
        ax.text(0.42, y_si, note, transform=ax.transAxes,
                fontsize=9.5, color=MID, va="top", zorder=4)
        y_si -= 0.040

    ax.text(0.5, y_stack_bot + 0.008,
            "MVP shortcut: Shopify CSV export  ->  VLOOKUP on the 7-row table  ->  email platform import.  Zero engineering.",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, color=MID, style="italic", zorder=4)

    plt.savefig(f"{OUT}/slide4a_pipeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4a_pipeline.png")


# =============================================================================
# SLIDE 4B — Tier Progression Value (clean rewrite)
# =============================================================================
def slide4b_tier_value():
    fig, ax = plt.subplots(figsize=(13, 10), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.axis("off")
    fig.suptitle("Customer Tier Progression — The Business Case for Layer 3",
                 fontsize=14, fontweight="bold", color=DARK, y=1.00)

    # Tier table (5 rows as bands)
    tiers = [
        ("PLATINUM",                   238, "S$388", "85%", "High spend & frequency. Already engaged. Retain & protect from blanket discounts.", GOLD),
        ("GOLD-A  (Whales)",           130, "S$300", "72%", "Large baskets, infrequent orders. Subscription converts infrequent to regular.", CORAL),
        ("GOLD-B  (Loyal Regulars)",   264, "S$105", "54%", "Predictable reorders. Proven product fit. Subscribe & Save ready — SUB-01 target.", TEAL),
        ("SILVER",                     858, "S$100", "45%", "Repeat buyers stuck at 1 category. L3 cross-sell introduces category 2.", BLUE),
        ("UNTIERED  (new / one-and-done)", 4204, "S$39", "11%", "Entry point. L1 cold-start + L3 timing develops these into Silver-level buyers.", MID),
    ]

    col_xs   = [0.03, 0.27, 0.44, 0.56, 0.65]
    col_hdrs = ["Tier", "Customers", "Avg GP", "Repeat", "Characteristics & Next Step"]
    col_ws   = [0.22, 0.16, 0.11, 0.08, 0.34]

    # Header row
    hdr_y = 0.945
    for hdr, cx in zip(col_hdrs, col_xs):
        ax.text(cx, hdr_y, hdr, transform=ax.transAxes,
                fontsize=10, fontweight="bold", color=WHITE, va="top",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=DARK, edgecolor=DARK))
    ax.plot([0.02, 0.98], [0.918, 0.918], color=DARK, lw=1.5, transform=ax.transAxes)

    tier_ys = [0.865, 0.775, 0.685, 0.595, 0.505]
    for (tier, n, gp, rep, desc, col), ty in zip(tiers, tier_ys):
        # Highlight band
        patch = FancyBboxPatch((0.01, ty - 0.055), 0.98, 0.088,
                                boxstyle="round,pad=0.005", facecolor=col + "22",
                                edgecolor=col, linewidth=1.8,
                                transform=ax.transAxes, zorder=2)
        ax.add_patch(patch)
        row_vals = [tier, str(n), gp, rep, desc]
        for val, cx, cw in zip(row_vals, col_xs, col_ws):
            is_tier = (val == tier)
            ax.text(cx, ty, val, transform=ax.transAxes,
                    fontsize=10 if not is_tier else 11,
                    fontweight="bold" if is_tier else "normal",
                    color=col if is_tier else DARK, va="center")

    # Progression arrows (between relevant tiers)
    arr_data = [
        # (from_tier_y, to_tier_y, label, color)
        (tier_ys[4], tier_ys[3], "L1 + L3: entry buyers\nbecome Silver repeaters", BLUE),
        (tier_ys[3], tier_ys[2], "L3 cross-sell: 1-cat\nSilver -> Gold-B", TEAL),
        (tier_ys[2], tier_ys[1], "SUB-01: regulars\n-> high-value whales", CORAL),
    ]
    ax_x = 0.995
    for (fy, ty, lbl, col) in arr_data:
        mid_y = (fy + ty) / 2
        ax.annotate("", xy=(ax_x - 0.005, ty + 0.015), xytext=(ax_x - 0.005, fy - 0.015),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, mutation_scale=10))

    # Prize box
    prize_top = 0.455
    prize_items = [
        ("5% of 3,681 single-cat customers reach 2 categories", "+S$5,152 GP/yr",  GOLD),
        ("5% of 3,681 single-cat customers reach 3 categories", "+S$10,693 GP/yr", GREEN),
        ("Subscribe & Save conversion — SUB-01 (689 targets)", "+S$2,262 GP/yr",  TEAL),
        ("Acquisition mix fix — stop shaker-led campaigns",     "+S$4,389 GP/yr",  BLUE),
    ]
    prize_height = 0.06 + len(prize_items) * 0.052 + 0.065
    prize_box = FancyBboxPatch((0.02, prize_top - prize_height), 0.96, prize_height,
                                boxstyle="round,pad=0.01", facecolor="#E8F5EE",
                                edgecolor=GREEN, linewidth=2,
                                transform=ax.transAxes, zorder=2)
    ax.add_patch(prize_box)

    ax.text(0.5, prize_top - 0.022, "Layer 3 Conservative Prize (5% conversion rate assumption)",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=12, fontweight="bold", color=DARK, zorder=4)

    y_p = prize_top - 0.072
    for scenario, prize, col in prize_items:
        ax.text(0.06, y_p, scenario, transform=ax.transAxes,
                fontsize=10, color=DARK, va="top", zorder=4)
        ax.text(0.88, y_p, prize, transform=ax.transAxes,
                fontsize=11, fontweight="bold", color=col, va="top", ha="right", zorder=4)
        y_p -= 0.050

    ax.plot([0.06, 0.94], [y_p + 0.008, y_p + 0.008], color=GREEN, lw=1.2, transform=ax.transAxes)
    y_p -= 0.01
    ax.text(0.06, y_p, "CONSERVATIVE TOTAL", transform=ax.transAxes,
            fontsize=12, fontweight="bold", color=DARK, va="top", zorder=4)
    ax.text(0.88, y_p, "S$17 – 30K GP/yr", transform=ax.transAxes,
            fontsize=14, fontweight="bold", color=CORAL, va="top", ha="right", zorder=4)

    ax.text(0.5, prize_top - prize_height + 0.012,
            "At 5% conversion — conservative. Actual lift from timed cross-sell is expected to be higher.",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, color=MID, style="italic", zorder=4)

    plt.savefig(f"{OUT}/slide4b_tier_value.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4b_tier_value.png")


if __name__ == "__main__":
    slide3c_evidence()
    slide4a_pipeline()
    slide4b_tier_value()
    print("\nAll 3 fixed charts complete.")
