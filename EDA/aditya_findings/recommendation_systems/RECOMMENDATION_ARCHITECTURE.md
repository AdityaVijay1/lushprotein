# Recommendation Engine Architecture — Business Justification & Lifecycle Map

**Purpose:** Explain the 4-layer recommendation system in founder terms — what problem each layer solves, why that method was chosen, and where it deploys in the customer journey.

**Parent doc:** `../FINDINGS_AND_RECOMMENDATIONS.md` (Recommendation 2)  
**Scripts:** `sku_market_basket.py` · `build_recommenders.py` · `hierarchical_clustering.py`  
**Data:** `EDA/outputs_finals/` (customers, orders, lines — COGS-enriched)

---

## Why a 4-layer architecture (not one model)

| If you use… | What breaks |
|-------------|-------------|
| Only ML / CF for everyone | 67% one-and-done = no history → cold-start failure |
| Only association rules | Works for same cart, misses *next order* timing |
| Only rule-based | Works for first purchase, doesn't personalise repeat buyers |
| Only post-purchase email | No basket expansion on active sessions |

**Each layer matches a lifecycle stage.** Deploy in order: L1 → L2 → L3 → L4, with subscription flows parallel to L3.

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CUSTOMER LIFECYCLE                                    │
├──────────────┬──────────────┬──────────────────┬────────────────────────┤
│  1st visit   │  Active cart │  Post-purchase   │  Logged-in repeat      │
│  (cold)      │  (same order)│  (future orders) │  (3+ orders)           │
├──────────────┼──────────────┼──────────────────┼────────────────────────┤
│  LAYER 1     │  LAYER 2     │  LAYER 3         │  LAYER 4               │
│  Rule-based  │  Assoc rules │  Sequential +    │  Item-item CF          │
│              │  (MBA)       │  timed Klaviyo   │                        │
├──────────────┼──────────────┼──────────────────┼────────────────────────┤
│  Klaviyo     │  Shopify PDP │  Klaviyo CS-01–05│  Account page /        │
│  welcome     │  Cart widget │  SUB-01–04       │  homepage widget       │
└──────────────┴──────────────┴──────────────────┴────────────────────────┘
                              │
                              ▼
                    SUBSCRIPTION ENGINE
              (after 2nd purchase — lock replenishment)
```

---

## Layer 1 — First purchase recommendation

### Problem
New customer has zero purchase history. Collaborative filtering and ML need data that doesn't exist yet.

### Method
**Rule-based** recommendations from observed co-purchase rates among CM D1 buyers.

### Why this method
- **Evidence-based:** 53% of CM D1 Clear buyers also buy Lean; 65% vice versa — measured on your customers, not industry benchmarks.
- **Interpretable:** Founder and CRM team can audit every rule.
- **Fast:** Deploy in Klaviyo week 1 without engineering.

### Rules (top priority)

| First purchase | Recommend | Confidence | CRM segment |
|----------------|-----------|------------|-------------|
| Clear Protein | Lean TMT/Taro 1kg | 53% D1 co-purchase | T4 First Purchasers |
| Lean Protein | Clear Peach/W.Grape 500g | 65% D1 co-purchase | T4 |
| Collagen only | Clear or Lean starter | Low protein attach | T4 |
| Accessories only | Protein starter (not shaker) | 20% repeat vs 37% Collagen | T4 — fix acquisition |

### Deploy
- Order confirmation email (day 1–3)
- Welcome series email 2
- Post-purchase page "Customers like you also bought…"

### Output file
`outputs/recommender_01_rule_based.csv`

### Business impact
Routes T4 first purchasers toward 2nd category → **S$20–85 CM uplift** per ladder step.

---

## Layer 2 — Same cart recommendation

### Problem
Customer is actively shopping. Goal is **basket expansion** on this visit, not a future order.

### Method
**Association rules** (market basket analysis) on 8,955 finals orders.

### Why this method
- Measures **same-order** co-purchase — exactly what you need for "Add to cart" widgets.
- Confidence % is founder-friendly ("36% of Peach buyers also buy White Grape in the same order").
- Top rules have 333+ order support — statistically reliable.

### Top rules

| Antecedent | Consequent | Confidence | Lift | Deploy |
|------------|------------|------------|------|--------|
| Lean TMT 1kg | Clear shaker | **93%** | 10.2× | Cart cross-sell |
| Lean Taro 1kg | Lean TMT | **92%** | 53× | Flavour exploration |
| Clear sachet Peach | Clear sachet W.Grape | **71%** | 27.7× | Trial bundle |
| Clear Peach 500g | Clear W.Grape 500g | **36%** | 2.5× | PDP "Add both" |

### Deploy
- PDP bundle widget (top 5 revenue SKUs)
- Cart drawer "Frequently bought together"
- Checkout upsell (single high-confidence pair)

### Output files
`outputs/sku_association_rules.csv` · `outputs/sku_association_rules_full.csv`

### Business impact
Increases AOV without discounting. True bundle GP **S$73.60** (Clear+Lean, COGS-backed).

### Mockups
`../pitch_analysis/INTEGRATION_DEMO.md`

---

## Layer 3 — Post-purchase sequential recommendation

### Problem
Drive **2nd and 3rd product categories** on future orders. Customer has tried the product but hasn't reordered yet.

### Method
**Timed journey rules** + sequential SKU transition matrix — not immediate post-purchase cross-sell.

### Why this method
- Cross-sell for *next order* must land **before** the customer decides to reorder or churn.
- 739 measured 1st→2nd SKU transitions tell you what repeaters actually buy next.
- Day 14 after order 1 is the sweet spot: product experienced, reorder not yet placed.

### Timing table (non-negotiable)

| Trigger | Delay | Recommend | Target order | Klaviyo flow |
|---------|-------|-----------|--------------|--------------|
| Order 1 fulfilled | **Day 14** | Other protein category | Order 2 | CS-01 / CS-02 / CS-03 |
| Order 2 fulfilled | **Day 7** | 3rd category (Collagen, 2nd flavour) | Order 3 | CS-04 |
| Order 2 fulfilled | **Day 48** | Subscribe & Save | Ongoing | SUB-01 |
| Middle decile, 1-cat stuck | Day 7 after order 2+ | Same as CS-04 | Order 3+ | CS-05 |

**Do NOT** recommend cross-category on the thank-you page unless testing same-cart (Layer 2). The sequential goal is the *next* order.

### Sequential evidence

| 1st order SKU | Most common 2nd order | Insight |
|---------------|----------------------|---------|
| Clear Peach 500g | Clear White Grape | Flavour rotation within category |
| Clear Peach 500g | Lean TMT 1kg | Category expansion |
| Lean TMT 1kg | Lean Taro 1kg | Flavour rotation within Lean |

### Deploy
- Klaviyo post-purchase flows (primary)
- SMS reminder at day 12 (optional)
- Sample insert in fulfilment (see sample strategy below)

### Output files
`outputs/first_to_second_sku_matrix.csv` · `outputs/next_best_sku_per_first.csv`  
`../Recommendation_B/outputs/klaviyo_cross_sell_flows.csv`

### Business impact
- 8% of 2,514 single-category → 2nd category = **S$3,969 GP/yr**
- 5% → 3 categories = **S$10,693 GP/yr**

---

## Layer 4 — Logged-in personalised recommendation

### Problem
Repeat customers (3+ orders) need SKU-level suggestions beyond generic rules.

### Method
**Item-item collaborative filtering** — cosine similarity on customer × SKU purchase matrix.

### Why this method
- **User-based CF fails:** 67% one-and-done makes user vectors too sparse.
- **Item-item works from order 1:** "Customers who bought TMT also bought Taro" is valid after a single purchase.
- 83 SKUs with 10+ buyers — sufficient density for protein catalogue.

### Top similarities

| Anchor SKU | Similar SKU | Similarity |
|------------|-------------|------------|
| Lean TMT 1kg | Lean Taro 1kg | 0.40 |
| Lean TMT 1kg | Clear shaker | 0.30 |
| Clear Peach 500g | Clear W.Grape 500g | 0.16 |

### Deploy
- "Recommended for you" on account page
- Post-login homepage module
- Replenishment reminder with personalised SKU

### Output file
`outputs/recommender_04_item_similarity_matrix.csv`

### Business impact
Supports T1/T2 retention — surfaces next flavour/category without discounting.

### Deploy timing
Week 6+ after Layers 1–3 are live and measured.

---

## Sample strategy (cross-cutting Layer 3)

**Principle:** Samples are a **CM-budgeted** discovery tool, not a default first-order freebie.

| Moment | Goal | Sample type | Timing vs reorder |
|--------|------|-------------|-------------------|
| First order fulfilment | Reduce uncertainty | 1 complementary sachet (e.g. collagen for Clear buyer) | N/A |
| Day 14 email | Drive order 2 | Category discovery sachet offer | Before reorder window |
| Pre-reorder | Prevent lapse | Next-flavour sample | **7–10 days before** median reorder |

**Reorder medians (send reminder/sample before these):**

| Product | Median days |
|---------|-------------|
| Clear Protein 500g | 54 |
| Lean Protein 1kg TMT | 35 |
| Collagen Glow | 42 |
| Creatine 250g | 66 |

**Cost cap:** Use Rec 1 CM incentive framework — sample COGS ≤ X% of customer CM.

---

## Subscription engine (parallel to Layer 3)

**Ultimate goal:** Lock replenishment after product fit is proven.

| Signal | Pool | Offer | Why after 2nd purchase |
|--------|------|-------|----------------------|
| 2+ orders, not subscribed | 689 | Subscribe & Save | Demonstrated repeat intent |
| Freq D1, not subscribed | 228 | Replenishment sub | Highest order frequency |
| `is_top_both` VIP | 500 | VIP sub tier (no discount) | 51% already subscribed — grow the rest |

**Evidence:** Subscribers repeat **62%** vs **19%** · avg CM **S$134** vs **S$69**

**Prize:** 5% of 689 = **S$2,262 GP/yr** (direct) + compounding

---

## CRM segment → layer mapping

| CRM tier (Rec 1) | Primary layers | Subscription |
|------------------|----------------|--------------|
| T1 VIP Champions | L4 personalisation + exclusives | Already 51% sub — grow remainder |
| T2 High-Value Repeaters | L3 day 14/7 + L4 | SUB-01 at order 2 + 48 days |
| T3 Growth Customers | L3 CS-04/05 (3rd category) | SUB-01 after order 3 |
| T4 First Purchasers | L1 rules + L3 CS-01–03 | Not yet — prove fit first |
| T5 Low Value | Win-back only | No sub push |

---

## Side-by-side: 4 systems on same input

From `outputs/recommender_comparison_demo.csv`:

| Input SKU | L1 Rule | L2 Association | L3 Sequential | L4 Item-CF |
|-----------|---------|----------------|---------------|------------|
| Clear Peach 500g | Lean; Accessories | White Grape | Peach (replenish) | W.Grape, Shaker, TMT |

**Reading this:** Each layer gives a *different* valid answer for a *different* moment. L2 says add W.Grape to cart now. L3 says email Lean at day 14 for order 2. L4 says show TMT on account page.

---

## Deployment roadmap

| Week | Layer | System | Where | Success metric |
|------|-------|--------|-------|----------------|
| 1–2 | L1 + L3 | Rule-based + Klaviyo CS-01–03 | Email | 5–8% CTR |
| 2–3 | L2 | Association rules | PDP top 5 SKUs | Bundle attach rate |
| 3–4 | L3 | CS-04 + samples | Email + fulfilment | +5pp 2nd-category |
| 4–5 | Sub | SUB-01–02 | Email | 5% sub conversion |
| 6+ | L4 | Item-CF | Account page | Repeat SKU click rate |

---

## Regenerate

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
```

---

## Related files

| File | Content |
|------|---------|
| `RECOMMENDER_SYSTEMS.md` | Evidence tables + comparison |
| `SKU_MARKET_BASKET.md` | MBA method + top rules |
| `HIERARCHICAL_CLUSTERING.md` | Customer clusters (supplementary segmentation) |
| `../Recommendation_B/RECOMMENDATION_B.md` | Klaviyo flow detail |
| `../pitch_analysis/INTEGRATION_DEMO.md` | Email + PDP mockups |
