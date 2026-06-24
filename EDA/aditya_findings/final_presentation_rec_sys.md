# Recommendation System — Final Presentation Guide

**Who:** LushProtein founder(s)  
**What:** How to present Recommendation 2 — the 4-layer engine + subscription system  
**Goal:** Convince them to implement, in the right order, for the right reasons  
**Charts folder:** `outputs/charts/rec_sys_*.png` · `outputs/charts/r2_*.png`  
**Companion technical doc:** `recommendation_sys.md`

---

## The one-line pitch (memorise this first)

> *"Most customers buy one category and never come back. A recommendation system tells each customer the right next product at the right moment — and once they've bought twice, Subscribe & Save locks in their replenishment without any discount."*

Rec 1 answers **who** to treat differently.  
Rec 2 answers **what to recommend, exactly when, and through which channel** — then offers subscription only after they've proven they'll come back.

---

## Story arc — how to flow through the presentation

```
PROBLEM                     WHY A SYSTEM               4 LAYERS
"Most customers              "One widget                 "Match one algorithm
 buy once and leave"    →    can't do all this"     →   to each lifecycle moment"

↓
SAMPLE TIMING               SUBSCRIPTION               IMPLEMENTATION
"Before reorder,       →    "After order 2,       →    "6 weeks, easy to hard,
 not at checkout"            not at checkout"            measurable at each step"
```

---

## Part 1 — Open with the business problem (60 seconds)

**Do NOT start with "we built 4 algorithms."** Start with the problem the founder already feels.

### The numbers to open with

| Say this | Number | Why it lands |
|----------|--------|--------------|
| "Most customers never come back" | **67.6%** buy once | Founder's biggest worry — retention |
| "They're stuck at just one product category" | **59%** (2,514 customers) | Makes the cross-sell opportunity concrete |
| "One category = low repeat" | **17%** repeat at 1 cat vs **55%** at 3 cats | The prize is visible |
| "Subscribers behave completely differently" | **62%** repeat vs **19%** | Subscription is the destination, not the entry point |

**Chart to show:** `rec2_problem_retention_gap.png`  
*(Or `r2_category_ladder.png` if you only have one slide)*

**Script:**
> *"You don't have a traffic problem — you have a next-order problem. Almost 7 in 10 customers buy once. 6 in 10 never try a second category. When they do reach 3 categories, repeat rate triples. The question is: do customers discover the next category on their own? Or do you need to show them the right product at the right moment?"*

### The bridge — why timing and moment matter more than the product itself

The same product recommendation is **right or wrong depending on when you show it**.

> **Example:** Clear Protein — Peach 500g  
> - At checkout: show White Grape 500g (36% of Peach buyers add it in the same order)  
> - At day 14: email recommending Lean Protein (for order 2, not this order)  
> - At day 44: ship a Collagen or Lean sachet (10 days before the 54-day median reorder)  
> - On account page after 3 orders: show TMT or Taro from their purchase history similarity

One SKU. Four different correct answers. Completely different moments.

**Chart to show:** `rec2_one_sku_four_layers.png`

---

## Part 2 — Why Shopify's widget isn't enough (45 seconds)

**Chart to show:** `r2_shopify_vs_custom_engine.png`

This slide answers the implicit founder question: *"Can't we just turn something on in Shopify?"*

| What you need | Shopify default | Your 4-layer engine |
|---------------|-----------------|----------------------|
| Cross-category push (Clear → Lean) | No category model | L1 rules + L3 day-14 email (53–65% D1 co-purchase) |
| **When** to nudge (not just what) | Always on PDP | Day 14 email, day 44 sample, pre-reorder |
| **Who** gets what | Same for everyone | T1–T5 profit margin tiers |
| Sample/sachet timing | Not supported | Per-category timing from reorder data |
| Subscription after product fit | Separate app | Subscribe & Save after order 2 + 48 days |
| VIP experience | Same experience | T1 account page + no % discounts |

**Script:**
> *"Shopify is fine for Layer 2 — 'add White Grape to cart with your Peach.' It cannot answer your real question: should the Collagen sachet go in the first order box, or 10 days before their next reorder? That's Layer 3 — and that timing comes from your own data."*

---

## Part 3 — The 4-layer mental model (90 seconds)

**Chart to show:** `rec_sys_architecture_v2.png`  
*(This is the definitive architecture slide — 4 layers + lifecycle bar + data proof column)*

### The simple mental model

Think of the 4 layers as **four different questions** you're answering at four different moments:

| Layer | The question | When | Algorithm | Data source |
|-------|-------------|------|-----------|-------------|
| **L1** | "What should a new customer try next?" | After 1st order, no history | Rule-based co-purchase | D1 buyer co-purchase rates |
| **L2** | "What else goes in the cart right now?" | Active session — browsing | Association rules (MBA) | 8,955 same-order purchase pairs |
| **L3** | "What should I email before they reorder?" | Between orders | Timed sequential rules | 739 measured SKU transitions + reorder medians |
| **L4** | "What does this specific customer love?" | Logged-in, 3+ purchases | Item-item CF | 4,290 × 83 SKU similarity matrix |

### Why can't you use just one model?

**Chart to show:** `rec_sys_why_4_layers.png`

- **If you use only ML/CF:** 67% of customers have no history → cold-start failure for the majority
- **If you use only association rules:** works for same cart, misses the post-order timing entirely
- **If you use only rule-based:** works for first purchase, never personalises repeat buyers
- **If you use only post-purchase email:** misses basket expansion on active sessions (no PDP widget)

**The insight:** each layer solves a problem the others cannot. They work together, in sequence.

---

## Part 4 — How each layer actually works (2 minutes)

### Layer 1 — Rule-based cold start

**Chart:** `rec_sys_l1_cold_start.png`

**The problem:** A brand new customer has zero purchase history. Machine learning needs history that doesn't exist yet.

**The solution:** Use observed co-purchase rates from your top (D1) customers as rules.

```
IF customer buys Clear Protein
THEN recommend Lean Protein (TMT or Taro 1kg)
WHY: 53% of your highest-value customers bought both
WHEN: day 1–3 post-purchase email
```

```
IF customer buys Lean Protein
THEN recommend Clear Protein (Peach or White Grape 500g)  
WHY: 65% of your highest-value customers bought both
WHEN: day 1–3 post-purchase email
```

**Why this works:** You're using the actual buying behaviour of your best customers as a template for new ones — not industry benchmarks or guesses.

**Founder talking point:** *"We're not inventing rules. We measured what your most profitable customers actually bought together. We're just using those patterns to guide first-timers."*

---

### Layer 2 — Market basket association rules

**Chart:** `rec_sys_l2_mba_rules.png`

**The problem:** Customer is on the product page or in their cart, right now. The goal is to expand this specific order.

**The solution:** Association rules from 8,955 orders — "customers who bought X in the same order also bought Y."

**Top rules from your data:**

| If customer has... | Also show... | Confidence | Order count |
|--------------------|--------------|------------|-------------|
| Lean TMT 1kg | Clear Shaker | **93%** | 144 orders |
| Clear Peach 500g | Clear White Grape 500g | **36%** | 333 orders |
| Clear Sachet Peach | Clear Sachet White Grape | **71%** | 152 orders |
| Lean Taro 1kg | Lean TMT 1kg | **92%** | 123 orders |

**Where it deploys:** Product page "Frequently Bought Together" widget + cart drawer.

**Founder talking point:** *"This is the only layer where Shopify can help. We give them the exact pairs and confidence scores — Shopify shows the widget. Everything else requires your own automation."*

---

### Layer 3 — Sequential timed cross-sell

**Chart:** `rec_sys_l3_timing_detail.png`

**The problem:** Drive 2nd and 3rd category on FUTURE orders — not the current one. This is where most brands fail: they cross-sell at checkout for the NEXT product when the customer just decided what they want.

**The critical insight:**
- The right moment to recommend Lean Protein to a Clear buyer is **day 14 after delivery** — not at checkout
- The right moment to ship a Collagen sachet is **day 44** — 10 days *before* the 54-day median reorder

**Timing table (non-negotiable):**

| Trigger | Action | Day | Goal |
|---------|--------|-----|------|
| Order 1 fulfilled | Email: recommend cross-category | **Day 14** | Drive 2nd category on order 2 |
| Order 2 fulfilled | Email: recommend 3rd category | **Day 7** | Drive 3rd category by order 3 |
| Order 2 + 48 days | Subscribe & Save offer | **Day 48** | Lock replenishment |
| Pre-reorder window | Physical sachet shipped | **-10 days** | Introduce new category before decision |

**The sachet timing question (your strongest moment):**
> *"Should the Collagen sachet go in the first order box or before their next reorder?"*
> **Answer: 10 days BEFORE their reorder median. Not in the first box.**
> A sachet in the first box is ignored (they're focused on what they just bought). A sachet arriving 10 days before they need to reorder introduces Collagen exactly when they're thinking about their next order.

**Chart for this specific point:** `r2_cross_sell_timeline_clear.png`

---

### Layer 4 — Item-item collaborative filtering

**Chart:** `rec_sys_l4_item_cf_heatmap.png`

**The problem:** Repeat customers (3+ orders) need personalised SKU-level suggestions based on their actual purchase history.

**The solution:** Item-item collaborative filtering — cosine similarity on a 4,290 × 83 SKU purchase matrix.

**How it works (in plain terms):**
1. Build a matrix: for each of your 4,290 customers, mark which of 83 SKUs they bought
2. For each pair of SKUs, measure how often the same customers bought both (cosine similarity)
3. For any SKU a customer has bought, find the top-3 most similar SKUs they haven't tried
4. Show those on their account page as "Recommended for you"

**What the similarity scores look like:**

| If customer bought | Also similar to | Similarity |
|--------------------|-----------------|------------|
| Lean TMT 1kg | Lean Taro 1kg | **0.86** (very high — same-category flavour swap) |
| Lean TMT 1kg | Clear Shaker | **0.42** (same buyers often add shaker) |
| Clear Peach 500g | Clear White Grape 500g | **0.41** (flavour rotation in Clear line) |
| Clear Peach 500g | Clear Shaker | **0.22** (accessory cross-sell) |

**Why item-item, not user-user CF?**
67% of customers buy only once — user vectors are too sparse for user-user CF to work. Item vectors have enough density (83 active SKUs, each with 10+ buyers) for reliable similarity scores.

**Deploy timing:** Week 6+ — after Layers 1–3 are running and generating repeat buyers for L4 to personalise.

---

## Part 5 — Sample timing (your strongest specific moment)

This is where you answer the founder's question directly with data.

**Charts to show:** `r2_cross_sell_timeline_clear.png` + `rec_sys_l3_timing_detail.png`

| Moment | Do this | Layer | Why |
|--------|---------|-------|-----|
| At checkout | Same-category bundle only (Peach + White Grape) | L2 | Customer is in cart, different mindset |
| Day 3 after order | Post-purchase email: welcome + soft intro to Lean | L1 | Fresh impression, product excitement |
| Day 14 after delivery | Email: try Lean on order 2 | L3 CS-01 | Product experienced, reorder not yet placed |
| Day 44 after delivery | Ship Collagen/Lean sachet (**10d before** 54d reorder) | L3 + fulfilment | Customer discovers new category before deciding |
| After order 2 + 48 days | Subscribe & Save offer | SUB-01 | They've proven they'll come back |

---

## Part 6 — Subscription follows repeat, not cold traffic

**Chart to show:** `r2_subscription_by_profit_decile.png`

**Key numbers:**
- Subscribers repeat at **62%** vs **19%** for non-subscribers
- Subscriber avg profit margin: **S$134** vs **S$69** for non-subs
- **51% of your 500 VIPs already subscribe** — subscription is a signal of your best customers, not an acquisition tool

**The trigger rule:** Offer Subscribe & Save only after their **second successful purchase** — they've demonstrated product fit.

**Pool:** 689 customers with 2+ orders who have never subscribed (SUB-01 pool).

**Script:**
> *"Don't push subscription at first purchase. That's the equivalent of asking someone to marry you on the first date. Wait until they've bought twice — then offer replenishment. This is when it makes sense to them, and when it's cheapest for you because you're not discounting to acquire a subscriber who might not stick."*

---

## Part 7 — CRM tier × layer matrix (who gets what)

**Chart to show:** `rec_sys_tier_layer_matrix.png`

This chart ties Rec 1 and Rec 2 together — the CRM tier (from Rec 1) determines which recommendation layers fire and what incentive is available.

| CRM Tier | Primary layers | Subscription treatment |
|----------|----------------|------------------------|
| **T1 VIP** (500) | L4 personalisation primary; L2/L3 always on | 51% already sub; grow remaining VIPs — no % discount |
| **T2 High-Value** (744) | L3 day-14/7 + L4 (week 6+) | **Primary sub conversion target** — SUB-01 at order 2 |
| **T3 Growth** (63) | L1 + L3 CS-04/05 (3rd category push) | After order 3 |
| **T4 First Buyer** (2,120) | L1 critical + L3 CS-01–03 | Not yet — prove fit first |
| **T5 Low Value** (831) | Win-back email only | No push |

---

## Part 8 — Implementation roadmap (close the presentation)

**Chart to show:** `rec_sys_implementation_roadmap.png`

The sequencing is deliberate — easiest and highest-impact first:

| Week | Action | Why first | Measurable outcome |
|------|--------|-----------|-------------------|
| **1–2** | L1 post-purchase email (T4 first buyers) + L3 day-14 email | No engineering, highest customer volume | Email CTR 5–8% |
| **2–3** | L2 PDP bundle widget (top 5 SKUs) | Shopify-native, quick to deploy | Bundle add-to-cart >10% |
| **3–4** | L3 day-44 sachet logistics | Fulfilment coordination | Sample-to-purchase conversion >15% |
| **4–5** | Subscribe & Save trigger (689 eligible) | Proven repeaters already exist | 5% sub conversion |
| **6+** | L4 account page CF | Needs repeat buyer pool from earlier layers | Repeat SKU click rate >8% |

**The ask of the founders:**

1. Confirm which email automation platform they're moving to (for post-purchase flow setup)
2. Approve sachet/sample budget for T4 (≤S$2.54/customer from CM incentive framework)
3. Confirm product page capability for bundle widget (Shopify PDP)
4. Agree on Subscribe & Save discount structure (or no-discount replenishment model)
5. Sign off on timeline — which week to start

---

## Anticipated Q&A — sharp one-line answers

| Question | Answer |
|----------|--------|
| "Why not just one recommender?" | 67% one-and-done = cold start; CF fails without history. L1 covers those 2,870 customers CF cannot. |
| "Can Shopify do this?" | Layer 2 only (PDP widget). Layers 1, 3, 4 + subscription timing require post-purchase email automation with custom rules from this analysis. |
| "Why not recommend at checkout?" | Checkout is for same-cart (L2). Cross-category at checkout is noise — customer has already decided. Day 14 email lands before next order decision. |
| "Should the sample go in the first order box?" | No — day 44, 10 days before the 54d median reorder. Sachet at order 1 is ignored. Sachet before reorder window introduces the category exactly when they're deciding. |
| "When do we push subscription?" | After order 2 — product fit proven. Pushing subscription at order 1 gets 19% repeat conversion. Waiting until order 2 gives you a buyer who already came back. |
| "What if our email platform doesn't support this?" | The logic (day 14, day 7, day 48 triggers) is platform-agnostic. Any email automation tool with order-fulfillment triggers supports this. The recommendation data is in CSVs already built. |
| "How do we measure if it's working?" | 2nd-category attach rate (target: +5pp vs control), bundle add-to-cart rate (>10%), subscription conversion (5% of 689-customer pool). |

---

## Chart reference map — which chart for which slide

| Presentation moment | Primary chart | Backup chart |
|---------------------|---------------|--------------|
| Open: problem is retention | `rec2_problem_retention_gap.png` | `r2_category_ladder.png` |
| Same SKU, 4 answers | `rec2_one_sku_four_layers.png` | — |
| Why not Shopify | `r2_shopify_vs_custom_engine.png` | — |
| 4-layer architecture | `rec_sys_architecture_v2.png` | `r2_four_layer_architecture.png` |
| Why 4 layers (coverage) | `rec_sys_why_4_layers.png` | — |
| L1 cold-start rules | `rec_sys_l1_cold_start.png` | — |
| L2 MBA rules | `rec_sys_l2_mba_rules.png` | `rec2_v2_pdp_mockup.png` |
| L3 timing | `rec_sys_l3_timing_detail.png` | `r2_cross_sell_timeline_clear.png` |
| L3 gantt / journey | `rec2_v2_gantt_clear_journey.png` | — |
| L4 item-CF | `rec_sys_l4_item_cf_heatmap.png` | — |
| Subscription | `r2_subscription_by_profit_decile.png` | — |
| Who gets what | `rec_sys_tier_layer_matrix.png` | — |
| Roadmap + close | `rec_sys_implementation_roadmap.png` | — |
| Combined prize | `combined_annual_impact.png` | `rec2_conservative_prize.png` |

---

## Output files already built (hand these over)

| What | File | Use for |
|------|------|---------|
| L1 cold-start rules | `recommendation_systems/outputs/recommender_01_rule_based.csv` | Post-purchase email content |
| L2 association rules | `recommendation_systems/outputs/sku_association_rules.csv` | PDP bundle widget configuration |
| L3 cross-sell timing | `recommendation_systems/outputs/next_best_sku_per_first.csv` | Email day-14 product selection |
| L3 sample timing | `outputs/cross_sell_timing_and_samples.csv` | Fulfilment sachet dispatch schedule |
| L4 item-CF matrix | `recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv` | Account page personalisation |
| Full comparison demo | `recommendation_systems/outputs/recommender_comparison_demo.csv` | Shows 4 systems side-by-side |
| CRM tier export | `outputs_finals/crm_treatment_tiers.csv` | Tier tagging for email segmentation |

---

*Regenerate all charts: `python EDA/aditya_findings/build_rec_sys_charts.py`*  
*Technical deep-dive: `recommendation_sys.md`*
