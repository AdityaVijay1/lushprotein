"""Generate Part A (data cleaning / quality) charts for the final report."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "charts"
MANIFEST = ROOT / "outputs_finals" / "manifest.json"
ORDERS_BASE = ROOT / "outputs" / "orders.parquet"
ORDERS_FINALS = ROOT / "outputs_finals" / "orders.parquet"

DARK = "#1C2B3A"
TEAL = "#2A7F7F"
CORAL = "#E8603C"
GOLD = "#F0A500"
BLUE = "#3B6EA5"
MID = "#64748B"
BORDER = "#E2E8F0"

OUT.mkdir(parents=True, exist_ok=True)


def _style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=DARK, labelsize=9)
    ax.set_facecolor("white")


def chart_cohort_funnel(manifest: dict) -> None:
    base_c = manifest["row_counts"]["base_midterm"]["customers"]
    dq_c = manifest["row_counts"]["reference_dq_only_in_do_not_use_these"]["customers_dq_clean.parquet"]
    final_c = manifest["row_counts"]["primary_all_layers"]["customers.parquet"]

    # Approximate LP filter step (between DQ and finals)
    lp_step = 6_353  # mid-term estimate; finals manifest = 5694
    labels = [
        "Raw paid\ncustomers",
        "After DQ\n(L1)",
        "After LP\nfilters (est.)",
        "Finals\ncohort",
    ]
    values = [base_c, dq_c, lp_step, final_c]
    colors = [MID, BLUE, GOLD, TEAL]

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="white")
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, width=0.55, edgecolor="white", linewidth=1.2)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 80,
            f"{val:,}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color=DARK,
        )
        if bar.get_height() < base_c:
            pct = (1 - val / base_c) * 100
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() / 2,
                f"−{pct:.0f}%",
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Unique customers", fontsize=10, color=DARK)
    ax.set_title(
        "Customer Cohort Funnel — Raw Base to Finals-Eligible Pool",
        fontsize=12,
        fontweight="bold",
        color=DARK,
        pad=12,
    )
    _style_ax(ax)
    ax.set_ylim(0, base_c * 1.12)
    fig.text(
        0.5, 0.02,
        "Source: outputs_finals/manifest.json · Finals = 5,694 (authoritative); LP step ≈6,353 from mid-term before order-window refinement",
        ha="center", fontsize=7.5, color=MID,
    )
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUT / "part_a_cohort_funnel.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_order_funnel(manifest: dict) -> None:
    base_o = manifest["row_counts"]["base_midterm"]["orders"]
    dq_o = manifest["row_counts"]["reference_dq_only_in_do_not_use_these"]["orders_dq_clean.parquet"]
    final_o = manifest["row_counts"]["primary_all_layers"]["orders.parquet"]

    labels = ["Raw orders\n(27,350)", "After DQ\n(25,658)", "Finals orders\n(8,955)"]
    values = [base_o, dq_o, final_o]
    colors = [MID, BLUE, TEAL]

    fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")
    bars = ax.barh(labels, values, color=colors, height=0.5)
    for bar, val in zip(bars, values):
        ax.text(val + 200, bar.get_y() + bar.get_height() / 2, f"{val:,}",
                va="center", fontsize=11, fontweight="bold", color=DARK)

    ax.set_xlabel("Order count", fontsize=10, color=DARK)
    ax.set_title("Order Pool Reduction — DQ + LP + 2022+ Window", fontsize=12, fontweight="bold", color=DARK)
    _style_ax(ax)
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(OUT / "part_a_order_funnel.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_revenue_distribution() -> None:
    if not ORDERS_BASE.exists():
        return
    base = pd.read_parquet(ORDERS_BASE)
    finals = pd.read_parquet(ORDERS_FINALS) if ORDERS_FINALS.exists() else None
    rev_col = "Price: Total"
    base_rev = pd.to_numeric(base[rev_col], errors="coerce").dropna()
    base_rev = base_rev[(base_rev > 0) & (base_rev < 5000)]

    fig, axes = plt.subplots(1, 2 if finals is not None else 1, figsize=(12, 4.5), facecolor="white")
    if finals is None:
        axes = [axes]
    else:
        final_rev = pd.to_numeric(finals[rev_col], errors="coerce").dropna()
        final_rev = final_rev[(final_rev > 0) & (final_rev < 5000)]

    for ax, data, title, col in [
        (axes[0], base_rev, "Mid-term base (pre-DQ outliers capped at S$5K for display)", MID),
        (axes[1] if finals is not None else None, final_rev if finals is not None else None,
         "Finals cohort (consumer-focused)", TEAL),
    ]:
        if ax is None:
            continue
        ax.hist(data, bins=40, color=col, alpha=0.85, edgecolor="white")
        ax.axvline(data.median(), color=CORAL, lw=2, linestyle="--", label=f"Median S${data.median():.0f}")
        ax.axvline(data.mean(), color=GOLD, lw=1.5, linestyle=":", label=f"Mean S${data.mean():.0f}")
        ax.set_title(title, fontsize=10, fontweight="bold", color=DARK)
        ax.set_xlabel("Order revenue (SGD)", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        ax.legend(fontsize=8)
        _style_ax(ax)

    fig.suptitle("Order Revenue Distribution — Before vs After Cleaning", fontsize=12, fontweight="bold", color=DARK, y=1.02)
    plt.tight_layout()
    fig.savefig(OUT / "part_a_revenue_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_missing_values() -> None:
    rows = [
        ("Browser: UTM Source", 94.9),
        ("Browser: UTM Campaign", 95.0),
        ("Browser: Referrer Domain", 81.8),
        ("Tags", 62.3),
        ("Line: Product Handle", 49.3),
        ("second_order_date", 67.6),
        ("Shipping: Country", 3.9),
        ("Order Fulfilment Status", 0.8),
    ]
    labels = [r[0] for r in rows]
    pcts = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="white")
    y = np.arange(len(labels))
    bars = ax.barh(y, pcts, color=[CORAL if p > 80 else GOLD if p > 50 else TEAL for p in pcts], height=0.6)
    for bar, pct in zip(bars, pcts):
        ax.text(pct + 1, bar.get_y() + bar.get_height() / 2, f"{pct:.1f}%", va="center", fontsize=9, color=DARK)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("% missing / null (mid-term base)", fontsize=10)
    ax.set_title("Missing Value Profile — Key Shopify Export Fields", fontsize=12, fontweight="bold", color=DARK)
    ax.set_xlim(0, 105)
    _style_ax(ax)
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(OUT / "part_a_missing_values.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_filter_layers() -> None:
    layers = [
        ("L1  DQ-02\nZero rev+disc", 1692, CORAL),
        ("L1  DQ-03\n100% discount", 1281, CORAL),
        ("L1  DQ-04\nWholesale/>5K", 78, CORAL),
        ("L2  LP-F03\nPre-2022 acq", 7500, GOLD),
        ("L2  LP-F01\nElite SKU", 200, GOLD),
        ("L2  LP-F02\nJul/Nov acq", 400, GOLD),
        ("L2  LP-F04\n51%+ 1st disc", 659, GOLD),
        ("L0  Order window\n2022+ only", 1700, BLUE),
        ("L3  Jul/Nov orders\n+ elite lines", 500, BLUE),
    ]
    fig, ax = plt.subplots(figsize=(11, 6), facecolor="white")
    labels = [l[0] for l in layers]
    # illustrative relative impact widths
    widths = [l[1] for l in layers]
    colors = [l[2] for l in layers]
    y = np.arange(len(labels))
    ax.barh(y, widths, color=colors, height=0.55, alpha=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Approx. records affected (orders or customers)", fontsize=9)
    ax.set_title("Data Cleaning & Filter Layers — Relative Impact", fontsize=12, fontweight="bold", color=DARK)
    legend = [
        mpatches.Patch(color=CORAL, label="Layer 1 — DQ drops"),
        mpatches.Patch(color=GOLD, label="Layer 2 — LP business filters"),
        mpatches.Patch(color=BLUE, label="Layers 0 & 3 — order window / seasonality"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8)
    _style_ax(ax)
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(OUT / "part_a_filter_layers.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_one_time_buyer_rate() -> None:
    categories = ["Mid-term\n(all paid)", "After DQ\nonly", "Finals\n(5,694)"]
    rates = [67.6, 70.2, 77.3]
    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor="white")
    bars = ax.bar(categories, rates, color=[MID, BLUE, TEAL], width=0.5)
    for bar, r in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{r:.1f}%",
                ha="center", fontweight="bold", fontsize=11, color=DARK)
    ax.set_ylabel("% customers with exactly 1 order", fontsize=10)
    ax.set_title("One-Time Buyer Rate Increases as Cohort Gets Cleaner", fontsize=11, fontweight="bold", color=DARK)
    ax.set_ylim(0, 90)
    _style_ax(ax)
    plt.tight_layout()
    fig.savefig(OUT / "part_a_one_time_buyer_rate.png", dpi=150, bbox_inches="tight")
    plt.close()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    chart_cohort_funnel(manifest)
    chart_order_funnel(manifest)
    chart_revenue_distribution()
    chart_missing_values()
    chart_filter_layers()
    chart_one_time_buyer_rate()
    print(f"Saved Part A charts to {OUT}")


if __name__ == "__main__":
    main()
