# Four Recommendation Systems — Comparison & Deployment Guide

**Script:** `build_recommenders.py`

---

## The four systems

### 1. Rule-based (deploy first)

**File:** `recommender_01_rule_based.csv`

Hard-coded category rules from T3 cross-category analysis:
- Clear → Lean, Lean → Clear, Collagen → Clear, Accessories → Lean

| Pros | Cons |
|------|------|
| Works on 1st purchase (cold start) | Same rules for everyone |
| 1 day to deploy in Klaviyo | No flavour-level precision |

**Best for:** Post-purchase email flows (Rec B Phase 1)  
**Expected lift:** 5–8% category attach

---

### 2. Association rules (same-order MBA)

**File:** `sku_association_rules.csv`

SKU pairs that appear in the same basket (support/confidence/lift).

| Pros | Cons |
|------|------|
| Flavour-specific (Peach + White Grape) | Needs basket data |
| High confidence on accessories attach | Doesn't know order sequence |

**Best for:** Shopify PDP "Frequently bought together"  
**Expected lift:** 2–4% on PDP

---

### 3. Sequential next-best

**File:** `first_to_second_sku_matrix.csv`

Given what a customer bought on order 1, what do they buy on order 2?

| Pros | Cons |
|------|------|
| Order-sequence aware | Needs 1 prior order |
| Best for replenishment + cross-sell timing | Sparse for rare SKUs |

**Best for:** Post-purchase email at order 2–3  
**Expected lift:** 3–5% on repeat orders

---

### 4. Item-based collaborative filtering (ML)

**File:** `recommender_04_item_similarity_matrix.csv`

Customer × SKU binary matrix → cosine similarity between items.  
*"Customers who bought X also bought Y"* based on 83 SKUs with 10+ buyers.

**Why item-based, not user-based:**
- LP has **4,290 customers** but **sparse SKU space** — item similarity is more stable
- New customers can get recommendations from day 1 if they buy a popular SKU
- User-based CF fails on cold-start (67% one-and-done)

| Pros | Cons |
|------|------|
| Discovers non-obvious pairs | Poor for brand-new SKUs |
| Personalises for logged-in users | Needs periodic retrain |

**Best for:** "You may also like" on account page  
**Expected lift:** 2–3% incremental vs rules alone

---

## Demo comparison (`recommender_comparison_demo.csv`)

| Input SKU | Rule-based | Association | Sequential | Item-CF |
|-----------|------------|-------------|------------|---------|
| Clear Peach | Lean; Accessories | White Grape | Peach (replenish) | White Grape, Shaker, Lean TMT |
| Lean TMT | Clear; Accessories | — | TMT (replenish) | Taro, Shaker, Clear Peach |

---

## Deployment roadmap

| Week | System | Where |
|------|--------|-------|
| 1–2 | Rule-based | 3 Klaviyo flows (Rec B) |
| 3–4 | Association rules | PDP widgets on top 5 SKUs |
| 5–6 | Sequential | Post-purchase flow order 2 |
| 7+ | Item-CF | Logged-in recommendations |

---

## Chart

`fig_recommender_effort_impact.png` — Rule-based = best effort/impact ratio for LP's stage.

---

## Regenerate

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
```
