# New Recommendations C, D, E — Founder Pitch (Product × Customer)

**Source:** `pitch_analysis/HYPOTHESES.md` + true COGS on enriched `outputs_finals/`

These are the **lead recommendations** for the deck. Rec A is the guardrail; Rec B is the execution engine for Rec C.

---

## Recommendation C — Climb the category ladder (LEAD)

**One sentence:** 59% of your customers (2,514) have only ever bought **one product category**. Moving even 5% of them to **3 categories** is worth **S$10,693 GP/yr**.

### Hypothesis
Customers who add categories become disproportionately valuable — GP rises from S$59 → S$144 and repeat rate from 17% → 55%.

### Pattern
| Categories | Customers | Avg GP | Repeat |
|------------|-----------|--------|--------|
| 1 | 2,514 (59%) | S$59 | 17% |
| 2 | 1,216 (28%) | S$79 | 30% |
| 3 | 410 (10%) | S$144 | 55% |
| 4+ | 150 (3%) | S$249 | 82% |

### Driver
Clear and Lean are complementary (65% D1 Lean buyers also buy Clear). Single-category buyers are in "trial mode" — one flavour, not the brand.

### Opportunity
- 5% of 2,514 reach 3 categories: **S$10,693 GP/yr**
- 8% add 2nd category: **S$3,969 GP/yr**
- 8% of middle decile (D5–D7): **S$2,067 GP/yr**

### Execution — 4-layer stack (see `FOUNDER_MEETING_PREP.md` Section 2A)

**Layer 1 — Klaviyo flows (week 1–2):**

| Flow | Trigger | Delay | Recommend |
|------|---------|-------|-----------|
| CS-01 | Order 1 has Clear | Day 14 | Lean TMT/Taro 1kg |
| CS-02 | Order 1 has Lean | Day 14 | Clear Peach/White Grape 500g |
| CS-03 | Order 1 Collagen only | Day 21 | Clear Peach starter |
| CS-04 | Order 2 fulfilled | Day 7 | Collagen or 2nd flavour |
| CS-05 | Order 2+, D5–D7, 1-cat stuck | Day 7 | Same as CS-04 |

**Layer 2 — Checkout & PDP (week 2–3):** Clear+Lean bundle (S$73.60 true GP), association-rule widgets on top 5 PDPs.

**Layer 3 — Product logic:** `first_to_second_sku_matrix.csv` + `sku_association_rules.csv` — SKU-specific, not generic.

**Layer 4 — Measure at 60 days:** +5pp category attach; 5–8% email click-to-purchase.

**Full playbook:** `FOUNDER_MEETING_PREP.md` · **Mockups:** `INTEGRATION_DEMO.md` · **Flows CSV:** `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv`

**Chart:** `pitch_analysis/outputs/fig_category_ladder.png`

---

## Recommendation D — Build a subscription growth engine (LEAD)

**One sentence:** Subscribers repeat at **62%** vs **19%** for non-subs — expand subscription across **four tiers**, not just 689 repeat non-subscribers, to lock replenishment and build D1 customers.

### Hypothesis
Repeat non-subscribers proved product fit but LP captures no replenishment value. Hero SKUs (Clear Peach, Lean TMT) have 35–54 day reorder windows. **38% of D1 ever subscribed** — subscription is a D1 signal, not just a convenience feature.

### Pattern
| Segment | N | Avg GP | Repeat rate |
|---------|---|--------|-------------|
| Subscriber | 713 | S$134 | 62% |
| Non-subscriber | 3,577 | S$69 | 19% |
| **GP gap** | | **S$66/customer** | **3.3× repeat** |

### Four subscription tiers

| Tier | Pool | Trigger | Prize |
|------|------|---------|-------|
| D1 Repeat non-subs | 689 | Order 2 + 48 days | 5% = **S$2,262/yr** |
| D2 Freq D1 non-subs | 228 | Order 3 + 35 days | 10% = **S$1,497/yr** |
| D3 First-time hero buyers | ~400/yr | Order 1 + 42 days | Compounding |
| D4 Checkout subscribe | New hero SKU orders | At checkout | Lowest-CAC subs |

### Klaviyo flows (SUB-01–04)

| Flow | Trigger | Delay | Segment |
|------|---------|-------|---------|
| SUB-01 | Order 2 fulfilled, hero SKU | 48 days | Repeat non-subscriber |
| SUB-02 | Order 3 fulfilled | 35 days | Freq D1 non-subscriber |
| SUB-03 | Order 1 fulfilled, Peach/TMT | 42 days | 1 order, no sub |
| SUB-04 | Subscription started | Day 1 | New subscriber → Collagen cross-sell |

### Product depth
Hero replenishment SKUs: Clear Peach 500g (54-day cycle, 171 loyal buyers), Lean TMT 1kg (35-day cycle, 125 loyal buyers). Pre-check S&S at checkout on PDP — not on shakers or accessories.

### How D + C build D1
Cross-sell widens basket (2+ categories, index 189). Subscription locks habit (index 258). Together they move customers through the D1 creation journey (Section 3 in `FOUNDER_MEETING_PREP.md`).

**Full playbook:** `FOUNDER_MEETING_PREP.md` Sections 2B + 3 · **D1 profile:** `decile_analysis/D1_CUSTOMER_PROFILE.md`

**Chart:** `pitch_analysis/outputs/fig_prize_by_hypothesis.png`

---

## Recommendation E — Fix acquisition product mix (Product depth)

**One sentence:** Accessories-first buyers repeat at **20%** vs Collagen-first at **37%**. Stop leading acquisition with shakers.

### Hypothesis
First purchase category sets the ceiling. Accessories-first = shaker-only, no protein habit.

### Pattern
| First product | N | Repeat rate | Avg revenue |
|---------------|---|-------------|-------------|
| Collagen Glow | 209 | **37%** | S$136 |
| Accessories | 371 | **20%** | S$71 |
| Clear Protein | — | 20% | — |

### Opportunity
15% of 371 accessories-first buyers convert to protein in 30 days: **S$4,389 GP**

### Experiment
Mandatory 30-day protein upsell: sachet trial pack (Peach Clear 25g + TMT Lean 40g) at S$9.90.

---

## Deck recommendation order (updated)

| Priority | Rec | Prize (GP/yr) | Ease |
|----------|-----|---------------|------|
| **1** | **C** Category ladder | **S$11–17K** | Medium |
| **2** | **D** Subscription engine (4 tiers) | **S$4–5K** + repeat compounding | Medium |
| **3** | **B** Cross-sell flows (executes C) | Included in C | Medium |
| **4** | **E** Acquisition mix | **S$4K** | High |
| **5** | **A** VIP guardrail | **S$14K** protected | High |

**Combined conservative GP: S$30–35K/yr**

---

## Data files

| File | Contents |
|------|----------|
| `pitch_analysis/HYPOTHESES.md` | Full hypothesis framework (H1–H5) |
| `pitch_analysis/outputs/prize_scenarios_explained.csv` | All scenarios with pool explained |
| `pitch_analysis/outputs/category_ladder_gp.csv` | Category × GP × repeat |
| `outputs_finals/customers.parquet` | Now has `true_gross_profit`, `n_categories_ever`, `crm_tier` |
| `outputs_finals/lines.parquet` | Now has `unit_cost`, `gross_profit`, `pack_size` |
