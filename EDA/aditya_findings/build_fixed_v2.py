"""
Fixed v2: proper spacing for slide3b, slide4a, slide4b
- slide3b: fix last-column text clip
- slide4a: add white gaps between fused step boxes
- slide4b: fix right-side text overflow on tier bands
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


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3B — Routing grid (fix last-column clip)
# ─────────────────────────────────────────────────────────────────────────────
def slide3b_routing():
    fig, ax = plt.subplots(figsize=(16, 8.5), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    fig.suptitle(
        "Layer 3 — Sample Routing: What to Send to Whom\n"
        "Every rule derived from D1 co-purchase rates (your best customers' actual behaviour)",
        fontsize=13, fontweight="bold", color=DARK, y=0.99
    )

    # Column layout — adjusted so last column fits inside xlim=16
    #           x-center  label                width
    cols = [
        (1.10,  "First\nPurchase",      1.90),
        (3.20,  "Email Day\n& Flow",    1.90),
        (5.55,  "Email\nRecommends",    2.50),
        (8.15,  "Sample\nShips Day",    1.80),
        (10.55, "Sample\nProduct",      2.60),
        (13.30, "Co-purchase\nEvidence",2.50),
    ]
    header_y = 7.5
    for cx, lbl, cw in cols:
        patch = FancyBboxPatch((cx - cw/2, header_y - 0.42), cw - 0.12, 0.84,
                                boxstyle="round,pad=0.06", facecolor=DARK,
                                edgecolor=DARK, linewidth=0, zorder=3)
        ax.add_patch(patch)
        ax.text(cx, header_y, lbl, ha="center", va="center",
                fontsize=9.5, fontweight="bold", color=WHITE, zorder=4, linespacing=1.4)

    rows = [
        ("Clear Protein\n500g",    "Day 14\n(CS-01)",        "Lean TMT 1kg\nor Lean Taro 1kg",
         "Day 44\n(-10d gap)",    "Lean 40g single-serve\nOR Collagen 25g sachet",
         "53% of D1 Clear\nbuyers also buy Lean",    BLUE),
        ("Lean Protein\n1kg",      "Day 14\n(CS-02)",        "Clear Peach 500g\nor Clear White Grape",
         "Day 25\n(-10d gap)",    "Clear 25g sachet\nOR Collagen 25g sachet",
         "65% of D1 Lean\nbuyers also buy Clear",    TEAL),
        ("Collagen\nGlow 300g",    "Day 21\n(CS-03)",        "Clear Peach 500g\n(protein starter)",
         "Day 32\n(-10d gap)",    "Clear 25g sachet\nOR Lean 40g",
         "30.5% Collagen-first\nrepeat; needs protein",  CORAL),
        ("Accessories\n(Shaker)",  "Day 7\n(CS-04 URGENT)",  "Lean TMT 1kg\n(protein trial)",
         "Day 25\n(-10d gap)",    "Clear 25g sachet\nNOT another shaker",
         "41% Accessories buyers\nmove to Lean",          GOLD),
        ("Soy Protein\n1kg",       "Day 14\n(CS-01)",        "Clear Peach 500g\n(hero gateway)",
         "Day 74\n(-10d gap)",    "Clear or Lean\n25g/40g single-serve",
         "Low co-purchase;\npush hero protein",           MID),
    ]

    row_ys = [6.35, 5.35, 4.35, 3.35, 2.35]
    row_h  = 0.80

    for (f_cat, e_day, e_rec, s_day, s_prod, ev, col), ry in zip(rows, row_ys):
        vals = [f_cat, e_day, e_rec, s_day, s_prod, ev]
        for idx, (val, (cx, _, cw)) in enumerate(zip(vals, cols)):
            is_first = (idx == 0)
            fc = col       if is_first else (col + "1A")
            tc = WHITE     if is_first else DARK
            ec = col
            patch = FancyBboxPatch((cx - cw/2, ry - row_h/2), cw - 0.12, row_h,
                                    boxstyle="round,pad=0.06", facecolor=fc,
                                    edgecolor=ec, linewidth=1.0, zorder=3)
            ax.add_patch(patch)
            ax.text(cx, ry, val, ha="center", va="center",
                    fontsize=8.8, color=tc, zorder=4, linespacing=1.35)

    # After-Order-2 bar
    bar_y = 1.55
    patch_b = FancyBboxPatch((0.2, bar_y - 0.35), 15.6, 0.70,
                              boxstyle="round,pad=0.06", facecolor=GREEN,
                              edgecolor=GREEN, linewidth=0, zorder=3)
    ax.add_patch(patch_b)
    ax.text(8.0, bar_y,
            "After Order 2 fulfilled:  Day 7 email recommends 3rd category  "
            "|  Order 2 + 48 days: SUB-01 Subscribe & Save on hero SKU",
            ha="center", va="center", fontsize=10, fontweight="bold", color=WHITE, zorder=4)

    # Design rule
    ax.text(8.0, 0.75,
            "KEY DESIGN RULE: Sample ships SEPARATELY — not in first order box. "
            "Arrives 10 days BEFORE reorder so the customer tries the new category at exactly the right moment.",
            ha="center", va="center", fontsize=9, color=CORAL, zorder=4,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3F0", edgecolor=CORAL, lw=1.2))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f"{OUT}/slide3b_routing_grid.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide3b_routing_grid.png")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4A — Shopify Pipeline (fix fused boxes with explicit gaps)
# ─────────────────────────────────────────────────────────────────────────────
def slide4a_pipeline():
    fig, ax = plt.subplots(figsize=(12, 13), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.axis("off")
    fig.suptitle(
        "Layer 3 — Shopify Data Pipeline\nPhase 1: Live in 4 Weeks, No Custom App Required",
        fontsize=14, fontweight="bold", color=DARK, y=1.00
    )

    # Each step box defined with explicit top y in axes coords (0–1)
    # Gap between boxes = GAP (white space)
    LPAD, RPAD = 0.06, 0.94
    GAP = 0.030   # white gap between consecutive step boxes

    step_specs = [
        # (top_y, title, body_lines, fc)
        (0.955, "TRIGGER — Shopify orders/fulfilled webhook",
         ["Fires automatically every time an order ships  |  Free, native to Shopify",
          "Payload: customer_id  |  SKUs ordered  |  order date  |  store"],
         DARK),
        (None,  "STEP 1 — Data Extraction  (nightly batch job)",
         ["Query Shopify Admin API for all fulfilled orders in the last 24 hours",
          "For each customer: look up first-ever product category from order history",
          "Store mapping:  customer_id  ->  first_product_category"],
         BLUE),
        (None,  "STEP 2 — Batch Inference  (lookup table — NO machine learning needed)",
         ["Input:   first_product_category  (7 possible values)",
          "Lookup:  cross_sell_timing_and_samples.csv  (7 rows, already built)",
          "Output:  email_day  |  sample_day  |  recommended_sku  |  sample_sku"],
         TEAL),
    ]

    TITLE_H = 0.038   # height for title line
    LINE_H  = 0.033   # height per body line
    PAD_V   = 0.016   # internal vertical padding (top+bottom)

    def box_height(body_lines):
        return TITLE_H + len(body_lines) * LINE_H + PAD_V * 2

    # First pass: compute tops
    tops = []
    cur_top = step_specs[0][0]
    for i, (ytop, title, body, fc) in enumerate(step_specs):
        if i == 0:
            tops.append(cur_top)
        else:
            prev_h = box_height(step_specs[i-1][2])
            cur_top = tops[-1] - prev_h - GAP
            tops.append(cur_top)

    step_bottoms = []
    for i, ((_, title, body, fc), top) in enumerate(zip(step_specs, tops)):
        h = box_height(body)
        bot = top - h
        step_bottoms.append(bot)
        cx = (LPAD + RPAD) / 2
        cy = top - h / 2

        patch = FancyBboxPatch((LPAD, bot), RPAD - LPAD, h,
                                boxstyle="round,pad=0.008",
                                facecolor=fc, edgecolor=WHITE, linewidth=3,
                                transform=ax.transAxes, zorder=3, clip_on=False)
        ax.add_patch(patch)
        ax.text(cx, top - PAD_V - TITLE_H / 2, title,
                transform=ax.transAxes, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=WHITE, zorder=4)
        y_body = top - PAD_V - TITLE_H - LINE_H / 2
        for line in body:
            ax.text(cx, y_body, line,
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=9.3, color=WHITE, zorder=4)
            y_body -= LINE_H

        # Arrow below (not for last step)
        if i < len(step_specs) - 1:
            arrow_y_top = bot
            arrow_y_bot = bot - GAP
            ax.annotate("",
                        xy=(cx, arrow_y_bot + 0.003),
                        xytext=(cx, arrow_y_top - 0.003),
                        xycoords="axes fraction", textcoords="axes fraction",
                        arrowprops=dict(arrowstyle="-|>", color=MID, lw=2.0, mutation_scale=14))

    # Branch to 3 output boxes
    branch_y = step_bottoms[-1] - GAP
    branch_line_y = branch_y - 0.02
    ax.plot([cx, cx], [step_bottoms[-1], branch_line_y],
            color=MID, lw=2.0, transform=ax.transAxes)
    ax.plot([0.17, 0.83], [branch_line_y, branch_line_y],
            color=MID, lw=1.5, transform=ax.transAxes)

    out_specs = [
        (0.17, CORAL, "OUTPUT A\nEmail Schedule",
         ["CS-01 / CS-02 / CS-03 flows",
          "Email fires at Day 14",
          "(Day 21 for Collagen buyers)"]),
        (0.50, GOLD,  "OUTPUT B\nFulfilment Tag",
         ["Shopify customer tag:",
          "sample_sku + ship_date",
          "Fulfilment dispatches sachet"]),
        (0.83, GREEN, "OUTPUT C\nSubscribe Trigger",
         ["After Order 2 fulfilled:",
          "SUB-01 fires at Day 48",
          "Subscribe & Save offer"]),
    ]
    OW = 0.28
    out_h = TITLE_H * 2 + 3 * LINE_H + PAD_V * 2
    out_top = branch_line_y - 0.018
    out_bot = out_top - out_h

    for (ox, col, title, body) in out_specs:
        ax.annotate("", xy=(ox, out_top + 0.003), xytext=(ox, branch_line_y - 0.003),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=MID, lw=1.4, mutation_scale=10))
        patch = FancyBboxPatch((ox - OW/2, out_bot), OW, out_h,
                                boxstyle="round,pad=0.008",
                                facecolor=col, edgecolor=WHITE, linewidth=3,
                                transform=ax.transAxes, zorder=3, clip_on=False)
        ax.add_patch(patch)
        title_lines = title.split("\n")
        ty = out_top - PAD_V - TITLE_H / 2
        for tl in title_lines:
            ax.text(ox, ty, tl, transform=ax.transAxes, ha="center", va="center",
                    fontsize=9.5, fontweight="bold", color=WHITE, zorder=4)
            ty -= TITLE_H
        ty -= 0.005
        for bl in body:
            ax.text(ox, ty, bl, transform=ax.transAxes, ha="center", va="center",
                    fontsize=8.8, color=WHITE, zorder=4)
            ty -= LINE_H

    # Phase roadmap
    y_ph = out_bot - 0.045
    phases = [
        (TEAL,  "Phase 1 (Weeks 1-4):",  "L3 cross-sell emails + physical sample dispatch LIVE"),
        (BLUE,  "Phase 2 (Weeks 4-6):",  "L2 'Frequently Bought Together' widget on product pages"),
        (CORAL, "Phase 3 (Weeks 6-10):", "L4 Item-CF personalised recs on logged-in account page"),
    ]
    for col, label, desc in phases:
        ax.text(0.07, y_ph, label, transform=ax.transAxes,
                fontsize=10, fontweight="bold", color=col, va="top")
        ax.text(0.33, y_ph, desc, transform=ax.transAxes,
                fontsize=10, color=DARK, va="top")
        y_ph -= 0.042

    # Tech stack
    y_st = y_ph - 0.025
    stack_items = [
        ("Shopify webhooks / Admin API",  "Native — free"),
        ("7-row CSV lookup table",         "cross_sell_timing_and_samples.csv — already built"),
        ("Email automation platform",      "Klaviyo / Omnisend / Mailchimp — trigger-based"),
        ("Shopify customer tags",          "Store first_cat, sample_sku, email_scheduled"),
        ("Shopify Flow (optional)",        "Free Shopify app — automates tag-to-action logic"),
    ]
    stack_h = 0.04 + len(stack_items) * 0.042 + 0.03
    patch_st = FancyBboxPatch((0.05, y_st - stack_h), 0.90, stack_h,
                               boxstyle="round,pad=0.008", facecolor=LGREY,
                               edgecolor=BLUE, linewidth=1.5,
                               transform=ax.transAxes, zorder=2)
    ax.add_patch(patch_st)
    ax.text(0.50, y_st - 0.015, "Tech Stack — Phase 1  (no custom Shopify app required)",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=10.5, fontweight="bold", color=DARK, zorder=4)
    y_si = y_st - 0.054
    for tool, note in stack_items:
        ax.text(0.08, y_si, tool, transform=ax.transAxes,
                fontsize=9.3, fontweight="bold", color=DARK, va="top", zorder=4)
        ax.text(0.43, y_si, note, transform=ax.transAxes,
                fontsize=9.3, color=MID, va="top", zorder=4)
        y_si -= 0.040
    ax.text(0.50, y_st - stack_h + 0.008,
            "MVP shortcut: Shopify CSV export -> VLOOKUP on 7-row table -> email platform import.  Zero engineering.",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, color=MID, style="italic", zorder=4)

    plt.savefig(f"{OUT}/slide4a_pipeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4a_pipeline.png")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4B — Tier Value (fix right overflow and merged text)
# ─────────────────────────────────────────────────────────────────────────────
def slide4b_tier_value():
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.axis("off")
    fig.suptitle("Customer Tier Progression — The Business Case for Layer 3",
                 fontsize=14, fontweight="bold", color=DARK, y=1.00)

    # Column positions (axes coords 0–1)
    # Tier | Customers | Avg GP | Repeat | Characteristics
    C_TIER  = 0.03
    C_N     = 0.26
    C_GP    = 0.38
    C_REP   = 0.49
    C_DESC  = 0.60   # description starts here, runs to 0.97

    col_headers = [
        (C_TIER + 0.09, "Tier"),
        (C_N + 0.04,    "Customers"),
        (C_GP + 0.04,   "Avg GP"),
        (C_REP + 0.03,  "Repeat"),
        (C_DESC + 0.16, "Characteristics & Action"),
    ]

    # Header row
    hdr_y = 0.945
    ax.add_patch(FancyBboxPatch((0.01, hdr_y - 0.028), 0.98, 0.056,
                                 boxstyle="round,pad=0.005", facecolor=DARK,
                                 edgecolor=DARK, linewidth=0,
                                 transform=ax.transAxes, zorder=2))
    for cx, lbl in col_headers:
        ax.text(cx, hdr_y, lbl, transform=ax.transAxes,
                ha="left", va="center", fontsize=10.5, fontweight="bold",
                color=WHITE, zorder=4)
    ax.plot([0.01, 0.99], [hdr_y - 0.032, hdr_y - 0.032],
            color=WHITE, lw=0.5, transform=ax.transAxes)

    tiers = [
        ("PLATINUM",                   238,  "S$388", "85%",
         "High spend & high frequency. Already engaged.", GOLD),
        ("GOLD-A  (Whales)",           130,  "S$300", "72%",
         "Large baskets, infrequent. Subscription lifts frequency.", CORAL),
        ("GOLD-B  (Loyal Regulars)",   264,  "S$105", "54%",
         "Predictable reorders. Subscribe & Save ready — SUB-01 target.", TEAL),
        ("SILVER",                     858,  "S$100", "45%",
         "Repeat buyers stuck at 1 category. L3 introduces category 2.", BLUE),
        ("UNTIERED  (new buyers)", 4204, "S$39",  "11%",
         "Entry point. L1 cold-start + L3 timing builds repeat habit.", MID),
    ]

    BAND_H   = 0.080   # height of each tier band
    GAP_H    = 0.010   # white gap between bands
    start_y  = hdr_y - 0.040  # top of first band

    for i, (tier, n, gp, rep, desc, col) in enumerate(tiers):
        band_top = start_y - i * (BAND_H + GAP_H)
        band_bot = band_top - BAND_H
        band_mid = (band_top + band_bot) / 2

        # Band background
        ax.add_patch(FancyBboxPatch((0.01, band_bot), 0.98, BAND_H,
                                    boxstyle="round,pad=0.005",
                                    facecolor=col + "22", edgecolor=col, linewidth=1.8,
                                    transform=ax.transAxes, zorder=2))

        # Tier name
        ax.text(C_TIER, band_mid, tier,
                transform=ax.transAxes, ha="left", va="center",
                fontsize=10.5, fontweight="bold", color=col, zorder=4)
        # Customer count
        ax.text(C_N, band_mid, f"{n:,}",
                transform=ax.transAxes, ha="left", va="center",
                fontsize=10.5, color=DARK, zorder=4)
        # Avg GP
        ax.text(C_GP, band_mid, gp,
                transform=ax.transAxes, ha="left", va="center",
                fontsize=10.5, color=DARK, zorder=4)
        # Repeat
        ax.text(C_REP, band_mid, rep,
                transform=ax.transAxes, ha="left", va="center",
                fontsize=10.5, color=DARK, zorder=4)
        # Description — font 9.5, stays within 0.60–0.97
        ax.text(C_DESC, band_mid, desc,
                transform=ax.transAxes, ha="left", va="center",
                fontsize=9.5, color=DARK, zorder=4,
                wrap=True)

    # Divider lines between bands (thin, so not confused with borders)
    for i in range(1, len(tiers)):
        dy = start_y - i * (BAND_H + GAP_H) + GAP_H / 2
        ax.plot([0.02, 0.98], [dy, dy],
                color=WHITE, lw=1.0, transform=ax.transAxes, zorder=5)

    # ── Prize summary box ────────────────────────────────────────────────────
    last_band_bot = start_y - len(tiers) * (BAND_H + GAP_H) + GAP_H
    prize_top = last_band_bot - 0.025

    prize_items = [
        ("5% of 3,681 single-cat customers reach 2 categories", "+S$5,152 GP/yr",  GOLD),
        ("5% of 3,681 single-cat customers reach 3 categories", "+S$10,693 GP/yr", GREEN),
        ("Subscribe & Save conversion — SUB-01 (689 targets)",  "+S$2,262 GP/yr",  TEAL),
        ("Acquisition mix fix — stop shaker-led campaigns",     "+S$4,389 GP/yr",  BLUE),
    ]
    prize_line_h = 0.046
    total_line_h = 0.054
    prize_h = 0.04 + len(prize_items) * prize_line_h + 0.012 + total_line_h + 0.025

    ax.add_patch(FancyBboxPatch((0.02, prize_top - prize_h), 0.96, prize_h,
                                 boxstyle="round,pad=0.008", facecolor="#E8F5EE",
                                 edgecolor=GREEN, linewidth=2,
                                 transform=ax.transAxes, zorder=2))

    ax.text(0.50, prize_top - 0.018,
            "Layer 3 Conservative Prize  (5% conversion rate assumption)",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=11.5, fontweight="bold", color=DARK, zorder=4)

    y_p = prize_top - 0.058
    for scenario, prize, col in prize_items:
        ax.text(0.05, y_p, scenario,
                transform=ax.transAxes, ha="left", va="top",
                fontsize=9.8, color=DARK, zorder=4)
        ax.text(0.95, y_p, prize,
                transform=ax.transAxes, ha="right", va="top",
                fontsize=10, fontweight="bold", color=col, zorder=4)
        y_p -= prize_line_h

    ax.plot([0.05, 0.95], [y_p + 0.008, y_p + 0.008],
            color=GREEN, lw=1.2, transform=ax.transAxes, zorder=4)
    y_p -= 0.008

    ax.text(0.05, y_p, "CONSERVATIVE TOTAL",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=12, fontweight="bold", color=DARK, zorder=4)
    ax.text(0.95, y_p, "S$17 – 30K GP/yr",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=14, fontweight="bold", color=CORAL, zorder=4)
    y_p -= total_line_h

    ax.text(0.50, prize_top - prize_h + 0.008,
            "Conservative — at 5% conversion. Actual cross-sell lift expected to be higher.",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, color=MID, style="italic", zorder=4)

    plt.savefig(f"{OUT}/slide4b_tier_value.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4b_tier_value.png")


if __name__ == "__main__":
    slide3b_routing()
    slide4a_pipeline()
    slide4b_tier_value()
    print("\nAll 3 charts fixed and saved.")
