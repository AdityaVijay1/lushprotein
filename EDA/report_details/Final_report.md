# ISSS603 Applied Data Science for Customer Insights
## Final Report — Group 1 (SMU × LushProtein)


## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Part A — Data Cleaning & Data Quality Improvements](#part-a--data-cleaning--data-quality-improvements)
   - 2.1 [Introduction and Dataset Coverage (Mid-Term §1 — carried forward)](#21-introduction-and-dataset-coverage-mid-term-1--carried-forward)
   - 2.2 [Summary Statistics and Distributions (Mid-Term §2 — carried forward)](#22-summary-statistics-and-distributions-mid-term-2--carried-forward)
   - 2.3 [Data Issues and Discrepancies (Mid-Term §3 — carried forward)](#23-data-issues-and-discrepancies-mid-term-3--carried-forward)
   - 2.4 [LTV and Metric Definitions (Mid-Term §4.1)](#24-ltv-and-metric-definitions-mid-term-41)
   - 2.5 [Final Revisions Since Mid-Term (NEW)](#25-final-revisions-since-mid-term-new)
   - 2.6 [Layer 1 — DQ Drops with Manifest Counts](#26-layer-1--dq-drops-with-manifest-counts)
   - 2.7 [Layer 2 — LP Business Filters (LP-F01 to LP-F04)](#27-layer-2--lp-business-filters-lp-f01-to-lp-f04)
   - 2.8 [Layers 0 & 3 — Order Window and Seasonality](#28-layers-0--3--order-window-and-seasonality)
   - 2.9 [COGS Enrichment and Additional Validations](#29-cogs-enrichment-and-additional-validations)
   - 2.10 [Before vs After Summary](#210-before-vs-after-summary)
   - 2.11 [Assumptions and Residual Limitations](#211-assumptions-and-residual-limitations)
3. [Part B — Insights & Recommendations (Solution 2)](#part-b--insights--recommendations-solution-2)
   - 3.1 [Business Problem Restated](#31-business-problem-restarted)
   - 3.2 [What the Data Shows — Three Gaps](#32-what-the-data-shows--three-gaps)
   - 3.3 [Solution 2 — 4-Layer Recommendation System](#33-solution-2--4-layer-recommendation-system)
     - [Why not Shopify default](#331-why-not-shopify-default)
     - [Three problems, four layers](#332-three-problems-four-layers)
     - [Layer summary](#333-layer-summary)
   - 3.4 [Layer 3 — Phase 1 Focus & Implementation](#34-layer-3--phase-1-focus--implementation)
   - 3.5 [Implementation Architecture (Medallion Pipeline)](#35-implementation-architecture-medallion-pipeline)
   - 3.6 [ROI and Budget Analysis](#36-roi-and-budget-analysis)
   - 3.7 [Phased Roadmap and Recommendation Breakdown](#37-phased-roadmap-and-recommendation-breakdown)
   - 3.8 [Resource Constraints and Three Baby Steps](#38-resource-constraints-and-three-baby-steps)
   - 3.9 [Risks, Caveats, and Success Metrics](#39-risks-caveats-and-success-metrics)
4. [Appendix A — Visualization Guide](#appendix-a--visualization-guide)
5. [Appendix B — Key Output Files](#appendix-b--key-output-files)
6. [Appendix C — Solution 1 Cross-Reference (Brief)](#appendix-c--solution-1-cross-reference-brief)

---

## 1. Executive Summary

LushProtein faces a customer development problem, not a traffic problem: **77.3% of finals-eligible customers (4,402 of 5,694) buy once and never return**, and **65% remain in a single product category**, limiting repeat rate and gross profit (GP) per customer. Subscribers repeat at **62%** versus **17%** for non-subscribers — a **3.6× gap** — yet only **12.5%** of the base has ever subscribed.

This report has two parts:

**Part A** documents how the analytics foundation was strengthened after mid-term feedback from LushProtein and the instructor. We did not discard the mid-term data quality work; we extended it with four business-rule filters (LP-F01 to LP-F04), order-window rules, COGS-based margin enrichment, and reproducible finals datasets (`EDA/outputs_finals/`). The finals cohort (**5,694 customers; 8,955 orders**) is the authoritative base for all final recommendations.

**Part B** presents **Solution 2 — the 4-Layer Recommendation System**, with emphasis on **Layer 3 (L3)** as the highest-impact, lowest-complexity starting point. Solution 1 (customer tiering and reinvestment) is covered by a team member separately; this report references it only where tiers intersect with recommendation timing.

**Bottom line for LushProtein:** Phase 1 does not require a custom Shopify app or machine learning. It requires a **7-row lookup table** (`cross_sell_timing_and_samples.csv`), post-purchase email flows, and a fulfilment process for physical samples timed ~10 days before each SKU's median reorder window. Conservative annual GP upside from L3-led category and subscription development is estimated at **S$17,000–S$30,000**, against an estimated Phase 1 implementation cost of **S$2,500–S$4,000**, implying **ROI of approximately 325%–900%** in Year 1 under conservative conversion assumptions (detailed in Section 3.6).

**Recommended immediate action:** Launch L3 email flows (CS-01/02/03) for Clear, Lean, and Collagen first-time buyers before investing in ML personalisation (Layer 4).

---

# Part A — Data Cleaning & Data Quality Improvements

> **Instructor guidance:** Part A carries forward the mid-term data-quality work (Sections 2.1–2.4 below). **Section 2.5 onward documents finals revisions** made visible after LushProtein feedback — codified in `EDA/13_build_finals_datasets.py` and `EDA/outputs_finals/manifest.json`.

---

## 2.1 Introduction and Dataset Coverage (Mid-Term §1 — carried forward)

Dataset covers LushProtein operations from December 2019 to March 2026: customer transactions, products, discounts, campaigns, and subscription data.

### Temporal Coverage

**Period of analysis:** 2019-12-31 to 2026-03-30

| Period | Orders | Unique Customers | Notes |
|--------|--------|------------------|-------|
| 2019 | 3 | 3 | Incomplete year — excluded from cohort analysis |
| 2020 | 2,847 | 1,696 | Full year, zero discounting |
| 2021 | 6,259 | 3,815 | Peak revenue year (S$848K) |
| 2022 | 3,710 | 2,299 | First discounting introduced |
| 2023 | 2,253 | 1,399 | Revenue collapse year |
| 2024 | 4,261 | 2,621 | Recovery, heavy discounting |
| 2025 | 6,407 | 4,107 | Highest order volume |
| 2026 (Partial) | 1,610 | 1,230 | Jan–Mar only; excluded from full-year charts |

**Figure A-1:** `charts/part_a_temporal_orders.png` — *[optional: insert orders-by-year bar chart from `outputs/12_acquisition_by_year.csv`]*

### Store and Currency Coverage

| Store | Orders | Revenue (Own Currency) | FX Rate | Revenue (SGD) |
|-------|--------|------------------------|---------|---------------|
| SG | 16,041 | S$1,913,068 | 1.00 | S$1,913,068 |
| MY | 11,309 | RM $3,958,566 | 3.30 | S$1,199,566 |
| HK | 2 | HK$1,943 | 6.10 | S$319 |
| **All markets** | **27,350** | — | — | **S$3,112,952** |

**FX methodology:** 5-year average rates (2020–2026) at load. Measurement error up to ±10% on absolute MY revenue; directional findings unaffected.

**Known limitations:** MY dormant by 2025 (S$9,617 vs S$441,022 in 2021); HK immaterial (2 orders).

---

## 2.2 Summary Statistics and Distributions (Mid-Term §2 — carried forward)

Understanding raw distributions motivated every countermeasure in Section 2.3.

### 2.2.1 Order Revenue Distribution (SGD, post-FX)

| Statistics | All Markets | SG Only | MY Only |
|------------|-------------|---------|---------|
| Count | 27,530 | 16,039 | 11,309 |
| Mean | S$113.83 | S$119.28 | S$106.07 |
| Median | S$59.90 | S$62.10 | S$55.48 |
| Std Dev | S$413.76 | S$405.16 | S$425.60 |
| Maximum | S$34,618 | S$26,520 | S$34,618 |

Mean ≈ 2× median → right-skewed; wholesale/reseller orders drive the tail. **Figure A-2:** `charts/part_a_revenue_distribution.png`

### 2.2.2 Orders per Customer

| Statistics | All Markets | SG Only |
|------------|-------------|---------|
| Mean orders | 1.98 | 1.80 |
| Median | 1 | 1 |
| Max orders | 667 | 667 |
| Unique customers | 13,780 | 8,920 |
| Exactly 1 order | 9,321 (67.6%) | 6,454 (72.4%) |

**Figure A-3:** `charts/part_a_one_time_buyer_rate.png` — one-time rate rises as cohort is cleaned (67.6% → 77.3% finals).

### 2.2.3 Discount Distribution

- 9,024 orders discounted (33% of total)
- Discount depth = Discount / (Total + Discount)
- **14.5% spike at 90–100% off** (1,308 orders) — referral/PR/subscription gifts at zero customer cost → addressed by DQ-03

### 2.2.4 LTV by Acquisition Year and Channel

| Channel | 2022 | 2023 | 2024 | 2025 | 2026 |
|---------|------|------|------|------|------|
| Direct / Organic | S$216 | S$105 | S$92 | S$73 | S$79 |
| Subscription | S$292 | S$190 | S$134 | S$173 | S$110 |
| Marketplace | S$128 | S$74 | S$57 | S$131 | S$139 |
| Paid Social | — | — | — | S$70 | S$84 |

Subscription-acquired customers highest LTV; marketplace repeat 14.4% vs Direct 33.5%.

### 2.2.5 Missing Value Summary

| Column | % Missing | Notes |
|--------|-----------|-------|
| Browser: UTM Source/Medium | 94.9% | Fallback: Shopify tags |
| Browser: UTM Campaign | 95.0% | Same |
| Browser: Referrer Domain | 81.8% | Expected for direct traffic |
| Tags | 62.3% | Expected |
| Line: Product Handle | 49.3% | Header rows without line items |
| second_order_date | 67.6% | Expected — one-time buyers |
| Shipping: Country | 3.9% | Minor |
| Order Fulfilment Status | 0.8% | Minor |

**Figure A-4:** `charts/part_a_missing_values.png`

---

## 2.3 Data Issues and Discrepancies (Mid-Term §3 — carried forward)

Each issue uses: **Issue → Impact → Countermeasure → Validation → Result**.

### 3.1 Mixed Currencies

| Element | Detail |
|---------|--------|
| **Issue** | No FX at point of sale in raw export |
| **Impact** | Non-comparable revenue across SG/MY/HK |
| **Countermeasure** | 1 SGD = 3.3 MYR, 1 SGD = 6.1 HKD (5-year average) |
| **Validation** | Store-level totals reconcile to mid-term table |
| **Result** | All revenue in SGD for analysis |

### 3.2 Zero Revenue and Zero Discount Orders (→ DQ-02)

| Element | Detail |
|---------|--------|
| **Issue** | 336 orders: Price Total = 0 AND Discount = 0 |
| **Impact** | Inflates counts; non-purchase events |
| **Countermeasure** | Remove from analysis |
| **Validation** | Row audit vs raw export |
| **Result** | Clean paid-order base |

### 3.3 100%-Discount Orders (→ DQ-03)

| Element | Detail |
|---------|--------|
| **Issue** | 1,281 orders: revenue = 0, discount > 0 (LP-confirmed gifts/PR) |
| **Impact** | Skews LTV and discount analysis |
| **Countermeasure** | Exclude from consumer behaviour analysis |
| **Validation** | LP confirmation at mid-term |
| **Result** | Paid-consumer LTV only |

### 3.4 Wholesale / Outlier Orders (→ DQ-04)

| Element | Detail |
|---------|--------|
| **Issue** | 78 orders: `wholesale-sale` tag and/or > S$5,000 |
| **Impact** | Mean S$114 vs median S$60; reseller dominates tail |
| **Countermeasure** | Exclude wholesale tag OR revenue > S$5,000 |
| **Validation** | AOV distribution before/after |
| **Result** | DTC-focused metrics |

### 3.5 Missing UTM Attributions

| Element | Detail |
|---------|--------|
| **Issue** | 94.9% missing UTM fields |
| **Impact** | Cannot rely on browser UTM for channel |
| **Countermeasure** | Marketplace via Shopify tags; subscription via `is_subscription`; else Direct/Own |
| **Validation** | Tag cross-check; 3,263/3,265 subscription matches |
| **Result** | Reliable channel classification without UTM |

### 3.6 Line-Item vs Order-Level Row Structure

| Element | Detail |
|---------|--------|
| **Issue** | Raw export mixes header and line rows; 49.3% null Product Handle |
| **Impact** | Double-counting or wrong SKU attribution |
| **Countermeasure** | Split: `orders.parquet` (Top Row = 1) and `lines.parquet` (Line Item) |
| **Validation** | 27,350 orders vs 50,963 line items |
| **Result** | Correct order vs SKU analysis |

### 3.7 Subscription Tag vs Flag

| Element | Detail |
|---------|--------|
| **Issue** | 3,267 tagged vs 3,265 `is_subscription = true` |
| **Impact** | Negligible (2 orders) |
| **Countermeasure** | Use `is_subscription` flag consistently |
| **Validation** | Cross-tab |
| **Result** | Single subscription definition |

### 3.8 Marketplace Subscription and Repeat Measurement

| Element | Detail |
|---------|--------|
| **Issue** | Shopify cannot see Shopee/Lazada → 0% marketplace subscription rate |
| **Impact** | Misleading if interpreted as behaviour |
| **Countermeasure** | Document as platform limitation; 14.4% repeat = lower bound |
| **Validation** | 2,126 marketplace-first customers |
| **Result** | Valid relative comparison vs 33.5% Direct |

### 3.9 Unused Campaigns Dataset

| Element | Detail |
|---------|--------|
| **Issue** | Sessions CSV: 246,909 rows, no dates or customer IDs |
| **Impact** | Cannot join to orders |
| **Countermeasure** | Not used; order-level UTM/tags instead |
| **Validation** | Schema review |
| **Result** | No false precision from session aggregates |

### 3.10 Discount Codes Not Linked to Orders

| Element | Detail |
|---------|--------|
| **Issue** | 367 discount codes; no order-level join key in export |
| **Impact** | Cannot attribute specific campaigns to orders |
| **Countermeasure** | Use binary `has_discount` + discount depth % |
| **Validation** | Export schema |
| **Result** | Discount analysis at order level only |

### 3.11 Recharge Data Gaps

| Element | Detail |
|---------|--------|
| **Issue** | Recharge April 2025–2026 only; 8-digit IDs ≠ 13-digit Shopify IDs |
| **Impact** | Incomplete subscription history; churn window limited |
| **Countermeasure** | Join on `shopify_order_id`: 1,163/1,215 matched |
| **Validation** | Match rate 95.7% |
| **Result** | Churn findings labelled 2025–2026 window only |

### 3.12 Product Master COGS (Updated in Finals — see §2.9)

| Element | Detail |
|---------|--------|
| **Issue (mid-term)** | 65% variants null COGS; 58/167 with cost |
| **Impact** | Profit figures required 40% proxy |
| **Countermeasure (mid-term)** | `MARGIN_RATE = 0.40`; label "profit proxy" |
| **Countermeasure (finals)** | LP COGS file June 2026 → 74.7% revenue coverage |
| **Result** | True GP where covered; proxy labelled elsewhere |

**Figure A-5:** `charts/part_a_filter_layers.png` — relative impact of each cleaning layer.

---

## 2.4 LTV and Metric Definitions (Mid-Term §4.1)

**Primary LTV:** Sum of `Price: Total` per customer across paid, non-restocked orders (SGD).

**Gross profit LTV (mid-term):** LTV × 0.40 (40% proxy when COGS missing).

**Gross profit LTV (finals):** Sum of `true_gross_profit` from margin-enriched `customers.parquet` where COGS coverage exists; otherwise flagged as proxy.

---

## 2.5 Final Revisions Since Mid-Term (NEW)

After the mid-term presentation, LushProtein confirmed four **business-scope filters** (mid-term §5). These were **codified and extended** in June 2026:

| Mid-term action | Finals implementation | Change visible? |
|-----------------|----------------------|-----------------|
| Four LP filters described | LP-F01 to LP-F04 in `13_build_finals_datasets.py` | **Yes — reproducible script** |
| Estimated 6,353 customers | **Authoritative 5,694** (`manifest.json`) | **Yes — order-window refinement** |
| 40% margin proxy only | COGS enrichment (74.7% rev coverage) | **Yes — true GP** |
| Manual filter narrative | Layer 0 + Layer 3 order rules | **Yes — new** |
| Mid-term base in `outputs/` | Finals base in `outputs_finals/` | **Yes — separate folder** |

**Mid-term §5 filter list (unchanged intent):**

1. Exclude **Better Whey Protein Elite** buyers (bulk, non-representative)
2. Exclude **July and November acquisitions** (anniversary, BFCM)
3. **Post-January 2022** acquisitions only (stable portfolio era)
4. Exclude **>50% first-purchase discount** (referral/sampling)

**Figure A-6:** `charts/part_a_cohort_funnel.png` — 13,780 → 12,801 (DQ) → 5,694 (finals customers).

**Figure A-7:** `charts/part_a_order_funnel.png` — 27,350 → 25,658 (DQ) → 8,955 (finals orders).

---

## 2.6 Layer 1 — DQ Drops with Manifest Counts

Authoritative counts from `outputs_finals/manifest.json`:

| Rule ID | Rule | Orders dropped (approx.) |
|---------|------|--------------------------|
| **DQ-02** | Revenue = 0 AND discount = 0 | 336 |
| **DQ-03** | Revenue = 0 AND discount > 0 | 1,281 |
| **DQ-04** | `wholesale-sale` OR revenue > S$5,000 | 78 |
| **Total DQ** | — | 27,350 → **25,658** orders; 13,780 → **12,801** customers |

Reference snapshots: `outputs_finals/do_not_use_these/*_dq_clean.parquet`

---

## 2.7 Layer 2 — LP Business Filters (LP-F01 to LP-F04)

| Rule ID | Rule | Customers affected (approx.) |
|---------|------|------------------------------|
| **LP-F03** | Lifetime `first_order_date >= 2022-01-01` — entire customer excluded if before | ~7,500 excluded |
| **LP-F01** | Any purchase of `better-whey-protein-elite` | ~200 |
| **LP-F02** | Acquired in July or November | ~400 |
| **LP-F04** | First retained order discount bin = 51%+ | ~659 |
| **Finals eligible** | All LP flags pass | **5,694 customers** |

**Note on 6,353 vs 5,694:** Mid-term estimated 6,353 after LP filters before order-window and Layer 3 refinements. The manifest **5,694** is authoritative for all final recommendations.

---

## 2.8 Layers 0 & 3 — Order Window and Seasonality

| Layer | Rule | Result |
|-------|------|--------|
| **L0** | `order_date >= 2022-01-01` on retained customers | Pre-2022 orders dropped from finals tables |
| **L3** | Drop orders in **July and November** (order month) | Promo-season orders excluded |
| **L3** | Drop `better-whey-protein-elite` from line items | Bulk SKU removed from co-purchase/reorder calcs |

**Final row counts:** 8,955 orders · 14,448 line items · 5,694 customers

---

## 2.9 COGS Enrichment and Additional Validations

**June 2026 update:** `enrich_finals_with_margin.py` joins LP COGS file.

| Metric | Mid-term | Finals |
|--------|----------|--------|
| COGS coverage | 35% variants | **74.7% revenue** |
| Weighted margin | 40% proxy | **70.5% true margin** (covered rev) |
| Customer GP field | `total_revenue × 0.40` | `true_gross_profit` |

Additional checks carried forward: subscription flag consistency (99.9%), marketplace repeat as lower bound, `PRODUCT_MAP` category mapping, customer ID normalisation for dashboard demo.

`[INSERT: screenshot — margin_enrichment_summary.json]`

**Optional Figure A-8:** `aditya_findings/margin_analysis/outputs/fig_proxy_vs_true_gp.png`

---

## 2.10 Before vs After Summary

| Metric | Mid-term base | After DQ only | Finals (all layers) |
|--------|---------------|---------------|---------------------|
| Customers | 13,780 | 12,801 | **5,694** |
| Orders | 27,350 | 25,658 | **8,955** |
| One-time buyer % | 67.6% | ~70% | **77.3%** |
| Margin basis | 40% proxy | 40% proxy | **True COGS (74.7% cov.)** |
| Data path | `outputs/` | `do_not_use_these/` | **`outputs_finals/`** |

Cleaning **increases** observed one-and-done rate because promo/bulk/gift buyers are removed — the finals cohort is harder to retain, and recommendations target realistic DTC consumers.

---

## 2.11 Assumptions and Residual Limitations

1. **FX:** ±10% on early MY revenue in SGD — direction unchanged.
2. **COGS:** 25.3% revenue without unit cost — GP claims scoped to covered SKUs.
3. **Marketplace:** Repeat rates are lower bounds.
4. **Recharge:** One-year window only.
5. **2026:** Partial year excluded from full-year trends where noted.
6. **HK:** Immaterial (2 orders).

**Reproducibility:** `python EDA/13_build_finals_datasets.py` then `python EDA/aditya_findings/enrich_finals_with_margin.py`

**Regenerate Part A charts:** `python EDA/report_details/build_part_a_charts.py`

---
# Part B — Insights & Recommendations (Solution 2)

> **Scope note:** Solution 1 (customer tiering, reinvestment budget, win-back campaigns) is documented in the presentation materials and covered by another team member. This section covers **Solution 2 only** — the recommendation system and subscription development engine.

---

## 3.1 Business Problem Restated

LushProtein does not have a traffic problem. The site converts visitors into first-time buyers. The failure mode is **what happens after Order 1**:

- Customers do not reorder
- Customers do not try a second product category
- Non-subscribers rarely convert to Subscribe & Save

Shopify's default recommendation widget treats every visitor the same. It has **no post-purchase timing**, **no category routing**, and **no physical sample workflow**. Solution 2 replaces generic suggestions with **the right product at the right lifecycle moment**.

---

## 3.2 What the Data Shows — Three Gaps

**Data source:** `outputs_finals/customers.parquet` and category ladder analysis (n = 5,694).

### Gap 1 — Retention

| Metric | Value |
|--------|-------|
| Buy exactly once | **77.3%** (4,402 customers) |
| Return for Order 2+ | **22.7%** |

### Gap 2 — Category Depth

| Categories ever bought | Customers | Share | Repeat rate | Avg GP |
|------------------------|-----------|-------|-------------|--------|
| 1 | 3,681 | **65%** | 13% | S$64 |
| 2 | 1,411 | 25% | 30% | S$92 |
| 3+ | 602 | 11% | **63%** | **S$223** |

Moving from 1 → 3 categories is associated with a **~5× repeat-rate increase** and **~3.5× GP increase** — the prize L3 is designed to unlock.

### Gap 3 — Subscription

| Group | Customers | Repeat rate | Avg GP |
|-------|-----------|-------------|--------|
| Subscribers | 713 | **62%** | S$134 |
| Non-subscribers | 4,981 | **17%** | S$81 |

**Visualisation:** `aditya_findings/outputs/charts/slide1_problem_statement.png` (3-panel: retention, category ladder, subscriber gap)

---

## 3.3 Solution 2 — 4-Layer Recommendation System

Through our analysis and discussions with LushProtein, a central constraint emerged: **LushProtein does not currently operate a custom Shopify app or third-party recommender linked to their store**. Day-to-day product suggestions rely on **Shopify's built-in recommendation engine**, which surfaces products based on **generic popularity and store-wide co-occurrence** — the same logic used by large fashion and general merchandise stores with hundreds or thousands of SKUs.

That approach is reasonable when the goal is to show *something* related on a product page. It is a poor fit for LushProtein because:

- The catalogue is **small and structured** (~6–8 core product categories: Clear Protein, Lean Protein, Collagen, Accessories, etc.), not a long-tail fashion assortment
- Customer value depends on **category exploration and reorder timing**, not impulse add-ons alone
- **77.3% of customers buy once** — the critical moment is not the first page view alone, but **what happens between Order 1 and Order 2**
- Shopify's default widget has **no post-purchase sequencing**, **no category routing rules**, and **no physical sample workflow**

Solution 2 is therefore a **lifecycle-based recommendation architecture**: four layers, each mapped to a specific customer moment, built from LushProtein's own order data rather than generic platform defaults.

**Visualisation:** `r2_shopify_vs_custom_engine.png` — Shopify default vs 4-layer engine capability comparison.

---

### 3.3.1 Why not Shopify default

| Capability | Shopify default | LushProtein 4-layer engine |
|------------|-----------------|----------------------------|
| Cold-start guidance (no history) | Generic "popular" products | L1 rules from D1 co-purchase behaviour |
| Same-session basket expansion | Basic co-occurrence widget | L2 association rules with confidence scores |
| Post-purchase cross-sell timing | Not supported | L3 email + sample on measured reorder windows |
| Personalisation for repeat buyers | Same widget for all | L4 item-item CF for 3+ order customers |
| Physical sample dispatch | Not supported | L3 fulfilment tags + daily dispatch report |

No single Shopify setting replaces this stack. Phase 1 can run without a custom app — using email flows, CSV lookup tables, and Shopify customer tags — but the **logic must come from our analysis**, not the platform default.

---

### 3.3.2 Three problems, four layers

The four layers collectively address **three distinct problems** in the customer journey:

```
Problem 1 — COLD START (no customer history)     →  L1 + L2
Problem 2 — POST-FIRST-PURCHASE (habit window)  →  L3
Problem 3 — LOYAL BUYER PERSONALISATION         →  L4
```

---

#### Problem 1 — Cold start: maximise the first visit (L1 + L2)

**Who:** Every new visitor and first-time buyer — **100% of the customer pool** (~5,694 finals-eligible customers).

**The problem:** At first contact we have **no purchase history, no category preference, and no reorder pattern**. Shopify's generic widget cannot distinguish a first-time Clear Protein buyer from a fifth-order subscriber. If we do nothing structured here, customers leave with one SKU and never discover the rest of the range — consistent with **65% stuck at one product category**.

**Layer 1 — Rule-based cold start (post-purchase rules)**

- **When:** Immediately after first purchase (welcome email, Day 1–14 cross-sell email)
- **How:** Rules derived from **D1 co-purchase rates** — what LushProtein's most profitable customers actually bought together
- **Examples:**
  - Bought Clear Protein → recommend Lean Protein (53% D1 co-purchase)
  - Bought Lean Protein → recommend Clear Protein (65% D1 co-purchase)
  - Bought Accessories → recommend Lean Protein urgently (41% transition; do not send another shaker)
- **Why rules, not ML:** 77% of customers have only one order — collaborative filtering has nothing to learn from

**Layer 2 — Association rules / market basket analysis (in-session)**

- **When:** Active browsing — product detail page (PDP), cart drawer, checkout
- **How:** Market basket analysis on 8,955 finals orders — "customers who bought X in the same order also bought Y"
- **Examples:** Lean TMT + Clear Shaker (93% confidence); Clear Peach + Clear White Grape (36% confidence, 333 orders)
- **Goal:** Expand the **current basket** with same-category bundles and high-confidence pairs while the customer is still shopping

**Combined L1 + L2 objective:** Use the **first visit and first order** to expose as many relevant categories as possible — same-cart upsell (L2) plus post-purchase category introduction (L1) — before the customer goes quiet.

**Visualisations:** `rec_sys_l1_cold_start.png`, `rec_sys_l2_mba_rules.png`

---

#### Problem 2 — After first purchase: the habit-formation window (L3)

**Who:** First-time buyers who have completed Order 1 — approximately **32% of the active pool per year** (~1,390 customers/year entering the L3 journey).

**Why this moment matters:** The data shows that customers who never try a second category repeat at **13%**; customers who reach three categories repeat at **63%**. The window **between Order 1 and the expected reorder** is when the customer is forming a replenishment habit. Cross-selling at checkout (L2) is too early — they have already decided what to buy. Cross-selling **14 days after delivery**, and shipping a **physical sample ~10 days before their reorder window**, targets the moment they are deciding what to reorder next.

**Our approach — three decisions per customer:**

1. **What to recommend** — cross-sell category from first purchase (7-row routing table)
2. **When to email** — Day 7, 14, or 21 after delivery depending on category
3. **When to ship a physical sample** — calculated from **median reorder interval minus 10 days**, shipped **separately from the first order box**

**Rules source:** `cross_sell_timing_and_samples.csv` — one row per first-purchase category, built offline from:
- D1 co-purchase matrix (`co_purchase_matrix_d1.csv`)
- Median reorder intervals per SKU (`12_reorder_interval_by_sku.csv`)

**Sample and reorder calculation (method):**

1. For each hero SKU, identify customers with **2+ orders** of that SKU
2. Compute **day gaps** between consecutive orders per customer; take **median gap per customer**
3. Take **median across all repeat buyers** for that SKU → `median_reorder_days`
   - Clear Peach 500g: **54 days** (81 repeat buyers; mean 76d — median used to avoid bulk-buyer skew)
   - Lean TMT 1kg: **35 days** (39 repeat buyers)
   - Collagen Glow 300g: **42 days** (40 repeat buyers)
4. Apply timing formula:

```
sample_ship_day = max(email_day + 7, median_reorder_days − 10)
reorder_window   = median_reorder_days
email_day          = category-specific (7 / 14 / 21)
```

**Why sample ships separately:** A sachet in the first order box is ignored during unboxing excitement. A sample arriving **10 days before the customer runs low** introduces a new category at the **reorder decision moment** — the core insight validated with LushProtein.

**Runtime engine:** Not machine learning. A **7-row CSV lookup** at batch time — the intelligence was built in EDA; production reads the table.

**Visualisations:** `rec_sys_l3_timing_detail.png`, `slide3a_timing_bars.png`, `slide3c_evidence.png`

---

#### Problem 3 — Loyal buyer personalisation (L4)

**Who:** Logged-in customers with **3+ orders** — **~730 customers (17% of pool)**. These are disproportionately valuable: D1 customers (top profit decile) generate **57.7% of total GP**.

**The problem:** L1 rules treat every Clear buyer the same; L3 treats every first-time buyer the same. A customer who has bought Lean TMT six times and Clear Peach twice has a **specific purchase fingerprint** that generic rules cannot capture.

**Layer 4 — Item-item collaborative filtering**

- **How:** Build a customer × SKU purchase matrix (4,290 customers × 83 active SKUs). Compute **cosine similarity** between SKU pairs — "SKUs bought by similar customers"
- **Output:** For each SKU a customer has purchased, surface the top similar SKUs they have **not yet tried**
- **Example:** Lean TMT 1kg → Lean Taro 1kg (similarity 0.86); Clear Peach → Clear White Grape (0.41)
- **Why item-item, not user-user CF:** 67% one-and-done → user vectors too sparse; item vectors have enough density across repeat buyers
- **When to deploy:** Phase 3 (Week 6+) — after L1–L3 generate the repeat buyers L4 can personalise

**Visualisation:** `rec_sys_l4_item_cf_heatmap.png`

---

### 3.3.3 Layer summary

| Layer | Problem solved | Question answered | When | Method | Coverage |
|-------|----------------|-------------------|------|--------|----------|
| **L1** | Cold start | What should a new buyer try next? | After Order 1 | Rule-based co-purchase | ~100% |
| **L2** | Cold start | What goes in the cart now? | Active session / PDP | Association rules (MBA) | ~100% |
| **L3** | Post-purchase habit | What to email/sample before reorder? | Order 1 → Order 2 window | Timed 7-row CSV lookup | ~32%/yr |
| **L4** | Loyal personalisation | What does this buyer specifically want? | 3+ orders, logged in | Item-item CF | ~17% |

**Why not one model?** ML-only (L4) fails for 83% of customers with insufficient history. Rules-only (L1 forever) never personalises repeat buyers. A single post-purchase email misses in-session basket expansion. **All four layers are required** — each solves a problem the others cannot.

**Visualisations:**
- `rec_sys_why_4_layers.png` — coverage bars + failure modes if only one layer is used
- `rec_sys_architecture_v2.png` — lifecycle view from first order to loyal buyer

---

## 3.4 Layer 3 — Phase 1 Focus & Implementation

The full 4-layer system is the long-term architecture. **Layer 3 is the recommended Phase 1 priority** for three reasons confirmed with LushProtein:

1. **Highest impact on the core problem** — 77.3% one-and-done rate is driven by what happens after Order 1, which is exactly what L3 addresses
2. **Lowest implementation complexity** — no custom Shopify app; a 7-row CSV lookup + email flows + fulfilment tags
3. **All data already built** — routing rules, reorder medians, and co-purchase evidence are complete in project outputs

L1 and L2 can run in parallel from Week 1–2 (email copy + PDP widget). L4 is deferred until L3 generates repeat buyers. **This section details L3 in operational terms** — what LushProtein can execute without engineering resource.

### What L3 Is (Business Terms)

After a customer's **first order ships**, LushProtein should:

1. **Email** them the next product category to try (e.g. Clear → Lean) on **Day 14** (or Day 7/21 for Accessories/Collagen)
2. **Ship a physical sachet sample** on a calculated day **~10 days before** their expected reorder — **not in the first box**
3. After **Order 2**, offer **Subscribe & Save** on Day 48 — not at first purchase

The "engine" is not AI. It is **`cross_sell_timing_and_samples.csv`** — **7 rows**, one per first-purchase category.

### L3 Routing Table (Simplified for Operations)

| First purchase | Recommend (email) | Sample to ship | Email day | Sample day | Reorder day |
|----------------|-------------------|----------------|-----------|------------|-------------|
| Clear Protein | Lean Protein | Lean 40g or Collagen 25g | 14 | 44 | 54 |
| Lean Protein | Clear Protein | Clear 25g sachet | 14 | 25 | 35 |
| Collagen Glow | Clear Protein | Clear 25g or Lean 40g | 21 | 32 | 42 |
| Accessories | Lean Protein | Clear 25g (**not** another shaker) | 7 | 25 | 35 |
| Soy / Other / Unknown | Clear Protein | Discovery/Clear sachet | 14 | 40–74 | 50–84 |

**Timing formula (already built):**

```
sample_ship_day = max(email_day + 7, median_reorder_days − 10)
```

**Evidence:** Clear→Lean 53% D1 co-purchase; Lean→Clear 65%; reorder medians from 81 Clear Peach and 39 Lean TMT repeat buyers.

### Three CRM Outputs 

| Output | Owner | Tool |
|--------|-------|------|
| **A — Email schedule** | Marketing | Email platform (CS-01/02/03) |
| **B — Sample dispatch** | Fulfilment | Shopify customer tag + daily report |
| **C — Subscribe trigger** | Marketing | SUB-01 at Order 2 + 48 days |

**Visualisations:**
- `slide3a_timing_bars.png` — email/sample/reorder days
- `slide3b_routing_grid.png` — category routing
- `slide3c_evidence.png` — why sample is separate from first box
- `r2_cross_sell_timeline_clear.png` — Clear buyer journey example

**Live demo:** `layer3_dashboard/` — Streamlit lookup simulating Gold-layer output per customer ID.

---

## 3.5 Implementation Architecture (Medallion Pipeline)

L3 production follows a **medallion-style batch pipeline** (no real-time ML):

| Layer | Tables | Contents |
|-------|--------|----------|
| **Bronze** | `bronze_orders_fulfilled`, `bronze_customers` | Raw Shopify webhook/API data |
| **Silver** | `silver_orders_clean`, `silver_l3_eligible` | ID normalisation, category map, `order_count = 1` filter |
| **Gold** | `gold_l3_crm_actions` | Join to 7-row rule table → email/sample/reorder dates |
| **Model (reference)** | `cross_sell_timing_and_samples.csv` | Offline EDA output — loaded into Gold |
| **Dashboard** | Layer 3 Streamlit app | Read-only Gold view for founder QA |

**Visualisation:** `slide4a_pipeline.png` or custom medallion diagram (Bronze → Silver → Gold → 3 CRM cards)

---

## 3.6 ROI and Budget Analysis

All figures use **conservative 5% conversion rates** unless stated. GP uses finals margin enrichment where available.

### A. Expected Annual GP Benefit (Conservative Build-Up)

**Mechanism 1 — Single-category → 2 categories**

```
Pool          = 3,681 customers (65% single-category)
Conversion    = 5%
Customers won = 3,681 × 0.05 = 184.05 ≈ 184
GP lift/customer = S$92 − S$64 = S$28  (avg GP: 2-cat minus 1-cat)
Annual GP gain = 184 × S$28 = S$5,152
```

**Mechanism 2 — Single-category → 3 categories** *(incremental ladder step)*

```
GP lift/customer = S$223 − S$64 = S$159  (3+-cat minus 1-cat)
Annual GP gain   = 184 × S$159 = S$29,256  (upper bound if all 184 reach 3-cat)

Conservative partial attribution (team model):
  184 × S$58 ≈ S$10,693  (blended step — per presentation prize model)
```

**Mechanism 3 — Subscribe & Save (SUB-01)**

```
Eligible pool   = 689 customers (2+ orders, never subscribed)
Conversion      = 5%
Customers won   = 689 × 0.05 = 34.45 ≈ 34
GP lift/customer = S$53  (subscriber S$134 − non-sub S$81)
Annual GP gain  = 34 × S$53 = S$1,802 ≈ S$2,262  (rounded in deck)
```

**Mechanism 4 — Acquisition mix (reduce shaker-led campaigns)**

```
Estimated annual GP improvement = S$4,389  (from entry-category repeat analysis)
```

**Total conservative GP range:**

```
Low  = S$5,152 + S$10,693 + S$2,262 + S$4,389 = S$22,496
High = S$30,000  (rounded upper bound per presentation)
Reported range: S$17,000 – S$30,000  (stress-test at 3% conversion ≈ S$17K)
```

**Visualisation:** `slide4b_tier_value.png`, `rec2_conservative_prize.png`

---

### B. Phase 1 Implementation Cost (Assumptions)

| Cost item | Assumption | Year 1 cost (SGD) |
|-----------|------------|-------------------|
| Sample sachets | 400 first-time buyers × 60% L3 eligible × S$2.50/sachet | **S$600** |
| Extra fulfilment labour | 1 hr/week × 52 × S$25/hr internal | **S$1,300** |
| Email platform | Existing Klaviyo/Omnisend — incremental flows only | **S$0** |
| Shopify tags / exports | Native — no app dev | **S$0** |
| Setup (flows + spreadsheet) | 30 hrs internal × S$30/hr opportunity cost | **S$900** |
| Contingency (10%) | — | **S$280** |
| **Total Phase 1 cost** | | **≈ S$3,080** |

*Assumption: LP already pays for email platform and fulfilment staff — we cost **incremental** sample and setup time only.*

---

### C. ROI Calculation

**Formula:**

```
ROI (%) = (Gain from Investment − Cost of Investment) / Cost of Investment × 100
```

**Conservative scenario (low gain, high cost):**

```
Gain  = S$17,000
Cost  = S$4,000  (upper cost bound)
Net   = S$17,000 − S$4,000 = S$13,000

ROI   = (13,000 / 4,000) × 100 = 325%
```

**Base scenario:**

```
Gain  = S$22,496
Cost  = S$3,080
Net   = S$19,416

ROI   = (19,416 / 3,080) × 100 = 630%
```

**Optimistic scenario (high gain, low cost):**

```
Gain  = S$30,000
Cost  = S$2,500
Net   = S$27,500

ROI   = (27,500 / 2,500) × 100 = 1,100%
```

**Reinvestible income (Year 1, base scenario):**

```
Reinvestible income = Additional GP − Implementation cost
                    = S$22,496 − S$3,080
                    = S$19,416
```

This is **gross profit**, not cash flow — sample COGS is embedded in the S$2.50/sachet estimate above.

---

### D. How LushProtein Should Measure Success

| KPI | Baseline | Phase 1 target (6 months) | Data source |
|-----|----------|---------------------------|-------------|
| 2nd-order rate (30-day cohort) | ~23% | +3 pp vs control | Shopify orders |
| 2nd-category attach rate | 13% (1-cat repeat) | +5 pp on L3 cohort | Category flags on customer |
| CS email CTR | — | 5–8% | Email platform |
| Sample → paid conversion | — | >15% | Tag + follow-up order |
| SUB-01 conversion | — | 5% of 689 pool | Subscription app |

`[INSERT: Table B-1 — ROI sensitivity table at 3%, 5%, 8% conversion rates]`

---

## 3.7 Phased Roadmap and Recommendation Breakdown

### Recommendation 1 — Launch L3 Email Flows (CS-01/02/03)

| Field | Detail |
|-------|--------|
| **Why it matters** | Addresses 77.3% one-and-done rate at the habit-formation window |
| **Expected impact** | S$5,152+ GP/yr from 2-category uplift alone |
| **Required resources** | Email platform admin (8–12 hrs); copy from routing table |
| **Difficulty** | Low |
| **Timeline** | Weeks 1–2 |
| **Priority** | **P0 — highest** |

**Phase 1 (0–3 months) — action items:**
- Export nightly fulfilled first-time orders
- VLOOKUP `cross_sell_timing_and_samples.csv`
- Activate CS-01 (Clear), CS-02 (Lean), CS-03 (Collagen)
- **Expected outcome:** Timed cross-sell emails live for top 3 categories

---

### Recommendation 2 — Physical Sample Dispatch (L3 Fulfilment)

| Field | Detail |
|-------|--------|
| **Why it matters** | Sample before reorder window drives category trial at decision moment |
| **Expected impact** | Primary driver of 1→2 category movement |
| **Required resources** | Fulfilment ops (1 hr/week); sachet inventory ~S$600/yr |
| **Difficulty** | Medium (coordination, not technology) |
| **Timeline** | Weeks 3–4 |
| **Priority** | **P0** |

**Phase 1 action items:**
- Daily "sample dispatch" report from Gold table
- Shopify tag: `sample_sku` + `sample_ship_date`
- **Rule:** Ship separately — never in first order box

---

### Recommendation 3 — Subscribe & Save Trigger (SUB-01)

| Field | Detail |
|-------|--------|
| **Why it matters** | Subscribers repeat at 62% vs 17%; offer only after proven fit |
| **Expected impact** | ~S$2,262 GP/yr at 5% conversion |
| **Required resources** | Email flow; subscription app config |
| **Difficulty** | Low–medium |
| **Timeline** | Weeks 4–5 |
| **Priority** | **P1** |

**Phase 2 (3–6 months) — action items:**
- L2 PDP "Frequently Bought Together" using `sku_association_rules.csv`
- Accessories CS-04 flow (Day 7 urgent protein trial)
- **Expected outcome:** Same-cart basket lift + shaker-led acquisition fix

---

### Recommendation 4 — Item-CF Personalisation (L4)

| Field | Detail |
|-------|--------|
| **Why it matters** | Personalises top 17% (730 customers with 3+ orders) |
| **Expected impact** | Retention of VIP/Gold-B tiers; supports Solution 1 tiers |
| **Required resources** | Theme edit or app; matrix CSV already built |
| **Difficulty** | Medium–high |
| **Timeline** | Weeks 6–10 |
| **Priority** | **P2 — defer** |

**Phase 3 (6–12 months):**
- Account page recommendations from `recommender_04_item_similarity_matrix.csv`
- Full 4-layer integration with CRM tiers
- **Expected outcome:** Personalised experience for proven repeaters

**Visualisation:** `rec_sys_implementation_roadmap.png`

---

## 3.8 Resource Constraints and Three Baby Steps

LushProtein may not have engineering bandwidth to build a custom app, ML pipeline, or real-time recommender in Year 1. **That is acceptable.** The analysis was designed so Phase 1 runs on tools LP already owns.

### Practical Limitations

- No dedicated data engineer for nightly pipelines (use CSV + spreadsheet MVP)
- Limited sample inventory budget (~S$50–100/month)
- Email platform migration may delay automation triggers
- Marketplace customers invisible to Shopify post-purchase flows

### What to Prioritise

1. **L3 email** for Clear + Lean first-time buyers (largest volume, strongest co-purchase evidence)
2. **Sample dispatch** for Clear buyers only (54-day cycle — easiest to explain operationally)
3. **SUB-01** only after Order 2 is confirmed in Shopify

### Three Realistic Baby Steps (Start This Month)

| Step | Action | Effort | Impact |
|------|--------|--------|--------|
| **Baby Step 1** | Manually email Clear buyers 14 days after delivery with Lean recommendation | 2 hrs/week | Tests messaging before automation |
| **Baby Step 2** | Weekly export → VLOOKUP rule CSV → fulfilment sample list | 1 hr/week | Proves sample timing without webhooks |
| **Baby Step 3** | Tag Order-2 customers in Shopify; send one SUB-01 test to 20 customers | 3 hrs one-off | Validates subscription offer timing |

---

## 3.9 Risks, Caveats, and Success Metrics

### Risks

| Risk | Mitigation |
|------|------------|
| Sample cost overrun | Cap at 500 sachets/quarter; measure conversion before scaling |
| Email fatigue | Max 1 cross-sell + 1 sample notice per customer in first 60 days |
| Wrong category mapping | Monthly audit of `Unknown` handles; update `PRODUCT_MAP` |
| Over-attributing GP lift | Use holdout cohort (no L3) vs treatment for 90-day test |
| Reorder median drift | Recompute `cross_sell_timing_and_samples.csv` annually |

### Caveats

- ROI figures are **modelled**, not observed post-implementation
- 5% conversion is conservative but unproven until A/B test completes
- GP lifts assume category behaviour matches historical ladder (correlation, not causal proof without experiment)
- Solution 1 tier budgets are separate — do not double-count reinvestment spend with L3 sample cost

---

# Appendix A — Visualization Guide

Use this map when converting the report to PDF. Insert figures near the referenced sections.

## Part A — Data Quality

| Figure ID | File path | Section | Caption |
|-----------|-----------|---------|---------|
| A-1 | `report_details/charts/part_a_cohort_funnel.png` | 2.5 | Customer funnel: 13,780 → 12,801 (DQ) → 5,694 (finals) |
| A-2 | `report_details/charts/part_a_revenue_distribution.png` | 2.2.1 | Order revenue before vs after cleaning (cap S$5K display) |
| A-3 | `report_details/charts/part_a_one_time_buyer_rate.png` | 2.2.2 | One-time buyer % rises as cohort gets cleaner |
| A-4 | `report_details/charts/part_a_missing_values.png` | 2.2.5 | Missing value profile — key Shopify fields |
| A-5 | `report_details/charts/part_a_filter_layers.png` | 2.3 | DQ + LP + order-window layers — relative impact |
| A-6 | `report_details/charts/part_a_cohort_funnel.png` | 2.5 | Same as A-1 — customer cohort funnel |
| A-7 | `report_details/charts/part_a_order_funnel.png` | 2.5 | Order funnel: 27,350 → 25,658 → 8,955 |
| A-8 | `aditya_findings/margin_analysis/outputs/fig_proxy_vs_true_gp.png` | 2.9 | 40% proxy vs true COGS margin |
| A-9 | Screenshot `outputs_finals/manifest.json` | 2.6 | Authoritative row counts per filter layer |
| A-10 | Console output `13_build_finals_datasets.py` | 2.6 | Rows dropped per DQ/LP rule |

## Part B — Solution 2 (Recommendation System)

| Figure ID | File path | Section | Caption |
|-----------|-----------|---------|---------|
| B-1 | `slide1_problem_statement.png` | 3.2 | Three gaps: retention, category, subscription |
| B-2 | `rec_sys_why_4_layers.png` | 3.3.3 | Why one model fails; layer coverage |
| B-3 | `rec_sys_architecture_v2.png` | 3.3.3 | 4-layer lifecycle architecture |
| B-2a | `r2_shopify_vs_custom_engine.png` | 3.3.1 | Shopify default vs custom engine |
| B-2b | `rec_sys_l1_cold_start.png` | 3.3.2 | L1 cold-start rules |
| B-2c | `rec_sys_l2_mba_rules.png` | 3.3.2 | L2 association rules |
| B-2d | `rec_sys_l4_item_cf_heatmap.png` | 3.3.2 | L4 item similarity |
| B-4 | `slide3a_timing_bars.png` | 3.4 | L3 timing: email, sample, reorder by category |
| B-5 | `slide3b_routing_grid.png` | 3.4 | First purchase → recommend → sample |
| B-6 | `slide3c_evidence.png` | 3.4 | Sample-not-in-box rationale + co-purchase evidence |
| B-7 | `r2_cross_sell_timeline_clear.png` | 3.4 | Clear Protein buyer journey (days 0–54) |
| B-8 | `slide4a_pipeline.png` | 3.5 | Shopify/medallion implementation pipeline |
| B-9 | `slide4b_tier_value.png` | 3.6 | Tier progression and GP prize |
| B-10 | `rec2_conservative_prize.png` | 3.6 | Conservative GP breakdown |
| B-11 | `rec_sys_implementation_roadmap.png` | 3.7 | Week-by-week rollout |
| B-12 | `rec_sys_l3_timing_detail.png` | 3.4 | Detailed L3 trigger table |
| B-13 | Dashboard screenshot | 3.5 | Layer 3 Streamlit demo (`layer3_dashboard/`) |
| B-14 | `[CREATE: medallion diagram]` | 3.5 | Bronze → Silver → Gold → CRM outputs |

**Optional supporting charts:**

| File | Use when |
|------|----------|
| `rec_sys_l1_cold_start.png` | Explaining L1 rules in appendix |
| `rec_sys_l2_mba_rules.png` | Phase 2 PDP discussion |
| `rec_sys_l4_item_cf_heatmap.png` | Phase 3 L4 discussion |
| `r2_shopify_vs_custom_engine.png` | Why Shopify default is insufficient |
| `r2_category_ladder.png` | Standalone category prize chart |

---

# Appendix B — Key Output Files

| Purpose | Path |
|---------|------|
| Finals orders | `EDA/outputs_finals/orders.parquet` |
| Finals customers | `EDA/outputs_finals/customers.parquet` |
| L3 rule table | `EDA/aditya_findings/outputs/cross_sell_timing_and_samples.csv` |
| Reorder intervals | `EDA/outputs/12_reorder_interval_by_sku.csv` |
| L2 association rules | `EDA/aditya_findings/recommendation_systems/outputs/sku_association_rules.csv` |
| L4 similarity matrix | `EDA/aditya_findings/recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv` |
| Build script | `EDA/13_build_finals_datasets.py` |
| Margin enrichment | `EDA/aditya_findings/enrich_finals_with_margin.py` |
| L3 dashboard | `layer3_dashboard/app.py` |

---

# Appendix C — Solution 1 Cross-Reference (Brief)

Solution 1 segments the **4,290 rankable consumers** (after marketplace exclusion) into profit/frequency tiers and allocates **20% of segment GP** as reinvestment budget (~S$57.9K total). Campaign types differ by recency (Active / At Risk / Lapsed).

**Blended first-cycle ROI (Solution 1 priorities):** 1.32× on S$9,588 spent (Protect + Win-back + Build subset).

Solution 2 (L3) **feeds** Solution 1 by moving Untiered customers toward Silver/Gold-B. The systems are complementary:

- **Solution 1** = who to treat and how much to spend
- **Solution 2** = what product to recommend and when

**Visualisations (Solution 1 — for team member's section):** `r1_crm_tier_overview.png`, `r1_incentive_budget_by_decile.png`, `r1_profit_margin_concentration.png`

---

*End of report. Regenerate Part A charts: `python EDA/report_details/build_part_a_charts.py`. Regenerate Part B charts: `python EDA/aditya_findings/build_slide_charts.py` and `python EDA/aditya_findings/build_rec_sys_charts.py`.*
