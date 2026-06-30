"""
Split charts — each chart is a focused standalone slide visual.

Slide 3 splits into 3 charts:
  slide3a_timing_bars.png    — timing by SKU (bar chart)
  slide3b_routing_grid.png   — sample routing as a clean table/grid
  slide3c_evidence.png       — data evidence panel

Slide 4 splits into 2 charts:
  slide4a_pipeline.png       — Shopify data pipeline flow
  slide4b_tier_value.png     — customer tier progression + prize
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


def rbox(ax, x, y, w, h, text, fc, ec=DARK, fs=10, tc=WHITE, bold=False, lw=1.3, va="center"):
    patch = FancyBboxPatch((x - w/2, y - h/2), w, h,
                            boxstyle="round,pad=0.06", facecolor=fc,
                            edgecolor=ec, linewidth=lw, zorder=3, clip_on=False)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va=va, fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", zorder=4,
            linespacing=1.5, clip_on=False)


def arr(ax, x1, y1, x2, y2, color=MID, lw=1.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=12),
                clip_on=False)


# =============================================================================
# SLIDE 3A — Timing Bar Chart
# =============================================================================
def slide3a_timing():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=WHITE)
    ax.set_facecolor(WHITE)

    skus        = ["Soy Protein\n1kg", "Creatine\n250g", "Collagen\n300g", "Lean Protein\n1kg", "Clear Protein\n500g"]
    med_reorder = [84, 66, 42, 35, 54]
    email_day   = [14, 14, 21, 14, 14]
    sample_day  = [74, 55, 32, 25, 44]
    gap_days    = [10, 11, 10, 10, 10]
    bar_colors  = ["#6B7A8D", GOLD, CORAL, TEAL, BLUE]

    y = np.arange(len(skus))
    h = 0.22

    # Reorder window bars (faint background)
    ax.barh(y + h, med_reorder, h * 0.85,
            color=[c + "30" for c in bar_colors], label="Median reorder window")
    # Sample dispatch bars
    ax.barh(y, sample_day, h * 0.85,
            color=[c + "99" for c in bar_colors], label="Sample ships (day after delivery)")
    # Email day bars
    ax.barh(y - h, email_day, h * 0.85,
            color=bar_colors, label="Cross-sell email fires (day after delivery)")

    # Labels inside email bars
    for i, (e, col) in enumerate(zip(email_day, bar_colors)):
        ax.text(e - 0.8, i - h, f"Day {e}", va="center", ha="right",
                fontsize=9, fontweight="bold", color=WHITE)

    # Labels on sample bars
    for i, (s, col) in enumerate(zip(sample_day, bar_colors)):
        ax.text(s + 1.5, i, f"Day {s}", va="center", ha="left",
                fontsize=9, color=DARK)

    # Gap annotations on reorder bars
    for i, (m, s, g) in enumerate(zip(med_reorder, sample_day, gap_days)):
        ax.text(m + 1.5, i + h, f"Reorder: Day {m}  (-{g}d gap)", va="center",
                ha="left", fontsize=9, color=DARK)

    ax.set_yticks(y)
    ax.set_yticklabels(skus, fontsize=11)
    ax.set_xlabel("Days after order delivery", fontsize=11, color=MID)
    ax.tick_params(colors=MID)
    ax.set_xlim(0, 115)
    ax.set_ylim(-0.6, len(skus) - 0.3)

    # Legend
    leg_patches = [
        mpatches.Patch(color=DARK + "30", label="Median reorder window (when they typically reorder)"),
        mpatches.Patch(color=DARK + "99", label="Sample ships (day after delivery)"),
        mpatches.Patch(color=DARK, label="Cross-sell email fires (day after delivery)"),
    ]
    ax.legend(handles=leg_patches, loc="lower right", fontsize=9.5, framealpha=0.9)

    ax.set_title("Layer 3 — Timing by First-Purchase SKU\nSample always dispatched 10 days BEFORE the reorder window",
                 fontsize=14, fontweight="bold", color=DARK, pad=14)

    # Design rule callout
    ax.text(57, -0.52,
            "KEY RULE: Sample does NOT ship in the first order box — it ships separately, arriving right before the customer decides to reorder.",
            ha="center", va="bottom", fontsize=9.5, color=CORAL, fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#FFF3F0", edgecolor=CORAL, lw=1))

    plt.tight_layout()
    plt.savefig(f"{OUT}/slide3a_timing_bars.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide3a_timing_bars.png")


# =============================================================================
# SLIDE 3B — Sample Routing Grid (table layout, no trees)
# =============================================================================
def slide3b_routing():
    fig, ax = plt.subplots(figsize=(15, 8), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis("off")

    fig.suptitle("Layer 3 — Sample Routing: What to Send to Whom\n"
                 "Every rule is derived from D1 co-purchase rates (your best customers' actual behaviour)",
                 fontsize=14, fontweight="bold", color=DARK, y=0.99)

    # Column headers
    col_positions = [1.2, 3.5, 6.1, 9.0, 12.1, 14.3]
    col_labels    = ["First\nPurchase", "Email Day\n& Flow", "Email\nRecommends", "Sample\nShips Day", "Sample\nProduct", "Co-purchase\nEvidence"]
    col_widths    = [2.0, 2.0, 2.8, 1.8, 2.8, 2.2]
    header_y = 7.3

    for cx, lbl, cw in zip(col_positions, col_labels, col_widths):
        rbox(ax, cx, header_y, cw - 0.1, 0.85, lbl, DARK, fs=10, bold=True)

    # Row data
    rows = [
        # (first_cat, email_day+flow, email_rec, sample_day, sample_product, evidence, row_color)
        ("Clear Protein\n500g", "Day 14\n(CS-01)", "Lean TMT 1kg\nor Lean Taro 1kg", "Day 44\n(-10d gap)", "Lean 40g single-serve\nOR Collagen 25g sachet", "53% D1 Clear buyers\nalso buy Lean", BLUE),
        ("Lean Protein\n1kg", "Day 14\n(CS-02)", "Clear Peach 500g\nor Clear White Grape", "Day 25\n(-10d gap)", "Clear 25g sachet\nOR Collagen 25g sachet", "65% D1 Lean buyers\nalso buy Clear", TEAL),
        ("Collagen\nGlow 300g", "Day 21\n(CS-03)", "Clear Peach 500g\n(protein starter)", "Day 32\n(-10d gap)", "Clear 25g sachet\nOR Lean 40g", "30.5% Collagen-first\nrepeat; needs protein attach", CORAL),
        ("Accessories\n(Shaker)", "Day 7\n(CS-04 — URGENT)", "Lean TMT 1kg\n(protein trial)", "Day 25\n(-10d gap)", "Clear 25g sachet\nNOT another shaker", "41% Accessories buyers\nmove to Lean", GOLD),
        ("Soy Protein\n1kg", "Day 14\n(CS-01)", "Clear Peach 500g\n(hero gateway)", "Day 74\n(-10d gap)", "Clear or Lean\n25g/40g single-serve", "Low co-purchase;\npush hero protein", MID),
    ]

    row_ys = [6.1, 5.1, 4.1, 3.1, 2.1]

    for (f_cat, e_day, e_rec, s_day, s_prod, ev, col), ry in zip(rows, row_ys):
        row_vals = [f_cat, e_day, e_rec, s_day, s_prod, ev]
        for cx, val, cw in zip(col_positions, row_vals, col_widths):
            is_first = (val == f_cat)
            fc = col if is_first else (col + "18")
            tc = WHITE if is_first else DARK
            ec = col
            rbox(ax, cx, ry, cw - 0.1, 0.82, val, fc, ec=ec, fs=9, tc=tc, lw=1.0)

    # Post-order-2 flow box at bottom
    rbox(ax, 7.5, 1.0, 14.5, 0.72,
         "After Order 2 fulfilled:  Day 7 email recommends 3rd category  |  Order 2 + 48 days: SUB-01 Subscribe & Save on hero SKU",
         GREEN, fs=10, bold=True)

    # Design rule
    ax.text(7.5, 0.28,
            "KEY DESIGN RULE: Sample ships SEPARATELY — not in first order box. "
            "It arrives 10 days before the reorder window so the customer tries the new category at exactly the right moment.",
            ha="center", va="center", fontsize=9.5, color=DARK,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#FFF3F0", edgecolor=CORAL, lw=1.2))

    plt.savefig(f"{OUT}/slide3b_routing_grid.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide3b_routing_grid.png")


# =============================================================================
# SLIDE 3C — Data Evidence Panel
# =============================================================================
def slide3c_evidence():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor=WHITE)
    fig.suptitle("Layer 3 — Data Evidence: Every Design Decision is Grounded in the Numbers",
                 fontsize=14, fontweight="bold", color=DARK, y=1.01)

    # LEFT: Why not first box + Reorder measurement
    ax = axes[0]
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Why not first box
    rbox(ax, 5, 9.2, 9.5, 0.8, "Why does the sample ship separately — not in the first order box?",
         DARK, fs=11, bold=True)

    reasons = [
        ("Sachet in first box = ignored",
         "Customer is excited about their new product. The sachet sits at the bottom of the bag.\nBy the time they try it, they've already decided whether to reorder."),
        ("Pre-reorder arrival = maximum influence",
         "Day 44 (for Clear Protein buyers): the customer is running low.\nThey're thinking 'what do I reorder?' A Lean TMT sachet arrives.\nThey try it. They add it to the cart."),
        ("The sample doesn't introduce a product — it appears at the decision moment",
         "This timing is not intuitive, but it's what the reorder data supports.\nFounder test: ask Clear Peach buyers if they remember the sachet in box 1."),
    ]
    y_r = 8.2
    for title, body in reasons:
        ax.text(0.3, y_r, f"  {title}", fontsize=10, fontweight="bold", color=CORAL, va="top")
        ax.text(0.5, y_r - 0.32, body, fontsize=9, color=DARK, va="top", linespacing=1.4)
        y_r -= 1.15

    # Reorder measurement
    rbox(ax, 5, 4.65, 9.5, 0.7, "How was the reorder timing measured? (not assumed)", BLUE, fs=11, bold=True)
    method_lines = [
        "1. For each (SKU, customer): collect all order dates for that SKU.",
        "2. Sort the dates. Compute day gaps between consecutive orders using .diff().",
        "3. Take the MEDIAN gap per customer (not mean — handles irregular buyers).",
        "4. Take the MEDIAN across all customers for that SKU.",
        "5. Sample ships: median - 10 days.",
    ]
    y_m = 4.1
    for line in method_lines:
        ax.text(0.4, y_m, line, fontsize=9.5, color=DARK, va="top")
        y_m -= 0.42

    # Cohort table
    cohort_data = [
        ("Clear Peach 500g", "81 repeat buyers", "54 days", "76 days", "Day 44"),
        ("Clear White Grape 500g", "48 repeat buyers", "54 days", "71 days", "Day 44"),
        ("Collagen Glow 300g", "40 repeat buyers", "42 days", "50 days", "Day 32"),
        ("Lean TMT 1kg", "39 repeat buyers", "35 days", "69 days", "Day 25"),
        ("Creatine 250g", "37 repeat buyers", "66 days", "85 days", "Day 55"),
    ]
    headers = ["SKU", "Cohort size", "Median reorder", "Mean reorder", "Sample ships"]
    col_xs  = [1.5, 3.5, 5.5, 7.3, 9.0]
    col_ws  = [2.6, 2.0, 1.8, 1.8, 1.8]

    y_t = 1.95
    colors_row = [BLUE, TEAL, CORAL, TEAL, GOLD]
    for hdr, cx, cw in zip(headers, col_xs, col_ws):
        rbox(ax, cx, y_t, cw - 0.1, 0.45, hdr, DARK, fs=8.5, bold=True, lw=1.0)

    for (sku, n, med, mean, ship), col in zip(cohort_data, colors_row):
        y_t -= 0.52
        row_vals = [sku, n, med, mean, ship]
        for val, cx, cw in zip(row_vals, col_xs, col_ws):
            is_first = (val == sku)
            rbox(ax, cx, y_t, cw - 0.1, 0.42, val, col + "22" if not is_first else col + "55",
                 ec=col, fs=8, tc=DARK, lw=0.8)

    ax.text(5, 0.08, "Median used (not mean): mean is skewed by customers who pause or buy in bulk.",
            ha="center", fontsize=9, color=MID, fontstyle="italic")

    # RIGHT: Co-purchase rates + Category prize
    ax2 = axes[1]
    ax2.set_facecolor(WHITE)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis("off")

    rbox(ax2, 5, 9.2, 9.5, 0.8, "Co-purchase rates — the source of routing rules (D1 customers)", TEAL, fs=11, bold=True)

    co_data = [
        ("If bought Clear Protein", "-> recommend Lean", "53% D1 Clear buyers also buy Lean", BLUE),
        ("If bought Lean Protein", "-> recommend Clear", "65% D1 Lean buyers also buy Clear", TEAL),
        ("If bought Collagen Glow", "-> recommend Clear", "24% attach rate (protein cross-sell)", CORAL),
        ("If bought Accessories", "-> recommend Lean (URGENT)", "41% Accessories -> Lean transition", GOLD),
        ("If bought Soy Protein", "-> recommend Clear (hero SKU)", "Low co-purchase; escalate to gateway", MID),
    ]
    y_c = 8.45
    for trigger, action, evidence, col in co_data:
        ax2.text(0.3, y_c, trigger, fontsize=10, fontweight="bold", color=col, va="top")
        ax2.text(3.5, y_c, action, fontsize=10, color=DARK, va="top", fontweight="bold")
        ax2.text(6.5, y_c, evidence, fontsize=9, color=MID, va="top", fontstyle="italic")
        y_c -= 0.7

    ax2.text(5, 5.0,
             "D1 = top 10% of customers by profit margin.\n"
             "These are the purchase behaviours worth replicating.\n"
             "The rules replicate what your best customers already do naturally.",
             ha="center", va="center", fontsize=10, color=DARK,
             bbox=dict(boxstyle="round,pad=0.4", facecolor=TEAL + "22", edgecolor=TEAL, lw=1.2))

    # Category prize
    rbox(ax2, 5, 4.0, 9.5, 0.8, "The category ladder prize — what L3 is trying to unlock", GREEN, fs=11, bold=True)

    cat_data = [
        ("1 category", "3,681 customers", "13% repeat", "S$64 avg GP", CORAL),
        ("2 categories", "1,411 customers", "30% repeat", "S$92 avg GP", GOLD),
        ("3+ categories", "602 customers", "63% repeat", "S$223 avg GP", GREEN),
    ]
    col_xs2  = [1.0, 3.0, 5.5, 7.8, 9.5]
    col_ws2  = [1.8, 2.0, 2.2, 2.0, 1.5]
    headers2 = ["Categories", "Customers", "Repeat rate", "Avg GP", ""]

    y_cat = 3.4
    for hdr, cx, cw in zip(headers2[:4], col_xs2[:4], col_ws2[:4]):
        rbox(ax2, cx, y_cat, cw - 0.1, 0.45, hdr, DARK, fs=8.5, bold=True, lw=1.0)

    for (cat, n, rep, gp, col) in cat_data:
        y_cat -= 0.6
        for val, cx, cw in zip([cat, n, rep, gp], col_xs2[:4], col_ws2[:4]):
            is_cat = (val == cat)
            rbox(ax2, cx, y_cat, cw - 0.1, 0.48, val,
                 col if is_cat else col + "22",
                 ec=col, fs=9, tc=WHITE if is_cat else DARK, lw=0.8)

    # Prize math
    prize_lines = [
        ("5% of 3,681 reach 2 categories", "43 custs x +S$28 GP",  "+S$1,204 GP/yr", GOLD),
        ("5% of 3,681 reach 3 categories", "184 custs x +S$159 GP", "+S$10,693 GP/yr", GREEN),
        ("Each category step up",           "+S$28 avg GP/customer", "+17pp repeat rate", TEAL),
    ]
    y_p = 1.35
    for scenario, calc, result, col in prize_lines:
        ax2.text(0.3, y_p, scenario, fontsize=9.5, color=DARK, va="top")
        ax2.text(5.5, y_p, calc, fontsize=9, color=MID, va="top")
        ax2.text(7.8, y_p, result, fontsize=10, fontweight="bold", color=col, va="top")
        y_p -= 0.52

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(f"{OUT}/slide3c_evidence.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide3c_evidence.png")


# =============================================================================
# SLIDE 4A — Shopify Pipeline Flow
# =============================================================================
def slide4a_pipeline():
    fig, ax = plt.subplots(figsize=(12, 11), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")
    ax.set_title("Layer 3 — Shopify Data Pipeline\nPhase 1: Live in 4 Weeks, No Custom App Required",
                 fontsize=14, fontweight="bold", color=DARK, pad=12)

    # Step boxes (vertical flow, centred)
    steps = [
        (5, 11.0, 9.0, 1.0, "TRIGGER — Shopify orders/fulfilled webhook",
         "Fires automatically every time an order ships  |  Free, native to Shopify\n"
         "Payload contains: customer_id, SKUs ordered, order date",
         DARK, WHITE),
        (5,  9.5, 9.0, 1.0, "STEP 1 — Data Extraction  (nightly batch job)",
         "Query Shopify Admin API for all fulfilled orders in the last 24 hours\n"
         "Look up each customer's first-ever product category from order history",
         BLUE, WHITE),
        (5,  7.9, 9.0, 1.1, "STEP 2 — Batch Inference  (lookup table — NO machine learning needed)",
         "Input:   first_product_category  (one of 7 values)\n"
         "Lookup:  cross_sell_timing_and_samples.csv  (7 rows, already built)\n"
         "Output:  email_day  |  sample_day  |  recommended_sku  |  sample_sku",
         TEAL, WHITE),
    ]

    for (x, y, w, h, title, body, fc, tc) in steps:
        patch = FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.1", facecolor=fc,
                                edgecolor=fc, linewidth=0, zorder=3, clip_on=False)
        ax.add_patch(patch)
        ax.text(x, y + h/2 - 0.17, title, ha="center", va="top",
                fontsize=10.5, fontweight="bold", color=tc, zorder=4)
        ax.text(x, y - 0.08, body, ha="center", va="center",
                fontsize=9.5, color=tc, zorder=4, linespacing=1.6)

    # Arrows between steps
    arr(ax, 5, 10.50, 5, 10.00)
    arr(ax, 5,  9.00, 5,  8.45)

    # Branching line
    ax.plot([5, 5], [7.35, 6.90], color=MID, lw=1.8, zorder=2)
    ax.plot([1.5, 8.5], [6.90, 6.90], color=MID, lw=1.5, zorder=2)

    # Three output boxes
    outputs = [
        (1.5, 5.9, 2.8, 1.35,
         "OUTPUT A\nEmail Schedule",
         "Add customer to email flow:\nCS-01 / CS-02 / CS-03\n\nEmail fires at Day 14 (or 21\nfor Collagen-first buyers)",
         CORAL),
        (5.0, 5.9, 2.8, 1.35,
         "OUTPUT B\nFulfilment Dispatch Tag",
         "Add Shopify customer tag:\nsample_sku + sample_ship_date\n\nFulfilment team runs daily\nreport & dispatches sachet",
         GOLD),
        (8.5, 5.9, 2.8, 1.35,
         "OUTPUT C\nSubscribe & Save Trigger",
         "After Order 2 fulfilled:\nschedule SUB-01 email\nfor Day 48\n\nOffers Subscribe & Save\non hero SKU",
         GREEN),
    ]
    for (ox, oy, ow, oh, title, body, col) in outputs:
        patch = FancyBboxPatch((ox - ow/2, oy - oh/2), ow, oh,
                                boxstyle="round,pad=0.08", facecolor=col,
                                edgecolor=col, linewidth=0, zorder=3, clip_on=False)
        ax.add_patch(patch)
        ax.text(ox, oy + oh/2 - 0.18, title, ha="center", va="top",
                fontsize=10, fontweight="bold", color=WHITE, zorder=4)
        ax.text(ox, oy - 0.12, body, ha="center", va="center",
                fontsize=9, color=WHITE, zorder=4, linespacing=1.5)
        arr(ax, ox, 6.90, ox, oy + oh/2 + 0.05)

    # Phase roadmap
    phases = [
        (TEAL,  "Phase 1 (Weeks 1-4):",  "L3 cross-sell emails + physical sample dispatch LIVE"),
        (BLUE,  "Phase 2 (Weeks 4-6):",  "L2 'Frequently Bought Together' widget on product pages"),
        (CORAL, "Phase 3 (Weeks 6-10):", "L4 Item-CF personalised recs on logged-in account page"),
    ]
    y_ph = 4.55
    for col, label, desc in phases:
        ax.text(1.0, y_ph, label, fontsize=10, fontweight="bold", color=col, va="center")
        ax.text(3.8, y_ph, desc, fontsize=10, color=DARK, va="center")
        y_ph -= 0.52

    # Tech stack
    stack_title = "Tech Stack — Phase 1  (no custom Shopify app required)"
    ax.text(5, 2.95, stack_title, ha="center", fontsize=11, fontweight="bold", color=DARK)
    stack = [
        ("Shopify webhooks / Admin API", "Native — free"),
        ("7-row lookup table CSV",       "cross_sell_timing_and_samples.csv — already built"),
        ("Email automation platform",    "Klaviyo / Omnisend / Mailchimp — trigger-based flows"),
        ("Shopify customer tags",        "Store first_cat, sample_sku, email_scheduled"),
        ("Shopify Flow app (optional)",  "Free app — automates tag-to-action logic"),
    ]
    col_a_x = 1.3
    col_b_x = 4.5
    y_s = 2.5
    for tool, note in stack:
        ax.text(col_a_x, y_s, f"  {tool}", fontsize=9.5, color=DARK, va="top", fontweight="bold")
        ax.text(col_b_x, y_s, note, fontsize=9.5, color=MID, va="top")
        y_s -= 0.44

    # Box around stack
    stack_box = FancyBboxPatch((0.4, 0.3), 9.2, 2.8,
                                boxstyle="round,pad=0.1", facecolor=LGREY,
                                edgecolor=BLUE, linewidth=1.5, zorder=1)
    ax.add_patch(stack_box)

    ax.text(5, 0.1, "For MVP (Week 1-2): Shopify export -> VLOOKUP on CSV -> email platform import. Zero engineering needed.",
            ha="center", fontsize=9, color=MID, fontstyle="italic")

    plt.tight_layout()
    plt.savefig(f"{OUT}/slide4a_pipeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4a_pipeline.png")


# =============================================================================
# SLIDE 4B — Customer Tier Progression Value
# =============================================================================
def slide4b_tier_value():
    fig, ax = plt.subplots(figsize=(13, 9), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    ax.set_title("Customer Tier Progression — The Business Case for Layer 3",
                 fontsize=14, fontweight="bold", color=DARK, pad=12)

    # Tier rows (5 tiers as clear horizontal bands)
    tiers = [
        ("PLATINUM", 238, "S$388", "85%", "High spend & frequency. Already engaged. Retain & protect.", GOLD, 8.4),
        ("GOLD-A  (Whales)", 130, "S$300", "72%", "Large baskets, infrequent orders. Subscription converts to frequent.", CORAL, 7.1),
        ("GOLD-B  (Loyal Regulars)", 264, "S$105", "54%", "Predictable reorders. Subscription-ready. SUB-01 target.", TEAL, 5.8),
        ("SILVER", 858, "S$100", "45%", "Repeat buyers, single category. L3 cross-sell moves them up.", BLUE, 4.5),
        ("UNTIERED  (new / one-and-done)", 4204, "S$39", "11%", "Entry point. L1 + L3 develop these into Silver-level buyers.", MID, 3.2),
    ]

    for (tier, n, gp, rep, desc, col, yt) in tiers:
        # Band
        band = FancyBboxPatch((0.4, yt - 0.52), 8.8, 1.0,
                               boxstyle="round,pad=0.06", facecolor=col + "22",
                               edgecolor=col, linewidth=2.0, zorder=2)
        ax.add_patch(band)
        # Tier name
        ax.text(0.75, yt + 0.18, tier, fontsize=12, fontweight="bold", color=col, va="center")
        # Stats row
        ax.text(0.75, yt - 0.16,
                f"  {n} customers   |   {gp} avg GP/customer   |   {rep} repeat rate",
                fontsize=10, color=DARK, va="center")
        # Description
        ax.text(0.75, yt - 0.42, f"  {desc}", fontsize=9, color=MID, va="center", fontstyle="italic")

    # Uplift arrows between tiers (right side)
    uplift_data = [
        (7.0, 3.85, BLUE, "L3 Cross-Sell\n(Silver -> Gold-B)",
         "5% of 858 Silver custs move up\n= 43 custs x +S$5 direct GP\nBUT repeat rate: 45% -> 54%\nCompounds over 2-3 years"),
        (7.0, 5.15, TEAL, "Subscribe & Save\n(Gold-B -> Gold-A)",
         "5% of 264 Gold-B custs convert\n= 13 custs x +S$195 GP\n= +S$2,535 GP / yr"),
        (7.0, 6.4, CORAL, "Frequency Drive\n(Gold-A -> Platinum)",
         "Top whales become frequent\nvia subscription compounding"),
    ]
    for (ux, uy, col, title, body) in uplift_data:
        rbox(ax, ux + 2.3, uy, 4.8, 1.0, f"{title}\n{body}", col + "22", ec=col, fs=8.5, tc=DARK, lw=1.2)
        ax.plot([9.2, ux + 0.1], [uy, uy], color=col, lw=1.2, linestyle="--", zorder=2)

    # Big uplift: Untiered -> Silver
    rbox(ax, 9.5, 3.2, 4.8, 0.95,
         "L1 + L3 Entry Drive\n(Untiered -> Silver)\n5% of 4,204 = 210 custs x +S$61 GP\n= +S$12,810 GP/yr",
         BLUE + "22", ec=BLUE, fs=8.5, tc=DARK, lw=1.2)
    ax.plot([9.2, 7.15], [3.2, 3.2], color=BLUE, lw=1.2, linestyle="--")

    # Prize summary box
    prize_lines = [
        ("5% of 3,681 single-cat reach 2 categories",      "+S$2,940 GP/yr",  GOLD),
        ("5% of 3,681 single-cat reach 3 categories",      "+S$10,693 GP/yr", GREEN),
        ("Subscription conversion — SUB-01 (689 targets)", "+S$2,262 GP/yr",  TEAL),
        ("Acquisition mix fix (stop shaker-led)",          "+S$4,389 GP/yr",  BLUE),
        ("CONSERVATIVE TOTAL",                             "S$17 – 30K GP/yr", CORAL),
    ]
    ax.text(6.6, 2.55, "Layer 3 Conservative Prize", fontsize=12,
            fontweight="bold", color=DARK, ha="center")

    prize_box = FancyBboxPatch((4.2, 0.2), 8.6, 2.25,
                                boxstyle="round,pad=0.1", facecolor="#E8F5EE",
                                edgecolor=GREEN, linewidth=2, zorder=2)
    ax.add_patch(prize_box)

    y_pr = 2.15
    for scenario, prize, col in prize_lines:
        is_total = "TOTAL" in scenario
        ax.text(4.45, y_pr, scenario, fontsize=9.5 if not is_total else 11,
                color=DARK, va="top", fontweight="bold" if is_total else "normal")
        ax.text(11.8, y_pr, prize, fontsize=10 if not is_total else 12,
                fontweight="bold", color=col, va="top", ha="right")
        y_pr -= 0.41

    ax.text(6.6, 0.08, "At 5% conversion rates — conservative. Actual lift from timed cross-sell is expected to be higher.",
            ha="center", fontsize=8.5, color=MID, fontstyle="italic")

    plt.tight_layout()
    plt.savefig(f"{OUT}/slide4b_tier_value.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4b_tier_value.png")


if __name__ == "__main__":
    slide3a_timing()
    slide3b_routing()
    slide3c_evidence()
    slide4a_pipeline()
    slide4b_tier_value()
    print("\nAll 5 split charts complete.")
