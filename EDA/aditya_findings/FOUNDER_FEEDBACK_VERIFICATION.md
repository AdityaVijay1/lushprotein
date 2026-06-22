# Founder Feedback Verification — Requirement Mapping & Gap Audit

**Date:** June 2026  
**Auditor:** Aditya · Group 1 · ISSS603  
**Scope:** `EDA/aditya_findings/` + related decile/category/recommender work  
**Method:** Read-only audit — no new analysis run. Evidence checked against files on disk.

**Core founder question:**

> *"How should LushProtein treat different customers differently, how much should they spend on retention, and when/how should they cross-sell?"*

**Overall verdict:** **~85% addressed.** Segmentation, CM formula, MBA, cross-sell timing, sample strategy, and subscription connection are substantiated with data. Gaps are mainly **operational** (single T1–T5 export), **loyalty programme specifics** (HYROX-style rewards), **forward LTV modelling**, and **per-customer discount depth** in tier logic.

---

# Founder Requirement Mapping

## PART 1 — Customer Segregation + Contribution Margin

---

### R1.1 — Customer value definition (CM formula)

| | |
|---|---|
| **Founder asked** | Define contribution margin per customer: Revenue − COGS; understand discount, refund, and LTV impact |
| **Evidence** | `margin_analysis/MARGIN_ANALYSIS.md` · `enrich_finals_with_margin.py` · `lushprotein_decile.ipynb` · `FINDINGS_AND_RECOMMENDATIONS.md` §Rec 1 |
| **Current status** | ✅ **Mostly met** |

**What is measured:**

```
Per line (hybrid):
  GP = line_revenue − qty × unit_cost     [if COGS known — 74.7% of revenue]
  GP = line_revenue × 40%                 [if COGS missing — proxy fallback]

Customer CM = SUM(line GP)  →  column: true_gross_profit
```

| Component | Status | Detail |
|-----------|--------|--------|
| Revenue | ✅ | `Line: Total` / `Price: Total` — **net of discounts** (Shopify export format) |
| COGS | ✅ | 129 SKUs from LP Excel; 80.5% line coverage |
| Discount impact | ⚠️ Partial | Discounts **already netted into revenue** — documented. Separate **margin leakage** model for *future* promos (`margin_leakage_scenarios.csv`: 10% site-wide on D1 = S$14K/yr). No per-customer historical discount depth in tier assignment. |
| Refund impact | ❌ Gap | Refunds **excluded** — no per-order refund amount in export. `partially_refunded` orders (0.4%) kept at load; CM does not subtract refund value. Documented as limitation. |
| LTV impact | ⚠️ Partial | Historical CM used for tiers. Budget framework references "expected future CM (LTV proxy)" but **no forward LTV model** per customer. Full-base LTV exists in `EDA/outputs/12_ltv_by_first_channel.csv` — not merged into v2 decile table. |
| True CM vs proxy | ✅ | Labelled *"CM (hybrid COGS coverage)"* — not audited net profit. 25.3% of revenue uses 40% fallback. |

| **Gap** | Refunds not in CM; forward LTV not computed per customer; historical discount depth not a tier input |
| **Recommended improvement** | (1) Add one-slide caveat: "CM excludes refunds and fulfilment — conservative." (2) Merge `total_revenue` LTV from `customers.parquet` into `decile_customer_table.csv` for budget examples. (3) Ask LP for refund report if they want true net CM. |
| **Next Monday** | Use current CM for segmentation — sufficient for relative tier ranking. Flag refund caveat in deck footnote. |

---

### R1.2 — Customer segmentation logic (5 tiers)

| | |
|---|---|
| **Founder asked** | Break customers into tiers by CM; VIP = high CM + frequency + AOV; consider categories and subscription |
| **Evidence** | `outputs_finals/decile_customer_table.csv` (4,290 rows) · `lushprotein_decile.ipynb` · `decile_summary.ipynb` · `FINDINGS_AND_RECOMMENDATIONS.md` T1–T5 table · `Recommendation_A/outputs/klaviyo_crm_tiers.csv` |
| **Current status** | ✅ **Met** (thresholds defined; export split across 2 files) |

**Segmentation dimensions — verified with data:**

| Dimension | In analysis? | Evidence (v2 pool) |
|-----------|--------------|-------------------|
| Total CM | ✅ | `true_gross_profit`; CM D1 avg **S$230** |
| Order frequency (AOF) | ✅ | `finals_orders`; Freq D1 avg **3.6 orders** |
| AOV | ⚠️ Implicit | Computable: CM D1 AOV **S$160**; `is_top_both` AOV **S$109**; in `klaviyo_crm_tiers.csv` as `aov` — **not a tier gate** |
| Categories purchased | ✅ | `n_categories_ever`; D1 both avg **2.50** cats |
| Subscription | ✅ | `ever_subscribed`; D1 both **51%** subscribed |

**VIP anchor (founder criteria met):**

| Segment | N | Avg CM | AOF | AOV | Categories | Sub rate |
|---------|---|--------|-----|-----|------------|----------|
| **`is_top_both`** | **500** | S$265 | 4.3 | S$109 | 2.50 | 51% |
| CM D1 only | 358 | S$181 | 2.5 | — | — | — |
| Freq D1 only | 358 | S$62 | 3.6 | S$82 | 2.22 | 48% |

**Recommended 5-tier framework — status:**

| Tier | Criteria in docs | N (approx.) | Supported by data? |
|------|------------------|-------------|-------------------|
| **T1 VIP Champions** | `is_top_both` OR CM D1 + subscribed | 500–550 | ✅ |
| **T2 High-Value Repeaters** | CM D1 only / Freq D1 only / CM D2 + ≥2 orders | ~950 | ✅ |
| **T3 Growth Customers** | 2 orders, CM D3–D4 | ~400 | ✅ |
| **T4 First Purchasers** | 1 order, CM D2–D4 | ~2,350 | ✅ |
| **T5 Low Value** | CM D5 or 1 order + CM < S$15 | ~850 | ✅ |

**Thresholds:** v2 uses **equal-sized quintiles** (top 20% = D1) via `pd.qcut` — reproducible, not arbitrary.

| **Gap** | T1–T5 labels exist in `FINDINGS_AND_RECOMMENDATIONS.md` but **no single CSV** with `crm_treatment_tier` (T1–T5). `klaviyo_crm_tiers.csv` uses old 4-tier Rec A schema (VIP / Profit_D1 / Freq_D1 / Standard). AOV not used as explicit tier gate. |
| **Recommended improvement** | Create `outputs_finals/crm_treatment_tiers.csv` merging v2 decile + T1–T5 logic (script only — no re-analysis). Add AOV as secondary sort within CM D2. |
| **Next Monday** | Export `decile_customer_table.csv` to Klaviyo; tag `is_top_both` = VIP immediately. Map T2–T5 manually from decile columns until unified export is built. |

---

### R1.3 — Retention incentive budget framework

| | |
|---|---|
| **Founder asked** | "If a customer is worth $X, how much can we spend to retain them?" — X% of CM or LTV |
| **Evidence** | `FINDINGS_AND_RECOMMENDATIONS.md` §CM incentive budget · `margin_analysis/outputs/margin_leakage_scenarios.csv` |
| **Current status** | ✅ **Framework met** · ⚠️ **Founder must set X%** |

**Framework (documented):**

```
Max retention investment = X% × Customer CM
                      OR X% × Expected future CM (LTV proxy)
```

**Worked examples in docs:**

| Segment | CM | At 5% | At 10% | Use |
|---------|-----|-------|--------|-----|
| `is_top_both` (median) | S$189 | S$9 | S$19 | Partner gift — not % off |
| Rec A VIP (n=245) | S$358 | S$18 | S$36 | Premium experience |
| T2 CM D1 only | S$181 | S$9 | S$18 | Sub first-month incentive |
| T4 first purchaser | S$40 | S$2 | S$4 | Sachet sample cap |
| T5 one-and-done | S$9 | S$0.45 | S$0.90 | Email only |

**Why VIP deserves higher budget:** D1 both generate **57.7%** of pool CM from **20%** of customers; blanket 10% promo costs **S$14K/yr** on D1 with no retention gain.

| **Gap** | No founder-signed X% yet. Example uses S$358 VIP, not S$900 — S$900 would be top-decile whale (max CM in table = **S$2,797**). No automated "budget_per_customer" column in export. |
| **Recommended improvement** | Add column `suggested_budget_5pct` / `suggested_budget_10pct` to CRM export. Founder workshop: pick X% by tier (T1: experiences not cash; T4: sample COGS cap). |
| **Next Monday** | Present framework with 5% and 10% scenarios; ask founder to approve tier-specific X%. |

---

## PART 2 — Market Basket Analysis

---

### R2.1 — What products/categories to recommend

| | |
|---|---|
| **Founder asked** | Understand what to recommend; increase category penetration |
| **Evidence** | `recommendation_systems/outputs/sku_association_rules.csv` · `first_to_second_sku_matrix.csv` · `Recommendation_B/outputs/co_purchase_matrix_d1.csv` · `pitch_analysis/outputs/category_ladder_gp.csv` · `category_analysis/outputs/ACTIONABLE_INSIGHTS.md` |
| **Current status** | ✅ **Fully met** |

**Category ladder (business value proven):**

| Categories | Customers | Avg CM | Repeat |
|------------|-----------|--------|--------|
| 1 | 2,514 (59%) | S$59 | 17% |
| 2 | 1,216 (28%) | S$79 | 30% |
| 3 | 410 (10%) | S$144 | 55% |
| 4+ | 150 (3%) | S$249 | 82% |

**MBA rules (same cart):** Peach↔W.Grape 36% conf (333 orders) · Lean TMT→shaker 93%

**Cross-category (order 2):** Clear→Lean 53% among CM D1 · Lean→Clear 65%

**Category penetration goal:** 1 → 2 → 3 categories. Prize: 5% reach 3 cats = **S$10,693 GP/yr**.

| **Gap** | None material. Flavour-level rules exist; founder asked category-level — both covered. |
| **Next Monday** | Lead deck slide with category ladder chart + top 3 MBA rules. |

---

## PART 3 — Cross-Sell Timing

---

### R3.1 — When is the correct time to recommend?

| | |
|---|---|
| **Founder asked** | Samples at purchase vs before reorder? Correct cross-sell timing? |
| **Evidence** | `Recommendation_B/RECOMMENDATION_B.md` · `RECOMMENDATION_ARCHITECTURE.md` · `FOUNDER_MEETING_PREP.md` §2A · `EDA/outputs/12_reorder_interval_by_sku.csv` |
| **Current status** | ✅ **Met** — explicit answer: **B) before reorder window** for retention; **A) same cart** only for basket expansion |

**Timing strategy (documented):**

| Stage | Goal | Timing | Action |
|-------|------|--------|--------|
| **First purchase** | Create 2nd purchase | **Day 14 after delivery** | Cross-sell email (other protein) — NOT immediate post-checkout for category cross-sell |
| **Second purchase** | Increase breadth | **Day 7 after order 2 ships** | 3rd category push |
| **Before reorder** | Prevent lapse | **7–10 days before median reorder** | Reminder + sample |

**Reorder intervals (verified):**

| Product | Median reorder days | Source |
|---------|---------------------|--------|
| Clear Protein 500g (Peach / W.Grape) | **54** | `12_reorder_interval_by_sku.csv` |
| Lean Protein TMT 1kg | **35** | same |
| Collagen Glow | **42** | same |
| Creatine 250g | **66** | same |

**VIP timing:** Personalised offers via L4 item-CF on account page — not mass promo calendar.

| **Gap** | Day-14 is email-based; **physical sample-in-box at fulfilment** not costed per SKU. Reorder triggers not yet in Klaviyo (documented, not deployed). |
| **Recommended improvement** | Add Klaviyo flow spec: "reorder_date = last_order + median_sku_days − 10". Cost sample inserts with CM budget cap. |
| **Next Monday** | Build CS-01 Klaviyo flow (day 14 after order 1) — highest-ROI single action. |

---

## PART 4 — Single-Serve Sample Strategy

---

### R4.1 — When should single-serve packets be used?

| | |
|---|---|
| **Founder asked** | Which customer stage gets samples? Not random. |
| **Evidence** | `FINDINGS_AND_RECOMMENDATIONS.md` §Sample strategy · `RECOMMENDATION_ARCHITECTURE.md` §Sample strategy |
| **Current status** | ✅ **Met** |

**Recommendation matrix (in docs):**

| Customer stage | Goal | Sample strategy | CM budget rule |
|----------------|------|-----------------|----------------|
| **First purchase** | Reduce uncertainty | 1 complementary sachet (e.g. Clear → collagen) | ≤ 5% of expected CM uplift |
| **Day 14 (order 1)** | Drive order 2 | Category discovery sachet in email/insert | Sample COGS only |
| **Second purchase** | Increase basket | Cross-category sample | T3 Growth tier |
| **Third+ / VIP** | Loyalty reward | Exclusive sample / partner gift | T1 — experience not discount |
| **Before reorder** | Prevent lapse | Next-flavour sample | 7–10 days before median reorder |

**Explicit rule:** Do NOT attach samples to every first order by default — justify against CM framework.

| **Gap** | No SKU-level sample COGS table (cost per sachet). Third-purchase VIP sample not tied to named partners. |
| **Recommended improvement** | LP provides sachet unit cost → add to budget calculator. |
| **Next Monday** | Propose 1 sachet insert for Clear first orders only (A/B test 500 orders). |

---

## PART 5 — Loyalty Programme Review

---

### R5.1 — Avoid failed generic points programme; target VIP loyalty

| | |
|---|---|
| **Founder asked** | Previous loyalty programme failed (low traffic). Recommend targeted VIP programme — partner rewards, HYROX, events, early access |
| **Evidence** | `FINDINGS_AND_RECOMMENDATIONS.md` T1 treatment · `Recommendation_A/RECOMMENDATION_A.md` · `FOUNDER_MEETING_PREP.md` |
| **Current status** | ⚠️ **Partially met** |

**What exists:**
- T1 VIP treatment: exclusive access, partner rewards, early launches, **no heavy discounts**
- Rec A: exclude VIP from site-wide % promos (S$14K protected)
- Segmentation: **500 `is_top_both`** = addressable VIP pool

**What is missing:**
- No explicit section: *"Why generic points-based loyalty failed"*
- Founder examples (**HYROX tickets, massage vouchers, exclusive events**) **not named** in recommendations
- No traffic/engagement analysis of prior loyalty programme (no data provided)
- No loyalty programme ROI model

| **Gap** | Strategic direction correct; **operational loyalty playbook** with founder-specific reward types not written |
| **Recommended improvement** | Add `LOYALTY_PROGRAM_VIP.md`: (1) why points fail for low-traffic DTC, (2) T1-only programme design, (3) example rewards mapped to CM budget (S$19–36/customer at 5–10%), (4) exclude T4/T5 from loyalty overhead |
| **Next Monday** | Propose "VIP Champions Club" for 500 `is_top_both` only — no points, partner-led rewards. Ask founder which partners (HYROX etc.) are feasible. |

---

# Quality Check — Founder Questions Coverage

| Founder question | Data evidence | Business interpretation | Action | Implementation |
|------------------|---------------|-------------------------|--------|----------------|
| Who are valuable customers? | `decile_customer_table.csv`, 500 `is_top_both` | Top 20% = 57.7% CM | T1 VIP programme | Tag in Klaviyo |
| How to treat differently? | T1–T5 framework | Discounts hurt VIPs | Different promo policy per tier | Rec A guardrail |
| How much to spend on retention? | CM × X% framework | S$9–36 range by tier | Founder sets X% | Budget column in export |
| When to cross-sell? | Day 14 / day 7 / pre-reorder | After experience, before reorder | CS-01–04 flows | Klaviyo week 1 |
| What to recommend? | MBA + co-purchase matrix | Category ladder | Rule + association deploy | PDP + email |
| When to sample? | Stage matrix | CM-budgeted investment | Sachet A/B test | Fulfilment insert |
| Subscription connection? | 62% vs 19% repeat | Lock after 2nd purchase | SUB-01 at day 48 | Klaviyo week 4 |
| Loyalty programme? | VIP segmentation only | Targeted not mass | VIP Champions Club | **Gap — needs doc** |

---

# Final Actionable Insights

## Insight 1: Contribution Margin Driven Customer Segmentation

### Formula (use in deck)

```
Contribution Margin (hybrid) = Σ line_revenue − COGS   [where known]
                             = Σ line_revenue × 40%   [proxy fallback]
Discounts: already in net revenue
Refunds: NOT subtracted (disclose as limitation)
Label: "CM proxy using hybrid COGS coverage"
```

### Tiers and thresholds

| Tier | Gate | N | Avg CM | Treatment |
|------|------|---|--------|-----------|
| T1 | `is_top_both` | 500 | S$265 | Partner rewards, early access — **no % off** |
| T2 | CM D1 or Freq D1, not both | 716 | S$62–181 | Subscribe & Save, bundles |
| T3 | 2 orders, mid CM | ~400 | S$50 | Day-14 cross-sell, samples |
| T4 | 1 order, trial | ~2,350 | S$30–50 | Onboarding, 2nd purchase journey |
| T5 | CM D5 / one-and-done | ~850 | S$9 | Low-cost automation only |

### Incentive budget (founder sets X%)

| Tier | Illustrative CM | 5% budget | 10% budget |
|------|-----------------|-----------|------------|
| T1 VIP | S$265 | S$13 | S$27 |
| T1 VIP (Rec A whales) | S$358 | S$18 | S$36 |
| T2 | S$120 | S$6 | S$12 |
| T4 | S$40 | S$2 | S$4 |
| T5 | S$9 | <S$1 | S$1 |

**What LP should do next Monday:** Export `is_top_both` to Klaviyo as "VIP Champions"; block from site-wide promos; approve X% budget per tier.

---

## Insight 2: Market Basket + Recommendation Timing Engine

### Recommended products (by layer)

| Layer | When | What to recommend | Evidence |
|-------|------|-------------------|----------|
| L1 First purchase | Day 1–3 | Other protein (Clear↔Lean) | 53–65% D1 co-purchase |
| L2 Same cart | Checkout | Peach + W.Grape bundle | 36% confidence |
| L3 Post-purchase | Day 14 / Day 7 | 2nd then 3rd category | 739 SKU transitions |
| L4 Logged-in | 3+ orders | Similar SKU (CF) | 83-SKU matrix |
| Subscription | Order 2 + 48d | Subscribe & Save hero SKU | 62% vs 19% repeat |

### Timing (founder answer)

- **Cross-category retention:** Day 14 after order 1 — **not** at checkout
- **Basket expansion:** Same cart (Layer 2) — at checkout/PDP
- **Samples:** Before reorder window (Clear 54d, Lean 35d, Collagen 42d, Creatine 66d)
- **Subscription:** After 2nd successful purchase

### Sample matrix

| Stage | Sample? | Why |
|-------|---------|-----|
| 1st purchase | Optional 1 sachet | Reduce category uncertainty |
| 2nd purchase journey | Yes — cross-category | Drive breadth |
| 3rd+ / VIP | Partner/exclusive sample | Loyalty — not acquisition |
| Random / all orders | **No** | CM-budgeted only |

**What LP should do next Monday:** Launch CS-01 (Clear→Lean, day 14). Add Peach+W.Grape PDP bundle. Schedule SUB-01 for repeat non-subs.

---

# Gap Summary — Priority Fixes

| Priority | Gap | Effort | File to add/update |
|----------|-----|--------|-------------------|
| **P0** | Unified T1–T5 Klaviyo export | ✅ Done | `outputs_finals/crm_treatment_tiers.csv` |
| **P0** | Cross-sell + sample timing matrix | ✅ Done | `outputs/cross_sell_timing_and_samples.csv` |
| **P0** | Dollar budgets per decile/tier | ✅ Done | `outputs/cm_decile_incentive_budgets.csv` |
| **P1** | Loyalty programme doc with HYROX/events | Partial | T1 incentives in `CRM_AND_INCENTIVES.md` |
| **P1** | Reorder-triggered Klaviyo spec | Doc + flow | `FOUNDER_MEETING_PREP.md` or new timing doc |
| **P2** | Refund-adjusted CM | Needs LP refund data | Blocked |
| **P2** | Per-customer historical discount depth in tiers | Small analysis | Optional |
| **P2** | Sachet unit cost for sample budget | Needs LP input | Blocked |

---

# Document Cross-Reference (what already answers the prompt)

| Prompt section | Primary file | Status |
|----------------|--------------|--------|
| CM framework | `FINDINGS_AND_RECOMMENDATIONS.md` §Rec 1 | ✅ |
| 5 CRM tiers | `FINDINGS_AND_RECOMMENDATIONS.md` T1–T5 | ✅ |
| Incentive budget | `FINDINGS_AND_RECOMMENDATIONS.md` §CM incentive | ✅ |
| MBA / category ladder | `pitch_analysis/outputs/category_ladder_gp.csv` | ✅ |
| 4-layer recommender | `recommendation_systems/RECOMMENDATION_ARCHITECTURE.md` | ✅ |
| Cross-sell timing | `Recommendation_B/RECOMMENDATION_B.md` | ✅ |
| Sample strategy | `RECOMMENDATION_ARCHITECTURE.md` | ✅ |
| VIP guardrail | `Recommendation_A/RECOMMENDATION_A.md` | ✅ |
| Decile evidence | `decile_summary.ipynb` · v2 PNGs/CSV | ✅ |
| Loyalty specifics | — | ❌ Gap |
| Unified CRM export | — | ❌ Gap |

---

# Audit Conclusion

The existing work **does answer** the founder's core question with data-backed segmentation, CM-driven budgets, MBA-driven recommendations, and lifecycle-timed cross-sell. The analysis is **founder-ready for a meeting** with two additions before final delivery:

1. **Operational:** Single `crm_treatment_tiers.csv` with T1–T5 labels for Klaviyo import  
2. **Strategic:** `LOYALTY_PROGRAM_VIP.md` naming targeted rewards (HYROX, events) and explicitly rejecting points-based mass loyalty

No full re-analysis is required. Remaining gaps are documentation, export hygiene, and founder inputs (X%, sachet COGS, partner list).

**Regenerate evidence (if needed):**

```bash
python EDA/aditya_findings/enrich_finals_with_margin.py
# Re-run lushprotein_decile.ipynb
python EDA/aditya_findings/run_all.py
```
