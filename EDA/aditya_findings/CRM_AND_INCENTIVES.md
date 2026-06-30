# CRM Segmentation, Incentive Budgets & Cross-Sell Timing

**Script:** `build_crm_tiers_and_timing.py`  
**Exports:** `outputs_finals/crm_treatment_tiers.csv` (4,290 customers, Klaviyo-ready)

**Answers founder questions:**
1. How much can we give each customer? (profit margin × 5%/10% by tier and decile)
2. When and what to recommend/sample for cross-category selling?

---

## 1. Why treat customers differently

67.6% buy once. The top 20% (PM D1) generate **57.7%** of profit margin. A T5 customer averages **S$9 CM**; a T1 VIP averages **S$258 CM** with **4.1 orders** and **54% subscribed**.

Treating them the same — same discounts, same emails, same samples — **costs S$14K/yr** in VIP margin leakage and misses **S$11–17K/yr** in category-ladder uplift.

**Founder intent:** High-CM customers deserve to feel special — partner rewards, early access, experiences — not 10% off codes.

---

## 2. Automated T1–T5 thresholds

Assigned in `crm_treatment_tiers.csv` by `build_crm_tiers_and_timing.py`:

| Tier | Automated criteria | N | Avg profit margin | Why they deserve different treatment |
|------|-------------------|---|--------|--------------------------------------|
| **T1 VIP Champions** | `is_top_both` OR (PM D1 + subscribed) | **532** | **S$258** | Top CM **and** loyalty — protect and reward |
| **T2 High-Value Repeaters** | PM D1 only, Freq D1 only, or PM D2 + ≥2 orders | **744** | **S$117** | Proven value — convert to sub + 2nd category |
| **T3 Growth Customers** | Exactly 2 orders, PM D3–D4 | **63** | **S$41** | One nudge from becoming T2 |
| **T4 First Purchasers** | 1 order, PM D2–D4 | **2,120** | **S$51** | Trial mode — onboarding + 2nd purchase |
| **T5 Low Value** | PM D5 or 1 order + CM < S$15 | **831** | **S$9** | Low ROI — automation only |

---

## 3. Dollar incentive budgets (by profit margin decile)

**Formula:** `retention_budget = profit margin × 5%` (conservative) or `profit margin × 10%` (generous)

Per-customer columns in export: `retention_budget_5pct_sgd`, `retention_budget_10pct_sgd`, `max_sample_cost_sgd`

### By profit margin decile (pool average)

| CM Decile | Customers | Avg profit margin | **5% budget** | **10% budget** | Max sample cap |
|-----------|-----------|--------|---------------|----------------|----------------|
| **D1** | 858 | S$230 | **S$11.50** | **S$23.01** | S$23 |
| D2 | 858 | S$81 | S$4.06 | S$8.12 | S$5 |
| D3 | 858 | S$49 | S$2.43 | S$4.86 | S$3 |
| D4 | 858 | S$30 | S$1.48 | S$2.97 | S$2 |
| D5 | 858 | S$9 | S$0.44 | S$0.88 | S$0 |

### By treatment tier (what to actually spend)

| Tier | Avg 5% budget | Avg 10% budget | Incentive type (not always cash) |
|------|---------------|----------------|----------------------------------|
| **T1** | **S$12.91** | **S$25.82** | HYROX tickets, massage vouchers, early access, partner merch |
| **T2** | S$5.85 | S$11.69 | Subscribe & Save first month, shaker/merch bundle |
| **T3** | S$2.06 | S$4.12 | Cross-category sachet (COGS ~S$2–4) |
| **T4** | S$2.54 | S$5.08 | Single-serve sachet insert (cap at 5% profit margin) |
| **T5** | S$0.44 | S$0.88 | Email only — no product gift |

**Example (founder S$900 whale):** Top CM in pool = **S$2,797**. At 5% = **S$140**; at 10% = **S$280** for a one-off VIP experience. Median T1 VIP (S$184 CM) = **S$9–18** per touchpoint — enough for a sachet pack or partner perk, not a deep discount.

**Rule:** Spend ≤ `max_sample_cost_sgd` from CSV. Never exceed 10% profit margin on T1–T2 without founder approval.

---

## 4. Incentives by tier (what to give, not just how much)

| Tier | Incentives LP can offer | Do NOT |
|------|-------------------------|--------|
| **T1** | Partner rewards (HYROX, massage, events), early product access, exclusive shaker/merch, handwritten note | Site-wide % off, mass promo codes |
| **T2** | Subscribe & Save offer, Clear+Lean bundle, category sample pack, loyalty shaker | Blanket 10–15% discounts |
| **T3** | Cross-category sachet (Lean/Collagen for Clear buyers), small bundle discount on 2nd order | Premium discounting |
| **T4** | Onboarding email series, optional 1 sachet (≤S$2.54), education content | Treat as VIP |
| **T5** | Win-back email; recent acquirers only | Product gifts, manual outreach |

---

## 5. Cross-sell timing — the founder answer

### During order vs before reorder?

| Action | When | Why |
|--------|------|-----|
| **Same-category bundle** (Peach + W.Grape) | **At checkout** (Layer 2) | Same-cart MBA — 36% confidence |
| **Cross-category email** (Clear → Lean) | **Day 14 after delivery** | Product tasted; 2nd order not placed yet |
| **Cross-category physical sample** | **~10 days BEFORE median reorder** | Experience new category *before* reorder decision |
| **NOT default** | In first order box | Dilutes trial; no timing signal yet |

### Clear Protein buyer — exact schedule

| Day | Action | Product |
|-----|--------|---------|
| 0 | Order fulfilled | Clear Protein (e.g. Peach 500g) |
| 1–3 | Welcome email | Education only |
| **14** | **Email CS-01** | Recommend **Lean Protein** (TMT/Taro 1kg) for order 2 |
| **44** | **Ship physical sample** | **Collagen Glow 25g sachet** OR Lean 40g single-serve (≤S$2–4 COGS) |
| ~54 | Natural reorder window | Reminder if no order 2 |
| **48** after order 2 | SUB-01 | Subscribe & Save if they repeat |

**Evidence:** Median Clear reorder **54 days** · 25% all-pool / **53% D1** co-purchase Clear→Lean · Category ladder +S$85 CM at 3 categories.

### Full timing matrix

See `outputs/cross_sell_timing_and_samples.csv`:

| First category | Email day | Sample ship day | Cross-sell category | Sample product |
|----------------|-----------|-----------------|---------------------|----------------|
| Clear Protein | 14 | **44** | Lean Protein | Collagen/Lean sachet |
| Lean Protein | 14 | **25** | Clear Protein | Clear 25g sachet |
| Collagen Glow | 21 | **32** | Clear Protein | Clear/Lean sachet |
| Accessories | 7 | **25** | Lean Protein | Clear sachet (not shaker) |

### 1st vs 2nd vs 3rd purchase — who gets samples?

| Purchase # | Sample? | What | When |
|------------|---------|------|------|
| **1st** | Yes (T4/T3) | Cross-category **sachet** | Pre-reorder window (table above) — **not** in order 1 box by default |
| **2nd** | Yes (T3) | **3rd category** sachet (Collagen) | Day 7 after order 2 ships |
| **3rd+** | VIP only (T1) | Merch, shaker, partner gift | Budget = 10% profit margin (S$26 avg) |

---

## 6. Which product to recommend (cannot be done by Shopify alone)

Shopify "Recommended products" uses generic co-occurrence across all merchants. It does **not** know:

- Lush Protein's **category ladder** (1→2→3 categories)
- **profit margin tier** (VIP vs one-and-done)
- **Day 14 vs day 44** timing
- **Collagen sachet for Clear buyers** before reorder at day 44

Our rules come from `co_purchase_matrix_all.csv`, `first_to_second_sku_matrix.csv`, and `cross_sell_timing_and_samples.csv` — **your** 8,955 orders.

---

## Regenerate

```bash
python EDA/aditya_findings/build_crm_tiers_and_timing.py
```
