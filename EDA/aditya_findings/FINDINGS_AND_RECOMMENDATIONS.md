# LushProtein — Findings & Recommendations (Final Consolidated)

**Author:** Aditya · Group 1 · ISSS603  
**Data:** `EDA/outputs_finals/` · 4,290-customer decile pool · hybrid COGS on **74.7%** of revenue  
**Date:** June 2026 (updated after v2 decile merge)

> **Founder questions this doc answers:**
> 1. *Who do I treat differently, why, when, and how much can I afford to spend?*
> 2. *How do recommendations + subscriptions increase retention and lifetime value?*

**Deck structure:** Lead with **Recommendation 1** (segmentation + CM) and **Recommendation 2** (recommendation engine + subscription). Legacy Rec A–E are folded into these two pillars — see Section 5.

---

## Executive summary

**67.6% of customers buy once and never return.** Revenue and contribution margin are concentrated: the top 20% of customers (CM D1) generate **57.7%** of total contribution margin. **500 customers** are D1 on *both* contribution margin and order frequency — the highest-confidence VIP segment.

The fix is not treating every customer the same. LushProtein should:

1. **Segment by economic value** (contribution margin) and **behaviour** (order frequency, categories, subscription) — then assign different CRM treatment and incentive budgets per tier.
2. **Deploy a 4-layer recommendation engine** tied to the customer lifecycle — cold-start rules → same-cart MBA → timed post-purchase cross-sell → logged-in personalisation — with **Subscribe & Save** as the end-state for proven repeaters.

**Combined measurable opportunity (existing prize models):** **S$30–35K GP/yr** from category ladder + subscription + acquisition fixes, plus **S$14K GP protected** by excluding VIPs from blanket discounts.

---

## Recommendation 1: Customer Value Segmentation + Contribution Margin Driven CRM

### The core insight

> *"We should stop treating every customer equally."*

A one-time buyer averaging **S$9** contribution margin should not receive the same promotions as a **500-customer VIP cohort** averaging **S$265** CM with **51%** already subscribed. Blanket 10% site-wide discounts cost **S$14K GP/yr** if they hit profit D1 customers — with no retention gain.

---

### Contribution margin — definition and formula

**Founder-scoped formula:**

```
Contribution Margin = Net Revenue − COGS
```

Variable fulfillment costs and refunds are excluded (no reliable per-order data). Discounts are already netted in Shopify revenue.

**Our implementation (hybrid COGS coverage):**

| Line type | Gross profit per line |
|-----------|----------------------|
| COGS known (74.7% of revenue) | `line_revenue − quantity × unit_cost` |
| COGS missing | `line_revenue × 40%` (proxy fallback) |

**Customer contribution margin** = SUM(line gross profit)

**Label in all founder materials:** *Contribution Margin (CM — hybrid COGS coverage)*. Do not call this audited net profit.

**Coverage:** 129 SKUs with unit cost · **80.5%** of line items · **70.5%** measured margin on covered lines (vs 40% assumed proxy).

**Proof:** `margin_analysis/MARGIN_ANALYSIS.md` · `margin_analysis/outputs/`

---

### Latest segmentation foundation (v2 decile — June 2026)

**Source:** `lushprotein_decile.ipynb` → `outputs_finals/decile_customer_table.csv`  
**Pool:** 4,290 customers (`finals_eligible`, 100% Marketplace excluded)

| Ranking | Metric | D1 = | Customers/tier |
|---------|--------|------|----------------|
| **Contribution Margin Decile** | `true_gross_profit` | Highest CM | ~858 each (D1–D5) |
| **Order Frequency (AOF) Decile** | `finals_orders` | Most orders | ~858 each (D1–D5) |

**Why 5 tiers not 10:** Founder meeting ask — simpler for CRM and non-technical stakeholders. ~858 customers per tier is large enough for reliable analysis.

#### Headline v2 stats

| Segment | N | Avg CM | Avg orders | Key share |
|---------|---|--------|------------|-----------|
| **CM D1** | 858 | **S$230** | 3.1 | **57.7%** of pool CM |
| CM D5 | 858 | S$9 | 1.1 | 2.2% of pool CM |
| **Freq D1** | 858 | S$181 | **3.6** | **45.4%** of pool orders |
| **`is_top_both`** | **500** | **S$265** | ~3.4 | **11.7%** of pool — VIP core |
| CM D1 only | 358 | S$181 | ~2.5 | High value, lower frequency |
| Freq D1 only | 358 | S$62 | 3.6 | Loyal but lower spend |

**Overlap insight:** CM D1 and Freq D1 are *not* the same people. Only **500** (58% of each D1 group) rank D1 on both — use `is_top_both` as the VIP anchor.

**D1 vs D2 gap (CM):** D1 avg **S$230** vs D2 **S$81** (2.8×). Margin *rates* are similar (~69–70%) — the gap is **order count** (3.1 vs 1.5) and **category breadth** (2.26 vs 1.68 categories). D2 is a frequency + breadth problem, not a discount problem.

**Charts:** `decile_contribution_margin.png` · `decile_order_frequency.png` · `decile_overlap_heatmap.png`  
**Slide summary:** `decile_summary.ipynb`

---

### Practical CRM tier system (5 treatment tiers)

Map v2 deciles + behaviour into **actionable Klaviyo/Shopify segments**:

| CRM Tier | Name | Criteria (implementable) | N (approx.) | Avg CM |
|----------|------|------------------------|-------------|--------|
| **T1** | **VIP Champions** | `is_top_both = True` OR (CM D1 + ever_subscribed) | **500–550** | S$265+ |
| **T2** | **High-Value Repeaters** | CM D1 only OR Freq D1 only OR (CM D2 + ≥2 orders) | **~950** | S$80–181 |
| **T3** | **Growth Customers** | Exactly 2 orders, CM D3–D4, not D1 on either axis | **~400** | S$50 |
| **T4** | **First Purchasers** | 1 order, CM D2–D4 (trial mode) | **~2,350** | S$30–50 |
| **T5** | **Low Value / One-and-Done** | CM D5 OR 1 order + CM < S$15 | **~850** | S$9 |

#### Treatment by tier

| Tier | Treatment | Do NOT |
|------|-----------|--------|
| **T1 VIP Champions** | Exclusive access, early launches, partner rewards, referral perks, personal thank-you | Heavy % discounts, site-wide promo codes |
| **T2 High-Value Repeaters** | Subscribe & Save conversion, category bundles, 2nd/3rd category push | Blanket 10–15% off |
| **T3 Growth Customers** | 2nd category incentive, sampling, day-14 cross-sell email | Premium discounting |
| **T4 First Purchasers** | Onboarding series, second-purchase journey, complementary sample | Treat as loyal — they haven't repeated yet |
| **T5 Low Value** | Low-cost automation, selective win-back (recent only) | High CAC manual outreach |

**Export for Klaviyo:** Merge `decile_customer_table.csv` with `Recommendation_A/outputs/klaviyo_crm_tiers.csv` for operational tags.

**Legacy guardrail (Rec A):** Exclude T1/T2 CM D1 from site-wide % promos → **S$14K GP/yr protected**. See `Recommendation_A/RECOMMENDATION_A.md`.

---

### Contribution margin incentive budget framework

**Founder question:** *"If we give a customer an incentive, how much can we afford?"*

This is a **CRM decision framework**, not a fixed percentage. LP should set X% based on margin goals, payback period, and channel CAC.

```
Maximum retention investment per customer
  = X% × Customer Contribution Margin
  OR
  = X% × Expected future CM (LTV proxy)
```

| Input | How to get it |
|-------|---------------|
| Customer CM | `decile_customer_table.csv` → `true_gross_profit` |
| Expected future CM | CM × projected orders (use reorder intervals + category ladder uplift) |
| X% | Founder sets by tier — higher for T1 retention, lower for T4 acquisition |

#### Worked examples (illustrative — LP sets final X%)

| Segment | Customer CM | If X = 5% | If X = 10% | Appropriate use |
|---------|-------------|-----------|------------|-----------------|
| T1 VIP (`is_top_both`, median) | S$189 | S$9 | S$19 | Partner gift, exclusive sample — **not** % off |
| T1 VIP (top quartile) | S$289+ | S$14 | S$29 | Event invite, loyalty credit |
| Legacy VIP tier (Rec A, n=245) | S$358 avg | S$18 | S$36 | Premium experience budget |
| T2 CM D1 only | S$181 | S$9 | S$18 | Subscribe & Save first-month incentive |
| T4 first purchaser | S$40 | S$2 | S$4 | Sachet sample cost cap |
| T5 one-and-done | S$9 | S$0.45 | S$0.90 | Win-back email only — no product gift |

**Rule of thumb for deck:** Never spend more on an incentive than the **incremental CM** you expect from the action. A S$5 sample for a Clear Protein buyer is justified if it lifts 2nd-category conversion (avg uplift **S$20–85 GP** per step on the category ladder).

**Margin leakage proof:** 10% discount on 429 profit-D1 (10-tier) = **S$14K GP/yr** erosion. `margin_analysis/outputs/margin_leakage_scenarios.csv`

---

### Market basket + category ladder (connects segmentation to product strategy)

**MBA source:** `recommendation_systems/outputs/sku_association_rules.csv` · `Recommendation_B/outputs/co_purchase_matrix_d1.csv`

**Category ladder source:** `pitch_analysis/outputs/category_ladder_gp.csv`

| Categories ever purchased | Customers | % pool | Avg CM | Repeat rate |
|----------------------------|-----------|--------|--------|-------------|
| 1 | 2,514 | **59%** | S$59 | 17% |
| 2 | 1,216 | 28% | S$79 | 30% |
| 3 | 410 | 10% | **S$144** | **55%** |
| 4+ | 150 | 3% | S$249 | 82% |

**The ladder:**

```
Protein only  →  Protein + 2nd category  →  Protein + 3rd category
   (59%)              (28%)                      (10%)
  S$59 CM            S$79 CM                   S$144 CM
```

**MBA connections:**

| Pattern | Evidence | Action |
|---------|----------|--------|
| Clear ↔ Lean co-purchase | 53–65% among CM D1 buyers | Cross-sell other protein on order 2 |
| Peach ↔ White Grape same cart | 36% confidence, 333 orders | PDP bundle widget |
| More categories → higher CM | 2.4× CM, 3× repeat at 3 cats | Tier T3/T4 get category discovery |
| Accessories-first acquisition | 20% repeat vs Collagen 37% | **Do not** use shaker as lead product |

**Hero proteins for D1 strategy (category T4 index):** Lean **275**, Clear **265** — acquisition and cross-sell leads. Accessories index **127** — add-on only.

**Prize (category ladder):** 5% of 2,514 reach 3 categories = **S$10,693 GP/yr** · 8% add 2nd = **S$3,969 GP/yr**

---

### Recommendation 1 — implementation pathway

| Week | Action | Owner | Output |
|------|--------|-------|--------|
| 1 | Export `decile_customer_table.csv` → Klaviyo segments T1–T5 | CRM | 5 tagged segments |
| 1 | Exclude T1/T2 from site-wide % promos (Rec A) | Marketing | S$14K protected |
| 2 | Set CM-based incentive caps per tier (founder signs off X%) | Founder + CRM | Budget table |
| 2–4 | Launch CS-01–03 cross-sell flows for T4 (day 14) | CRM | 2nd category on order 2 |
| 4+ | VIP programme for T1 (`is_top_both`) — no discounts | Brand | Exclusive access |

**Deep dives:** `margin_analysis/` · `Recommendation_A/` · `decile_summary.ipynb` · `category_analysis/outputs/ACTIONABLE_INSIGHTS.md`

---

## Recommendation 2: Recommendation Engine + Subscription Growth System

### The core insight

> *The goal is not only cross-selling — it is increasing customer lifetime value through the right product, at the right time, for the right segment.*

Subscriptions prove the point: subscribers repeat at **62%** vs **19%** for non-subscribers (S$134 vs S$69 avg CM). The recommendation engine moves customers through the category ladder; the subscription engine **locks in** proven repeaters.

---

### 4-layer recommendation architecture

Each layer solves a different problem. Do not use one algorithm for everything.

| Layer | Lifecycle stage | Method | Why this method |
|-------|-----------------|--------|-----------------|
| **L1 — First purchase** | Cold start (no history) | **Rule-based** | 67% one-and-done = too sparse for ML; use observed co-purchase rates |
| **L2 — Same cart** | Active session | **Association rules (MBA)** | Same-order co-purchase is measurable (Peach↔W.Grape 36%) |
| **L3 — Post-purchase sequential** | After order 1 or 2 | **Timed journey rules** | Cross-sell lands *before* next order — not at checkout |
| **L4 — Logged-in personalisation** | 3+ orders, repeat buyer | **Item-item CF** | Enough purchase history; 83 SKUs with similarity scores |

**Full technical doc:** `recommendation_systems/RECOMMENDATION_ARCHITECTURE.md`

---

### Layer 1 — First purchase (cold start)

**Problem:** New customer has no behaviour data.

**Approach:** Rule-based recommendations from D1 co-purchase matrix.

| If first purchase contains… | Recommend | Evidence |
|----------------------------|-----------|----------|
| Clear Protein | Lean Protein (TMT/Taro 1kg) | 53% CM D1 co-purchase |
| Lean Protein | Clear Protein (Peach/W.Grape 500g) | 65% CM D1 co-purchase |
| Collagen only | Clear or Lean starter 500g | 30.5% first-tx repeat for Collagen |
| Accessories only | Protein starter (not another accessory) | 20% repeat vs 37% Collagen-first |

**Where:** Post-purchase email (day 3–5), order confirmation page, welcome series.  
**Output:** `recommendation_systems/outputs/recommender_01_rule_based.csv`

---

### Layer 2 — Same cart (basket expansion)

**Problem:** Increase basket size on current visit.

**Approach:** Association rules from 8,955 finals orders.

| Antecedent | Consequent | Confidence | Deploy |
|------------|------------|------------|--------|
| Clear Peach 500g | Clear White Grape 500g | **36%** | PDP "Add both" |
| Lean TMT 1kg | Clear shaker | **93%** | Cart cross-sell |
| Clear sachet Peach | Clear sachet W.Grape | **71%** | Trial pack bundle |

**Where:** PDP widget, cart drawer, checkout upsell.  
**Output:** `recommendation_systems/outputs/sku_association_rules.csv`  
**Mockups:** `pitch_analysis/INTEGRATION_DEMO.md`

---

### Layer 3 — Post-purchase sequential (timed cross-sell)

**Problem:** Drive 2nd and 3rd category on future orders — not same cart.

**Critical timing (most common mistake):**

| When | Action | Recommend for | Goal |
|------|--------|---------------|------|
| **Day 14 after order 1 ships** | Klaviyo CS-01/02/03 | Other protein category | 2nd category on **order 2** |
| **Day 7 after order 2 ships** | Klaviyo CS-04 | 3rd category (Collagen, 2nd flavour) | 3rd category by **order 3** |
| **Day 48 after order 2** (hero SKUs) | Klaviyo SUB-01 | Subscribe & Save | Lock replenishment |

**Do NOT** fire cross-sell immediately after purchase unless the goal is same-cart expansion (Layer 2).

**Sequential evidence:** 739 measured 1st→2nd SKU transitions · `first_to_second_sku_matrix.csv`

**Full playbook:** `Recommendation_B/RECOMMENDATION_B.md` · `FOUNDER_MEETING_PREP.md` Section 2A

---

### Layer 4 — Logged-in personalised recommendations

**Problem:** Repeat customers need SKU-level personalisation.

**Approach:** Item-item collaborative filtering (cosine similarity on 4,290 × 83 SKU matrix).

**Examples:** TMT → Taro (0.40 similarity) · TMT → Shaker (0.30) · Clear Peach → W.Grape (0.16)

**Where:** "Recommended for you" on account page, post-login homepage.  
**Output:** `recommender_04_item_similarity_matrix.csv`

**Deploy after** Layers 1–3 are live (week 6+).

---

### Single-serve / sample strategy

**Founder question:** *"When should we give samples?"*

**Do NOT** blindly attach samples to every first order — margin cost must be justified by expected CM uplift.

| Moment | Goal | Sample strategy | Cost cap (use CM framework) |
|--------|------|-----------------|------------------------------|
| **First order** | Reduce category uncertainty | 1 complementary category sachet (e.g. Clear buyer → collagen sachet) | ≤ 5% of expected CM if repeat lifts to S$79+ |
| **Day 14 post-order 1** | Drive 2nd purchase | Category discovery sample in email (not discount) | Sample COGS only — no blanket % off |
| **Before reorder window** | Prevent lapse | Reminder + sample of *next* flavour | Time to SKU reorder median |

**Reorder windows (send sample/reminder 7–10 days BEFORE):**

| SKU / Product | Median reorder days |
|---------------|---------------------|
| Clear Protein Peach 500g | **54 days** |
| Clear Protein White Grape 500g | **54 days** |
| Lean Protein TMT 1kg | **35 days** |
| Collagen Glow | **42 days** |
| Creatine 250g | **66 days** |

**Source:** `EDA/outputs/12_reorder_interval_by_sku.csv`

---

### Subscription growth engine (connects to Recommendation 2)

**Why subscription is the end-state:** Subscribers repeat **62%** vs **19%**; avg CM **S$134** vs **S$69**. **51%** of `is_top_both` VIPs already subscribe — subscription is a D1 signal.

| Tier | Pool | Trigger | Treatment |
|------|------|---------|-----------|
| **SUB-1** Repeat non-subs | 689 (2+ orders, never subscribed) | Order 2 + **48 days** | "Subscribe & Save" on hero SKU |
| **SUB-2** Freq D1 non-subs | 228 | Order 3 + **35 days** | Replenishment lock-in |
| **SUB-3** First-time hero buyers | ~400/yr | Order 1 + **42 days** | Trial sub offer |
| **SUB-4** Checkout | New orders | At checkout | Pre-checked S&S on Peach/TMT |

**Trigger rule:** Offer subscription **after second successful purchase** — customer has demonstrated product fit.

**Prize:** 5% of 689 repeat non-subs convert = **S$2,262 GP/yr** · Freq D1 tier = **S$1,497 GP/yr** · All tiers **~S$4.5K** direct + compounding repeat

**Full doc:** `pitch_analysis/NEW_RECOMMENDATIONS.md` (Rec D) · `FOUNDER_MEETING_PREP.md` Section 2B

---

### Recommendation 2 — implementation pathway

| Week | Layer | Deploy | Expected signal |
|------|-------|--------|-----------------|
| 1–2 | L1 + L3 | Klaviyo CS-01–03 (day 14) | Email CTR 5–8% |
| 2–3 | L2 | PDP bundles on top 5 SKUs | +AOV on bundle PDPs |
| 3–4 | L3 | CS-04 (day 7 after order 2) | 2nd-category attach +5pp |
| 4–5 | Subscription | SUB-01–02 flows | Sub conversion 5% of pool |
| 6+ | L4 | Logged-in CF recommendations | Repeat SKU discovery |

**Regenerate recommender outputs:**

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
```

---

## Combined business impact

| Source | GP/yr | Pillar |
|--------|-------|--------|
| Category ladder (5% → 3 categories) | **S$10,693** | Rec 1 + Rec 2 L3 |
| Category ladder (8% → 2nd category) | **S$3,969** | Rec 1 + Rec 2 L3 |
| Subscription (5% repeat non-subs) | **S$2,262** | Rec 2 |
| Subscription (Freq D1 tier) | **S$1,497** | Rec 2 |
| Acquisition mix fix (Rec E) | **S$4,389** | Rec 1 T4 routing |
| VIP discount guardrail (Rec A) | **S$14,000 protected** | Rec 1 T1/T2 |
| **Total** | **~S$30–35K** | |

---

## Legacy recommendations map (A–E → new structure)

| Old rec | Now lives in | Role |
|---------|--------------|------|
| Rec A — VIP guardrail | **Rec 1** T1/T2 treatment | Operational guardrail |
| Rec B — Cross-sell engine | **Rec 2** Layer 3 | Execution timing |
| Rec C — Category ladder | **Rec 1** MBA + **Rec 2** L3 | Lead economic story |
| Rec D — Subscription | **Rec 2** subscription engine | Lead retention story |
| Rec E — Acquisition mix | **Rec 1** T4 routing | Product entry fix |

**Execution playbooks:** `FOUNDER_MEETING_PREP.md`  
**Hypotheses H1–H5:** `pitch_analysis/HYPOTHESES.md`  
**Integration mockups:** `pitch_analysis/INTEGRATION_DEMO.md`

---

## Data sources and decile systems (do not mix)

| System | File | Tiers | CM metric | Use for |
|--------|------|-------|-----------|---------|
| **v2 (founder CRM)** | `outputs_finals/decile_customer_table.csv` | D1–D5 | `true_gross_profit` | **Rec 1 tiers, this doc** |
| v1 (category T1–T9) | `decile_analysis/outputs/customers_decile_table.csv` | D1–D10 | 40% proxy | Category analysis tables only |
| 10-tier true CM | `margin_analysis/outputs/true_profit_decile_summary.csv` | D1–D10 | true GP | Margin leakage, Rec A proof |

**Primary data (always):** `outputs_finals/customers.parquet` · `orders.parquet` · `lines.parquet`  
**Do NOT use:** `do_not_use_these/` for recommendations.

---

## Folder index

| Folder / file | Purpose |
|---------------|---------|
| `FINDINGS_AND_RECOMMENDATIONS.md` | **This file** — founder-facing consolidated recs |
| `FOUNDER_MEETING_PREP.md` | Meeting prep + Klaviyo flow copy |
| `lushprotein_decile.ipynb` | v2 CM + AOF decile build |
| `decile_summary.ipynb` | Slide charts + D1/D2 profiling handoff |
| `margin_analysis/` | COGS proof + margin leakage |
| `Recommendation_A/` | VIP guardrail + Klaviyo tier export |
| `Recommendation_B/` | Cross-sell flows + bundle ROI |
| `recommendation_systems/` | MBA + 4 recommenders + architecture doc |
| `pitch_analysis/` | Hypotheses, prize scenarios, integration demo |
| `outputs_finals/` | Enriched parquets + v2 decile CSV/PNGs |

---

## Regenerate all analysis

```bash
python EDA/13_build_finals_datasets.py
python EDA/aditya_findings/enrich_finals_with_margin.py
# Run lushprotein_decile.ipynb for v2 deciles
python EDA/aditya_findings/run_all.py
```
