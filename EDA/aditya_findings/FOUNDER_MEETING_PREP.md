# Lush Protein Founder Meeting — Prep Guide

**Author:** Aditya · Group 1 · ISSS603  
**Date:** June 17, 2026  
**Purpose:** Walk into the LP meeting with a clear story, validated numbers, and the right questions to get direction.

---

## 1. Executive summary (30-second version)

We analysed **4,290 Shopify customers** (excl. pure marketplace) with LP's real COGS on **74.7% of revenue**. Two patterns dominate:

1. **59% of customers never buy a second product category** — they average S$59 GP and 17% repeat. Customers with 3 categories average S$144 GP and 55% repeat. Moving even 5% up the ladder is worth **~S$11K GP/yr**.

2. **689 repeat customers never subscribed** — subscribers repeat at **62%** vs **19%**. Converting 5% to Subscribe & Save on hero SKUs (Clear Peach, Lean TMT) is worth **~S$2K GP/yr** with compounding repeat benefit.

Everything else (VIP guardrails, acquisition mix, flavour routing) supports these two moves. **Sections 2–4 below turn the headlines into an executable plan** — customer analytics (who, when, which segment) plus product analytics (which SKU, which category, which bundle).

---

## 2. Your two hero pitch insights

These are the data-backed recommendations to lead with. **Section 2A** is how Rec C becomes real. **Section 2B** expands Rec D into a full subscription growth engine. **Section 3** explains what a D1 customer looks like and how cross-sell + subscription move people there.

### Hero 1 — Rec C: Climb the category ladder (CUSTOMER insight)

| | |
|---|---|
| **Problem** | 2,514 customers (59%) bought only one category ever |
| **Economics** | 1-cat: S$59 GP, 17% repeat → 3-cat: S$144 GP, 55% repeat |
| **Fix** | Day 14 after order 1: cross-sell complementary protein. Day 7 after order 2: introduce 3rd category (Collagen). Checkout: Clear+Lean bundle. |
| **Prize** | 5% reach 3 categories = **S$10,693 GP/yr**; 8% add 2nd = **S$3,969** |
| **Evidence** | `pitch_analysis/outputs/fig_category_ladder.png`, 65% Clear↔Lean co-purchase |
| **Execution** | **Section 2A** — 4-layer stack over 6 weeks |

**One-liner for the meeting:** *"Your biggest pool isn't churned customers — it's customers who liked one product and never discovered the rest of the range."*

### Hero 2 — Rec D: Build a subscription engine (PRODUCT + CUSTOMER insight)

| | |
|---|---|
| **Problem** | Only **713 subscribers** (17% of pool) vs **3,577 non-subs** at 19% repeat |
| **Economics** | Subscribers: S$134 GP, 62% repeat. Non-subs: S$69 GP, 19% repeat |
| **Fix** | Tiered subscription offers across the journey — not just repeat non-subs (Section 2B) |
| **Prize** | Repeat non-subs: **S$2,262** · Freq D1 non-subs: **S$1,497** · New acquirers on hero SKUs: compounding |
| **Evidence** | 54-day reorder (Peach), 35-day reorder (TMT); 38% of D1 ever subscribed |
| **Execution** | **Section 2B** — 4 subscription tiers + D1 path in Section 3 |

**One-liner for the meeting:** *"Subscription isn't a checkout toggle — it's the retention layer that turns repeat buyers into D1 customers."*

---

## 2A. Execution playbook — Rec C cross-sell (headline → reality)

Cross-sell only works when **customer segment**, **timing**, **product recommendation**, and **channel** are wired together. This is a 4-layer stack — each layer has a data source and a deploy surface.

### The customer journey we are engineering

```
Order 1 ships          Day 14 email           Order 2 ships          Day 7 email            Order 3
     │                      │                      │                      │                  │
     ▼                      ▼                      ▼                      ▼                  ▼
  Gateway SKU          Cross-sell OTHER        2nd category         Push 3rd category    D1 trajectory
  (Peach/TMT)          protein category        acquired?              (Collagen)          (2.3+ cats)
     │                      │                      │                      │
     └─ Checkout bundle ────┴─ PDP widget ─────────┴─ Stuck repeater retry (88 pool)
```

**Goal:** Move single-category buyers from 1 → 2 → 3 categories before they churn. Each category step lifts GP **S$20–85** and repeat **+13–38pp**.

### Layer 1 — Klaviyo post-purchase flows (highest impact, week 1–2)

**Prerequisites (ask LP in meeting):**
- Klaviyo connected to Shopify with order-fulfilled events
- Ability to segment on `line items contain product type` and `customer has not purchased category X`
- Dynamic product blocks or manual SKU links per flow

| Flow ID | Trigger | Delay | Customer filter | Product recommendation | Data source |
|---------|---------|-------|-----------------|------------------------|-------------|
| **CS-01** | Order 1 fulfilled, contains Clear Protein | **Day 14** | `n_categories_ever = 1` · never bought Lean | Lean TMT 1kg or Taro 1kg | 65% Clear↔Lean co-purchase among D1 |
| **CS-02** | Order 1 fulfilled, contains Lean Protein | **Day 14** | `n_categories_ever = 1` · never bought Clear | Clear Peach 500g or White Grape 500g | Same co-purchase matrix |
| **CS-03** | Order 1 fulfilled, Collagen only (no protein) | **Day 21** | No Clear or Lean in order history | Clear Peach 500g starter | Collagen T9 index 111; protein habit needed |
| **CS-04** | Order 2 fulfilled | **Day 7** | Still `n_categories_ever ≤ 2` | Collagen Glow 300g OR 2nd flavour (Peach↔Grape) | Category breadth jumps at order 3 |
| **CS-05** | Order 2 fulfilled | **Day 7** | D5–D7 · 1-cat · 2+ orders (stuck) | Same as CS-04 — second bite at apple | 88-customer retarget pool |

**Exclusions (Rec A guardrail):** Do not send discount-led cross-sell to profit D1 / VIP (`crm_tier` in `klaviyo_crm_tiers.csv`). Use early-access framing instead.

**Email personalisation — use real numbers:**
- Subject: *"65% of Clear buyers also use Lean — here's the #1 pairing"*
- Body: SKU-specific CTA from `first_to_second_sku_matrix.csv` (not generic "shop now")
- Full mockup: `pitch_analysis/INTEGRATION_DEMO.md`

**Success metrics (measure at 60 days):**
- Primary: +5pp category attach rate among single-category buyers
- Secondary: order-2 conversion rate from CS-01/02/03 emails (target 5–8% click-to-purchase)
- Tertiary: % reaching 3 categories within 90 days

### Layer 2 — Checkout & PDP (product analytics, week 2–3)

| Surface | Who sees it | What to show | Data rule |
|---------|-------------|--------------|-----------|
| **Cart upsell** | Single-category buyer at checkout | Clear+Lean starter bundle (S$5 off) | Bundle true GP S$73.60; 5% discount nets S$69.92 GP |
| **PDP widget** | Any visitor on hero PDPs | "Frequently bought together" | `sku_association_rules.csv` — Peach↔White Grape 26% conf, 333 co-orders |
| **Post-add-to-cart** | Just added Clear or Lean | Complementary category sachet trial S$9.90 | Low-commitment 2nd category trial |

**Top 5 PDPs to instrument first:** Clear Peach 500g, Lean TMT 1kg, Clear White Grape 500g, Lean Taro 1kg, Collagen Glow 300g.

**Shopify tooling options:** Rebuy, Zipify, or native bundles — ask LP which they have.

### Layer 3 — Recommendation logic (which product for which customer)

| Customer state | First product bought | Recommend for order 2 | Recommend for order 3 |
|----------------|---------------------|----------------------|----------------------|
| Single-cat, trial mode | Clear Protein | Lean (TMT #1) | Collagen or 2nd Clear flavour |
| Single-cat, trial mode | Lean Protein | Clear (Peach #1) | Collagen or 2nd Lean flavour |
| Single-cat | Collagen only | Clear Peach 500g starter | Lean TMT 1kg |
| Single-cat | Accessories (shaker) | Protein sachet trial pack | Full-size Clear or Lean |
| 2-cat, no Collagen | Clear + Lean | Collagen Glow 300g | 1kg pack upgrade |
| Stuck repeater (2+ orders, 1-cat) | Whatever they repeat | Force different category — CS-05 | Collagen or complementary protein |

**Recommender priority:** Rule-based (Klaviyo) → Sequential (order-history SKU) → Association rules (PDP) → Item-CF (logged-in). See `recommendation_systems/RECOMMENDER_SYSTEMS.md`.

### Layer 4 — Measurement & iteration (week 4–6)

| Week | Action |
|------|--------|
| 1–2 | Launch CS-01, CS-02, CS-03. A/B subject lines (data-led vs generic). |
| 3 | Add checkout bundle + top 3 PDP widgets. |
| 4 | Launch CS-04 (post-order-2). Add CS-05 for stuck repeaters. |
| 5–6 | Review: category attach rate, email CTR, bundle conversion. Refine SKU recommendations from `first_to_second_sku_matrix.csv`. |

**What we need from LP to go live:** Named CRM owner, Klaviyo segment access, confirmation of Shopify bundle app, approval on bundle discount depth (COGS-backed margin floor).

---

## 2B. Execution playbook — Rec D subscription growth engine

Rec D starts with **689 repeat non-subscribers** but the real opportunity is building subscription into the **entire customer journey** — from first purchase through D1. Subscription is both a **product play** (replenishment SKUs) and a **customer play** (38% of D1 ever subscribed; subscription-first channel over-indexes D1 by 57%).

### Why subscription = path to D1

| Signal | D1 | Non-D1 | Index |
|--------|-----|--------|-------|
| Ever subscribed | 38% | 15% | **258** |
| First channel = Subscription | 54% | 35% | **157** |
| Repeat rate | 88% | 21% | **427** |
| Avg categories | 2.5 | 1.5 | **164** |

Subscribers don't just repeat more — they **stay in the brand ecosystem**. Cross-sell (Rec C) widens the basket; subscription **locks in replenishment** so they don't need to be re-acquired every 35–54 days.

### Four subscription tiers (expand beyond repeat non-subs)

| Tier | Pool | Trigger | Offer | Prize (conservative) |
|------|------|---------|-------|----------------------|
| **D1 — Repeat non-subs** | **689** | 2nd order fulfilled + **48 days** | S&S on exact SKU (Peach 500g / TMT 1kg) | 5% convert = **S$2,262/yr** |
| **D2 — Freq D1 non-subs** | **228** | 3rd order fulfilled + 35 days | S&S + 1kg pack nudge (raise $/unit toward profit D1) | 10% convert = **S$1,497/yr** |
| **D3 — First-time hero SKU buyers** | ~800/yr est. | 1st order fulfilled + **42 days** (mid-reorder window) | "Your Peach is running low" — S&S with 10% off first delivery | Compounding — catches before churn |
| **D4 — Checkout subscribe** | All new orders on replenishment SKUs | At checkout | Pre-checked S&S option on Peach, TMT, White Grape | Lowest CAC subscriber — no email needed |

**Hero SKUs for all tiers** (product analytics):

| SKU | Reorder cycle | Repeat (first-buyers) | Loyal buyers | Why |
|-----|---------------|----------------------|--------------|-----|
| Lean TMT 1kg | **35 days** | 35% | 125 | Fastest cycle; highest stickiness |
| Clear Peach 500g | **54 days** | 27% | 171 | Highest volume gateway |
| Clear White Grape 500g | **54 days** | 25% | 64 | Flavour rotation pair |

### Klaviyo flows to build (SUB-01 through SUB-04)

| Flow | Trigger | Delay | Segment | Message angle |
|------|---------|-------|---------|---------------|
| **SUB-01** | Order 2 fulfilled, hero replenishment SKU | 48 days | Repeat non-subscriber | "54% of Peach subscribers reorder every 6 weeks" |
| **SUB-02** | Order 3 fulfilled | 35 days | Freq D1, non-subscriber | "Upgrade to 1kg + subscribe — better $/serve" |
| **SUB-03** | Order 1 fulfilled, Peach or TMT | 42 days | 1 order, no subscription | Replenishment nudge before they forget |
| **SUB-04** | Subscription started | Day 1 | New subscriber | Welcome + cross-sell Collagen (widens basket toward D1) |

**A/B test:** 10% subscription discount vs free shipping on first delivery. Use COGS to set floor — Peach/TMT at 70.5% margin allows ~10% sub discount without going below 60% margin.

### Checkout subscribe (Tier D4) — product surface

On PDP and checkout for Peach, TMT, White Grape:
- Pre-select "Subscribe & Save 10% — delivery every 6 weeks"
- Show $/serve comparison vs one-time
- **Do not** offer subscribe on shakers, samplers, or accessories — not replenishment products

### Subscription × cross-sell sequence (how C and D work together)

```
New customer (Gateway Hero SKU)
    │
    ├─ Day 14: Cross-sell other protein (Rec C / CS-01)
    │
    ├─ Day 42: Subscribe nudge if no order 2 (Rec D / SUB-03)
    │
    ├─ Order 2: Cross-sell 3rd category (Rec C / CS-04)
    │
    ├─ Day 48 post-order-2: Subscribe on exact SKU (Rec D / SUB-01)
    │
    └─ Subscriber welcome: Collagen cross-sell (Rec C → D1 breadth)
```

Neither rec works alone. Cross-sell without subscription = wide basket but re-acquire every cycle. Subscription without cross-sell = locked replenishment but single-category ceiling.

### Expanded prize (all tiers)

| Tier | Pool | Conv. | GP/yr |
|------|------|-------|-------|
| D1 repeat non-subs | 689 | 5% | S$2,262 |
| D2 freq D1 non-subs | 228 | 10% | S$1,497 |
| D3 first-time hero | ~400 eligible/yr | 3% | ~S$800 (est.) |
| D4 checkout subscribe | ~800 new hero buyers/yr | 2% incremental | Compounding |
| **Direct year 1** | | | **~S$4.5K** |
| **Compounding repeat benefit** | | | 62% vs 19% over 2–3 years |

---

## 3. What makes a D1 customer — and how to lead customers there

**Profit D1** = top 10% by true gross profit. **368 customers**, **S$357 avg GP**, **41% of all GP**. This is the customer LP should be systematically creating — not hoping for.

### The D1 fingerprint (customer analytics)

A D1 customer is **not** "someone who orders a lot." They combine:

| Dimension | D1 profile | D10 (bottom) | What it means |
|-----------|------------|--------------|---------------|
| **Basket quality** | S$61/unit | S$8/unit | 1kg packs, premium proteins — not sachets/shakers |
| **Category breadth** | 2.5 categories | 1.4 categories | Clear + Lean + Collagen — not single-flavour trial |
| **Repeat behaviour** | 88% repeat | 4% repeat | Habit, not one-off |
| **Subscription** | 38% ever subscribed | ~15% | Replenishment lock-in |
| **Hero products** | Lean index 275, Clear 265, Collagen 202 | Accessories-led | Product mix predicts profit |

**Strongest predictive signals (ranked):**
1. Loyal repeater (3+ orders) — index **1052**
2. 3+ categories ever — index **434**
3. Is repeat buyer — index **427**
4. Ever bought Collagen — index **286**
5. Ever subscribed — index **258**

### Three D1 archetypes — different playbooks

| Archetype | N | Profile | How Rec C + D move them |
|-----------|---|---------|-------------------------|
| **VIP** (profit + freq D1) | 238 | 5.9 orders, 2.7 cats, 54% subscribed | **Protect** — Rec A guardrail, no blanket promos. Early access. |
| **Profit D1 only** | 130 | AOV S$368, 1.7 orders — whales | **Premium upsell** — 1kg bundles, not frequency pushes |
| **Freq D1 only** | 264 | 3.7 orders, AOV S$54 — replenishment without premium | **Subscribe + upgrade** — SUB-02, 500g→1kg, cross-sell to raise $/unit |

### D1 scoring — route customers in Klaviyo (0–100)

Use this to segment every customer into nurture tracks:

| Criterion | Points | Klaviyo property |
|-----------|--------|------------------|
| 2+ categories ever | +25 | `n_categories_ever >= 2` |
| 3+ categories ever | +15 | `n_categories_ever >= 3` |
| Ever bought Lean | +15 | product purchase history |
| Ever bought Clear | +15 | product purchase history |
| $/unit above S$45 | +10 | computed from order lines |
| 1kg pack dominant | +10 | variant title parsing |
| Subscribed | +10 | `ever_subscribed` |
| 3+ orders | +10 | `total_orders` |
| Accessories-only | **-20** | single category = Accessories |
| Single order, AOV < S$50 | **-15** | low-commitment buyer |

| Score | Segment | CRM track |
|-------|---------|-----------|
| **≥ 60** | High D1 potential | VIP nurture — protect, early access, subscription perks |
| **35–59** | Moveable middle (D5–D7) | **Rec C + D full stack** — cross-sell, subscribe, pack upgrade |
| **< 35** | Standard acquisition | Gateway Hero entry SKUs (Rec F), protein trial if accessories-first |

### The D1 creation journey — stage by stage

| Stage | Customer state | Metrics | Actions (product × customer) |
|-------|----------------|---------|------------------------------|
| **0 — Acquire** | New visitor | — | Land on Gateway Hero (Peach/TMT/Collagen). Not shaker. Rec E + F. |
| **1 — First order** | 1 category, 1 order | S$59 GP, 17% repeat | Checkout bundle. Gateway SKU. Score assigned. |
| **2 — Trial → habit** | 1 category, considering order 2 | — | CS-01/02/03 day 14. PDP cross-sell widget. |
| **3 — Widen basket** | 2 categories | S$79 GP, 30% repeat | CS-04 day 7 post-order-2. Collagen or 2nd flavour. |
| **4 — Lock replenishment** | 2+ orders, non-subscriber | S$69 GP if non-sub | SUB-01/02/03. Checkout subscribe on hero SKUs. |
| **5 — D1 territory** | 3+ categories, subscribed, 1kg | S$144–357 GP, 55–88% repeat | VIP track. Rec A guardrail. Flavour drops. |

**First product predicts D1 probability** (product analytics at acquisition):

| First product | % become D1 | Repeat | Action |
|---------------|-------------|--------|--------|
| Collagen Glow | **12%** | 37% | VIP onboarding from day 1 — protein cross-sell at day 21 |
| Clear Protein | 8% | 20% | Standard Rec C stack |
| Lean Protein | 6% | 21% | Standard Rec C stack |
| Accessories | **5%** | 20% | Mandatory protein trial within 30 days — do not treat as equal |

### How the two hero recs build D1

| D1 signal | Rec C contribution | Rec D contribution |
|-----------|-------------------|---------------------|
| 2+ categories (index 189) | CS-01/02 cross-sell at day 14 | — |
| 3+ categories (index 434) | CS-04 Collagen push at order 2 | SUB-04 welcome cross-sell |
| Ever subscribed (index 258) | — | SUB-01–04 full tier stack |
| 1kg pack (index 160) | Bundle includes 1kg Lean | SUB-02 upgrade nudge |
| Repeat buyer (index 427) | Category ladder lifts repeat 17%→55% | Subscribers at 62% repeat |

**Meeting framing:** *"We're not pitching two isolated tactics. Cross-sell builds the D1 basket. Subscription locks the D1 habit. Together they turn the 2,514 single-category customers and 3,577 non-subscribers into the next cohort of 368 D1s."*

**Full D1 doc:** `decile_analysis/D1_CUSTOMER_PROFILE.md`

---

## 4. Full recommendation stack (A–G)

| # | Rec | What | Prize (validated) | Deck role |
|---|-----|------|-------------------|-----------|
| **C** | Category ladder | Cross-sell 2nd/3rd category | **S$11–17K** | **LEAD** |
| **D** | Subscription engine | 4-tier S&S across journey | **S$4–5K** | **LEAD** |
| B | Cross-sell flows | Day 14 / day 7 Klaviyo emails | — | Executes C |
| E | Acquisition mix | Stop shaker-led; protein upsell | S$4K | Product |
| A | VIP guardrail | Exclude profit D1 from blanket % off | S$14K protected | Defensive |
| F | Gateway flavours | Feature Peach/TMT; deprioritise traps | ~S$1K | Sharpens C/E |
| G | Middle decile retry | Post-order-2 cross-sell for 88 stuck | ~S$269 | Nuance on C/B |

**Combined addressable GP:** S$30–35K/yr (not additive — some pools overlap).

**Deck order:** C (what) → 2A (how to cross-sell) → D (what) → 2B (how to subscribe) → 3 (D1 path) → A (guardrail).

---

## 5. Key data findings (reference during Q&A)

### Customer pool
- **4,290** finals-eligible customers (Shopify-primary, excl. 100% marketplace)
- **368** profit D1 (true COGS deciles) · **41% of true GP** from top decile
- **2,514** single-category · **1,216** two-category · **410** three-category

### Category ladder
| Categories | N | % | Avg GP | Repeat |
|------------|---|---|--------|--------|
| 1 | 2,514 | 59% | S$59 | 17% |
| 2 | 1,216 | 28% | S$79 | 30% |
| 3 | 410 | 10% | S$144 | 55% |
| 4+ | 150 | 3% | S$249 | 82% |

### Subscription gap
| Segment | N | Avg GP | Repeat |
|---------|---|--------|--------|
| Subscriber | 713 | S$134 | 62% |
| Non-subscriber | 3,577 | S$69 | 19% |

### Entry SKU quadrants (Rec F)
- **Gateway Heroes:** Clear Peach 500g (27%), Lean TMT 1kg (35%), Collagen 300g (34%)
- **Acquisition Traps:** Clear Shaker (21%), legacy "1 x Pack" handles (7–13%)
- **Hidden Gems:** high-repeat, low-volume flavours for email/PDP

### D1 customer fingerprint
- 368 profit D1 · S$357 avg GP · 88% repeat · 2.3 categories
- Top signals: Lean (index 275), Clear (265), Collagen (202), 1kg packs, 3+ categories
- Collagen-first buyers: 12% become D1 vs 5% accessories-first

### Decile × category (middle deciles)
- D5–D7: 1,309 customers, 70.5% at 1 category, avg 1.35 categories
- D1 grew 1.2 → 2.2 categories (2022–2025); middle deciles flat
- "Stuck repeaters" (1-cat, 3+ orders): 21 in D5–D7, 88 pool-wide with 2+ orders

---

## 6. How we use LP's margin data

### What LP provided
- **File:** `20260616-COGS_Data_Request_LushProtein (1).xlsx`
- **129 SKUs** with unit COGS (41 from product master + 214 LP-filled rows)
- Join key: `Line: SKU` on order line items

### Hybrid GP formula (used in all downstream analysis)

```
For each order line:
  IF SKU has COGS  →  GP = line_revenue − (qty × unit_cost)
  IF SKU missing   →  GP = line_revenue × 40%  (proxy fallback)

Customer GP = sum of all line GPs
```

**Why hybrid:** 74.7% of revenue has true COGS; 25.3% falls back to 40% proxy. This avoids dropping customers with partial SKU coverage.

### Coverage and impact

| Metric | Value |
|--------|-------|
| SKUs with COGS | 129 |
| Line-item coverage | 80.5% of finals lines |
| Revenue coverage | **74.7%** |
| Weighted margin (COGS lines) | **70.5%** (not 40%) |
| True GP on covered lines | S$418,263 |
| Old 40% proxy on all | S$317,786 |

**Key finding:** The 40% proxy **understates** margin on hero proteins. Profit D1 is more valuable than we initially thought.

### Where margin data is used today

| Analysis | Uses true COGS? | What it enables |
|----------|----------------|-----------------|
| `enrich_finals_with_margin.py` | ✅ | Enriches all `outputs_finals/*.parquet` with `unit_cost`, `gross_profit`, `true_gross_profit`, `profit_decile_true` |
| Profit deciles (D1–D10) | ✅ | True GP ranking; D1 = 368 customers, 41% of GP |
| Rec A (VIP guardrail) | ✅ | S$14K GP at risk from 10% blanket promo on D1 |
| Rec C prize math | ✅ | Category ladder GP uses `true_gross_profit` per customer |
| Rec D prize math | ✅ | Subscriber vs non-sub GP gap |
| D1 customer profile | ✅ | 368 true-COGS D1 fingerprint |
| Rec F/G validation | Partial | Repeat/LTV from revenue; GP uplift from true category ladder |
| Market basket / recommenders | ❌ (revenue) | Co-purchase patterns; not margin-weighted yet |
| Decile × category T4/T9 | ⚠️ Proxy | Category tables still use 40% uniform — **next refresh** |

### Planned next uses of margin data (ask LP to enable)

| Use | What we need | Impact |
|-----|--------------|--------|
| **SKU-level true margin ranking** | Remaining 25% SKU COGS filled | Rank Gateway Heroes by GP, not just repeat rate |
| **Promo ROI by SKU** | Discount depth per line + COGS | Quantify which promos destroy margin on hero SKUs |
| **Category T4/T9 refresh** | Rerun decile-category with true GP | Replace 40% proxy in Section 15 tables |
| **Bundle pricing** | COGS for bundle constituents | Price Clear+Lean bundle at target margin |
| **Subscribe & Save discount** | COGS on Peach/TMT | Set max sub discount without going below floor margin |
| **CAC payback by entry SKU** | CAC data from LP + COGS | Full Gateway Hero ranking (repeat × margin ÷ CAC) |

### What to tell LP about margin data

> "Your COGS file changed our profit story — real margin is **70.5%** on covered SKUs, not 40%. We've integrated it into customer GP, deciles, and all prize math. **74.7% coverage is strong** for a first pass. Filling the remaining ~25% of SKUs (legacy handles, marketplace-only, discontinued) would let us rank products by true margin and validate bundle/subscription pricing."

---

## 7. Questions to ask the LP team

Organised by topic. Prioritise **bold** questions — they directly affect recommendation sizing and feasibility.

### A. Validate execution readiness (Rec C + D)

1. **Who owns Klaviyo / CRM?** We have 5 cross-sell flows + 4 subscription flows ready to spec — need a named implementer.
2. **Can you trigger on "order fulfilled + X days" with product-level filters?** Required for CS-01/02/03 and SUB-01/03.
3. **Shopify bundle app?** Rebuy, Zipify, or native — needed for checkout cross-sell (Layer 2).
4. **Is Subscribe & Save live on Peach 500g and TMT 1kg?** If not, what's the timeline?
5. **Can you segment by custom properties** (`n_categories_ever`, D1 score, `crm_tier`)?

### B. Validate our two hero insights

1. **Does the single-category problem resonate?** Do you see customers who buy one flavour and never try Clear, Lean, or Collagen?
2. **What's your current cross-sell setup?** Any Klaviyo flows at day 14 post-order-1? What's the open/click/conversion rate?
3. **Subscribe & Save:** How many active subscribers today? What's the churn rate? Is subscription available on all hero SKUs (Peach 500g, TMT 1kg)?
4. **Which recommendation would you try first — category cross-sell or subscription?** (Tests appetite and operational readiness.)

### C. Product & acquisition (Rec E, F)

5. **How are featured/landing products chosen for ads and homepage?** Data shows shaker and legacy variant handles may be over-featured vs Peach/TMT.
6. **SKU handle cleanup:** We see the same product under multiple handles (e.g. barcode `0724999807814` at 27% repeat vs legacy `CLEAR-PEA-500G-V2` at 7%). Which is canonical in Shopify?
7. **What's your CAC by acquisition channel/product?** We have repeat rates by entry SKU but not cost — needed to fully rank Gateway Heroes.
8. **Are shakers used as paid acquisition lead?** Data: accessories-first = 20% repeat vs collagen-first = 37%.
9. **Discovery Sampler / sachet packs:** Are these actively promoted? Hidden Gems show 24–40% repeat on small volume.

### D. CRM & execution (Rec B, C, D, G)

10. **Klaviyo capability:** Can you trigger flows on "order fulfilled + X days"? Segment by `n_categories` and decile?
11. **Is there a post-order-2 email today?** We identified 88 middle-decile customers who ordered 2+ times on one category — what's their current touchpoint?
12. **Clear+Lean bundle:** Has this been tested? Any checkout upsell tooling (Rebuy, Zipify, native Shopify)?
13. **Personalisation:** Can Klaviyo dynamically insert SKU-specific recommendations (not generic "shop now")?

### E. Promotions & margin (Rec A)

14. **How often do you run site-wide % promos?** Our model: 10% off hitting profit D1 = **S$14K GP erosion/yr**.
15. **Do you segment promos by CRM tier today?** We built tiers: profit D1, freq D1, VIP, standard.
16. **What's your minimum acceptable margin on hero SKUs?** Needed to set Subscribe & Save discount floor and bundle pricing.

### F. Data & next steps

17. **Can you fill remaining COGS gaps?** ~25% of line revenue has no unit cost — mostly legacy/discontinued SKUs.
18. **Ad spend by product/campaign:** Would let us compute true CAC per entry SKU.
19. **Subscription economics:** Current sub discount %, avg subscription length, revenue per sub.
20. **What does success look like for this project?** Revenue lift? Repeat rate? GP? Reducing ad dependency?

### G. Strategic direction (most important)

21. **Is LP's growth priority acquisition or retention?** Our data says retention/depth (category ladder, subscription) outperforms new acquisition optimisation.
22. **Are you open to de-emphasising discounting in favour of product-structure plays?** (Bundles, cross-sell, subscription vs site-wide % off.)
23. **Timeline:** What's realistic for implementing a Klaviyo flow + bundle in the next 4–6 weeks?
24. **Who owns CRM execution?** (Need a named person for Rec B/C/D implementation.)

---

## 8. What we need from LP to sharpen the analysis

| Request | Why | Unlocks |
|---------|-----|---------|
| Remaining SKU COGS (25% gap) | True margin on all products | SKU margin ranking, bundle pricing |
| CAC by channel/campaign | Cost side of acquisition | Gateway Hero ranking with ROI |
| Klaviyo flow performance data | Validate conversion assumptions | Rec C/D/G prize refinement |
| Current promo calendar (last 12 months) | Quantify Rec A leakage | Exact GP at risk |
| Subscription metrics (churn, discount %, length) | Size Rec D opportunity | Compounding prize model |
| Canonical SKU / product handle mapping | Clean up duplicate handles | Accurate Rec F quadrant |
| Ad landing page product assignments | Validate acquisition trap hypothesis | Rec F/E execution |

---

## 9. What we can deliver after the meeting

Based on their answers, we can quickly:

1. **Klaviyo flow build sheet** — all 9 flows (CS-01–05, SUB-01–04) with triggers, delays, segments, and copy
2. **Refine prize math** with real Klaviyo conversion rates and CAC
2. **Refresh decile × category tables** with true COGS (T4/T9 margin columns)
3. **Build SKU margin ranking** once remaining COGS filled
4. **Draft Klaviyo flow copy** (already mocked in `pitch_analysis/INTEGRATION_DEMO.md`)
5. **Size subscription offer** with margin floor once LP confirms max discount
6. **D1 scoring Klaviyo segment export** — customers scored 0–100 for CRM routing
7. **Produce a 90-day experiment plan** with success metrics per recommendation

---

## 10. Anticipated pushback and how to respond

| Pushback | Response |
|----------|----------|
| "S$11K seems small" | It's conservative (5% conversion). 8% adds S$4K more. Compounding repeat over 2–3 years multiplies. And it costs near-zero vs ad spend. |
| "We already do cross-sell emails" | Great — what's the conversion rate? We have 5 flows specced with SKU-level personalisation, not generic. Our 88 stuck repeaters suggest gaps. |
| "Subscription isn't ready" | Phase it: cross-sell flows first (week 1–4), subscription flows once S&S is live on hero SKUs. Rec C alone is S$11K. |
| "How do we know who to target?" | D1 scoring checklist (Section 3). Klaviyo segments by score, category count, and first product. |
| "This sounds like a lot of flows" | 9 flows total, but launch in 2 waves: 3 cross-sell + 1 subscribe in week 1–2; rest in week 3–4. |
| "We need new customers, not retention" | 59% of existing customers are single-category — that's 2,514 people already acquired who haven't reached full value. Cheaper than new CAC. |
| "40% margin assumption" | We now use your real COGS. Weighted margin is 70.5% on covered SKUs. All prize math uses true GP where available. |
| "How confident are F and G?" | F is a merchandising framework with S$1K direct prize — low risk, permanent benefit. G is a 88-customer retargeting list, not a standalone rec. Both sharpen C and D. |

---

## 11. Meeting flow suggestion

| Time | Topic | Goal |
|------|-------|------|
| 5 min | Context: pool, COGS, what we built | Align on data foundation |
| 8 min | Hero 1: Category ladder (Rec C) | Validate the problem |
| 12 min | **Execution: Cross-sell playbook (Section 2A)** | Walk through flows, bundles, PDP — get CRM owner |
| 8 min | Hero 2: Subscription engine (Rec D) | Validate appetite |
| 10 min | **Execution: 4-tier subscription + D1 path (Sections 2B + 3)** | Show how C+D create D1 customers |
| 5 min | Guardrail: VIP promos (Rec A) | One slide |
| 12 min | **Questions (Section 7)** | Execution readiness + data requests |
| 5 min | Next steps: 90-day plan, what we need | Close with action items |

---

## 12. File index (everything built)

| Path | Contents |
|------|----------|
| `FINDINGS_AND_RECOMMENDATIONS.md` | Master summary |
| `pitch_analysis/NEW_RECOMMENDATIONS.md` | Rec C, D, E detail |
| `pitch_analysis/HYPOTHESES.md` | H1–H5 framework |
| `pitch_analysis/INTEGRATION_DEMO.md` | Email/PDP mockups |
| `Recommendation_A/RECOMMENDATION_A.md` | VIP guardrail |
| `Recommendation_B/RECOMMENDATION_B.md` | Cross-sell flows |
| `recommendation_systems/RECOMMENDER_SYSTEMS.md` | 4 recommender types |
| `margin_analysis/MARGIN_ANALYSIS.md` | COGS proof |
| `rec_f_g_validation/REC_F_G_FEEDBACK.md` | External rec critique |
| `rec_f_g_validation/REC_F_G_ANALYSIS.md` | Validated F/G analysis |
| `decile_analysis/D1_CUSTOMER_PROFILE.md` | D1 fingerprint + conversion |
| `enrich_finals_with_margin.py` | COGS enrichment pipeline |
| `outputs_finals/*.parquet` | Enriched customer/order/line data |

---

## 13. Regenerate all analysis

```bash
python EDA/aditya_findings/enrich_finals_with_margin.py
python EDA/aditya_findings/run_all.py
python EDA/aditya_findings/rec_f_g_validation/run_rec_f_g_analysis.py
python EDA/decile_analysis/run_d1_profile_analysis.py
```
