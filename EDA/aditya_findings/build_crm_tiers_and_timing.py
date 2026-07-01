"""
build_crm_tiers_and_timing.py

Automates:
  1. T1–T5 CRM treatment tiers (v2 decile thresholds)
  2. CM-based incentive budgets (5% and 10% of contribution margin)
  3. Cross-sell + sample timing matrix (email day, pre-reorder sample day, products)

Outputs → EDA/outputs_finals/ and EDA/aditya_findings/outputs/

Run: python EDA/aditya_findings/build_crm_tiers_and_timing.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

FINDINGS_DIR = Path(__file__).resolve().parent
EDA_DIR = FINDINGS_DIR.parent
FINALS_DIR = EDA_DIR / "outputs_finals"
AF_OUT = FINDINGS_DIR / "outputs"
AF_OUT.mkdir(parents=True, exist_ok=True)

# Incentive rates (founder can adjust; documented in outputs)
BUDGET_PCT_LOW = 0.05
BUDGET_PCT_HIGH = 0.10

# Reorder medians from 12_reorder_interval_by_sku.csv (hero SKUs)
REORDER_MEDIAN_DAYS = {
    "Clear Protein": 54,
    "Lean Protein": 35,
    "Collagen Glow": 42,
    "Soy Protein": 84,
    "Accessories": 35,  # use hero protein reorder window — not shaker reorder (88d)
    "Other": 50,
    "Unknown": 50,
    "micronized-creatine-monohydrate": 66,
}

# Cross-category recommendation map (from co_purchase_matrix_all + D1 matrix)
CROSS_CATEGORY_MAP = {
    "Clear Protein": {
        "recommend_category": "Lean Protein",
        "sample_category": "Collagen Glow",
        "sample_product": "Collagen Glow 25g sachet or Lean 40g single-serve (TMT/Taro)",
        "email_day": 14,
        "evidence_pct": 25.0,
        "evidence_note": "25% all-pool / 53% D1 co-purchase Clear→Lean",
    },
    "Lean Protein": {
        "recommend_category": "Clear Protein",
        "sample_category": "Collagen Glow",
        "sample_product": "Clear 25g sachet (Peach or White Grape) or Collagen sachet",
        "email_day": 14,
        "evidence_pct": 28.9,
        "evidence_note": "28.9% all-pool / 65% D1 co-purchase Lean→Clear",
    },
    "Collagen Glow": {
        "recommend_category": "Clear Protein",
        "sample_category": "Lean Protein",
        "sample_product": "Clear 25g sachet Peach OR Lean 40g single-serve",
        "email_day": 21,
        "evidence_pct": 23.8,
        "evidence_note": "Collagen-first buyers need protein attach; 30.5% repeat",
    },
    "Accessories": {
        "recommend_category": "Lean Protein",
        "sample_category": "Clear Protein",
        "sample_product": "Clear 25g sachet — do NOT send another shaker",
        "email_day": 7,
        "evidence_pct": 41.2,
        "evidence_note": "Accessories→Lean 41%; shaker-led acq only 20% repeat",
    },
    "Soy Protein": {
        "recommend_category": "Clear Protein",
        "sample_category": "Lean Protein",
        "sample_product": "Clear or Lean 25g/40g single-serve",
        "email_day": 14,
        "evidence_pct": 10.0,
        "evidence_note": "Low co-purchase; push hero protein",
    },
    "Other": {
        "recommend_category": "Clear Protein",
        "sample_category": "Lean Protein",
        "sample_product": "Discovery sampler 6-pack OR Clear 25g sachet",
        "email_day": 14,
        "evidence_pct": 15.5,
        "evidence_note": "Default to hero protein ladder",
    },
    "Unknown": {
        "recommend_category": "Clear Protein",
        "sample_category": "Lean Protein",
        "sample_product": "Clear 25g sachet Peach",
        "email_day": 14,
        "evidence_pct": 9.1,
        "evidence_note": "Fallback — map SKU in PRODUCT_MAP",
    },
}

TIER_TREATMENT = {
    "T1": "VIP Champions — exclusive access, partner rewards (HYROX/events), early launches. NO % discounts.",
    "T2": "High-Value Repeaters — Subscribe & Save, category bundles, 2nd/3rd category push.",
    "T3": "Growth Customers — day-14 cross-sell, pre-reorder category sample, 2nd-category incentive.",
    "T4": "First Purchasers — onboarding series, complementary sachet optional, 2nd-purchase journey.",
    "T5": "Low Value — automated win-back only; no product gifts.",
}


def assign_treatment_tier(row: pd.Series) -> str:
    """Automated T1–T5 from v2 decile + order behaviour."""
    cm_dec = row.get("contribution_margin_decile", "D5")
    orders = int(row.get("finals_orders", 0) or 0)
    cm = float(row.get("true_gross_profit", 0) or 0)
    is_both = bool(row.get("is_top_both", False))
    is_cm = bool(row.get("is_top_cm", False))
    is_freq = bool(row.get("is_top_freq", False))
    subscribed = bool(row.get("ever_subscribed", False))

    if is_both or (is_cm and subscribed):
        return "T1"
    if is_cm or is_freq or (cm_dec == "D2" and orders >= 2):
        return "T2"
    if orders == 2 and cm_dec in ("D3", "D4"):
        return "T3"
    if orders == 1 and cm_dec in ("D2", "D3", "D4"):
        return "T4"
    if cm_dec == "D5" or (orders == 1 and cm < 15):
        return "T5"
    if orders >= 2:
        return "T3"
    return "T4"


def promo_policy(tier: str) -> str:
    policies = {
        "T1": "NO_SITEWIDE_PCT_OFF | experiences_only",
        "T2": "SUBSCRIBE_AND_SAVE | bundle_offers | no_blanket_10pct",
        "T3": "CROSS_SELL_SAMPLE | category_incentive",
        "T4": "ONBOARDING | sachet_cap_5pct_cm",
        "T5": "WINBACK_EMAIL_ONLY",
    }
    return policies.get(tier, "STANDARD")


def incentive_type(tier: str) -> str:
    types = {
        "T1": "partner_reward|early_access|event_invite|merch_VIP",
        "T2": "subscribe_discount|bundle|category_sample",
        "T3": "cross_category_sachet|second_order_incentive",
        "T4": "onboarding_sachet|education",
        "T5": "none_or_email_only",
    }
    return types.get(tier, "standard")


def main():
    print("=" * 72)
    print("CRM TIERS + INCENTIVE BUDGETS + CROSS-SELL TIMING")
    print("=" * 72)

    decile_path = FINALS_DIR / "decile_customer_table.csv"
    if not decile_path.exists():
        raise FileNotFoundError(f"Run lushprotein_decile.ipynb first: {decile_path}")

    df = pd.read_csv(decile_path)
    df["customer_id"] = df["customer_id"].astype(str)
    # lushprotein_decile.ipynb exports profit_decile / is_top_profit (D1–D5)
    if "contribution_margin_decile" not in df.columns and "profit_decile" in df.columns:
        df["contribution_margin_decile"] = df["profit_decile"]
    if "is_top_cm" not in df.columns and "is_top_profit" in df.columns:
        df["is_top_cm"] = df["is_top_profit"]
    df["aov"] = df["finals_revenue"] / df["finals_orders"].clip(lower=1)

    # ── T1–T5 assignment ─────────────────────────────────────────────────────
    df["crm_treatment_tier"] = df.apply(assign_treatment_tier, axis=1)
    df["promo_policy"] = df["crm_treatment_tier"].map(promo_policy)
    df["incentive_types"] = df["crm_treatment_tier"].map(incentive_type)
    df["retention_budget_5pct_sgd"] = (df["true_gross_profit"] * BUDGET_PCT_LOW).round(2)
    df["retention_budget_10pct_sgd"] = (df["true_gross_profit"] * BUDGET_PCT_HIGH).round(2)
    df["max_sample_cost_sgd"] = np.where(
        df["crm_treatment_tier"].isin(["T1", "T2"]),
        df["retention_budget_10pct_sgd"],
        np.where(
            df["crm_treatment_tier"].isin(["T3", "T4"]),
            df["retention_budget_5pct_sgd"],
            0.0,
        ),
    ).round(2)

    export_cols = [
        "customer_id",
        "crm_treatment_tier",
        "contribution_margin_decile",
        "order_freq_decile",
        "true_gross_profit",
        "finals_orders",
        "finals_revenue",
        "aov",
        "n_categories_ever",
        "ever_subscribed",
        "is_top_cm",
        "is_top_freq",
        "is_top_both",
        "first_channel",
        "first_product_cat",
        "retention_budget_5pct_sgd",
        "retention_budget_10pct_sgd",
        "max_sample_cost_sgd",
        "promo_policy",
        "incentive_types",
    ]
    crm_out = FINALS_DIR / "crm_treatment_tiers.csv"
    df[export_cols].to_csv(crm_out, index=False)
    df[export_cols].to_csv(AF_OUT / "crm_treatment_tiers.csv", index=False)
    print(f"Wrote {crm_out} ({len(df):,} customers)")

    # ── Decile × tier budget summary ─────────────────────────────────────────
    tier_summary = (
        df.groupby("crm_treatment_tier", observed=True)
        .agg(
            n_customers=("customer_id", "count"),
            avg_cm=("true_gross_profit", "mean"),
            median_cm=("true_gross_profit", "median"),
            avg_orders=("finals_orders", "mean"),
            avg_aov=("aov", "mean"),
            pct_subscribed=("ever_subscribed", "mean"),
            budget_5pct_avg=("retention_budget_5pct_sgd", "mean"),
            budget_10pct_avg=("retention_budget_10pct_sgd", "mean"),
            max_sample_avg=("max_sample_cost_sgd", "mean"),
        )
        .reset_index()
    )
    tier_summary["treatment"] = tier_summary["crm_treatment_tier"].map(TIER_TREATMENT)
    tier_summary = tier_summary.round(2)
    tier_path = AF_OUT / "crm_tier_incentive_summary.csv"
    tier_summary.to_csv(tier_path, index=False)
    print(f"Wrote {tier_path}")

    cm_decile_summary = (
        df.groupby("contribution_margin_decile", observed=True)
        .agg(
            n=("customer_id", "count"),
            avg_cm=("true_gross_profit", "mean"),
            median_cm=("true_gross_profit", "median"),
            budget_5pct=("retention_budget_5pct_sgd", "mean"),
            budget_10pct=("retention_budget_10pct_sgd", "mean"),
            max_sample=("max_sample_cost_sgd", "mean"),
        )
        .reset_index()
        .round(2)
    )
    cm_path = AF_OUT / "cm_decile_incentive_budgets.csv"
    cm_decile_summary.to_csv(cm_path, index=False)
    print(f"Wrote {cm_path}")

    # ── Cross-sell + sample timing matrix ────────────────────────────────────
    timing_rows = []
    for cat, spec in CROSS_CATEGORY_MAP.items():
        reorder = REORDER_MEDIAN_DAYS.get(cat, 50)
        email_day = spec["email_day"]
        # Physical sample: BEFORE reorder window (not in first order box)
        sample_ship_day = max(email_day + 7, reorder - 10)
        days_before_reorder = reorder - sample_ship_day

        timing_rows.append({
            "first_product_category": cat,
            "cross_sell_category": spec["recommend_category"],
            "sample_category": spec["sample_category"],
            "sample_product_suggestion": spec["sample_product"],
            "email_cross_sell_day_after_delivery": email_day,
            "physical_sample_day_after_delivery": sample_ship_day,
            "median_reorder_days": reorder,
            "sample_timing_rationale": (
                f"Ship sample on day {sample_ship_day} ({days_before_reorder}d before median reorder at {reorder}d) — "
                "NOT in first order box. Customer tries new category before reorder decision."
            ),
            "email_timing_rationale": (
                f"Day {email_day} after order 1 delivery — product experienced, reorder not yet placed."
            ),
            "at_checkout_action": "Layer 2 only: same-category bundle (e.g. Peach+W.Grape) — not cross-category",
            "co_purchase_evidence_pct": spec["evidence_pct"],
            "evidence_note": spec["evidence_note"],
            "purchase_number_for_sample": "1st order buyers (T4/T3); 2nd order buyers get 3rd-category sample day 7",
            "subscribe_trigger_day": 48 if cat in ("Clear Protein", "Lean Protein") else 42,
        })

    timing_df = pd.DataFrame(timing_rows)
    timing_path = AF_OUT / "cross_sell_timing_and_samples.csv"
    timing_df.to_csv(timing_path, index=False)
    timing_df.to_csv(FINDINGS_DIR / "recommendation_systems" / "outputs" / "cross_sell_timing_and_samples.csv", index=False)
    print(f"Wrote {timing_path}")

    # ── Purchase-stage sample matrix ─────────────────────────────────────────
    stage_rows = [
        {
            "purchase_stage": "1st purchase (T4)",
            "goal": "Drive 2nd order + 2nd category",
            "email_action": "Day 14: recommend other protein category",
            "physical_sample": f"Day {44 if True else 0}: ship cross-category sachet BEFORE reorder (Clear→Collagen sachet)",
            "in_checkout": "Optional: do NOT default — cost cap = 5% CM (~S$2-4)",
            "subscribe": "No — prove fit first",
            "why_not_at_first_order": "Category cross-sell sample at checkout dilutes focus; pre-reorder timing lifts 2nd-category attach",
        },
        {
            "purchase_stage": "2nd purchase (T3)",
            "goal": "3rd category by order 3",
            "email_action": "Day 7 after order 2: Collagen or 2nd flavour",
            "physical_sample": "Ship 3rd-category sachet with order 2 confirmation or day 7 insert",
            "in_checkout": "Bundle upsell (Clear+Lean) if still 1-cat",
            "subscribe": "SUB-01: offer S&S 48 days after order 2 if not subscribed",
            "why_not_at_first_order": "N/A — second purchase proved repeat intent",
        },
        {
            "purchase_stage": "3rd+ / VIP (T1)",
            "goal": "Loyalty + retention",
            "email_action": "Personalised L4 recommendations",
            "physical_sample": "Partner merch / shaker / event (budget = 10% CM, S$19-36)",
            "in_checkout": "VIP early access SKUs",
            "subscribe": "VIP Subscribe tier if not already (51% of is_top_both already sub)",
            "why_not_at_first_order": "VIP gifts reward loyalty, not acquisition",
        },
    ]
    # Fix Clear protein sample day in first row
    stage_rows[0]["physical_sample"] = (
        "Day 44 (Clear) / Day 25 (Lean) / Day 32 (Collagen): cross-category sachet BEFORE median reorder"
    )
    stage_df = pd.DataFrame(stage_rows)
    stage_path = AF_OUT / "sample_strategy_by_purchase_stage.csv"
    stage_df.to_csv(stage_path, index=False)
    print(f"Wrote {stage_path}")

    manifest = {
        "pool_customers": len(df),
        "tier_counts": df["crm_treatment_tier"].value_counts().to_dict(),
        "budget_pct_low": BUDGET_PCT_LOW,
        "budget_pct_high": BUDGET_PCT_HIGH,
        "outputs": [
            str(crm_out),
            str(tier_path),
            str(cm_path),
            str(timing_path),
            str(stage_path),
        ],
    }
    (AF_OUT / "crm_tiers_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("\nTier counts:", manifest["tier_counts"])
    print("Done.")


if __name__ == "__main__":
    main()
