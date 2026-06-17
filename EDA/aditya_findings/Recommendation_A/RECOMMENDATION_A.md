# Recommendation A — VIP Guardrail (Operational, Not the Lead Story)

**Script:** `run_recommendation_a.py`  
**Status:** Keep and implement — but **do not lead the deck with this.**

---

## Why it stays (but isn't the headline)

Rec A is **correct**: VIP customers should not get the same 10%-off codes as one-and-dones.

But the prize is **S$14K GP/yr** (margin leakage stopped) — real, but **smaller than**:
- Category ladder (S$11K–17K from moving single-cat buyers up)
- Subscription conversion (S$2–4K in pool + 62% vs 19% repeat rate proof)
- Pack-size upgrade (S$13K potential)

**Pitch order:** Lead with **Rec C (category ladder)** and **Rec D (subscription)**. Rec A is the **guardrail** that stops you from undermining those gains with blanket promos.

---

## What to do (unchanged)

Export `outputs/klaviyo_crm_tiers.csv` → tag in Klaviyo/Shopify:

| Tier | Count | Policy |
|------|-------|--------|
| VIP | 245 | No site-wide % off |
| Profit D1 | 184 | No blanket promo |
| Freq D1 | 184 | Replenishment only |
| Standard | 3,677 | Normal promos |

---

## The one number (for appendix slide)

10% site-wide discount on profit D1 = **S$14K GP lost** (true COGS).

---

## Proof charts

- `fig_gp_by_decile_true.png`
- `fig_discount_erosion.png`
- `fig_crm_tier_summary.png`

See also **H5** in `pitch_analysis/HYPOTHESES.md`.
