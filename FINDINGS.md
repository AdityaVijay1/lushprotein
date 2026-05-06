# LushProtein — EDA Findings Document

**Project:** ISSS603 Science of Customer Analytics · SMU Sem 5
**Data period:** 2020 – Q1 2026
**Dataset:** 27,350 Shopify orders · 13,780 unique customers · SGD + MYR revenue

---

## Quick Reference — Key Numbers

| Metric | Value |
|---|---|
| Unique customers | 13,780 |
| Total orders (2020–2026) | 27,350 |
| Overall repeat purchase rate | **32.4%** |
| 90-day retention rate | **22.1%** |
| Median days to 2nd order | **49 days** |
| Subscriber avg LTV | **S$1,063** |
| Non-subscriber avg LTV | S$371 |
| Subscriber LTV uplift | **+186%** |
| Raw subscription churn rate | **64.7%** |

---

## Finding 1 — Revenue and the Discount Problem

Revenue peaked at **S$1.86M in 2021 with zero discounting**. As the brand introduced promotions from 2022 onward, discount rates climbed to **54% of all 2025 orders** — and revenue did not recover.

| Year | Revenue (SGD) | Discount Rate |
|---|---|---|
| 2020 | S$849,726 | 0% |
| 2021 | **S$1,862,280** | **0%** |
| 2022 | S$1,581,361 | 3.7% |
| 2023 | S$368,113 | 17.1% |
| 2024 | S$594,696 | 42.4% |
| 2025 | S$432,896 | **54.3%** |

The 2023 revenue collapse (–77% vs 2021) coincides with the first aggressive discounting campaigns. The partial recovery in 2024–2025 has been achieved on the back of heavily discounted orders, meaning revenue is growing but at the cost of margin and cohort quality (see Finding 4).

**Chart:** `01a_revenue_discount_trend.png`

---

## Finding 2 — Channel Quality Gap: Marketplace vs Own Website

Not all acquisition channels produce the same customer. The data reveals a fundamental split between own-website customers and marketplace customers:

| Channel | Customers | Repeat Rate | Avg LTV (SGD) | % Subscribed |
|---|---|---|---|---|
| Subscription | 4,275 | 40.9% | S$364 | 18.8% |
| **Direct / Organic** | **6,920** | **33.5%** | **S$583** | 3.8% |
| Paid Social | 382 | 19.4% | S$71 | 6.0% |
| Affiliate | 26 | 19.2% | S$94 | 3.8% |
| **Marketplace** | **2,126** | **14.4%** | **S$118** | **0.0%** |
| Email | 48 | 12.5% | S$53 | 2.1% |

Marketplace customers (Shopee, Lazada, Tokopedia) represent **15% of total customers** but:
- Repeat at **14.4%** vs **33.5%** for Direct/Organic — a **2.3x gap**
- Generate **S$118 avg LTV** vs **S$551** for own-website — a **4.7x gap**
- Have **zero subscription conversion** — not a single marketplace customer ever subscribed

Marketplace channels inflate order counts and headline customer numbers without building a loyal customer base. The business is treating marketplace volume as growth when it is largely transactional traffic.

**Charts:** `02a_retention_by_channel.png`, `05b_marketplace_vs_website.png`

---

## Finding 3 — Cross-Sell is the Single Largest LTV Lever

Every additional product category a customer buys roughly doubles their lifetime loyalty:

| Products Purchased | Customers | Repeat Rate | Avg LTV (SGD) | vs 1-Product LTV |
|---|---|---|---|---|
| 1 product | 9,537 | 23.6% | S$329 | baseline |
| 2 products | 2,679 | 39.7% | S$399 | +21% |
| 3 products | 1,052 | **65.5%** | **S$890** | **+171%** |
| 4+ products | 512 | **88.7%** | **S$1,421** | **+332%** |

Moving a customer from 1 to 3 product categories:
- Raises repeat rate from **23.6% → 65.5%** (+178%)
- Raises avg LTV from **S$329 → S$890** (+171%)

**Top cross-purchase combinations among repeat buyers:**

| Combination | Customers |
|---|---|
| Accessories + Clear Protein + Lean Protein | 69 |
| Clear Protein + Lean Protein | 59 |
| Accessories + Clear Protein | 56 |
| Accessories + Other | 54 |
| Lean Protein + Other | 80 |

This is not a demand-side insight requiring heavy persuasion — it is a supply-side gap. Customers who are exposed to multiple products become loyal. The implication is a targeted cross-sell email sequence in the 7–21 days after first purchase.

**Charts:** `03a_cross_product_ltv.png`, `03d_top_product_combos.png`

---

## Finding 4 — Discount Depth Destroys Long-Term Loyalty

The relationship between first-order discount depth and long-term customer quality is consistent and damaging:

| First-Order Discount Depth | Customers | Repeat Rate | Avg LTV (SGD) |
|---|---|---|---|
| **Full price (0%)** | 9,398 | **36.4%** | **S$542** |
| 1–5% off | 186 | 17.7% | S$157 |
| 6–10% off | 395 | 26.1% | S$260 |
| 11–20% off | 1,250 | 25.5% | S$162 |
| 21–30% off | 458 | 25.5% | S$237 |
| 31–50% off | 1,189 | 23.0% | S$196 |
| **51%+ off** | 430 | **21.9%** | **S$181** |

Full-price buyers repeat at **36.4%** with **S$542 LTV**.
51%+ discount buyers repeat at **21.9%** with **S$181 LTV** — a **66% LTV drop**.

The sharpest drop is at the 1–5% tier: going from free → any discount immediately drops repeat rate from 36.4% to 17.7%. This suggests discounting itself signals price-sensitivity regardless of depth, and any discount-acquired cohort is structurally weaker than a full-price cohort.

With discount rates at 54% in 2025, the business is predominantly acquiring weaker cohorts. The compounding effect over multiple acquisition years explains why the LTV baseline has deteriorated despite revenue recovering partially.

**Chart:** `05a_discount_depth_impact.png`

---

## Finding 5 — Subscription is High Value but Churns Early

Subscribers are the most valuable customer segment by a significant margin:

| Metric | Subscriber | Non-Subscriber | Uplift |
|---|---|---|---|
| Repeat rate | 74.4% | 28.7% | +159% |
| Avg LTV | S$1,063 | S$371 | **+186%** |
| Avg orders | 4.9 | 1.7 | +188% |
| Avg customer lifespan | 399 days | 93 days | +329% |

But **64.7% of subscribers eventually cancel**. Churn is concentrated in the first 90 days:

| Subscription Cycle | Cancellations | % of Total Churn |
|---|---|---|
| Cycle 0 (< 30 days) | 60 | 11.4% |
| **Cycle 1 (30–60 days)** | **110** | **20.9%** ← peak |
| Cycle 2 (60–90 days) | 101 | 19.2% |
| Cycle 3 (90–120 days) | 81 | 15.4% |
| **Cycles 1–3 combined** | **292** | **55.5%** |

**The most revealing signal is the top cancellation reason:**

| Reason | Count | % |
|---|---|---|
| **"I already have more than I need"** | **143** | **31.9%** |
| Other reason | 131 | 29.2% |
| I no longer use this product | 88 | 19.6% |
| Created by accident | 40 | 8.9% |
| Too expensive | 19 | 4.2% |

"Already have more than I need" is not a satisfaction failure. It is a **cadence mismatch**. The standard 30-day delivery interval delivers product faster than many customers consume it. Tubs accumulate, the customer feels wasteful, and they cancel — not because the product failed them but because the subscription timing did.

**The fix is operational:** add a 45-day and 60-day interval option, and make the skip-delivery button prominent before each renewal.

**Win-back rate:** 43 of 347 churned subscribers reactivated (12.4%). Median time to reactivation: 112 days.

**Charts:** `04a_subscriber_vs_onetime.png`, `04b_churn_by_cycle.png`, `04c_cancellation_reasons.png`

---

## Finding 6 — Time-to-Second-Purchase Window

Of 13,780 customers who ever bought, **4,459 (32.4%) placed a second order.**

| Time Window | Repeaters | Cumulative % of All Repeaters |
|---|---|---|
| 0–7 days | 336 | 7.5% |
| 8–14 days | 222 | 12.5% |
| 15–30 days | 568 | 25.3% |
| 31–60 days | 692 | 40.8% |
| **61–90 days** | **461** | **51.1%** ← largest single window |
| 91–180 days | 603 | 64.6% |
| 181–365 days | 450 | 74.7% |
| 365+ days | 463 | 85.1% |

- **P50 (median): 49 days** — half of all repeat buyers return within 49 days
- **P75: 141 days** — three-quarters return within 5 months
- **66% return within 90 days** — after 90 days without a second order, probability of return drops sharply

The 61–90 day bucket is the largest single window. This is the period when the brand either retains a customer or loses them permanently. Any marketing touchpoint — win-back email, loyalty incentive, cross-sell offer — has maximum effectiveness in this window.

**Chart:** `02c_time_to_second_purchase.png`

---

## Finding 7 — Hero Product Retention Comparison

| First Product Bought | Customers | Repeat Rate | Avg LTV (SGD) | Median Days to 2nd |
|---|---|---|---|---|
| Collagen Glow | 439 | **31.2%** | S$231 | 48 days |
| Lean Protein | 1,324 | 23.2% | S$118 | **36 days** |
| Clear Protein | 1,550 | 22.5% | S$149 | 44 days |
| Soy Protein | 361 | 20.8% | S$138 | 64 days |
| Accessories | 696 | 22.1% | S$97 | 20 days |

Collagen Glow leads on repeat rate (31.2%) and has the highest subscription loyalty ratio in the Recharge data (50% of checkout subscribers stay for recurring). Lean Protein drives the fastest repurchase cycle (36 days median).

**Subscription SKU loyalty ratios (recurring customers / checkout customers):**

| SKU | Loyalty Ratio |
|---|---|
| Soy Protein Isolate | 54% |
| Collagen Glow 300g | **50%** |
| Creatine Monohydrate | 42% |
| Lean Protein Taro 1kg | 38% |
| Clear Protein Peach 500g | 32% |

**Chart:** `02b_retention_by_product.png`, `03c_sku_loyalty.png`

---

## Finding 8 — RFM Customer Segments

| Segment | Customers | % of Base | Avg LTV | Avg Orders | Priority Action |
|---|---|---|---|---|---|
| Loyal | 4,789 | 34.8% | S$292 | 1.9 | Cross-sell to 2nd product |
| Hibernating | 3,321 | 24.1% | S$200 | 1.0 | Low-cost reactivation |
| **At Risk** | **2,351** | **17.1%** | **S$1,072** | 3.4 | **Win-back urgently** |
| Champions | 1,398 | 10.1% | S$703 | 3.8 | Reward + upsell |
| **Can't Lose** | **1,218** | **8.8%** | **S$218** | 1.0 | **Re-engage now** |
| Promising | 688 | 5.0% | S$61 | 1.0 | Nurture to 2nd order |
| New | 15 | 0.1% | S$67 | 1.0 | Welcome sequence |

The **At Risk segment (2,351 customers, S$1,072 avg LTV)** represents the most urgent reactivation opportunity. These customers have demonstrated a willingness to spend significantly but have gone quiet. Combined with Can't Lose (1,218 customers), **over 3,500 proven-spenders are currently disengaging** from the brand.

**Chart:** `05c_rfm_segments.png`

---

## Prioritised Findings — If/Then Table

| Rank | Finding | Key Evidence | Confidence | Suggested Experiment |
|---|---|---|---|---|
| 1 | Marketplace cannibalises LTV | 14.4% repeat vs 33.5% direct · 0% sub conversion · 4.7x LTV gap | High | Reduce marketplace SKU breadth; redirect budget to owned channels |
| 2 | Cross-sell drives biggest LTV jump | 3-product buyers: 65% repeat, +171% LTV | High | Post-purchase cross-sell email at Day 14 |
| 3 | Deep discounting destroys cohort quality | 51%+ off: 21.9% repeat, S$181 LTV vs S$542 full-price | High | Cap new-customer discount at 10–15%; remove 50%+ deals |
| 4 | Subscription cadence causes stockpile churn | 32% cancel "already have too much"; peak churn at Cycle 1 | High | Add 45/60-day interval option + skip-delivery CTA |
| 5 | At Risk segment = urgent win-back opportunity | 2,351 customers, S$1,072 avg LTV, currently dormant | Medium | Targeted win-back campaign with strongest available offer |
| 6 | Expectation mismatch drives early exit *(minor hypothesis)* | 66% of repeaters return within 90 days; churn peaks pre-90d | Medium | Post-purchase onboarding sequence setting timeline expectations |

---

## Mid-Term Presentation — Highest-Impact Charts

For the 4 slides that carry the most visual weight, use:

| Slide topic | Chart file | Why it works |
|---|---|---|
| Cross-sell LTV | `03a_cross_product_ltv.png` | The staircase visually shows the exponential value of breadth — one glance tells the story |
| Subscription churn | `04b_churn_by_cycle.png` | The shaded 30–90 day danger zone and peak at Cycle 1 make the timing pattern immediately clear |
| Discount impact | `05a_discount_depth_impact.png` | The V-drop from full-price to any discount, then the flat line, makes the argument visually |
| Channel quality | `02a_retention_by_channel.png` | Side-by-side repeat rate and LTV bars make the marketplace gap undeniable |

---

*Document generated from EDA scripts in `/EDA/` · Charts in `/visualizations/charts/`*
*ISSS603 Science of Customer Analytics · Singapore Management University · May 2026*
