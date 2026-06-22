# Recommendation 2 — 4-Layer Recommendation Engine & Subscription Growth

**Purpose:** Justify the custom recommendation engine over Shopify defaults; define *when* to cross-sell, *what* samples to send, and *how* the decile study drives subscriber growth.

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

---

### Layer 2 — Same cart (basket expansion)

| Antecedent | Consequent | Confidence |
|------------|------------|------------|
| Clear Peach 500g | Clear White Grape 500g | **36%** |
| Lean TMT 1kg | Clear shaker | **93%** |
| Clear sachet Peach | Clear sachet W.Grape | **71%** |

**Use at checkout:** Same-category bundles only — not cross-category samples.

**Output:** `recommendation_systems/outputs/sku_association_rules.csv`

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

**Full matrix:** `outputs/cross_sell_timing_and_samples.csv`

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

**Output:** `recommender_04_item_similarity_matrix.csv`

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
| `recommendation_systems/RECOMMENDATION_ARCHITECTURE.md` | Full technical architecture |
| `Recommendation_B/RECOMMENDATION_B.md` | Cross-sell flow playbook |
| `CRM_AND_INCENTIVES.md` | Sample timing + tier budgets |
| `RECOMMENDATION_1_CUSTOMER_SEGREGATION_AND_INCENTIVES.md` | Segmentation pillar |
