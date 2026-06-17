# Integration Demo — Recommendation Systems on Website & Email

This is a **data-backed mockup** of how each recommender plugs into LP's Shopify + Klaviyo stack.
All product pairs below come from `sku_association_rules.csv` with measured confidence.

---

## 1. Post-purchase email (Rule-based + Sequential) — Klaviyo

**Trigger:** Order fulfilled, customer on order 1, bought Clear Protein Peach 500g

```
Subject: Your Peach Clear is on the way — here's what loyal customers try next

Hi {{ first_name }},

Thanks for your order. Based on 1,614 Clear Protein buyers in our data:

  65% also use Lean Protein — Thai Milk Tea is the #1 pairing.

[Shop Lean TMT 1kg — S$XX]  ← CTA

P.S. 36% of Peach buyers also love White Grape — try a flavour rotate next order.
```

**Evidence:** D1 Lean->Clear co-purchase 65.4% (`co_purchase_matrix_d1.csv`).  
Peach->White Grape association confidence 26% (`sku_association_rules.csv` row 18).

**Expected attach:** 5-8% click-to-purchase on order 2 (rule-based benchmark for DTC supplements).

---

## 2. Shopify PDP — Association rules widget

**Page:** `/products/clear-protein-peach-500g`

```
┌─────────────────────────────────────────────────────┐
│  Frequently bought together (based on 333 orders)   │
│                                                     │
│  [x] Clear Peach 500g          S$59.90              │
│  [x] Clear White Grape 500g    S$54.90  (-8%)       │
│  [ ] Clear Shaker White        S$12.90              │
│                                                     │
│  Bundle price: S$109.70  (save S$18.10)              │
│  [Add bundle to cart]                               │
└─────────────────────────────────────────────────────┘
```

**Data rule:** `clear-protein|Peach` -> `clear-protein|White Grape` (confidence 26%, lift 2.5x, 333 co-orders)

---

## 3. Cart drawer — Item-based CF (logged-in repeat buyer)

**Customer:** Bought Lean TMT 1kg on previous order. Now viewing Lean Taro.

```
You may also like (based on customers like you):
  • Lean Thai Milk Tea 1kg  (40% similarity)
  • Clear Shaker White      (30% similarity)
  • Clear Peach 500g        (16% similarity)
```

**Source:** `recommender_04_item_similarity_matrix.csv` — cosine similarity on 83 SKUs.

---

## 4. Subscribe & Save offer (Sequential + replenishment)

**Trigger:** 48 days after Lean TMT 1kg purchase (median reorder gap: 35-54 days)

```
Your Thai Milk Tea is running low — 54% of subscribers reorder every 6 weeks.

Subscribe & Save 10%:
  Lean TMT 1kg every 6 weeks — S$XX/delivery

[Start subscription]
```

**Evidence:** Reorder gap median 48 days (all repeaters), Lean protein category analysis.

---

## Which system to deploy first?

| Priority | System | Where | Why first |
|----------|--------|-------|-----------|
| 1 | Rule-based | Klaviyo post-purchase | Works on order 1, highest attach |
| 2 | Sequential | Klaviyo order 2-3 | Uses order history |
| 3 | Association rules | Top 5 PDPs | Peach, TMT, Taro, White Grape, Collagen |
| 4 | Item-CF | Account page | Needs login + history |

**Files to hand LP dev/agency:**
- `sku_association_rules.csv`
- `first_to_second_sku_matrix.csv`
- `klaviyo_cross_sell_flows.csv`
- `recommender_comparison_demo.csv`

<!-- Rule: 0724999810463|Thai Milk Tea -> lushprotein-clear-shaker|White conf=0.93 -->

<!-- Rule: 0724999810470|Taro -> 0724999810463|Thai Milk Tea conf=0.92 -->

<!-- Rule: 0724999810470|Taro -> lushprotein-clear-shaker|White conf=0.90 -->

<!-- Rule: 0724999810463|Thai Milk Tea -> 0724999810470|Taro conf=0.79 -->

<!-- Rule: clear-protein-25g-single-sachet|White Grape -> clear-protein-25g-single-sachet|Peach conf=0.71 -->
