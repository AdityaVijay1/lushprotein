# Recommendation System — Deep Dive (Your Personal Reference)

**Purpose:** Explain exactly how each of the 4 recommendation layers was built, how each algorithm works, and what the outputs mean. Includes specific examples from LushProtein data.  
**Scripts:** `recommendation_systems/sku_market_basket.py` · `recommendation_systems/build_recommenders.py`  
**Presentation guide:** `final_presentation_rec_sys.md`

---

## Overview — Four Layers, Four Different Problems

The reason you need 4 different systems is that **each one solves a problem the others physically cannot**:

```
CUSTOMER MOMENT          PROBLEM                     ALGORITHM USED
─────────────────────────────────────────────────────────────────────
1st purchase             No history exists           L1 — Rule-based
(new customer)           → cold start                (co-purchase rates)

Active session           Basket expansion            L2 — Association rules
(browsing now)           → same order only           (market basket analysis)

Between orders           Cross-sell to next order    L3 — Sequential timed
(after delivery)         → timing is everything      (day 14 / day 44 rules)

Logged-in repeater       Personalise at SKU level    L4 — Item-item CF
(3+ purchases)           → history now exists        (cosine similarity)
```

Deploy order: L1 → L3 → L2 → Subscribe & Save → L4. (Not in layer number order — L3 runs in parallel with L1 because both need the post-purchase email trigger.)

---

## Layer 1 — Rule-Based Cold Start

### The problem

A new customer places their first order. You have **zero** purchase history for them. Collaborative filtering needs history. Machine learning models need training data. You have nothing.

This affects **67.6% of all customers** — the one-and-done majority who never make a second purchase without a nudge.

### How it works

Instead of ML, you use **manually-defined rules** derived from the co-purchase behaviour of your best customers (PM D1 = top 20% by profit margin).

**Step 1:** Look at all customers in PM Decile 1 (858 customers, averaging S$230 profit margin).  
**Step 2:** For each product category, calculate: "what % of D1 buyers who bought category X also bought category Y?"  
**Step 3:** Write those percentages as IF-THEN rules.

### The actual rules (from `recommender_01_rule_based.csv`)

| IF first purchase is... | THEN recommend... | D1 co-purchase rate |
|-------------------------|-------------------|---------------------|
| Clear Protein | Lean Protein (TMT or Taro 1kg) | **53%** |
| Lean Protein | Clear Protein (Peach or White Grape 500g) | **65%** |
| Lean Protein | Accessories (shaker) | 35% |
| Collagen Glow only | Clear Protein or Lean starter | ~31% |
| Accessories only | Protein starter (NOT another accessory) | ~21% |

### Concrete example

> Customer A places an order for **Clear Protein Peach 500g** (first order ever).  
>
> L1 fires:  
> "53% of top customers who bought Clear also bought Lean."  
> → Post-purchase email sent on day 1–3 after delivery  
> → Subject: "Your next step — Lean Protein TMT (what our top customers stack)"  
> → Call to action: shop Lean TMT 1kg

The customer has no history. But their first purchase matches a known pattern. The rule fires.

### Why rules, not ML, at this stage

- **67% of customers are one-and-done** → not enough repeat purchase data to train a meaningful ML model for first-timers
- Rules are **interpretable** — any team member can audit and update them as new products launch
- Rules can be **deployed in week 1** without engineering work
- D1 co-purchase rates are **evidence-based** — these are patterns from your actual best customers, not industry benchmarks

### Where it deploys

- Order confirmation email / thank-you page
- Day 1–3 post-purchase email (welcome series, email 2)
- Should NOT appear on the checkout page itself (that's L2's job)

### Output file

`recommendation_systems/outputs/recommender_01_rule_based.csv`

---

## Layer 2 — Market Basket Analysis (Association Rules)

### The problem

A customer is browsing the product page or has items in their cart **right now**. The goal is to **increase the value of this specific order** — not a future one. This is a fundamentally different problem from L1/L3.

### How association rules work

Association rules measure **same-order co-purchase** patterns from your 8,955 completed orders.

**The three key metrics:**

**Support** — how common is this pair overall?
```
Support(Peach, White Grape) = orders with BOTH / total orders
                            = 333 / 8955 = 3.7%
```
Support tells you if the rule is based on enough data. Low support = the rule is based on just a handful of orders and might be noise.

**Confidence** — if a customer has Peach, how likely are they to also buy White Grape in the same order?
```
Confidence(Peach → White Grape) = orders with BOTH / orders with Peach
                                 = 333 / ~924 = 36%
```
Confidence is the number you use to decide whether to show the recommendation. 36% means 1 in 3 Peach buyers adds White Grape to the same cart. That's a strong signal.

**Lift** — how much more likely is this pair vs random chance?
```
Lift(Peach → White Grape) = Confidence / (orders with White Grape / total orders)
                          = 2.5×
```
A lift of 2.5× means these two products are bought together 2.5× more than you'd expect if purchases were random. Any lift > 1.0 is a positive signal. Lift > 3× is very strong.

### Top rules from LushProtein data (`sku_association_rules.csv`)

| Antecedent | Consequent | Confidence | Lift | Orders |
|------------|------------|------------|------|--------|
| Lean TMT 1kg | Clear Shaker | **93%** | 10.2× | 144 |
| Lean Taro 1kg | Lean TMT 1kg | **92%** | 53× | 123 |
| Clear Sachet Peach | Clear Sachet White Grape | **71%** | 27.7× | 152 |
| Clear Peach 500g | Clear White Grape 500g | **36%** | 2.5× | 333 |

### Concrete example

> Customer B adds **Lean TMT 1kg** to their cart.  
>
> L2 fires:  
> "93% of customers who buy TMT also buy the Clear Shaker in the same order."  
> → Cart drawer shows: "Complete your stack — Clear Shaker (S$12.90)"  
> → Customer adds shaker → AOV increases by S$12.90

The 93% confidence and 10.2× lift make this one of the most reliable product pairings in the entire catalogue. The shaker is essentially a default accompaniment to Lean Protein.

### Important distinction from L1/L3

**L2 is same-order only.** The Lean Protein → Clear Protein cross-sell is L3 (next order) not L2. You would NOT put "try Clear Protein on your next order" in the cart widget — that's a distraction from the current purchase. The cart widget shows only items that 30%+ of buyers add to the same order.

### Where it deploys

- Product detail page (PDP) — "Frequently Bought Together" bundle widget
- Cart drawer — "Add both to cart" button
- Checkout page upsell (single highest-confidence pair only, to avoid distraction)
- Shopify can run the widget itself once you provide the pairs and confidence scores

### Output file

`recommendation_systems/outputs/sku_association_rules.csv` (top 20 rules)  
`recommendation_systems/outputs/sku_association_rules_full.csv` (all 46 rules)

---

## Layer 3 — Sequential Timed Journey (Post-Purchase Cross-Sell)

### The problem

Layer 3 solves the most common e-commerce mistake: cross-selling at the wrong time.

**Wrong:** Recommending Collagen in the cart when the customer just decided to buy Clear Protein.  
**Right:** Emailing them about Lean Protein 14 days after delivery, before they've decided what to buy next.

Layer 3 is built on two data sources:
1. **Sequential transition data** — what did customers actually buy as their 2nd, 3rd order?
2. **Reorder timing data** — how many days between orders for each key SKU?

### How it works

**Step 1 — Map first-to-second SKU transitions**

From all customers with 2+ orders, build a matrix of: "what was their 2nd order, given their 1st order?"

From `recommendation_systems/outputs/first_to_second_sku_matrix.csv` (739 measured transitions):

| 1st order SKU | Most common 2nd order SKU | Transition probability |
|---------------|---------------------------|------------------------|
| Clear Peach 500g | **Clear Peach 500g** (replenish) | 46.7% |
| Clear Peach 500g | Clear White Grape 500g | ~18% |
| Clear Peach 500g | Lean TMT 1kg (category expansion) | ~12% |
| Lean TMT 1kg | Lean TMT 1kg (replenish) | 47.2% |
| Clear Shaker | Lean TMT 1kg | 36.5% |

**Reading this:** Most second orders are replenishments of the same SKU. This tells you the cross-sell email should lead with the complementary category — not a repeat of what they already have.

**Step 2 — Map reorder timing**

From `EDA/outputs/12_reorder_interval_by_sku.csv`:

| SKU | Median reorder days | Email fires (day) | Sample ships (day) |
|-----|---------------------|-------------------|--------------------|
| Clear Protein 500g | **54 days** | Day 14 | Day 44 |
| Lean Protein 1kg | **35 days** | Day 14 | Day 25 |
| Collagen Glow 300g | **42 days** | Day 21 | Day 32 |
| Creatine 250g | **66 days** | Day 21 | Day 55 |

The sample ships **10 days before** the median reorder. This is the critical design choice: you're putting a Collagen or Lean sachet in their hands exactly when they're thinking about their next order.

**Step 3 — Define trigger rules**

| Trigger event | Delay | What fires |
|---------------|-------|------------|
| Order 1 fulfilled | + 14 days | CS-01/CS-02/CS-03 — cross-category email |
| Order 2 fulfilled | + 7 days | CS-04 — 3rd category push |
| Order 2 fulfilled | + 48 days | SUB-01 — Subscribe & Save offer |
| Pre-reorder window | - 10 days | Physical sample dispatched to customer |

### Concrete example

> Customer C orders Clear Protein Peach 500g on January 1.  
> Delivery estimated January 3.  
>
> **Day 14 (January 17):** Automated email fires → "Ready for your next challenge? Try Lean Protein TMT — your top customers stack these two."  
> *(This is 40 days before their median reorder — it's a discovery prompt, not a reorder reminder)*
>
> **Day 44 (February 16):** Fulfilment team ships a Lean 40g sachet + Collagen 15g sachet to their address.  
> *(This arrives around Day 47-48, ~7 days before their median 54-day reorder)*
>
> **Day 54 (February 24):** Customer decides to reorder. They've tried Lean. They add Lean to the cart.  
> → They've just stepped up the category ladder. Avg profit margin jumps from S$59 (1 cat) to S$79 (2 cats).

### The sachet timing question — answered with data

This was a specific founder question: *"Should the sachet go in the first order box or on the reorder?"*

**Data answer:** Ship separately, 10 days before reorder.

- In the first order box: the customer is focused on their Clear Protein. The Collagen sachet is noticed but not contextualised. No upcoming order to anchor it to.
- Day 44 after delivery: the customer is in their consumption window, will run out in ~10 days. A Collagen sachet arriving now lands when they're already thinking "what do I order next?"

### Where it deploys

- Post-purchase email automation (any platform with order fulfillment triggers)
- Physical sachet logistics (coordinate with fulfilment team on batch dispatch schedule)
- Does **not** require any changes to the Shopify storefront

### Output files

- `recommendation_systems/outputs/next_best_sku_per_first.csv` — for each first-order SKU, what to recommend
- `outputs/cross_sell_timing_and_samples.csv` — per-category email day, sample day, and sample product
- Flow copy: `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv` → adapt to current email platform

---

## Layer 4 — Item-Item Collaborative Filtering (Personalised)

### The problem

Repeat customers (3+ orders) have a purchase history. They've tried multiple products. They no longer need generic rules — they need recommendations based on what **they specifically** have bought.

### How collaborative filtering works — conceptually

The word "collaborative" means you're using the collective behaviour of ALL customers to make recommendations for any individual customer.

**User-user CF (the version that doesn't work here):**  
"Find customers who are similar to you based on purchase history, then recommend what they bought."  
Problem: 67% of customers have only 1 purchase. You can't find "similar customers" for someone with a single data point.

**Item-item CF (the version that does work here):**  
"Find items that are similar to each other based on which customers bought them."  
This works because even a single-purchase customer gives you information about item similarity.

### The mathematics

**Step 1 — Build the purchase matrix**

Create a matrix where:
- Each **row** is a customer (4,290 customers)
- Each **column** is a SKU (83 active SKUs with 10+ buyers)
- Each **cell** = 1 if that customer bought that SKU, 0 if not

```
         Clear Peach  Clear WGrape  Lean TMT  Lean Taro  Shaker  Collagen
Cust 1        1            0           1         0         1        0
Cust 2        1            1           0         0         0        0
Cust 3        0            0           1         1         1        0
Cust 4        1            0           0         0         0        1
...
```

**Step 2 — Compute cosine similarity between every pair of SKUs**

For any two SKUs (e.g., Lean TMT and Lean Taro), their "purchase vectors" are the columns from the matrix above.

Cosine similarity measures the angle between two vectors — how much do the same customers buy both?

```
                    vector_TMT · vector_Taro
similarity(TMT, Taro) = ─────────────────────────────────
                    ||vector_TMT|| × ||vector_Taro||
```

If all customers who buy TMT also buy Taro: similarity → 1.0  
If no customers overlap: similarity → 0.0  
If some overlap: similarity = a fraction between 0 and 1

**Key similarity scores from your data:**

| SKU A | SKU B | Cosine Similarity | Interpretation |
|-------|-------|-------------------|----------------|
| Lean TMT 1kg | Lean Taro 1kg | **0.86** | Very high — almost the same customers buy both (flavour rotation within Lean) |
| Lean TMT 1kg | Clear Shaker | **0.42** | Moderate-high — Lean buyers often add shaker |
| Clear Peach 500g | Clear White Grape 500g | **0.41** | Moderate-high — flavour rotation within Clear |
| Clear Peach 500g | Clear Shaker | **0.22** | Moderate — some crossover |
| Clear Peach 500g | Lean TMT 1kg | **0.04** | Low — Clear and Lean buyers have different purchase patterns (captured by L1 rules instead) |

**Step 3 — Build recommendation table**

For each SKU, rank all other SKUs by similarity score. The top 3–5 most similar = the recommendations.

```
Customer has bought: Clear Peach 500g
L4 recommendations (ranked by similarity):
  1. Clear White Grape 500g   (similarity: 0.41)
  2. Clear Shaker              (similarity: 0.22)
  3. Lean TMT 1kg              (similarity: 0.04)
```

**Step 4 — Match to customer purchase history**

For a logged-in customer with multiple purchases, look up all their bought SKUs, aggregate similarity scores, and surface the top items they haven't bought yet.

```
Customer D has bought: Clear Peach, Clear White Grape, Shaker
→ Already owns the top Clear similarities
→ Aggregate across all 3 items → Lean TMT emerges as top recommendation
→ Account page shows: "Based on what you love — try Lean TMT 1kg"
```

### Concrete example (full walk-through)

> Customer E has placed 3 orders:  
> Order 1: Clear Protein Peach 500g  
> Order 2: Clear Protein White Grape 500g (L3 email worked — flavour rotation)  
> Order 3: Clear Protein White Grape 500g + Clear Shaker (L2 PDP widget worked)  
>
> Customer E logs into their account. L4 fires:  
> - Clear Peach vector: top similar = White Grape (0.41), Shaker (0.22), Lean TMT (0.04)  
> - Customer already has White Grape and Shaker → filter out  
> - Remaining: Lean TMT (0.04), Lean Taro (0.03)...  
> - Also aggregate from White Grape vector: similar to Peach (0.41), Shaker (0.19), Lean TMT (0.14)  
> - And from Shaker vector: Lean TMT (0.42), Lean Taro (0.38)  
>
> **Final recommendation: Lean TMT 1kg** (strong signal from Shaker similarity + consistent across all purchase vectors)
>
> Account page shows: "Recommended for you — Lean TMT 1kg"

### Why item-item not user-user CF for this dataset

| Approach | Why it doesn't work for LP |
|----------|---------------------------|
| User-user CF | 67% have only 1 purchase → user vectors are too sparse to find similar users |
| Matrix factorisation (SVD, ALS) | Requires dense interaction data; LP's matrix is ~80% empty for most users |
| Content-based filtering | Requires rich product feature data (ingredients, macros, etc.) not available |
| **Item-item CF** | **Works because item vectors are dense enough (83 SKUs, 10+ buyers each); even single-purchase users contribute to item similarity** |

### Deploy timing and requirements

- Deploy in **week 6+** — after L1, L2, L3 have been running and generating repeat buyers
- Requires: logged-in account page on website, ability to query similarity matrix
- Refresh the similarity matrix monthly as new orders come in
- The matrix is pre-computed and stored as a CSV — lookup is fast

### Output file

`recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv`  
83 × 83 SKU matrix, cosine similarity scores, indexed by SKU slug.

---

## Subscribe & Save Engine (Parallel to Layer 3)

This is not a "5th layer" — it's an outcome engine that runs parallel to L3.

### The signal

Subscribers repeat at **62%** vs **19%** for non-subscribers. Average profit margin: **S$134** vs **S$69**. This is not a marginal difference — subscribers are nearly a different customer category.

51% of your 500 VIP customers (`is_top_both`) already subscribe. Subscription is a *signal* of your best customers, not a tool to acquire new ones. This means you should not push subscription at first purchase — wait for the signal to emerge naturally.

### The trigger logic

**Why order 2 + 48 days?**

- Order 2 proves product fit. The customer bought, received, and liked it enough to come back.
- 48 days after order 2 is typically 5–10 days before their 3rd reorder window
- At this point: they know they like the product, they're about to run out, subscription solves a problem they're already experiencing

**Eligible pools:**

| Pool | N | Trigger | Offer |
|------|---|---------|-------|
| Repeat non-subscribers (SUB-01) | 689 | Order 2 + 48 days | Subscribe & Save on hero SKU |
| Freq D1 non-subscribers (SUB-02) | 228 | Order 3 + 35 days | Replenishment subscription |
| First-time hero buyers (SUB-03) | ~400/yr | Order 1 + 42 days | Trial subscription |
| VIP remainder | ~244 | No % discount | VIP tier subscription (exclusives) |

### What NOT to do

- Do NOT offer subscription to T5 (one-and-done, S$9 avg margin) — the acquisition cost exceeds any subscription LTV gain
- Do NOT offer a % discount as a subscription incentive for T1 VIPs — they already subscribe at 51% without discounts
- Do NOT put Subscribe & Save as the CTA on order 1 — you haven't earned that yet

---

## How the Four Layers Work Together — A Full Customer Journey

Here is a complete end-to-end example showing how all layers interact for a single customer.

**Customer:** First-time buyer, T4 (first purchaser), buys Clear Protein Peach 500g.

### Day 0 — Order placed

**L2 fires at checkout:** PDP bundle widget shows "Clear White Grape 500g — 36% of buyers add both."  
→ Customer ignores it this time (fine — they're new, they know what they want).

**L1 queues post-purchase email:** Rule triggers — "this customer bought Clear, queue Lean email for day 3."

---

### Day 3 — L1 email sent

Email: Welcome email + soft introduction to Lean Protein.  
Subject: "How our top customers stack Clear + Lean"  
Content: Brief story about complementary nutrition + Lean product card.  
→ Customer opens, doesn't buy yet. That's normal.

---

### Day 14 — L3 email CS-01 fires

Email: Cross-category recommendation — Lean Protein TMT or Taro.  
Subject: "Your next step — before your Peach runs out"  
→ 5–8% of T4 customers click through and add to cart.  
→ This is 40 days before their reorder window — the email is about discovery, not urgency.

---

### Day 44 — Physical sample dispatched

Fulfilment dispatches a Lean Protein 40g single-serve sachet to the customer's address.  
The sachet arrives ~Day 47 — 7 days before the 54-day median reorder point.  
→ Customer tastes Lean Protein. Likes it.

---

### Day 54 — Customer places Order 2

Customer reorders Clear Peach AND adds Lean TMT 1kg (the L3 cross-sell worked).  
Customer is now a 2-category buyer. Avg profit margin jumps from ~S$59 to ~S$79.

**L2 fires again at checkout:** Shows Collagen Glow bundle (next category up).

---

### Day 61 (7 days after Order 2) — L3 CS-04 fires

Email: Recommend 3rd category — Collagen Glow.  
→ Setting up the potential move to S$144 avg profit margin.

---

### Day 102 (Order 2 + 48 days) — SUB-01 fires

Email: "Never run out — subscribe to Clear Protein + Lean Protein and save time."  
→ Customer has now proven product fit on both SKUs.  
→ If they subscribe: avg profit margin climbs toward S$134, repeat rate toward 62%.

---

### Week 6+ — If customer logs in with 3+ orders

**L4 activates:** Account page shows "Recommended for you — based on what you love."  
If they've bought Clear Peach, White Grape, and Lean TMT:  
→ L4 surfaces Lean Taro (similarity 0.86 with TMT) and Collagen Natural  
→ Discovery of new flavours/categories without you having to manually push them.

---

## Putting It All Together — The Decision Flowchart

```
Customer places order
        │
        ├─ Is it their 1st purchase?
        │   └─ YES → L1 rule fires (post-purchase email day 1-3)
        │         + L3 CS-01 queued (day 14 email)
        │         + L3 sample queued (day 44 dispatch)
        │
        ├─ Are they actively browsing?
        │   └─ YES → L2 bundle widget on PDP + cart
        │
        ├─ Is it their 2nd purchase?
        │   └─ YES → L3 CS-04 queued (day 7 email, 3rd category)
        │         + SUB-01 queued (day 48 subscription trigger)
        │
        └─ Are they logged in with 3+ purchases?
            └─ YES → L4 item-CF on account page
```

---

## Regenerating the Recommendation Outputs

```bash
# Rebuild MBA rules (L2)
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py

# Rebuild all 4 recommenders (L1, L3, L4 + comparison demo)
python EDA/aditya_findings/recommendation_systems/build_recommenders.py

# Rebuild CRM tier timing (L3 timing CSVs)
python EDA/aditya_findings/build_crm_tiers_and_timing.py

# Rebuild all charts
python EDA/aditya_findings/build_rec_sys_charts.py
```

---

## Key Numbers to Remember

| Metric | Value | Source |
|--------|-------|--------|
| One-and-done rate | 67.6% | `outputs_finals/decile_customer_table.csv` |
| Customers with 2+ orders | ~1,390 (32.4%) | Calculated from above |
| Customers with 3+ orders | ~730 (17%) | Estimated from order frequency |
| D1 co-purchase: Clear → Lean | 53% | `Recommendation_B/outputs/co_purchase_matrix_d1.csv` |
| D1 co-purchase: Lean → Clear | 65% | Same source |
| Top MBA rule confidence (TMT → Shaker) | 93% | `recommendation_systems/outputs/sku_association_rules.csv` |
| Clear Protein 500g median reorder | 54 days | `outputs/12_reorder_interval_by_sku.csv` |
| Lean Protein 1kg median reorder | 35 days | Same source |
| Subscriber repeat rate | 62% | `outputs_finals/decile_customer_table.csv` |
| Non-subscriber repeat rate | 19% | Same source |
| Subscriber avg profit margin | S$134 | Same source |
| SUB-01 eligible pool | 689 customers | `outputs/crm_treatment_tiers.csv` |
| Item-CF TMT → Taro similarity | 0.86 | `recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv` |
| Item-CF Peach → White Grape similarity | 0.41 | Same source |
