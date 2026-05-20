"""
style.py  -  Shared presentation style for all LushProtein charts.

Palette is brand-adjacent (clean, modern, professional).
All charts saved at 150 dpi as PNG, 16:9 or compact variants.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# -- Output folder -------------------------------------------------------------
OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)

# -- Brand palette -------------------------------------------------------------
TEAL      = "#2DC4A2"   # primary accent
NAVY      = "#1A2E44"   # dark text / strong bars
SLATE     = "#4A6274"   # secondary text / subtle bars
ORANGE    = "#F07D3E"   # warning highlight
RED       = "#E84545"   # danger / churn
GOLD      = "#F7B731"   # positive secondary
LILAC     = "#9B72CF"   # tertiary accent
LIGHT_BG  = "#F8F9FA"   # chart background
GRID_LINE = "#E2E8ED"   # grid

# Categorical sequence (up to 7 groups)
CAT_COLORS = [TEAL, NAVY, ORANGE, GOLD, SLATE, RED, LILAC]

# -- Global rcParams ------------------------------------------------------------
mpl.rcParams.update({
    "figure.facecolor":      LIGHT_BG,
    "axes.facecolor":        LIGHT_BG,
    "axes.edgecolor":        GRID_LINE,
    "axes.spines.top":       False,
    "axes.spines.right":     False,
    "axes.grid":             True,
    "axes.grid.axis":        "y",
    "grid.color":            GRID_LINE,
    "grid.linewidth":        1.0,
    "axes.labelcolor":       NAVY,
    "axes.titlecolor":       NAVY,
    "axes.titlesize":        14,
    "axes.titleweight":      "bold",
    "axes.titlepad":         12,
    "axes.labelsize":        11,
    "xtick.color":           SLATE,
    "ytick.color":           SLATE,
    "xtick.labelsize":       10,
    "ytick.labelsize":       10,
    "legend.fontsize":       10,
    "legend.frameon":        False,
    "font.family":           ["DejaVu Sans"],
    "figure.dpi":            150,
})

def save(fig: plt.Figure, name: str) -> Path:
    path = OUT / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=LIGHT_BG)
    plt.close(fig)
    print(f"  Saved: charts/{name}.png")
    return path

def bar_label(ax, fmt="{:.1f}", fontsize=9, color=NAVY, padding=3):
    """Add value labels on top of every bar."""
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(
                fmt.format(h),
                xy=(p.get_x() + p.get_width() / 2, h),
                xytext=(0, padding),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=fontsize, color=color,
            )

def hbar_label(ax, fmt="{:.1f}", fontsize=9, color=NAVY, padding=4):
    """Add value labels at the end of horizontal bars."""
    for p in ax.patches:
        w = p.get_width()
        if w > 0:
            ax.annotate(
                fmt.format(w),
                xy=(w, p.get_y() + p.get_height() / 2),
                xytext=(padding, 0),
                textcoords="offset points",
                ha="left", va="center",
                fontsize=fontsize, color=color,
            )

def subtitle(ax, text: str):
    ax.set_title(ax.get_title() + f"\n", fontsize=14, fontweight="bold")
    ax.annotate(
        text, xy=(0, 1.02), xycoords="axes fraction",
        fontsize=9, color=SLATE, va="bottom",
    )
