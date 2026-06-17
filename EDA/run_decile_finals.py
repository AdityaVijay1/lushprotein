"""
run_decile_finals.py
Re-run Lens 1 + Lens 2 decile analyses using outputs_finals parquets.

Does NOT modify decile_lens1.ipynb / decile_lens2.ipynb.
Uses orders.parquet + customers.parquet from EDA/outputs_finals/ (all 3 filter
layers already applied). Only adds the marketplace anomaly exclusion from the
original notebooks.

Outputs written to EDA/outputs_finals/ (same filenames as teammate's EDA/outputs/).
"""
import warnings
warnings.filterwarnings("ignore")

import importlib.util
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

def _load_config():
    spec = importlib.util.spec_from_file_location("lp_config", Path(__file__).parent / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg = _load_config()
FINALS_DIR = cfg.FINALS_DIR
MARGIN_RATE = 0.40

PERIOD_1_START = pd.Timestamp("2022-01-01", tz="Asia/Singapore")
PERIOD_1_END   = pd.Timestamp("2023-12-31", tz="Asia/Singapore")
PERIOD_2_START = pd.Timestamp("2024-01-01", tz="Asia/Singapore")
PERIOD_2_END   = pd.Timestamp("2025-12-31", tz="Asia/Singapore")

print("=" * 70)
print("DECILE ANALYSIS — outputs_finals data")
print("=" * 70)
print(f"Input:  {FINALS_DIR}")
print(f"Output: {FINALS_DIR}")

# ── Load finals parquets (Layer 0+1+2+3 already applied) ─────────────────────
orders = pd.read_parquet(FINALS_DIR / "orders.parquet")
cust   = pd.read_parquet(FINALS_DIR / "customers.parquet")

orders["order_date"] = pd.to_datetime(orders["order_date"], utc=True).dt.tz_convert("Asia/Singapore")
orders["price_total"] = pd.to_numeric(orders["Price: Total"], errors="coerce").fillna(0)
orders["price_disc"]  = pd.to_numeric(orders["Price: Total Discount"], errors="coerce").fillna(0)

print(f"\nLoaded orders:    {len(orders):,}")
print(f"Loaded customers: {len(cust):,}")

# ── Marketplace anomaly exclusion (notebook-only extra filter) ───────────────
cust_channel_mix = (
    orders.groupby("customer_id")["channel"]
    .value_counts(normalize=True)
    .unstack(fill_value=0)
)
if "Marketplace" in cust_channel_mix.columns:
    all_mkt_ids = set(cust_channel_mix[cust_channel_mix["Marketplace"] == 1.0].index.astype(str))
else:
    all_mkt_ids = set()

cust = cust.copy()
cust["is_all_marketplace"] = cust["customer_id"].astype(str).isin(all_mkt_ids)
cust = cust[~cust["is_all_marketplace"] & (cust["total_orders"] > 0)].copy()

orders = orders[orders["customer_id"].isin(set(cust["customer_id"]))].copy()

print(f"\nAfter marketplace exclusion:")
print(f"  Customers: {len(cust):,}")
print(f"  Orders:    {len(orders):,}")

# Rebuild clean stats from filtered orders (align with decile pool)
_cust_rebuild = orders.groupby("customer_id").agg(
    clean_orders=("order_id", "count"),
    clean_revenue=("price_total", "sum"),
).reset_index()

df = cust.merge(_cust_rebuild, on="customer_id", how="inner")
df["clean_orders"] = df["clean_orders"].astype(int)
df["aov"] = df["clean_revenue"] / df["clean_orders"].clip(lower=1)
df["profit_proxy"] = df["clean_revenue"] * MARGIN_RATE

print(f"  Decile pool: {len(df):,} customers")
print(f"  Revenue range: S${df['clean_revenue'].min():.2f} – S${df['clean_revenue'].max():,.2f}")

# ══════════════════════════════════════════════════════════════════════════════
# LENS 1 — Deciles
# ══════════════════════════════════════════════════════════════════════════════
DECILE_ORDER = [f"D{i}" for i in range(10, 0, -1)]  # D10 (lowest) → D1 (highest)

def assign_decile(series: pd.Series) -> pd.Series:
    """D1 = best, D10 = worst — matches decile_lens1.ipynb."""
    ranks = series.rank(method="first", ascending=True)
    return pd.qcut(ranks, q=10, labels=DECILE_ORDER)

df["profit_decile"] = assign_decile(df["profit_proxy"])
df["freq_decile"]   = assign_decile(df["clean_orders"])

# Profit decile summary
profit_summary = (
    df.groupby("profit_decile", observed=False)
    .agg(
        n_customers=("customer_id", "count"),
        total_revenue=("clean_revenue", "sum"),
        total_profit=("profit_proxy", "sum"),
        avg_revenue=("clean_revenue", "mean"),
        median_revenue=("clean_revenue", "median"),
        avg_profit=("profit_proxy", "mean"),
        avg_orders=("clean_orders", "mean"),
        avg_aov=("aov", "mean"),
    )
    .reset_index()
)
total_rev = df["clean_revenue"].sum()
profit_summary["pct_revenue"] = profit_summary["total_revenue"] / total_rev
profit_summary = profit_summary.set_index("profit_decile").reindex(DECILE_ORDER).reset_index()
profit_summary["cum_pct_revenue"] = profit_summary["pct_revenue"].cumsum()

# Frequency decile summary
freq_summary = (
    df.groupby("freq_decile", observed=False)
    .agg(
        n_customers=("customer_id", "count"),
        total_orders=("clean_orders", "sum"),
        avg_orders=("clean_orders", "mean"),
        median_orders=("clean_orders", "median"),
        avg_revenue=("clean_revenue", "mean"),
        avg_aov=("aov", "mean"),
        avg_profit=("profit_proxy", "mean"),
    )
    .reset_index()
)
total_ord = df["clean_orders"].sum()
freq_summary["pct_transactions"] = freq_summary["total_orders"] / total_ord
freq_summary = freq_summary.set_index("freq_decile").reindex(DECILE_ORDER).reset_index()
freq_summary["cum_pct_transactions"] = freq_summary["pct_transactions"].cumsum()
freq_summary["pct_revenue"] = (
    df.groupby("freq_decile", observed=False)["clean_revenue"].sum().reindex(DECILE_ORDER).values / total_rev
)

# Charts — decile1_profit.png
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle("Decile 1 — By Profit (D1 = Highest)", fontsize=14, fontweight="bold", y=1.01)
deciles = profit_summary["profit_decile"].astype(str)
colors  = ["#2E86AB" if d == "D1" else "#A8DADC" for d in deciles]

ax = axes[0]
bars = ax.bar(deciles, profit_summary["pct_revenue"] * 100, color=colors, edgecolor="white")
ax.set_title("% of Total Revenue per Decile")
ax.set_xlabel("Decile")
ax.set_ylabel("% Revenue")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
for bar, val in zip(bars, profit_summary["pct_revenue"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{val:.1%}", ha="center", va="bottom", fontsize=8)

ax = axes[1]
bars = ax.bar(deciles, profit_summary["avg_revenue"], color=colors, edgecolor="white")
ax.set_title("Avg Revenue per Customer")
ax.set_xlabel("Decile")
ax.set_ylabel("SGD")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("S$%.0f"))
for bar, val in zip(bars, profit_summary["avg_revenue"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"S${val:,.0f}", ha="center", va="bottom", fontsize=7)

ax = axes[2]
ax.plot(
    range(1, 11),
    profit_summary["cum_pct_revenue"] * 100,
    marker="o",
    color="#2E86AB",
    linewidth=2,
)
ax.axhline(80, color="gray", linestyle="--", alpha=0.6)
ax.set_title("Cumulative % Revenue (D1 → D10)")
ax.set_xlabel("Top N Deciles")
ax.set_ylabel("Cumulative % Revenue")
ax.set_xticks(range(1, 11))
ax.set_xticklabels([f"D{i}" for i in range(1, 11)])
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
for x, y in zip(range(1, 11), profit_summary["cum_pct_revenue"] * 100):
    ax.annotate(
        f"{y:.0f}%",
        (x, y),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=7,
    )
plt.tight_layout()
plt.savefig(FINALS_DIR / "decile1_profit.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: decile1_profit.png")

# Charts — decile2_frequency.png
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle("Decile 2 — By Frequency (D1 = Most Frequent)", fontsize=14, fontweight="bold", y=1.01)
deciles2 = freq_summary["freq_decile"].astype(str)
colors2  = ["#E76F51" if d == "D1" else "#F4A261" for d in deciles2]

ax = axes[0]
bars = ax.bar(deciles2, freq_summary["avg_orders"], color=colors2, edgecolor="white")
ax.set_title("Avg Orders per Customer")
ax.set_xlabel("Decile")
for bar, val in zip(bars, freq_summary["avg_orders"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f"{val:.1f}", ha="center", va="bottom", fontsize=8)

ax = axes[1]
bars = ax.bar(deciles2, freq_summary["pct_transactions"] * 100, color=colors2, edgecolor="white")
ax.set_title("% of Total Transactions per Decile")
ax.set_xlabel("Decile")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
for bar, val in zip(bars, freq_summary["pct_transactions"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.1%}", ha="center", va="bottom", fontsize=8)

ax = axes[2]
bars = ax.bar(deciles2, freq_summary["avg_revenue"], color=colors2, edgecolor="white")
ax.set_title("Avg Revenue per Customer")
ax.set_xlabel("Decile")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("S$%.0f"))
for bar, val in zip(bars, freq_summary["avg_revenue"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"S${val:,.0f}", ha="center", va="bottom", fontsize=7)
plt.tight_layout()
plt.savefig(FINALS_DIR / "decile2_frequency.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: decile2_frequency.png")

# Overlap heatmap — axes run D10 (lowest) → D1 (highest), matching bar charts
overlap = pd.crosstab(df["profit_decile"], df["freq_decile"])
overlap = overlap.reindex(index=DECILE_ORDER, columns=DECILE_ORDER, fill_value=0)

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(overlap.values, cmap="Blues", aspect="auto")
plt.colorbar(im, ax=ax, label="Customer count")
ax.set_xticks(range(10))
ax.set_yticks(range(10))
ax.set_xticklabels(DECILE_ORDER)
ax.set_yticklabels(DECILE_ORDER)
ax.set_xlabel("Frequency Decile")
ax.set_ylabel("Profit Decile")
ax.set_title("Overlap: Profit Decile vs Frequency Decile\n(Diagonal = customers ranked the same in both)")
for i in range(10):
    for j in range(10):
        val = overlap.values[i, j]
        ax.text(j, i, str(val), ha="center", va="center",
                color="white" if val > overlap.values.max() * 0.5 else "black", fontsize=9)
plt.tight_layout()
plt.savefig(FINALS_DIR / "decile_overlap_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: decile_overlap_heatmap.png")

# Equal-revenue slicing
sorted_df = df.sort_values("clean_revenue", ascending=False).reset_index(drop=True)
cum_rev = sorted_df["clean_revenue"].cumsum()
targets = [total_rev * (i / 10) for i in range(1, 11)]
slice_rows = []
prev_idx = 0
for i, target in enumerate(targets):
    idx = int(cum_rev.searchsorted(target, side="right"))
    chunk = sorted_df.iloc[prev_idx:idx]
    slice_rows.append({
        "revenue_slice": f"{i*10}-{(i+1)*10}%",
        "n_customers": len(chunk),
        "pct_of_base": len(chunk) / len(df),
        "rev_min": chunk["clean_revenue"].min() if len(chunk) else np.nan,
        "rev_max": chunk["clean_revenue"].max() if len(chunk) else np.nan,
        "rev_mean": chunk["clean_revenue"].mean() if len(chunk) else np.nan,
    })
    prev_idx = idx
slice_df = pd.DataFrame(slice_rows)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Equal-Revenue Slicing — Each Bar = 10% of Total Revenue",
             fontsize=13, fontweight="bold", y=1.01)
slices = slice_df["revenue_slice"]
colors3 = ["#2E86AB" if i == 0 else "#A8DADC" for i in range(len(slices))]

ax = axes[0]
bars = ax.bar(slices, slice_df["n_customers"], color=colors3, edgecolor="white")
ax.set_title("Customers Needed per 10% Revenue Slice")
ax.set_xlabel("Revenue Slice")
ax.set_ylabel("Number of Customers")
ax.tick_params(axis="x", rotation=45)
for bar, val in zip(bars, slice_df["n_customers"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            str(val), ha="center", va="bottom", fontsize=8)

ax = axes[1]
bars = ax.bar(slices, slice_df["pct_of_base"] * 100, color=colors3, edgecolor="white")
ax.set_title("% of Customer Base per 10% Revenue Slice")
ax.set_xlabel("Revenue Slice")
ax.set_ylabel("% of Customers")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.tick_params(axis="x", rotation=45)
for bar, val in zip(bars, slice_df["pct_of_base"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f"{val:.1%}", ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(FINALS_DIR / "equal_revenue_slicing.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: equal_revenue_slicing.png")

# Customer export table
export_df = df[[
    "customer_id", "clean_orders", "clean_revenue", "profit_proxy", "aov",
    "profit_decile", "freq_decile", "first_channel", "ever_subscribed",
]].copy()
export_df["is_top_profit"] = export_df["profit_decile"] == "D1"
export_df["is_top_freq"]   = export_df["freq_decile"] == "D1"
export_df["is_top_both"]   = export_df["is_top_profit"] & export_df["is_top_freq"]
export_df.to_csv(FINALS_DIR / "decile_customer_table.csv", index=False)
print("Saved: decile_customer_table.csv")

# Lens 1 summary
d1p = profit_summary[profit_summary["profit_decile"] == "D1"].iloc[0]
d1f = freq_summary[freq_summary["freq_decile"] == "D1"].iloc[0]
d1_both = len(set(df[df["profit_decile"] == "D1"]["customer_id"]) &
             set(df[df["freq_decile"] == "D1"]["customer_id"]))

print("\n" + "=" * 70)
print("LENS 1 SUMMARY (outputs_finals)")
print("=" * 70)
print(f"Customer pool: {len(df):,}  (~{len(df)//10} per decile)")
print(f"D1 profit:  {d1p['pct_revenue']:.1%} of revenue | avg S${d1p['avg_revenue']:,.0f}")
print(f"D1 freq:    {d1f['pct_transactions']:.1%} of orders | avg {d1f['avg_orders']:.1f} orders")
print(f"D1 both:    {d1_both:,} customers")
print(f"Equal-rev slice 1: {slice_rows[0]['n_customers']} customers ({slice_rows[0]['pct_of_base']:.1%})")
print(f"Equal-rev slice 10: {slice_rows[9]['n_customers']} customers ({slice_rows[9]['pct_of_base']:.1%})")

# ══════════════════════════════════════════════════════════════════════════════
# LENS 2 — Migration heatmap
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("LENS 2 — Migration (2022–2023 vs 2024–2025)")
print("=" * 70)

p1_orders = orders[(orders["order_date"] >= PERIOD_1_START) & (orders["order_date"] <= PERIOD_1_END)]
p2_orders = orders[(orders["order_date"] >= PERIOD_2_START) & (orders["order_date"] <= PERIOD_2_END)]

p1_customers = set(p1_orders["customer_id"].unique())
p2_customers = set(p2_orders["customer_id"].unique())
both_customers = p1_customers & p2_customers

print(f"Period 1 active: {len(p1_customers):,}")
print(f"Period 2 active: {len(p2_customers):,}")
print(f"Both periods:    {len(both_customers):,}")

p1_rev = (
    p1_orders[p1_orders["customer_id"].isin(both_customers)]
    .groupby("customer_id")["price_total"].sum().rename("p1_revenue").reset_index()
)
p2_rev = (
    p2_orders[p2_orders["customer_id"].isin(both_customers)]
    .groupby("customer_id")["price_total"].sum().rename("p2_revenue").reset_index()
)
migration_df = p1_rev.merge(p2_rev, on="customer_id", how="inner")

def assign_tier(series, n_tiers=5):
    ranks = series.rank(method="first", ascending=True)
    return pd.qcut(ranks, q=n_tiers, labels=[f"T{i}" for i in range(n_tiers, 0, -1)])

migration_df["p1_tier"] = assign_tier(migration_df["p1_revenue"])
migration_df["p2_tier"] = assign_tier(migration_df["p2_revenue"])

migration_matrix = pd.crosstab(migration_df["p1_tier"], migration_df["p2_tier"])
all_tiers = [f"T{i}" for i in range(1, 6)]
migration_matrix = migration_matrix.reindex(index=all_tiers, columns=all_tiers, fill_value=0)

migration_df["p1_tier_num"] = migration_df["p1_tier"].astype(str).str[1].astype(int)
migration_df["p2_tier_num"] = migration_df["p2_tier"].astype(str).str[1].astype(int)
migration_df["movement"] = migration_df["p1_tier_num"] - migration_df["p2_tier_num"]

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(migration_matrix.values, cmap="Blues", aspect="auto")
plt.colorbar(im, ax=ax, label="Number of Customers")
ax.set_xticks(range(5))
ax.set_yticks(range(5))
ax.set_xticklabels([f"T{i}" for i in range(1, 6)])
ax.set_yticklabels([f"T{i}" for i in range(1, 6)])
ax.set_xlabel("Period 2 Tier (2024–2025)", fontsize=11)
ax.set_ylabel("Period 1 Tier (2022–2023)", fontsize=11)
ax.set_title(
    f"Revenue Tier Migration Heatmap\n"
    f"2022–2023 → 2024–2025  |  {len(migration_df):,} both-period customers  |  T1 = Highest",
    fontsize=11, fontweight="bold",
)
for i in range(5):
    for j in range(5):
        val = migration_matrix.values[i, j]
        ax.text(j, i, str(val), ha="center", va="center", fontsize=11, fontweight="bold",
                color="white" if val > migration_matrix.values.max() * 0.5 else "black")
    ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#E76F51", linewidth=2.5))
plt.tight_layout()
plt.savefig(FINALS_DIR / "lens2_migration_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: lens2_migration_heatmap.png")

# Lens 2 CSV exports
t5_to_t1 = migration_df[(migration_df["p1_tier"] == "T5") & (migration_df["p2_tier"] == "T1")][
    ["customer_id", "p1_revenue", "p2_revenue"]
].copy()
t5_to_t1["revenue_change"] = t5_to_t1["p2_revenue"] - t5_to_t1["p1_revenue"]
t5_to_t1 = t5_to_t1.sort_values("revenue_change", ascending=False)

t1_dropped = migration_df[(migration_df["p1_tier"] == "T1") & (migration_df["p2_tier"] != "T1")][
    ["customer_id", "p1_revenue", "p2_revenue", "p2_tier"]
].copy()
t1_dropped["revenue_change"] = t1_dropped["p2_revenue"] - t1_dropped["p1_revenue"]
t1_dropped = t1_dropped.sort_values("revenue_change", ascending=True)

churned_ids = p1_customers - p2_customers
churned_orders = p1_orders[p1_orders["customer_id"].isin(churned_ids)]
churned_profile = (
    churned_orders.groupby("customer_id")
    .agg(
        p1_revenue=("price_total", "sum"),
        p1_orders=("order_id", "count"),
        last_order=("order_date", "max"),
        first_channel=("channel", "first"),
    )
    .reset_index()
    .sort_values("p1_revenue", ascending=False)
)

tier_rev_change = migration_df.groupby("p1_tier", observed=False).agg(
    n_customers=("customer_id", "count"),
    avg_p1_rev=("p1_revenue", "mean"),
    avg_p2_rev=("p2_revenue", "mean"),
).reset_index()
tier_rev_change["avg_change"] = tier_rev_change["avg_p2_rev"] - tier_rev_change["avg_p1_rev"]
tier_rev_change["pct_change"] = tier_rev_change["avg_change"] / tier_rev_change["avg_p1_rev"]

t5_to_t1.to_csv(FINALS_DIR / "next_t5_to_t1_jumpers.csv", index=False)
t1_dropped.to_csv(FINALS_DIR / "next_t1_dropped.csv", index=False)
churned_profile.to_csv(FINALS_DIR / "next_churned_customers.csv", index=False)
tier_rev_change.to_csv(FINALS_DIR / "next_tier_revenue_change.csv", index=False)

print("Saved: next_t5_to_t1_jumpers.csv")
print("Saved: next_t1_dropped.csv")
print("Saved: next_churned_customers.csv")
print("Saved: next_tier_revenue_change.csv")

stayed  = (migration_df["movement"] == 0).sum()
rose    = (migration_df["movement"] > 0).sum()
dropped = (migration_df["movement"] < 0).sum()
print(f"\nMigration: stayed {stayed} | rose {rose} | dropped {dropped}")
print(f"Avg P1 rev: S${migration_df['p1_revenue'].mean():,.2f}")
print(f"Avg P2 rev: S${migration_df['p2_revenue'].mean():,.2f}")
print(f"Churned (P1 only): {len(churned_profile):,}")

print("\n" + "=" * 70)
print("DONE — all outputs in EDA/outputs_finals/")
print("=" * 70)
