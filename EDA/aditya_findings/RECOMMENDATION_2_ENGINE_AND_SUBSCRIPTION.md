# Recommendation 2 — 4-Layer Recommendation Engine & Subscription Growth

**Purpose:** Justify the custom recommendation engine over Shopify defaults; define *when* to cross-sell, *what* samples to send, and *how* the decile study drives subscriber growth.

**How to present Rec 2:** `REC2_PRESENTATION_GUIDE.md` — problem → gap → solution → charts → conservative numbers → implementation map

**Data:** 8,955 finals orders · 4,290 customers · co-purchase + reorder intervals  
**Charts:** `outputs/charts/r2_*.png` · regenerate via `python EDA/aditya_findings/build_presentation_charts.py`

---

## What the LP team told us (meeting notes)

| Theme | Founder intent |
|-------|----------------|
| **Stick with custom engine** | Keep the recommendation system built in this project — not Shopify default |
| **Cross-sell = more categories** | Main push is category expansion (Clear → Lean → Collagen), not more of the same |
| **Right dates & items** | LP wants to know *when* to recommend and *what* single-serve/sample to send |
| **Sample timing** | Should samples go at order time or **before reorder** so customers experience a new category first? |
| **Purchase stage** | Should single-serve gifts target 1st, 2nd, or 3rd-time purchasers? |
| **Incentives allowed** | Merch, shakers, samples — **NO % discounts** |
| **Creatine push** | Creatine can be bundled with protein |
| **Retention > acquisition** | Engine serves existing customers through the category ladder |

---

## The core insight

> *The goal is not only cross-selling — it is increasing lifetime value through the right product, at the right time, for the right segment.*

| Metric | Subscribers | Non-subscribers |
|--------|-------------|-----------------|
| Repeat rate | **62%** | 19% |
| Avg profit margin | **S$134** | S$69 |

The recommendation engine moves customers up the **category ladder**; the subscription engine **locks in** proven repeaters.

**Presentation chart:** `r2_category_ladder.png`

---

## Why NOT Shopify's built-in recommender?

Shopify "Recommended products" is fine for **Layer 2** (same-cart PDP widgets). It cannot deliver what LP needs:

| Capability | Shopify default | Lush Protein 4-layer engine |
|------------|-----------------|------------------------------|
| Data source | Generic storefront co-views | **8,955 finals orders** + profit margin tiers |
| Category cross-sell | No category ladder | **Clear→Lean→Collagen** from co-purchase matrix |
| Timing | Always on PDP | **Day 14 email** + **day 44 sample** before 54d Clear reorder |
| Segment treatment | Same for everyone | T1 experiences; T5 email only |
| Cold start (67% one-and-done) | Weak | **Rule-based** from 53–65% PM D1 co-purchase |
| Samples / sachets | Not supported | `cross_sell_timing_and_samples.csv` per first category |
| Subscription trigger | Not integrated | **SUB-01** at order 2 + 48 days |

**Presentation charts:** `r2_shopify_vs_custom_engine.png` · `r2_four_layer_architecture.png`

**Technical doc:** `recommendation_systems/RECOMMENDATION_ARCHITECTURE.md`  
**Evidence & comparison:** `recommendation_systems/RECOMMENDER_SYSTEMS.md`

---

## Recommendation systems — how the 4 layers map to code & outputs

This is the implementation layer behind the architecture above. Each layer is a **different algorithm** because each lifecycle moment has different data available.

### Scripts → layers

| Script | Layer(s) | What it builds |
|--------|----------|------------------|
| `recommendation_systems/sku_market_basket.py` | **L2** | Association rules from 8,955 order lines |
| `recommendation_systems/build_recommenders.py` | **L1, L3, L4** | Rule table, sequential matrix, item–item CF |
| `recommendation_systems/hierarchical_clustering.py` | *(supplementary)* | Customer clusters for segmentation QA — not a deploy layer |
| `build_crm_tiers_and_timing.py` | **L3 + samples** | CRM tier gates + `cross_sell_timing_and_samples.csv` |
| `Recommendation_B/run_recommendation_b.py` | **L3** | Klaviyo flow definitions `klaviyo_cross_sell_flows.csv` |

**Regenerate all recommender outputs:**
```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
```

### Output files → layer → deploy surface

| Layer | Output file | Key columns / content | Where it deploys |
|-------|-------------|----------------------|-------------------|
| **L1** | `recommendation_systems/outputs/recommender_01_rule_based.csv` | `if_bought` → `recommend` | Klaviyo welcome, order confirmation |
| **L2** | `recommendation_systems/outputs/sku_association_rules.csv` | antecedent, consequent, confidence, lift | Shopify PDP bundle, cart drawer |
| **L2** | `recommendation_systems/outputs/sku_association_rules_full.csv` | full MBA rule set | Analysis / rule audit |
| **L3** | `recommendation_systems/outputs/first_to_second_sku_matrix.csv` | 1st→2nd SKU transition counts | Klaviyo CS-01–04 SKU selection |
| **L3** | `recommendation_systems/outputs/next_best_sku_per_first.csv` | `first_order_sku` → `recommended_next_sku`, `p_second_given_first` | Order-2 email product pick |
| **L3** | `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv` | flow ID, trigger day, segment, SKU | Klaviyo flow build |
| **L3** | `outputs/cross_sell_timing_and_samples.csv` | email day, sample ship day, sample SKU | Fulfilment + CRM ops |
| **L4** | `recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv` | anchor SKU → similar SKUs (cosine) | Logged-in account page |
| **All** | `recommendation_systems/outputs/recommender_comparison_demo.csv` | same input SKU → L1/L2/L3/L4 answers | Deck proof — one SKU, four moments |
| **All** | `recommendation_systems/outputs/recommender_system_comparison.csv` | cold_start, build_effort, expected_attach_lift | Prioritise build order |

### Why four systems, not one (from `recommender_system_comparison.csv`)

| System | Cold start | Best use | Build effort | Expected attach lift |
|--------|------------|----------|--------------|---------------------|
| L1 Rule-based | **Excellent** (1st purchase) | Klaviyo post-purchase | Low (1 day) | 5–8% |
| L2 Association rules | Good (needs basket) | PDP "Frequently bought together" | Low–medium | 2–4% on PDP |
| L3 Sequential | Medium (needs 1 prior order) | Day 14 / day 7 emails | Medium | 3–5% on repeat |
| L4 Item-CF | Poor for new customers | Logged-in personalisation | Medium–high | 2–3% incremental |

**Reading `recommender_comparison_demo.csv`:** For `clear-protein|Peach`:
- **L1** says Lean Protein (category cross-sell for order 2)
- **L2** says White Grape (same-cart bundle, 36% confidence)
- **L3** says Peach (replenishment / sequential next order)
- **L4** says W.Grape (0.41), Shaker (0.22), TMT (0.16) — personalised discovery

Each answer is correct for its moment. Shopify only covers L2.

### Co-purchase evidence chain (L1 + L3 rules source)

| Evidence file | Feeds | Example rule |
|---------------|-------|--------------|
| `Recommendation_B/outputs/co_purchase_matrix_d1.csv` | L1 category rules | Clear→Lean **53%** among PM D1 |
| `Recommendation_B/outputs/co_purchase_matrix_all.csv` | L1 fallback / T4 | Clear→Lean **25%** all-pool |
| `recommendation_systems/outputs/first_to_second_sku_matrix.csv` | L3 sequential | Clear Peach → Lean TMT as 2nd order |
| `EDA/outputs/12_reorder_interval_by_sku.csv` | L3 sample timing | Clear 54d · Lean 35d · Collagen 42d |

### CRM tier → which layers fire (Rec 1 × Rec 2)

| CRM tier | N | Primary layers | Subscription |
|----------|---|----------------|--------------|
| **T1 VIP** | 532 | L4 personalisation + partner gifts | 54% already sub — grow remainder |
| **T2 High-value** | 744 | L3 day 14/7 + L2 bundles | **SUB-01** at order 2 + 48d |
| **T3 Growth** | 63 | L3 CS-04 (3rd category sample) | SUB-01 after order 3 |
| **T4 First-tx** | 2,120 | **L1** rules + **L3** CS-01–03 + pre-reorder sachet | No — prove fit first |
| **T5 Low** | 831 | Win-back email only | No sub push |

### Supplementary: hierarchical clustering

`hierarchical_clustering.py` → `customer_cluster_assignments.csv`, `hierarchical_cluster_profiles.csv`

**Use:** Validates that T1–T5 tiers align with natural customer groups. **Not** a replacement for the 4-layer engine — clusters inform *who*, layers inform *what/when*.

**Deck figures (optional):** `recommendation_systems/outputs/fig_top_association_rules.png` · `fig_recommender_effort_impact.png`

### Integration mockups (founder-facing)

`pitch_analysis/INTEGRATION_DEMO.md` — Klaviyo email copy (day 14), PDP bundle wireframe, SUB-01 trigger. All product pairs pulled from `sku_association_rules.csv`, not invented.

---

## 4-layer architecture

Each layer solves a different lifecycle problem. Do not use one algorithm for everything.

| Layer | Stage | Method | Deploy |
|-------|-------|--------|--------|
| **L1 — First purchase** | Cold start | Rule-based co-purchase | Klaviyo welcome, order confirmation |
| **L2 — Same cart** | Active session | Association rules (MBA) | PDP bundle, cart drawer |
| **L3 — Post-purchase** | Between orders | Timed journey rules | Klaviyo CS-01–04 |
| **L4 — Logged-in** | 3+ orders | Item-item CF | Account page "Recommended for you" |
| **Subscription** | After order 2 | SUB-01 trigger | Klaviyo replenishment flow |

---

### Layer 1 — First purchase (cold start)

| If first purchase… | Recommend | Evidence |
|--------------------|-----------|----------|
| Clear Protein | Lean Protein (TMT/Taro 1kg) | 53% PM D1 co-purchase |
| Lean Protein | Clear Protein (Peach/W.Grape 500g) | 65% PM D1 co-purchase |
| Collagen only | Clear or Lean starter 500g | 30.5% Collagen-first repeat |
| Accessories only | Protein starter | 20% repeat vs 37% Collagen-first |

**Output:** `recommendation_systems/outputs/recommender_01_rule_based.csv`  
**Evidence source:** `Recommendation_B/outputs/co_purchase_matrix_d1.csv` (PM D1) + `co_purchase_matrix_all.csv` (all-pool fallback)

---

### Layer 2 — Same cart (basket expansion)

| Antecedent | Consequent | Confidence |
|------------|------------|------------|
| Clear Peach 500g | Clear White Grape 500g | **36%** |
| Lean TMT 1kg | Clear shaker | **93%** |
| Clear sachet Peach | Clear sachet W.Grape | **71%** |

**Use at checkout:** Same-category bundles only — not cross-category samples.

**Outputs:** `recommendation_systems/outputs/sku_association_rules.csv` · `sku_association_rules_full.csv`  
**Deck figure:** `recommendation_systems/outputs/fig_top_association_rules.png`

---

### Layer 3 — Post-purchase sequential (the founder's timing question)

**Critical answer: physical cross-category samples ship BEFORE the reorder window, NOT in the first order box.**

| Moment | Action | Example (Clear Protein buyer) |
|--------|--------|-------------------------------|
| **At first order (checkout)** | Same-category bundle only (L2) | Peach + White Grape — not Collagen |
| **Day 14 after delivery** | Email: recommend Lean for order 2 | Klaviyo CS-01 |
| **Day 44 after delivery** | **Physical sachet** (Collagen or Lean 40g) | **10 days before** 54d median reorder |
| **Day 48 after order 2** | Subscribe & Save | SUB-01 if not subscribed |

**Why before reorder, not at order?** Customer tries the new category *before* deciding to repurchase — they can add the original order plus a cross-sell, or switch categories.

**Presentation chart:** `r2_cross_sell_timeline_clear.png`

**Full matrix:** `outputs/cross_sell_timing_and_samples.csv` · `recommendation_systems/outputs/cross_sell_timing_and_samples.csv`  
**Sequential SKU picks:** `recommendation_systems/outputs/next_best_sku_per_first.csv` · `first_to_second_sku_matrix.csv`  
**Klaviyo flows:** `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv`

| First category | Email day | Sample ship day | Median reorder |
|----------------|-----------|-----------------|----------------|
| Clear Protein | 14 | 44 | 54 days |
| Lean Protein | 14 | 25 | 35 days |
| Collagen | 14 | 32 | 42 days |

---

### Single-serve strategy — which purchase number?

| Stage | Who | Sample / gift | Rationale |
|-------|-----|---------------|-----------|
| **1st purchase (T4)** | 2,120 customers | Cross-category sachet day 44 (pre-reorder) | Prove 2nd category before reorder decision |
| **2nd purchase (T3)** | 63 customers | 3rd-category sachet day 7 | Repeat intent proven — push 3rd category |
| **3rd+ / VIP (T1)** | 532 customers | Merch, shaker, partner event (budget 10% PM) | Loyalty reward — not acquisition |

**Do NOT** attach cross-category samples to every first order box — cost must be justified by expected profit margin uplift (cap ≤ 5% of PM for T4 ≈ S$2.54).

**Presentation chart:** `r2_sample_by_purchase_stage.png`

**CSV:** `outputs/sample_strategy_by_purchase_stage.csv`

---

### Layer 4 — Logged-in personalisation

Item-item collaborative filtering on 4,290 × 83 SKU matrix. Deploy **after** L1–L3 are live (week 6+).

**Output:** `recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv`  
**Demo (same SKU, all layers):** `recommendation_systems/outputs/recommender_comparison_demo.csv`

---

## Subscription growth — decile study justification

Subscription is concentrated in higher profit margin deciles:

| PM Decile | Subscription rate | Avg profit margin |
|-----------|-------------------|-------------------|
| **D1** | **33.4%** | S$230 |
| D2 | 22.3% | S$81 |
| D3 | 13.1% | S$49 |
| D4 | 11.8% | S$30 |
| D5 | 2.6% | S$9 |

**51%** of `is_top_both` VIPs already subscribe — subscription is a D1 signal.

**Presentation chart:** `r2_subscription_by_profit_decile.png`

### Subscription trigger rules

| Segment | Pool | Trigger | Treatment |
|---------|------|---------|-----------|
| **SUB-01** Repeat non-subs | 689 (2+ orders, never subscribed) | Order 2 + **48 days** | S&S on hero SKU (Peach/TMT) |
| **SUB-02** Freq D1 non-subs | 228 | Order 3 + **35 days** | Replenishment lock-in |
| **SUB-03** First-time hero buyers | ~400/yr | Order 1 + **42 days** | Trial sub offer |
| **SUB-04** Checkout | New orders | At checkout | Pre-checked S&S on Peach/TMT |

**Rule:** Offer subscription **after second successful purchase** — customer has demonstrated product fit.

### How each layer grows subscribers

```
L3 day 14 email → 2nd order → qualifies for SUB-01
L3 day 7 (order 2) → 3rd category → higher repeat → sub attach
SUB-01 (order 2 + 48d) → locks replenishment
T2 pool (744) → primary sub conversion target
T1 VIP → grow remaining 46% non-sub VIPs with VIP S&S (no deep discount)
```

**Prize model:** 5% of 689 repeat non-subs convert = **S$2,262 GP/yr** · Freq D1 tier = **S$1,497 GP/yr**

---

## Creatine bundle opportunity (founder ask)

702 orders include creatine; **360** combine creatine + protein in the same order history. Bundle creatine with hero proteins (Clear Peach, Lean TMT) in **L2 checkout** and **T2** email flows — not as a lead acquisition product.

---

## Implementation pathway

| Week | Layer | Deploy | Signal |
|------|-------|--------|--------|
| 1–2 | L1 + L3 | Klaviyo CS-01–03 (day 14) | Email CTR 5–8% |
| 2–3 | L2 | PDP bundles on top 5 SKUs | +AOV on bundle PDPs |
| 3–4 | L3 | CS-04 (day 7 after order 2) + pre-reorder samples | +5pp 2nd-category attach |
| 4–5 | Subscription | SUB-01–02 flows | 5% sub conversion of pool |
| 6+ | L4 | Logged-in CF | Repeat SKU discovery |

**Regenerate:**

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
python EDA/aditya_findings/build_crm_tiers_and_timing.py
python EDA/aditya_findings/build_presentation_charts.py
```

---

## Related files

| File | Purpose |
|------|---------|
| `REC2_PRESENTATION_GUIDE.md` | **How to present Rec 2** — story arc, charts, conservative prize, implementation |
| `PRESENTATION.md` | **10-slide deck guide** (cover + content, figures, speaker notes) |
| `recommendation_systems/RECOMMENDATION_ARCHITECTURE.md` | Full technical architecture |
| `recommendation_systems/RECOMMENDER_SYSTEMS.md` | Evidence tables + system comparison |
| `recommendation_systems/outputs/recommender_system_comparison.csv` | Effort vs attach lift by system |
| `recommendation_systems/outputs/recommender_comparison_demo.csv` | Same SKU → 4 different layer answers |
| `Recommendation_B/RECOMMENDATION_B.md` | Cross-sell flow playbook |
| `pitch_analysis/INTEGRATION_DEMO.md` | Email + PDP mockups with real pairs |
| `CRM_AND_INCENTIVES.md` | Sample timing + tier budgets |
| `RECOMMENDATION_1_CUSTOMER_SEGREGATION_AND_INCENTIVES.md` | Segmentation pillar |
