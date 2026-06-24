# Recommendation 2 — How to Present It (Founder Guide)

**Purpose:** Clear story arc for Rec 2 — from *problem* → *why a system* → *four layers + subscription* → *conservative prize* → *how to implement*.  
**Companion:** `RECOMMENDATION_2_ENGINE_AND_SUBSCRIPTION.md` (technical depth) · `PRESENTATION.md` (full 10-slide deck)  
**Charts:** `outputs/charts/` · regenerate: `python EDA/aditya_findings/build_presentation_charts.py`

---

## The one-line pitch (memorise this)

> *"Most customers buy one category once and leave. A recommendation system tells each customer the **right next product at the right moment** — not a generic Shopify widget — and subscription locks in the ones who prove they'll come back."*

Rec 1 tells you **who** to treat differently. Rec 2 tells you **what to recommend, when, and where** — then offers Subscribe & Save only after they've ordered twice.

---

## Part 1 — How to open: the problem (60–90 seconds)

### Don't start with "we built 4 algorithms"

Start with the **business pain** LP already feels:

| Say this | Number | Why it lands |
|----------|--------|--------------|
| "Most customers never come back" | **67.6%** buy once | Retention > acquisition (founder priority) |
| "They're stuck in one category" | **59%** (2,514) only ever buy 1 category | Cross-sell = more categories, not more discount |
| "One category = low repeat" | **17%** repeat at 1 cat vs **55%** at 3 cats | The prize is moving people up the ladder |
| "Subscribers behave completely differently" | **62%** repeat vs **19%** non-sub | Subscription is the end-state, not the opener |

**Chart:** `outputs/charts/rec2_problem_retention_gap.png`  
*(Alternative: `r2_category_ladder.png` if you only have room for one)*

**Script:**
> *"You don't have a traffic problem — you have a **next-order** problem. Almost 7 in 10 customers buy once. Nearly 6 in 10 never try a second product category. When they do reach 3 categories, repeat more than triples. The question isn't whether to recommend — it's **when** and **what**."*

### Bridge to "why a recommendation system"

Generic email blasts and site-wide promos fail because:

1. **Wrong moment** — cross-sell at checkout ≠ cross-sell before reorder  
2. **Wrong product** — Peach + White Grape in cart (same order) ≠ Lean Protein on order 2 (next order)  
3. **Wrong customer** — VIP gets same message as one-and-done  
4. **No path to subscription** — asking for S&S on first purchase before product fit

**That gap is why LP needs a lifecycle recommendation system** — not one Shopify block.

---

## Part 2 — The gap: what Shopify / generic tools miss (45 seconds)

**Chart:** `outputs/charts/r2_shopify_vs_custom_engine.png`

| Founder asked | Shopify "Recommended products" | Our system |
|---------------|-------------------------------|------------|
| Cross-sell **more categories** | Shows related SKUs on PDP | Clear→Lean rules from **your** co-purchase data (53–65%) |
| **When** to send samples | Can't time journeys | Day 14 email + day 44 sachet before 54d reorder |
| **Who** gets gifts | Everyone | T4 sachet · T1 merch · T5 email only (Rec 1 tiers) |
| Lock replenishment | Separate app | SUB-01 after order 2 + 48 days |

**Script:**
> *"Shopify is fine for **Layer 2** — 'add White Grape to cart with Peach.' It cannot answer your meeting question: should the Collagen sachet go in the first box or **10 days before they reorder**? That's Layer 3 — timed journeys from your reorder data."*

**Chart (optional depth):** `outputs/charts/rec2_one_sku_four_layers.png`  
Shows Clear Peach gets **four different valid recommendations** depending on moment — proves why one engine isn't enough.

---

## Part 3 — The solution: four layers + subscription (90 seconds)

### Simple mental model

Think of Rec 2 as **four answers to four questions**:

| Layer | Customer moment | Question answered | Algorithm | Built by |
|-------|-----------------|-------------------|-----------|----------|
| **L1** | Just bought (no history) | "What category next?" | Rule-based co-purchase | `build_recommenders.py` |
| **L2** | In cart / on PDP | "What goes with this order?" | Association rules (MBA) | `sku_market_basket.py` |
| **L3** | Between orders | "When & what for order 2/3?" | Sequential + clock | `build_recommenders.py` + `build_crm_tiers_and_timing.py` |
| **L4** | Logged in, 3+ orders | "What's personalised for me?" | Item-item CF | `build_recommenders.py` |
| **Sub** | After order 2 | "Lock replenishment?" | Klaviyo SUB-01 | `FOUNDER_MEETING_PREP.md` flows |

**Charts (pick 2 max on slide):**
- Architecture: `outputs/charts/r2_four_layer_architecture.png`
- Journey: `outputs/charts/rec2_lifecycle_implementation.png`

**Script:**
> *"We don't use one model for everything — 67% of customers are one-and-done, so collaborative filtering fails on first purchase. Layer 1 uses rules from your best customers. Layer 2 expands the cart today. Layer 3 emails and samples between orders. Layer 4 personalises repeat buyers. Subscription fires only after order 2 — when they've proven fit."*

### Founder's sample-timing question (your strongest Rec 2 moment)

**Chart:** `outputs/charts/r2_cross_sell_timeline_clear.png` + `r2_sample_by_purchase_stage.png`

| When | Do this | Layer |
|------|---------|-------|
| Checkout | Same-category bundle only (Peach + W.Grape) | L2 |
| Day 14 after delivery | Email: try Lean on order 2 | L3 (CS-01) |
| Day 44 after delivery | Ship Collagen/Lean sachet (**before** 54d reorder) | L3 + fulfilment |
| Day 48 after order 2 | Subscribe & Save if not subscribed | SUB-01 |

**Script:**
> *"Not in the first order box — ship the cross-category sample **before** they decide to reorder, so they can add original + new category. First purchase gets rules and email. Second purchase qualifies for subscription."*

---

## Part 4 — Conservative numbers you can say on stage

Use **base case** in the pitch; **conservative** if challenged; **upside** as aspiration.

**Chart:** `outputs/charts/rec2_conservative_prize.png`

### Modeled annual gross profit (Rec 2 only — engine + subscription)

| Scenario | Assumption | Calculation | **Annual GP** |
|----------|------------|-------------|---------------|
| **Conservative** | 3% of single-cat buyers add 2nd category + 3% of repeat non-subs subscribe | 2,514 × 3% × S$20 + 689 × 3% × S$66 | **~S$2,900** |
| **Base case** *(recommended slide number)* | 8% add 2nd category + 5% subscribe | 2,514 × 8% × S$20 + 689 × 5% × S$66 | **~S$6,200** |
| **Upside** | 5% reach 3 categories + 5% subscribe | 2,514 × 5% × S$85 + 689 × 5% × S$66 | **~S$12,900** |

**Source:** `pitch_analysis/outputs/prize_scenarios_explained.csv` (H1, H2 hypotheses)

### Operational KPIs (conservative, Year 1) — say these instead of over-promising GP

| KPI | Conservative target | Source |
|-----|---------------------|--------|
| Day-14 email click rate | **5%** | `recommender_system_comparison.csv` (L1 attach 5–8% low end) |
| 2nd-category attach lift | **+3 pp** on T4 pool | vs 17% baseline repeat at 1 cat |
| PDP bundle attach (L2) | **2–4%** on bundle PDPs | MBA expected attach |
| SUB-01 conversion | **3–5%** of 689 eligible | H2 at 5%; use 3% as conservative |
| Sample cost cap | **≤ S$2.54** per T4 customer | 5% of avg T4 profit margin (Rec 1) |

**Script for conservative close:**
> *"We're not claiming S$30K tomorrow. Base case from your data is **~S$6K direct GP in year one** from moving single-category buyers up one step and converting a small slice of repeaters to subscription — with operational targets we can measure in Klaviyo every week."*

### What NOT to say

- Don't promise "5% of everyone reaches 3 categories" as baseline — that's upside (S$10,693 alone)
- Don't lead with L4 / ML — it's week 6+ polish
- Don't pitch subscription on first purchase — founder and data both say after order 2

---

## Part 5 — Chart map: need vs solution

| Story beat | Chart file | Use when |
|------------|------------|----------|
| **Problem** — stuck at 1 category | `rec2_problem_retention_gap.png` | Opening Rec 2 |
| **Problem** — ladder economics | `r2_category_ladder.png` | Same slide or backup |
| **Gap** — Shopify vs custom | `r2_shopify_vs_custom_engine.png` | "Why not default?" |
| **Solution** — 4 layers | `r2_four_layer_architecture.png` | Architecture slide |
| **Solution** — one customer journey | `rec2_lifecycle_implementation.png` | Tie layers to timeline |
| **Solution** — one SKU, 4 answers | `rec2_one_sku_four_layers.png` | "Why 4 algorithms?" |
| **Timing** — sample before reorder | `r2_cross_sell_timeline_clear.png` | Founder's question |
| **Timing** — who gets sachets | `r2_sample_by_purchase_stage.png` | 1st vs 2nd vs VIP |
| **Subscription** — decile proof | `r2_subscription_by_profit_decile.png` | Sub after repeat |
| **Prize** — conservative range | `rec2_conservative_prize.png` | Business case close |
| **Evidence** — MBA rules | `recommendation_systems/outputs/fig_top_association_rules.png` | Appendix / Q&A |
| **Evidence** — effort vs impact | `recommendation_systems/outputs/fig_recommender_effort_impact.png` | "Why this order?" |

---

## Part 6 — Implementation: 4 layers + subscription engine

### Master implementation table

| Phase | Week | Layer / engine | What to build | Data file | Deploy surface | Owner |
|-------|------|----------------|---------------|-----------|----------------|-------|
| **1** | 1–2 | **L1 + L3** | Klaviyo CS-01, CS-02, CS-03 | `recommender_01_rule_based.csv` · `klaviyo_cross_sell_flows.csv` | Email day 14 after order 1 | CRM |
| **1** | 1–2 | **Rec 1 gate** | Import CRM tiers | `outputs_finals/crm_treatment_tiers.csv` | Segment filters in Klaviyo | CRM |
| **2** | 2–3 | **L2** | PDP bundles top 5 SKUs | `sku_association_rules.csv` | Shopify PDP / cart | E-com |
| **3** | 3–4 | **L3 samples** | Pre-reorder sachet fulfilment | `cross_sell_timing_and_samples.csv` | Ops / 3PL insert | Ops |
| **3** | 3–4 | **L3** | CS-04 day 7 after order 2 | `next_best_sku_per_first.csv` | Klaviyo email | CRM |
| **4** | 4–5 | **Subscription** | SUB-01, SUB-02 | `FOUNDER_MEETING_PREP.md` §2B | Klaviyo day 48 post-order-2 | CRM |
| **5** | 6+ | **L4** | Account recommendations | `recommender_04_item_similarity_matrix.csv` | Shopify account page | E-com |

**Chart:** `outputs/charts/rec2_lifecycle_implementation.png` (same timeline visually)

---

### Layer 1 — Rule-based (cold start)

**Problem:** 67% one-and-done → no purchase history for ML.

| Step | Action |
|------|--------|
| 1 | Run `python EDA/aditya_findings/recommendation_systems/build_recommenders.py` |
| 2 | Open `recommendation_systems/outputs/recommender_01_rule_based.csv` |
| 3 | Map `if_bought` → `recommend` into Klaviyo welcome / order confirmation |
| 4 | Segment: **T4 First Purchasers** only for category cross-sell rules |

**Top rules (from your data):**

| First purchase | Recommend | Evidence file |
|----------------|-----------|---------------|
| Clear Protein | Lean Protein | `Recommendation_B/outputs/co_purchase_matrix_d1.csv` (53%) |
| Lean Protein | Clear Protein | same (65%) |
| Collagen only | Clear or Lean starter | 30.5% Collagen-first repeat |
| Accessories only | Protein starter | 20% repeat vs 37% Collagen-first |

**Klaviyo flows:** CS-01, CS-02, CS-03 in `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv`

---

### Layer 2 — Association rules (same cart)

**Problem:** Increase basket on **this visit** — not next order.

| Step | Action |
|------|--------|
| 1 | Run `python EDA/aditya_findings/recommendation_systems/sku_market_basket.py` |
| 2 | Open `recommendation_systems/outputs/sku_association_rules.csv` |
| 3 | Add PDP widget on Clear Peach, Lean TMT, top 5 revenue SKUs |
| 4 | **Do not** use L2 for cross-category samples at checkout |

**Top rules to ship first:**

| Antecedent | Consequent | Confidence |
|------------|------------|------------|
| Clear Peach 500g | White Grape 500g | 36% |
| Lean TMT 1kg | Clear shaker | 93% |
| Clear sachet Peach | Clear sachet W.Grape | 71% |

**Mockup:** `pitch_analysis/INTEGRATION_DEMO.md` (PDP bundle wireframe)

---

### Layer 3 — Sequential + timed journeys (the core retention engine)

**Problem:** Drive order 2 and order 3 **between** purchases.

| Step | Action |
|------|--------|
| 1 | Run `build_crm_tiers_and_timing.py` → timing CSV |
| 2 | Build Klaviyo flows from `klaviyo_cross_sell_flows.csv` |
| 3 | Pick order-2 SKU from `next_best_sku_per_first.csv` / `first_to_second_sku_matrix.csv` |
| 4 | Schedule physical samples from `outputs/cross_sell_timing_and_samples.csv` |

**Klaviyo flow reference:**

| Flow | Trigger | Delay | Target order | Product | File column |
|------|---------|-------|--------------|---------|-------------|
| **CS-01** | Order 1, Clear bought | **14 days** | Order 2 | Lean TMT/Taro | `klaviyo_cross_sell_flows.csv` |
| **CS-02** | Order 1, Lean bought | **14 days** | Order 2 | Clear Peach/W.Grape | same |
| **CS-03** | Order 1, Collagen only | **21 days** | Order 2 | Clear/Lean starter | same |
| **CS-04** | Order 2 fulfilled | **7 days** | Order 3 | Collagen / 2nd flavour | `FOUNDER_MEETING_PREP.md` |
| **CS-05** | Order 2+, stuck 1-cat | **7 days** | Order 3+ | Same as CS-04 | middle decile retarget |

**Sample ship days (from `cross_sell_timing_and_samples.csv`):**

| First category | Email day | Sample ship day | Median reorder |
|----------------|-----------|-----------------|----------------|
| Clear Protein | 14 | **44** | 54 days |
| Lean Protein | 14 | **25** | 35 days |
| Collagen | 14 | **32** | 42 days |

**Purchase-stage logic:** `outputs/sample_strategy_by_purchase_stage.csv`

---

### Layer 4 — Item-item CF (logged-in personalisation)

**Problem:** Repeat buyers (3+ orders) need SKU-level discovery.

| Step | Action |
|------|--------|
| 1 | Output from `build_recommenders.py` → `recommender_04_item_similarity_matrix.csv` |
| 2 | Deploy on account page / post-login homepage |
| 3 | **Wait until L1–L3 live** (week 6+) — measure baseline first |

**Example similarities:** TMT → Taro (0.40) · TMT → Shaker (0.30) · Clear Peach → W.Grape (0.16)

**Why item-CF not user-CF:** 67% one-and-done = sparse user vectors (`RECOMMENDER_SYSTEMS.md`)

---

### Subscription engine (parallel track — not a "layer")

Subscription is the **outcome** when L3 proves repeat intent. It is not a recommender algorithm.

```
L3 day-14 email  →  customer places order 2  →  qualifies for SUB-01
                                              →  day 48 after order 2: Subscribe & Save offer
```

| Flow | Who | Pool | Trigger | Delay | Message angle |
|------|-----|------|---------|-------|---------------|
| **SUB-01** | T2 repeat non-subs | **689** | Order 2 fulfilled | **48 days** | Replenish hero SKU (Peach/TMT) |
| **SUB-02** | Freq D1 non-subs | **228** | Order 3 fulfilled | **35 days** | Lock high-frequency replenishment |
| **SUB-03** | Hero first-time buyers | ~400/yr | Order 1 fulfilled | **42 days** | Trial sub *(optional — lower priority)* |
| **SUB-04** | Checkout | New orders | At checkout | 0 | Pre-checked S&S on Peach/TMT |

**Decile proof chart:** `r2_subscription_by_profit_decile.png` — PM D1 sub rate **33.4%** vs D5 **2.6%**

**Rule:** Primary pitch = **SUB-01 after order 2**. Do not lead with checkout sub (SUB-04) — founder wants fit first.

**Full flow copy:** `FOUNDER_MEETING_PREP.md` · `pitch_analysis/INTEGRATION_DEMO.md`

---

### CRM tier → what fires (Rec 1 × Rec 2)

Import `crm_treatment_tiers.csv` first — layers respect tier:

| Tier | N | Layers active | Subscription |
|------|---|---------------|--------------|
| **T4** First-tx | 2,120 | L1 welcome + L3 CS-01–03 + pre-reorder sachet | ✗ Wait |
| **T3** Growth | 63 | L3 CS-04 + 3rd-cat sample | SUB-01 after order 3 |
| **T2** High-value | 744 | L2 bundles + L3 full | **SUB-01** primary pool |
| **T1** VIP | 532 | L4 + merch/events | VIP S&S (54% already sub) |
| **T5** Low | 831 | Win-back email only | ✗ No sub push |

---

## Part 7 — Suggested Rec 2 slide sequence (within your 10-slide deck)

If Rec 2 gets **~4 slides** inside `PRESENTATION.md`:

| Slide | Title | Chart |
|-------|-------|-------|
| A | The next-order problem | `rec2_problem_retention_gap.png` |
| B | Why Shopify isn't enough | `r2_shopify_vs_custom_engine.png` |
| C | Four layers + one journey | `rec2_lifecycle_implementation.png` |
| D | When to sample + conservative prize | `r2_cross_sell_timeline_clear.png` + `rec2_conservative_prize.png` |

Optional backup slides (not counted — appendix): `rec2_one_sku_four_layers.png` · `r2_subscription_by_profit_decile.png`

---

## Part 8 — Full talk track (3 minutes for Rec 2)

**0:00 — Problem**  
*"59% of customers only buy one category. Repeat at one category is 17%. At three categories it's 55%. They aren't discovering Lean or Collagen on their own."*  
→ Show `rec2_problem_retention_gap.png`

**0:45 — Why a system**  
*"Shopify recommends products on the product page. It can't time a Collagen sachet 10 days before a Clear buyer's 54-day reorder, or skip gifts for one-and-done customers. That's why we built a lifecycle engine on your 8,955 orders — and why you asked us to keep it custom."*  
→ Show `r2_shopify_vs_custom_engine.png`

**1:30 — Solution**  
*"Four layers, four moments. Rules when they're new. Basket rules in the cart. Timed emails and samples between orders. Personalisation when they're loyal. Subscription only after order two."*  
→ Show `rec2_lifecycle_implementation.png`

**2:15 — Founder's question**  
*"Cross-category samples ship day 44 — not in the first box — so they try Collagen before deciding to reorder. First-timers get email at day 14. VIPs get merch, not sachets."*  
→ Show `r2_cross_sell_timeline_clear.png`

**2:45 — Prize + ask**  
*"Base case ~S$6K year-one GP from 8% adding a second category and 5% subscribing — conservative ops targets we track weekly. Week 1: CS-01 in Klaviyo. Week 2: Peach bundle on PDP. Week 4: SUB-01."*  
→ Show `rec2_conservative_prize.png`

---

## Part 9 — Regenerate everything

```bash
# Recommender CSVs (L1, L2, L3, L4)
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py

# CRM tiers + sample timing
python EDA/aditya_findings/build_crm_tiers_and_timing.py

# All deck charts (including rec2_* story charts)
python EDA/aditya_findings/build_presentation_charts.py
```

---

## Quick reference — file tree

```
EDA/aditya_findings/
├── REC2_PRESENTATION_GUIDE.md          ← this file
├── RECOMMENDATION_2_ENGINE_AND_SUBSCRIPTION.md
├── recommendation_systems/
│   ├── sku_market_basket.py           → L2
│   ├── build_recommenders.py          → L1, L3, L4
│   ├── RECOMMENDATION_ARCHITECTURE.md
│   ├── RECOMMENDER_SYSTEMS.md
│   └── outputs/
│       ├── recommender_01_rule_based.csv
│       ├── sku_association_rules.csv
│       ├── first_to_second_sku_matrix.csv
│       ├── next_best_sku_per_first.csv
│       ├── recommender_04_item_similarity_matrix.csv
│       └── recommender_comparison_demo.csv
├── Recommendation_B/outputs/
│   └── klaviyo_cross_sell_flows.csv   → CS-01–03
├── outputs/
│   ├── cross_sell_timing_and_samples.csv
│   └── charts/rec2_*.png
└── FOUNDER_MEETING_PREP.md            → SUB-01–04 + CS-04/05 copy
```

---

## Anticipated confusion → clear answer

| Confusion | Clear answer |
|-----------|--------------|
| "Is this one recommender?" | No — **four algorithms for four moments**. See `rec2_one_sku_four_layers.png`. |
| "Is subscription part of the engine?" | **Parallel outcome** — L3 creates order 2; SUB-01 locks it. |
| "What's the first thing to ship?" | **CS-01** (Clear→Lean, day 14) + CRM tier import. Lowest effort, highest signal. |
| "Where did the rules come from?" | Your orders — `co_purchase_matrix_d1.csv`, `sku_association_rules.csv`, not industry defaults. |
| "How does Rec 1 connect?" | T4 gets L1+L3 sachet. T1 gets L4+merch. T5 gets nothing but email. |
