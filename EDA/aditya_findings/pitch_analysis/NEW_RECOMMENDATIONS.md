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

### Experiment
- **Day 14 after order 1:** email complementary category (Rec B flows)
- **Day 7 after order 2:** email 3rd category (Collagen or 2nd flavour)
- **Checkout:** Clear+Lean bundle for single-category buyers
- **Success metric:** +5pp category attach within 60 days

### Execution
Rec B Phase 1 flows + bundle. **4–6 weeks.**

**Chart:** `pitch_analysis/outputs/fig_category_ladder.png`

---

## Recommendation D — Subscribe the repeaters (Product: replenishment SKUs)

**One sentence:** 689 customers have ordered 2+ times but never subscribed. Subscribers repeat at **62%** vs **19%** for non-subs.

### Hypothesis
Repeat non-subscribers proved product fit but LP captures no replenishment value. Hero SKUs (Clear Peach, Lean TMT) have 48–54 day reorder windows.

### Pattern
| Segment | N | Avg GP | Repeat rate |
|---------|---|--------|-------------|
| Subscriber | 713 | S$134 | 62% |
| Non-subscriber | 3,577 | S$69 | 19% |
| **GP gap** | | **S$66/customer** | **3.3× repeat** |

### Driver
Without Subscribe & Save, LP re-acquires the same customer every cycle via email/ads — or loses them.

### Opportunity
- 5% of 689 repeat non-subs convert: **S$2,262 GP/yr**
- 10% of 228 Freq D1 non-subs convert: **S$1,497 GP/yr**
- **Strategic value:** 62% repeat rate compounds over years

### Experiment
Klaviyo flow: 2nd order fulfilled + 48 days → offer Subscribe & Save on **exact SKU/flavour** (Peach Clear 500g or TMT Lean 1kg). A/B: 10% sub discount vs free shipping.

### Product depth
Target SKUs with highest loyal-buyer revenue: Clear Peach 500g (171 loyal buyers), Lean TMT 1kg (125 loyal buyers).

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
| **2** | **D** Subscription | **S$2–4K** + repeat compounding | Medium |
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
