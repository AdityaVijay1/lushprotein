# Rec 2 — Story FAQ, Terminology & Better Charts

**Use with:** `REC2_PRESENTATION_GUIDE.md` · `RECOMMENDATION_2_ENGINE_AND_SUBSCRIPTION.md`

---

## Quick answers to your questions

### What does **S&S** mean?

**Subscribe & Save** — Shopify’s replenishment subscription (customer gets recurring deliveries of the same SKU, often at a small loyalty discount on the subscription price). In our docs, **SUB-01** is the Klaviyo flow that offers S&S **48 days after order 2** to customers who have proven they repeat but are not yet subscribed.

---

### What is a **PDP widget** (Layer 2)?

**PDP = Product Detail Page** — the Shopify page for a single product (e.g. `/products/clear-protein-peach-500g`).

A **PDP widget** is a block on that page showing “Frequently bought together” or “Add bundle to cart” while the customer is still shopping. It expands the **current order**, not a future order.

**Chart:** `outputs/charts/rec2_v2_pdp_mockup.png`  
**Real example in docs:** `pitch_analysis/INTEGRATION_DEMO.md` §2

Layer 2 rule example: Clear Peach 500g → add White Grape 500g (**36%** same-order confidence from `sku_association_rules.csv`).

---

### Layer 1 — what do these repeat stats mean?

#### “37% Collagen-first repeat” (use this number, not 30.5%)

Of customers whose **first-ever purchase category** was **Collagen Glow** (209 customers in the finals pool):

- **36.8%** placed a **second order or more** (`finals_orders ≥ 2`)
- That rounds to **~37% repeat**

**Meaning for L1:** Collagen-first buyers are **more likely to come back** than protein-only or shaker-first buyers. The L1 rule says: recommend **Clear or Lean protein** on the welcome journey so they attach a protein habit, not just collagen.

**Note:** Some older files say **30.5%** — that figure is **outdated**. Verified from `decile_customer_table.csv` June 2026: **36.8%**.

#### “20% repeat vs 37% Collagen-first” (Accessories comparison)

This compares **two acquisition entry points**:

| First purchase category | Customers | Repeat rate (2+ orders) |
|-------------------------|-------------|-------------------------|
| **Collagen Glow** | 209 | **37%** |
| **Accessories** (shaker, etc.) | 371 | **21%** |
| Clear Protein | 887 | 20% |
| Lean Protein | 616 | 21% |

**Meaning for L1:** Someone who only bought a **shaker** first behaves like a one-and-done acquirer (~20% repeat). Someone who bought **collagen** first is almost **2× more likely to repeat**. So:

- **Collagen-first** → cross-sell **protein** (they already have a supplement ritual)
- **Accessories-first** → cross-sell **protein trial** (sachet/starter) — **do not** send another shaker

**Chart:** `outputs/charts/rec2_v2_entry_category_repeat.png`

---

### Layer 3 — confirm sample ship days?

**Yes — confirmed** from `outputs/cross_sell_timing_and_samples.csv`. Full table:

| First category | Email day | Sample ship day | Median reorder | Sample product (not full pack) |
|----------------|-----------|-----------------|----------------|--------------------------------|
| **Clear Protein** | **14** | **44** | **54 days** | Collagen 25g sachet **or** Lean 40g single-serve |
| **Lean Protein** | **14** | **25** | **35 days** | Clear 25g sachet **or** Collagen sachet |
| **Collagen Glow** | **21** | **32** | **42 days** | Clear 25g sachet **or** Lean 40g single-serve |

**Logic:** Sample ships **~10 days before** median reorder so the customer tries a new category **before** deciding to repurchase. Samples are **sachets/single-serves**, not full tubs.

**Chart:** `outputs/charts/rec2_v2_pack_reorder_compare.png`  
**Journey chart:** `outputs/charts/rec2_v2_gantt_clear_journey.png`

---

### Are Clear and Lean the same pack size?

**No.** They are different hero SKUs with different pack weights **and** different scoop sizes.

#### Why “1kg = 25 serves” but “500g = 20 serves” is not a math error

Serve counts on the label are **grams per scoop**, not “weight ÷ weight” across product lines:

| Product | Pack | Labelled serves | Implied scoop | Median reorder |
|---------|------|-----------------|---------------|----------------|
| **Clear Protein** | 500g | 20 | **~25g** | **54 days** |
| **Lean Protein** | 1kg | 25 | **~40g** | **35 days** |
| **Collagen Glow** | 300g | 30 | **~10g** | **42 days** |

So Lean is not “half the serves for double the weight.” Lush labels Lean at **40g per serve** (meal-style scoop) and Clear at **~25g per serve** (lighter clear whey scoop). Collagen is **~10g**. Those labels come straight from variant titles in `12_reorder_interval_by_sku.csv` (e.g. `500g Pack (20 Serv)`, `1kg Pack (25 servings)`).

**Do not compare serve counts across lines** — compare **median reorder days**, which is what Layer 3 actually uses.

#### What Layer 3 is actually doing

Layer 3 does **not** calculate timing from serves. It uses **observed days between repeat purchases** for each hero SKU:

1. **Email day 14** — category cross-sell for order 2 (same for Clear and Lean).
2. **Sample ship day** — about **10 days before** that SKU’s median reorder (44 before 54, 25 before 35, 32 before 42).
3. **Median reorder** — from order history, not from tub math.

Lean buyers reorder at **35 days** because that is what the data shows for Lean TMT/Taro 1kg — likely heavier daily use (40g scoops) and a different buyer habit — not because “25 serves ÷ 1kg” implies it.

**Cross-sell email (day 14)** recommends the **full product** for order 2 (e.g. Lean TMT **1kg** in CS-01). **Physical sample** is always a **small trial size** (25g Clear / 40g Lean / 25g Collagen sachet).

---

## Why the old charts felt unusable

| Old chart | Problem | Use instead |
|-----------|---------|-------------|
| `rec2_one_sku_four_layers` | Four equal bars with text crammed inside — reads like a table, not a story | `rec2_v2_gantt_clear_journey.png` |
| `rec2_lifecycle_implementation` | Scattered dots on a line — hard to read timing | `rec2_v2_gantt_clear_journey.png` |
| `r2_four_layer_architecture` | Good as architecture summary, weak alone for “when” | Pair with Gantt chart |
| `r2_shopify_vs_custom` | Subjective 1–5 scores — feels made up | Use as backup; lead with **data proof** (36% co-purchase, 54d reorder) |
| `rec2_problem_retention_gap` | OK but generic | Keep OR use `r2_category_ladder.png` (profit + repeat dual axis) |
| `r2_cross_sell_timeline_clear` | Annotations overlap; SUB-01 timing confusing | `rec2_v2_gantt_clear_journey.png` |
| `rec2_conservative_prize` | Useful for prize slide — keep | Keep for business case |

---

## Recommended chart set for Rec 2 (tell the story in order)

| Order | Slide purpose | Chart | One line |
|-------|---------------|-------|----------|
| 1 | **Problem** | `r2_category_ladder.png` | Repeat and profit jump with each category |
| 2 | **Why L1 differs** | `rec2_v2_entry_category_repeat.png` | Collagen 37% vs shaker 21% repeat |
| 3 | **What is L2** | `rec2_v2_pdp_mockup.png` | Same-cart bundle on product page |
| 4 | **When L3 fires** | `rec2_v2_gantt_clear_journey.png` | Day 14 email, day 44 sample, day 54 reorder |
| 5 | **L3 timing differs by SKU** | `rec2_v2_pack_reorder_compare.png` | Observed reorder days drive sample timing |
| 6 | **Subscription proof** | `r2_subscription_by_profit_decile.png` | Higher deciles subscribe more |
| 7 | **Prize** | `rec2_conservative_prize.png` | Base case ~S$6.2K/yr |

**Optional appendix:** `Recommendation_B/outputs/fig_co_purchase_heatmap_d1.png` (L1 evidence heatmap)

Regenerate all:
```bash
python EDA/aditya_findings/build_presentation_charts.py
```

---

## Layer cheat sheet (for presenting)

| Layer | Plain English | When | Example |
|-------|---------------|------|---------|
| **L1** | “If they bought X first, suggest Y category next” | Right after first order | Clear buyer → suggest Lean |
| **L2** | “Add this to your cart now” | On product page / checkout | Peach + White Grape bundle |
| **L3** | “Email + sample before they reorder” | Days 14–44 after delivery | Lean email day 14; sachet day 44 |
| **L4** | “Personalised for logged-in repeaters” | After 3+ orders | Account page recommendations |
| **S&S** | “Lock in replenishment after they repeat” | Order 2 + 48 days | SUB-01 Klaviyo flow |

---

## Corrected numbers to use in slides

Replace **30.5%** with **37%** (Collagen-first repeat) everywhere you present.

| Metric | Correct value | Source |
|--------|---------------|--------|
| Collagen-first repeat | **37%** (36.8%) | `decile_customer_table.csv` |
| Accessories-first repeat | **21%** (20.5%) | same |
| Clear-first repeat | **20%** | same |
| Clear median reorder | **54 days** | `12_reorder_interval_by_sku.csv` |
| Lean median reorder | **35 days** | same |
| Peach → White Grape same cart | **36%** | `sku_association_rules.csv` |
| Subscribers vs non-sub repeat | **62% vs 19%** | `subscription_opportunity.csv` |
