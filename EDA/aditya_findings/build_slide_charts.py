"""
Build slide charts for 4-slide recommendation presentation.
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
OUT   = "EDA/aditya_findings/outputs/charts"


# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Slide 1: Problem Statement (3 panels)
# ─────────────────────────────────────────────────────────────────────────────
def chart_slide1_problem():
    fig, axes = plt.subplots(1, 3, figsize=(16, 7), facecolor="white")
    fig.suptitle(
        "The Three Retention Gaps - Why Lush Protein Needs a Recommendation Engine",
        fontsize=15, fontweight="bold", color=DARK, y=1.01
    )

    # Panel 1: One-and-done
    ax = axes[0]
    ax.set_facecolor("white")
    labels = ["Buy Once\n(77.3%)", "Come Back\n(22.7%)"]
    values = [77.3, 22.7]
    colors = [CORAL, TEAL]
    bars = ax.bar(labels, values, color=colors, width=0.5, zorder=3)
    ax.set_ylim(0, 105)
    ax.set_ylabel("% of all customers", color=MID, fontsize=10)
    ax.tick_params(colors=MID)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2,
                f"{val}%", ha="center", va="bottom", fontsize=20, fontweight="bold",
                color=bar.get_facecolor())
    ax.text(0, 40, "Founder's\n#1 worry", ha="center", va="center",
            fontsize=10, color="white", fontweight="bold")
    ax.set_title("Gap 1 - Retention\n5,694 total customers", fontsize=12,
                 fontweight="bold", color=DARK, pad=12)

    # Panel 2: Category ladder
    ax = axes[1]
    ax.set_facecolor("white")
    cat_labels = ["1 category\n3,681 customers\n65%", "2 categories\n1,411 customers\n25%", "3+ categories\n602 customers\n11%"]
    repeat_rates = [13, 30, 63]
    gps = [64, 92, 223]
    x = np.arange(len(cat_labels))
    w = 0.35
    cols_cat = [CORAL, GOLD, GREEN]
    b1 = ax.bar(x - w/2, repeat_rates, w, color=cols_cat, label="Repeat rate (%)", zorder=3)
    ax2r = ax.twinx()
    b2 = ax2r.bar(x + w/2, gps, w, color=[c + "77" for c in cols_cat], label="Avg GP (S$)", zorder=3)
    ax.set_ylim(0, 90)
    ax2r.set_ylim(0, 340)
    ax.set_ylabel("Repeat rate (%)", color=MID, fontsize=10)
    ax2r.set_ylabel("Avg gross profit (S$)", color=MID, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, fontsize=9, linespacing=1.5)
    ax.tick_params(colors=MID)
    ax2r.tick_params(colors=MID)
    ax2r.spines["right"].set_visible(True)
    ax2r.spines["right"].set_color(MID)
    for bar, val in zip(b1, repeat_rates):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.5,
                f"{val}%", ha="center", fontsize=12, fontweight="bold", color=DARK)
    for bar, val in zip(b2, gps):
        ax2r.text(bar.get_x() + bar.get_width()/2, val + 5,
                  f"S${val}", ha="center", fontsize=10, color=DARK)
    ax.set_title("Gap 2 - Category Depth\n65% stuck at one product type", fontsize=12,
                 fontweight="bold", color=DARK, pad=12)

    # Panel 3: Subscriber gap
    ax = axes[2]
    ax.set_facecolor("white")
    seg_labels = ["Subscribers\n(713 custs)", "Non-subscribers\n(4,981)"]
    rep_vals = [62, 17]
    gp_vals = [134, 81]
    cols3 = [TEAL, CORAL]
    bars3 = ax.bar(seg_labels, rep_vals, color=cols3, width=0.45, zorder=3)
    ax.set_ylim(0, 90)
    ax.set_ylabel("Repeat rate (%)", color=MID, fontsize=10)
    ax.tick_params(colors=MID)
    for bar, rv, gv in zip(bars3, rep_vals, gp_vals):
        ax.text(bar.get_x() + bar.get_width()/2, rv + 1.5,
                f"{rv}%", ha="center", fontsize=20, fontweight="bold",
                color=bar.get_facecolor())
        ax.text(bar.get_x() + bar.get_width()/2, rv / 2,
                f"Avg GP\nS${gv}", ha="center", fontsize=9, color="white", fontweight="bold")
    ax.annotate("", xy=(1, 17), xytext=(0, 62),
                arrowprops=dict(arrowstyle="<->", color=DARK, lw=1.5))
    ax.text(0.5, 42, "3.6x repeat\ngap", ha="center", fontsize=10,
            fontweight="bold", color=DARK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=LGREY, edgecolor=DARK, lw=1))
    ax.set_title("Gap 3 - Subscription\nSubscribers 3.6x more likely to return", fontsize=12,
                 fontweight="bold", color=DARK, pad=12)

    plt.tight_layout(rect=[0, 0.02, 1, 1])
    plt.savefig(f"{OUT}/slide1_problem_statement.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide1_problem_statement.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Slide 3: L3 Complete
# ─────────────────────────────────────────────────────────────────────────────
def draw_box(ax, x, y, w, h, text, fc, ec=DARK, fs=9, tc="white", bold=False, alpha=1.0):
    patch = FancyBboxPatch((x - w/2, y - h/2), w, h,
                            boxstyle="round,pad=0.07", facecolor=fc,
                            edgecolor=ec, linewidth=1.2, zorder=3, alpha=alpha)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", zorder=4, linespacing=1.4)

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=MID, lw=1.4, connectionstyle="arc3,rad=0"))


def chart_slide3_l3_complete():
    fig = plt.figure(figsize=(18, 9), facecolor="white")
    fig.suptitle("Layer 3: Sequential Timing Engine — What to Send, When, and to Whom",
                 fontsize=15, fontweight="bold", color=DARK, y=0.99)

    # ── LEFT panel: timing bar chart ──────────────────────────────────────────
    ax_bar = fig.add_subplot(1, 3, 1)
    ax_bar.set_facecolor("white")

    skus = ["Clear Protein\n500g", "Lean Protein\n1kg", "Collagen\n300g", "Creatine\n250g", "Soy Protein\n1kg"]
    med_reorder = [54, 35, 42, 66, 84]
    email_day   = [14, 14, 21, 14, 14]
    sample_day  = [44, 25, 32, 55, 74]
    y_pos = np.arange(len(skus))
    h = 0.24
    bar_colors = [BLUE, TEAL, CORAL, GOLD, MID]

    ax_bar.barh(y_pos + h, med_reorder, h * 0.85, color=[c + "44" for c in bar_colors], label="Median reorder")
    ax_bar.barh(y_pos,     sample_day,  h * 0.85, color=[c + "BB" for c in bar_colors], label="Sample ships (day)")
    ax_bar.barh(y_pos - h, email_day,   h * 0.85, color=bar_colors, label="Email fires (day)")

    for i, (m, s) in enumerate(zip(med_reorder, sample_day)):
        ax_bar.text(m + 1.5, i + h, f"-{m-s}d gap", fontsize=8, color=DARK, va="center")
    for i, e in enumerate(email_day):
        ax_bar.text(e + 1.5, i - h, f"Day {e}", fontsize=8, color="white" if False else DARK, va="center",
                    fontweight="bold")

    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(skus, fontsize=9.5)
    ax_bar.set_xlabel("Days after delivery", color=MID)
    ax_bar.tick_params(colors=MID)
    ax_bar.set_xlim(0, 104)
    ax_bar.legend(loc="lower right", fontsize=8, framealpha=0.8)
    ax_bar.set_title("Timing by First-Purchase SKU\n(Sample fires 10d before reorder window)",
                     fontsize=10.5, color=DARK, pad=8, fontweight="bold")
    ax_bar.text(0.5, -0.08, "Reorder cycles from 81-customer Clear Peach cohort (54d median)\nand 39-customer Lean TMT cohort (35d median) — NOT assumed.",
                ha="center", transform=ax_bar.transAxes, fontsize=8, color=MID, style="italic")

    # ── MIDDLE panel: decision tree ───────────────────────────────────────────
    ax_mid = fig.add_subplot(1, 3, 2)
    ax_mid.set_facecolor("white")
    ax_mid.set_xlim(0, 10)
    ax_mid.set_ylim(0, 10)
    ax_mid.axis("off")
    ax_mid.set_title("Sample Routing Decision\n(What goes to whom)", fontsize=10.5,
                     color=DARK, pad=8, fontweight="bold")

    # Root
    draw_box(ax_mid, 5, 9.4, 7.5, 0.7, "Order 1 Fulfilled -> First Category Detected", DARK, bold=True, fs=9)

    # 4 branches
    branch_data = [
        ("Bought\nClear Protein", 1.4, 8.1, BLUE),
        ("Bought\nLean Protein",  3.8, 8.1, TEAL),
        ("Bought\nCollagen Glow", 6.2, 8.1, CORAL),
        ("Bought\nAccessories",   8.6, 8.1, GOLD),
    ]
    for lbl, bx, by, col in branch_data:
        draw_box(ax_mid, bx, by, 2.1, 0.8, lbl, col, fs=8.5)
        draw_arrow(ax_mid, 5, 9.05, bx, by + 0.4)

    # Email actions (row at y=6.8)
    email_actions = [
        ("Email Day 14:\nLean TMT or Taro", 1.4, 6.8),
        ("Email Day 14:\nClear Peach or WG", 3.8, 6.8),
        ("Email Day 21:\nClear Peach starter", 6.2, 6.8),
        ("Email Day 7:\nProtein trial - urgent", 8.6, 6.8),
    ]
    for txt, ex, ey in email_actions:
        draw_box(ax_mid, ex, ey, 2.1, 0.85, txt, "#D6EAF8", ec=BLUE, fs=8, tc=DARK)
        draw_arrow(ax_mid, branch_data[email_actions.index((txt, ex, ey))][1], 8.1 - 0.4, ex, ey + 0.42)

    # Sample boxes (row at y=5.5)
    sample_actions = [
        ("Sample Day 44:\nLean 40g OR\nCollagen 25g", 1.4, 5.4),
        ("Sample Day 25:\nClear 25g OR\nCollagen 25g", 3.8, 5.4),
        ("Sample Day 32:\nClear 25g OR\nLean 40g", 6.2, 5.4),
        ("Sample Day 25:\nClear 25g sachet\n(NOT another shaker)", 8.6, 5.4),
    ]
    for txt, sx, sy in sample_actions:
        draw_box(ax_mid, sx, sy, 2.1, 0.95, txt, "#FEF9E7", ec=GOLD, fs=7.8, tc=DARK)
        idx = sample_actions.index((txt, sx, sy))
        draw_arrow(ax_mid, email_actions[idx][1], email_actions[idx][2] - 0.42, sx, sy + 0.47)

    # Outcome
    draw_box(ax_mid, 5, 4.05, 9, 0.7,
             "Customer tries new category BEFORE reorder decision  =>  Adds it on Order 2",
             GREEN, bold=True, fs=9)
    for sx, sy in [(a[1], a[2]) for a in sample_actions]:
        draw_arrow(ax_mid, sx, sy - 0.47, 5, 4.05 + 0.35)

    # Subscribe trigger
    draw_box(ax_mid, 5, 3.05, 9, 0.7,
             "Order 2 fulfilled + 48 days  =>  SUB-01: Subscribe & Save on hero SKU",
             TEAL, fs=9)
    draw_arrow(ax_mid, 5, 4.05 - 0.35, 5, 3.05 + 0.35)

    # Design rule
    draw_box(ax_mid, 5, 1.9, 9.3, 0.85,
             "KEY DESIGN RULE: Sample ships SEPARATELY — NOT in first order box.\n"
             "Arrives 10 days BEFORE reorder = customer experiences new category at decision moment.",
             "#FFF3F0", ec=CORAL, fs=8.5, tc=DARK)

    # ── RIGHT panel: data evidence ────────────────────────────────────────────
    ax_ev = fig.add_subplot(1, 3, 3)
    ax_ev.set_facecolor("white")
    ax_ev.axis("off")
    ax_ev.set_title("Data Evidence Behind L3 Design", fontsize=10.5,
                    color=DARK, pad=8, fontweight="bold")

    evidence_blocks = [
        ("Why NOT in the first box?", DARK,
         [
             "Sachet in order 1 box = ignored (product overload at first try).",
             "Pre-reorder arrival = focused moment of decision.",
             "Customer is thinking: 'Do I reorder?' -> sample answers that + adds new product."
         ]),
        ("Co-purchase rates (D1 customers)", TEAL,
         [
             "Clear -> Lean: 53% of D1 Clear buyers also buy Lean",
             "Lean -> Clear: 65% of D1 Lean buyers also buy Clear",
             "Collagen -> Clear: 24% attach rate",
             "Accessories -> Lean: 41% move to protein",
             "These rates are the source for the routing rules."
         ]),
        ("Reorder cycle — how it was measured", BLUE,
         [
             "For each (SKU, customer): compute gaps between all order dates",
             "Take median of those gaps per customer, then median across customers",
             "Clear Peach: 81 buyers, median = 54d (mean = 76d)",
             "Lean TMT: 39 buyers, median = 35d (mean = 69d)",
             "Sample ships: median - 10 days = trigger point"
         ]),
        ("The category prize", GREEN,
         [
             "1 category: 13% repeat, S$64 avg GP  (3,681 customers)",
             "2 categories: 30% repeat, S$92 GP  (1,411 customers)",
             "3+ categories: 63% repeat, S$223 GP  (602 customers)",
             "Each category step = +S$28 GP, +17pp repeat rate",
             "5% of 3,681 moving to 3-cat = S$10,693 GP/yr"
         ]),
    ]

    y_cursor = 0.97
    for title, col, bullets in evidence_blocks:
        ax_ev.text(0.02, y_cursor, title, transform=ax_ev.transAxes,
                   fontsize=9.5, fontweight="bold", color=col, va="top")
        y_cursor -= 0.04
        for b in bullets:
            ax_ev.text(0.04, y_cursor, f"  - {b}", transform=ax_ev.transAxes,
                       fontsize=8, color=DARK, va="top", linespacing=1.3)
            y_cursor -= 0.038
        y_cursor -= 0.015
        ax_ev.plot([0.02, 0.98], [y_cursor + 0.005, y_cursor + 0.005],
                   color=MID, lw=0.5, transform=ax_ev.transAxes)
        y_cursor -= 0.02

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(f"{OUT}/slide3_l3_complete.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide3_l3_complete.png")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Slide 4: Shopify Pipeline + Business Value
# ─────────────────────────────────────────────────────────────────────────────
def chart_slide4_shopify():
    fig = plt.figure(figsize=(18, 9), facecolor="white")
    fig.suptitle("Shopify Implementation — Layer 3 Data Pipeline & Tier Progression Value",
                 fontsize=15, fontweight="bold", color=DARK, y=0.99)

    # ── LEFT: pipeline flow ───────────────────────────────────────────────────
    ax_pipe = fig.add_subplot(1, 2, 1)
    ax_pipe.set_facecolor("white")
    ax_pipe.set_xlim(0, 10)
    ax_pipe.set_ylim(0, 10)
    ax_pipe.axis("off")
    ax_pipe.set_title("L3 Shopify Data Pipeline (Phase 1 — Weeks 1-4)",
                      fontsize=11, color=DARK, pad=8, fontweight="bold")

    steps = [
        # (x, y, w, h, header, body, fc)
        (5, 9.2, 8.5, 0.9,
         "TRIGGER: Shopify orders/fulfilled webhook",
         "Fires when any order is shipped  |  Payload: customer_id, SKUs, order date",
         DARK),
        (5, 7.9, 8.5, 0.95,
         "STEP 1 — Data Extraction (nightly batch)",
         "Query Shopify Admin API for new fulfilled orders\nMap each customer -> first_product_category using order history",
         BLUE),
        (5, 6.4, 8.5, 1.1,
         "STEP 2 — Batch Inference (lookup table, NO ML needed)",
         "Input: first_product_category\nLookup: cross_sell_timing_and_samples.csv (7 rows cover all categories)\nOutput: email_day, sample_day, recommended_sku, sample_sku",
         TEAL),
    ]
    for x, y, w, h, hdr, body, fc in steps:
        draw_box(ax_pipe, x, y, w, h, f"{hdr}\n{body}", fc, fs=8.5, bold=False)
        ax_pipe.text(x, y + h/2 - 0.12, hdr, ha="center", fontsize=9, fontweight="bold",
                     color="white", zorder=5)

    # Arrows between steps
    draw_arrow(ax_pipe, 5, 8.75, 5, 8.37)
    draw_arrow(ax_pipe, 5, 7.42, 5, 6.95)

    # Three outputs (split)
    output_data = [
        (2, 4.8, 2.9, 1.0,
         "OUTPUT A: Email Schedule",
         "Add customer to email segment:\nCS-01/02/03 flow\nFires at Day 14 or 21", CORAL),
        (5, 4.8, 2.9, 1.0,
         "OUTPUT B: Sample Dispatch Tag",
         "Shopify customer tag:\nsample_sku + ship_date\nFulfilment team dispatches sachet", GOLD),
        (8, 4.8, 2.9, 1.0,
         "OUTPUT C: Subscribe Trigger",
         "After Order 2 + 48 days:\nSUB-01 email trigger\nSubscribe & Save offer on hero SKU", GREEN),
    ]
    # Arrow from step 2 to each output
    for ox, oy, ow, oh, hdr, body, col in output_data:
        draw_box(ax_pipe, ox, oy, ow, oh, f"{hdr}\n{body}", col, fs=8, bold=False)
        ax_pipe.text(ox, oy + oh/2 - 0.14, hdr, ha="center", fontsize=8.5, fontweight="bold",
                     color="white", zorder=5)
        draw_arrow(ax_pipe, ox, 5.95, ox, oy + oh/2 + 0.05)

    # Branch line from step 2 bottom
    ax_pipe.plot([2, 8], [5.95, 5.95], color=MID, lw=1.2, zorder=2)
    draw_arrow(ax_pipe, 5, 5.9, 5, 5.9)

    # Phase notes
    phase_notes = [
        (5, 3.4, TEAL, "Phase 1 (Weeks 1-4):  L3 email + sample dispatch LIVE"),
        (5, 2.9, BLUE, "Phase 2 (Weeks 4-6):  L2 PDP association widget on Shopify storefront"),
        (5, 2.4, CORAL, "Phase 3 (Weeks 6+):  L4 Item-CF on logged-in account page"),
    ]
    for px, py, col, txt in phase_notes:
        ax_pipe.text(px, py, txt, ha="center", fontsize=9.5, fontweight="bold", color=col, zorder=4)

    # Tech stack box
    stack_lines = [
        "Tech Stack (Phase 1 — no custom dev required):",
        "  Shopify webhooks / Admin API  —  native, free",
        "  7-row CSV lookup table  —  already built",
        "  Email automation platform  —  Klaviyo / Omnisend / Mailchimp",
        "  Shopify customer tags  —  store first_cat + sample_sku",
        "  Shopify Flow app (optional)  —  tag-to-action automation, free",
    ]
    ax_pipe.text(5, 1.7, "\n".join(stack_lines), ha="center", va="center",
                 fontsize=8.5, color=DARK, zorder=4, linespacing=1.5,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#F0F8FF", edgecolor=BLUE, lw=1))

    # ── RIGHT: business value ─────────────────────────────────────────────────
    ax_bv = fig.add_subplot(1, 2, 2)
    ax_bv.set_facecolor("white")
    ax_bv.set_xlim(0, 10)
    ax_bv.set_ylim(0, 10)
    ax_bv.axis("off")
    ax_bv.set_title("Why It Matters — Customer Tier Progression",
                    fontsize=11, color=DARK, pad=8, fontweight="bold")

    # Tier funnel (5 tiers, funnel shape)
    tiers = [
        ("PLATINUM",        238, 388, 85, GOLD,    8.8, 8.0),
        ("GOLD-A  (Whales)", 130, 300, 72, CORAL,   7.4, 6.6),
        ("GOLD-B  (Loyal Regulars)", 264, 105, 54, TEAL,  5.9, 5.1),
        ("SILVER",          858, 100, 45, BLUE,    4.35, 3.55),
        ("UNTIERED\n(one-and-done / new)", 4204, 39, 11, MID, 2.7, 1.9),
    ]
    widths = [8.5, 7.5, 6.5, 5.5, 4.5]
    for (tier, n, gp, rep, col, ytop, ybot), w in zip(tiers, widths):
        ymid = (ytop + ybot) / 2
        h = ytop - ybot
        draw_box(ax_bv, 5, ymid, w, h, "", col + "33", ec=col, alpha=1.0)
        ax_bv.text(1.0, ymid + 0.08, tier, fontsize=9.5, fontweight="bold", color=col, va="center")
        ax_bv.text(1.0, ymid - 0.2,
                   f"  {n} customers   |   S${gp} avg GP   |   {rep}% repeat rate",
                   fontsize=8.5, color=DARK, va="center")

    # Uplift callouts
    uplift_boxes = [
        (8.5, 4.85,
         "Silver -> Gold-B\n+S$5 avg GP/cust\n858 in pool\n5% conv = +S$2,940 GP",
         BLUE),
        (8.5, 3.3,
         "Key pathway:\nL3 cross-sell\nmoves single-cat\nbuyers up ladder",
         TEAL),
    ]
    for bx, by, txt, col in uplift_boxes:
        ax_bv.text(bx, by, txt, ha="right", va="center", fontsize=8, color=col,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=col + "22", edgecolor=col, lw=1))

    # Prize summary
    prize_txt = (
        "L3 Conservative Prize (Category Ladder):\n\n"
        "  5% of 3,681 single-cat reach 2 categories:  +S$2,940 GP\n"
        "  5% of 3,681 single-cat reach 3 categories:  +S$10,693 GP\n"
        "  Subscription conversion (SUB-01):  +S$2,262 GP\n"
        "  Acquisition mix fix (stop shaker-led):  +S$4,389 GP\n\n"
        "  Conservative total:  S$17-30K GP/yr"
    )
    ax_bv.text(5, 1.05, prize_txt, ha="center", va="center", fontsize=9, color=DARK,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#E8F5EE", edgecolor=GREEN, lw=1.5))

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(f"{OUT}/slide4_shopify_pipeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved slide4_shopify_pipeline.png")


if __name__ == "__main__":
    chart_slide1_problem()
    chart_slide3_l3_complete()
    chart_slide4_shopify()
    print("All 3 slide charts complete.")
