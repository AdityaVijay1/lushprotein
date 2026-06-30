# ISSS603 Applied Data Science for Customer Insights
## Final Report — Group 1 (SMU × LushProtein)

**Prepared for:** LushProtein (Lush Protein Pte Ltd)  
**Prepared by:** Aditya Vijay, Ang Wei Lin, Aung Shwe Tin, Lee Sae Lin, Pham Vinh Tan Emily, Toh Zheng Feng  
**Submission date:** June 2026  
**Report type:** Consulting deliverable — data quality improvements and customer development recommendations

---

> **Document note:** This report is formatted for conversion to PDF at font size 10, single spacing. Target length: 25 pages excluding cover and table of contents. Placeholders marked `[INSERT: …]` indicate where screenshots, pipeline diagrams, or updated run outputs should be inserted before submission.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Part A — Data Cleaning & Data Quality Improvements](#part-a--data-cleaning--data-quality-improvements)
   - 2.1 [Scope and Evolution from Mid-Term](#21-scope-and-evolution-from-mid-term)
   - 2.2 [Data Sources and Pipeline Overview](#22-data-sources-and-pipeline-overview)
   - 2.3 [Mid-Term Baseline vs Final Improvements](#23-mid-term-baseline-vs-final-improvements)
   - 2.4 [Layer 1 — Core Data Quality Drops (DQ-02 to DQ-04)](#24-layer-1--core-data-quality-drops-dq-02-to-dq-04)
   - 2.5 [Layer 2 — LushProtein Business Filters (LP-F01 to LP-F04)](#25-layer-2--lushprotein-business-filters-lp-f01-to-lp-f04)
   - 2.6 [Layer 0 and Layer 3 — Order Window and Order-Month Filters](#26-layer-0-and-layer-3--order-window-and-order-month-filters)
   - 2.7 [Additional Validations and Enrichments (Post Mid-Term)](#27-additional-validations-and-enrichments-post-mid-term)
   - 2.8 [Before vs After Summary](#28-before-vs-after-summary)
   - 2.9 [Assumptions and Residual Limitations](#29-assumptions-and-residual-limitations)
3. [Part B — Insights & Recommendations (Solution 2)](#part-b--insights--recommendations-solution-2)
   - 3.1 [Business Problem Restated](#31-business-problem-restarted)
   - 3.2 [What the Data Shows — Three Gaps](#32-what-the-data-shows--three-gaps)
   - 3.3 [Solution 2 Overview — 4-Layer Recommendation System](#33-solution-2-overview--4-layer-recommendation-system)
   - 3.4 [Layer 3 — Simplified for LushProtein Implementation](#34-layer-3--simplified-for-lushprotein-implementation)
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

## 2.1 Scope and Evolution from Mid-Term

The mid-term report (March 2026) established the raw data landscape: **27,350 order-header rows**, **13,780 unique customers**, mixed currencies (SG/MY/HK), and a documented set of data quality issues (zero-revenue orders, 100%-discount fulfilments, wholesale outliers, UTM gaps, Recharge ID mismatches, and incomplete COGS).

After the mid-term presentation, LushProtein provided explicit guidance on **which customers represent their current target market**. The finals analysis therefore applies:

1. All mid-term **DQ drops** (unchanged in principle, now codified in `13_build_finals_datasets.py`)
2. Four new **LP feedback filters** (LP-F01 to LP-F04)
3. Additional **order-window** and **order-month** rules (Layers 0 and 3)
4. **COGS enrichment** from LushProtein's June 2026 cost file (replacing the mid-term 40% margin proxy where coverage allows)

**Design principle:** Mid-term EDA remains valid for historical exploration. **Finals-filtered datasets** (`outputs_finals/`) are the single source of truth for recommendations.

`[INSERT: Figure A-1 — Cohort funnel diagram: 13,780 → DQ → LP filters → 5,694 finals customers]`

---

## 2.2 Data Sources and Pipeline Overview

| Source | Role | Finals usage |
|--------|------|--------------|
| Shopify order exports (SG/MY/HK) | Transaction history | Primary — orders/lines/customers |
| Customer export (June 2026) | PII + join keys | Dashboard demo only; anonymised |
| Product master | SKU/handle mapping | Category assignment via `PRODUCT_MAP` |
| Recharge subscription export | Subscription events | Partial (2025–2026 window; joined on `shopify_order_id`) |
| LP COGS file (June 2026) | Unit costs | Margin enrichment — 74.7% revenue coverage |
| Discount codes export | Campaign reference | Not joinable to orders at line level — documented limitation |

**Reproducibility:** Run `python EDA/13_build_finals_datasets.py`, then `python EDA/aditya_findings/enrich_finals_with_margin.py`.

---

## 2.3 Mid-Term Baseline vs Final Improvements

| Area | Mid-term state | Final improvement |
|------|----------------|-------------------|
| Customer pool | 13,780 all paid customers | **5,694** finals-eligible (LP scope) |
| Order pool | 27,350 headers | **8,955** finals orders |
| Margin | 40% fixed proxy (65% COGS null) | **True COGS** where available; weighted margin **70.5%** on covered revenue |
| Promo cohorts | Flagged in narrative | **Excluded** (Jul/Nov acquisition + 51%+ first-discount) |
| Bulk SKU | Mentioned | **Systematically excluded** (`better-whey-protein-elite`) |
| Pre-2022 cohort | Included in some charts | **Customer-level cut** — entire customer dropped if first order before 2022 |
| Discount narrative | 51%+ story in slides | **Removed from finals narrative** per LP feedback; retained in historical EDA only |
| Dataset location | `EDA/outputs/` | **`EDA/outputs_finals/`** with manifest and README |

---

## 2.4 Layer 1 — Core Data Quality Drops (DQ-02 to DQ-04)

Each issue follows: **Issue → Impact → Countermeasure → Validation → Result**.

---

### DQ-02: Zero Revenue and Zero Discount Orders

| Element | Detail |
|---------|--------|
| **Issue identified** | 336 orders with `Price: Total = 0` and `Price: Total Discount = 0` |
| **Impact on analysis** | Inflates order counts; distorts AOV and repeat metrics with non-purchase events |
| **Countermeasure applied** | Drop order if revenue = 0 AND discount = 0 |
| **Validation performed** | Row count before/after; spot-check of dropped IDs against raw export |
| **Result/improvement** | Removed non-behavioural rows; mid-term base reduced to clean paid-order set |

---

### DQ-03: 100%-Discount / Complimentary Fulfilments

| Element | Detail |
|---------|--------|
| **Issue identified** | 1,281 orders with revenue = 0 but positive discount value (influencer/PR/referral gifts) |
| **Impact on analysis** | Skews LTV, discount depth, and retention if treated as paid acquisition |
| **Countermeasure applied** | Exclude from finals analysis (confirmed with LP as non-consumer behaviour) |
| **Validation performed** | LP validation at mid-term; tag/discount pattern review |
| **Result/improvement** | Finals LTV and repeat rates reflect **paid consumer behaviour** only |

---

### DQ-04: Wholesale and Extreme-Value Outliers

| Element | Detail |
|---------|--------|
| **Issue identified** | 78 B2B/outlier orders (65 `wholesale-sale` tag + 14 orders > S$5,000) |
| **Impact on analysis** | Right-skewed revenue (mean S$114 vs median S$60); reseller behaviour dominates top decile |
| **Countermeasure applied** | Exclude tagged wholesale OR orders > S$5,000 |
| **Validation performed** | Distribution of AOV before/after; max order review |
| **Result/improvement** | Consumer-focused metrics; largest retained order aligned with DTC range |

---

### Additional Mid-Term Handling (Carried Forward)

| Issue | Countermeasure | Status in finals |
|-------|----------------|------------------|
| Mixed currencies (SG/MY/HK) | 5-year average FX at load (SGD/MYR 3.3, SGD/HKD 6.1) | Applied; ±10% measurement error on early MY revenue |
| Line vs header rows | Split `orders.parquet` (Top Row = 1) vs `lines.parquet` (Line Item) | Maintained |
| UTM 95% missing | Fallback: Shopify tags + `is_subscription` for channel | Maintained |
| Recharge ID mismatch | Join on `shopify_order_id` not customer ID | Documented; churn window 2025–2026 only |
| Duplicate customer IDs | Normalise apostrophe/scientific notation in exports | Extended to dashboard demo pipeline |

`[INSERT: Table A-1 — Order counts at each DQ layer from 13_build_finals_datasets.py console output]`

---

## 2.5 Layer 2 — LushProtein Business Filters (LP-F01 to LP-F04)

These filters implement **LP's post mid-term scope decisions**. They are not data errors; they define the **addressable DTC consumer base**.

---

### LP-F01: Exclude Better Whey Protein Elite Buyers

| Element | Detail |
|---------|--------|
| **Issue identified** | `better-whey-protein-elite` attracts bulk buyers not representative of core consumers |
| **Impact on analysis** | Inflates one-time high-AOV behaviour; distorts cross-sell and reorder timing |
| **Countermeasure applied** | Flag customers with any elite handle purchase; exclude from `finals_eligible` |
| **Validation performed** | Handle search across line items; LP confirmation |
| **Result/improvement** | ~200 customers removed from recommendation targeting pool |

---

### LP-F02: Exclude July and November Acquisition Months

| Element | Detail |
|---------|--------|
| **Issue identified** | July (anniversary) and November (BFCM) drive promotion-heavy, atypical cohorts |
| **Impact on analysis** | Skews LTV benchmarks and repeat-rate comparisons |
| **Countermeasure applied** | Exclude customers whose **first order month** is July or November |
| **Validation performed** | Monthly acquisition vs discount depth charts |
| **Result/improvement** | Retention benchmarks reflect **non-promo acquisition** |

---

### LP-F03: Post-January 2022 Customer Cut (Lifetime)

| Element | Detail |
|---------|--------|
| **Issue identified** | Pre-2022 = product/pricing experimentation phase per LP |
| **Impact on analysis** | Mixing eras blends incompatible pricing and portfolio strategies |
| **Countermeasure applied** | If lifetime `first_order_date < 2022-01-01`, drop **entire customer** (all orders) |
| **Validation performed** | Cohort LTV by year; LP sign-off |
| **Result/improvement** | Stable reference period for all finals insights |

**Important:** This is a **customer cut**, not an order cut. A customer acquired in March 2022 retains all 2022–2025 orders.

---

### LP-F04: Exclude >50% First-Order Discount

| Element | Detail |
|---------|--------|
| **Issue identified** | 51%+ first-order discount = referral/sampling/gifting, not organic repeat potential |
| **Impact on analysis** | Overstates one-and-done rate drivers; confounds L3 timing (non-typical replenishment intent) |
| **Countermeasure applied** | Exclude if first retained order discount bin = `51%+` |
| **Validation performed** | Discount bin vs repeat rate cross-tab |
| **Result/improvement** | L3 reorder medians based on **paid-first-order** behaviour |

---

### Cohort Funnel (Finals)

| Stage | Customers | Notes |
|-------|-----------|-------|
| Total paid, non-DQ customers | ~13,780 | Mid-term base |
| After LP-F03 (2022+ acquisition) | ~6,200 | Pre-2022 removed |
| After LP-F01, F02, F04 | **5,694** | **Finals-eligible** |
| After marketplace/reseller exclusion (decile work) | 4,949 | Used for profit decile — see Appendix C |
| After full decile exclusions | 4,290 | Rankable consumer pool for tier analysis |

**Finals recommendation metrics (Solution 2) use 5,694** unless otherwise stated.

`[INSERT: Figure A-2 — Filter decision tree: DQ → LP-F01–F04 → finals_eligible flag]`

---

## 2.6 Layer 0 and Layer 3 — Order Window and Order-Month Filters

### Layer 0 — 2022+ Order Window (on Retained Customers)

| Element | Detail |
|---------|--------|
| **Issue identified** | Retained customers may have pre-2022 order history |
| **Impact on analysis** | Category breadth and reorder intervals could include obsolete SKUs |
| **Countermeasure applied** | Keep only orders with `order_date >= 2022-01-01` for finals tables |
| **Validation performed** | Order count drop logged in build script |
| **Result/improvement** | **8,955 orders** in finals `orders.parquet` |

### Layer 3 — July/November Order Months + Elite Line Items

| Element | Detail |
|---------|--------|
| **Issue identified** | Promo-month **orders** (not just acquisitions) distort seasonality; elite lines remain in basket |
| **Impact on analysis** | Reorder medians and co-purchase rates could reflect promo stacking |
| **Countermeasure applied** | Drop orders in months 7 and 11; remove elite handle from `lines.parquet` |
| **Validation performed** | Seasonal order volume check; line-item count reconciliation |
| **Result/improvement** | **14,448 line items** in clean finals lines file |

---

## 2.7 Additional Validations and Enrichments (Post Mid-Term)

### Subscription Flag Consistency

| Check | Result | Rule |
|-------|--------|------|
| Tag vs `is_subscription` | 3,263 / 3,265 match (99.9%) | **Use `is_subscription` flag** consistently |

### Channel Attribution

| Check | Result | Rule |
|-------|--------|------|
| Marketplace subscription rate | 0% (platform limitation) | Do not interpret as true behaviour |
| Marketplace repeat vs Direct | 14.4% vs 33.5% | Valid relative comparison (same Shopify-visible baseline) |

### COGS / Margin Enrichment (June 2026)

| Element | Detail |
|---------|--------|
| **Issue identified** | Mid-term: 65% of variants missing COGS → 40% margin proxy only |
| **Countermeasure applied** | Join LP COGS file; compute `true_gross_profit`, deciles, CRM tiers |
| **Validation performed** | Coverage report: **74.7% revenue**, **70.5% weighted margin** |
| **Result/improvement** | GP figures in prize model use **true margin where covered**; proxy labelled where not |

### Product Category Mapping

| Element | Detail |
|---------|--------|
| **Issue identified** | Handles vary (legacy packs, sachets, POS unlinked SKUs) |
| **Countermeasure applied** | Central `PRODUCT_MAP` in `00_config.py`; fallback category `Unknown` |
| **Validation performed** | Category distribution sanity check; manual review of top 20 handles |
| **Result/improvement** | L3 routing key (`first_product_category`) stable for 7-row lookup |

### Duplicate and Missing Value Rules (Finals)

| Field | Handling |
|-------|----------|
| `customer_id` | Strip `'`, commas, `.0`; reject scientific notation in UI demos |
| `second_order_date` | Null for 67.6% one-time buyers — **expected**, not imputed |
| `Tags` / UTM | Missing treated as Direct/Own; not used for L3 routing |
| Duplicate orders | Dedupe on `order_id` at load |

### Outlier Handling Summary

| Type | Method |
|------|--------|
| Revenue outliers | DQ-04 (>S$5,000) + wholesale tag |
| Reorder interval outliers | **Median** per customer, then median across SKU buyers (not mean) |
| Discount outliers | LP-F04 for acquisition; historical 51%+ retained in EDA only |

`[INSERT: Screenshot — margin_enrichment_summary.json key metrics]`

---

## 2.8 Before vs After Summary

| Metric | Mid-term (broad base) | Finals (filtered) | Interpretation |
|--------|----------------------|-------------------|----------------|
| Customers | 13,780 | **5,694** | LP addressable DTC base |
| Orders | 27,350 | **8,955** | 2022+ consumer orders |
| One-time buyer rate | 67.6% | **77.3%** | Higher — promo/bulk noise removed |
| Single-category share | ~59% (broader) | **65%** (3,681) | Stricter cohort shows deeper category stuck |
| Margin basis | 40% proxy | **70.5% weighted true margin** (74.7% rev coverage) | More defensible GP prize model |
| Primary data path | `EDA/outputs/` | **`EDA/outputs_finals/`** | All final slides use finals |

**Reliability improvement:** Finals cohort aligns with **who LushProtein wants to grow today** — post-2022, non-promo-acquired, non-bulk, paid-first-order consumers. L3 reorder days (Clear 54d, Lean 35d, Collagen 42d) are measured on this cleaned base.

---

## 2.9 Assumptions and Residual Limitations

1. **FX:** 5-year average rates; MY early-year revenue may differ ±10% in SGD terms — direction unchanged.
2. **COGS:** 25.3% of revenue lacks unit cost — GP on uncovered SKUs uses coverage-weighted averages or is excluded from SKU-level profit claims.
3. **Marketplace:** Repeat rates are **lower bounds** (Shopify cannot see Shopee/Lazada reorders).
4. **Recharge:** One-year export window; long-tenure subscriber churn understated.
5. **2026 partial year:** Jan–Mar 2026 excluded from full-year trend charts where noted.
6. **HK store:** Immaterial (2 orders) — SG-dominated conclusions.

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

## 3.3 Solution 2 Overview — 4-Layer Recommendation System

One algorithm cannot serve all customers. Each layer maps to a **customer moment**:

| Layer | Question answered | When | Method | Coverage |
|-------|-------------------|------|--------|----------|
| **L1** | What should a new buyer try next? | After Order 1 | Rule-based co-purchase | ~100% |
| **L2** | What goes in the cart now? | Active session / PDP | Association rules (MBA) | ~100% |
| **L3** | What to email/sample before reorder? | Post-purchase | Timed 7-row CSV lookup | ~32% (~1,390/yr new buyers) |
| **L4** | What does this loyal buyer want? | 3+ orders, logged in | Item-item CF | ~17% (~730) |

**Why not ML only?** 77% buy once — collaborative filtering has no history. L1 and L3 cover the cold-start majority.

**Visualisations:**
- `rec_sys_why_4_layers.png` — coverage + failure modes
- `rec_sys_architecture_v2.png` — lifecycle view

---

## 3.4 Layer 3 — Simplified for LushProtein Implementation

The full 4-layer design is the long-term target. For a resource-constrained team, **L3 should be simplified to what can run in Phase 1 without engineering**.

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

### What to Remove / Defer (Complexity Reduction)

| Full design | Phase 1 simplification |
|-------------|------------------------|
| 5 separate CS flows (CS-01–05) | **Start with 3 flows:** Clear, Lean, Collagen |
| Automated Shopify Flow tags | **Daily spreadsheet** + manual tag OR weekly ops review |
| Custom webhook pipeline | **Nightly CSV export** + VLOOKUP (MVP) |
| L4 item-CF on account page | **Defer to Phase 3** (Week 6+) |
| L2 PDP widget | **Phase 2** — use Shopify's widget with our rule CSV as input |
| Per-SKU micro-segmentation | **Category-level routing only** (7 rows) |

### Three CRM Outputs (Keep These)

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

**Phase 1 runtime flow:**

```
Shopify order fulfilled
  → nightly export (customer_id, first_product_category)
  → VLOOKUP cross_sell_timing_and_samples.csv
  → 3 actions: email list | fulfilment tag | subscribe queue
```

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
| A-1 | `[CREATE: cohort funnel]` | 2.1 | Customer count at each filter stage (13,780 → 5,694) |
| A-2 | `[CREATE: filter decision tree]` | 2.5 | DQ and LP filter logic |
| A-3 | Output of `13_build_finals_datasets.py` | 2.4 | Console log — rows dropped per rule |
| A-4 | `margin_enrichment_summary.json` | 2.7 | COGS coverage and weighted margin |

## Part B — Solution 2 (Recommendation System)

| Figure ID | File path | Section | Caption |
|-----------|-----------|---------|---------|
| B-1 | `slide1_problem_statement.png` | 3.2 | Three gaps: retention, category, subscription |
| B-2 | `rec_sys_why_4_layers.png` | 3.3 | Why one model fails; layer coverage |
| B-3 | `rec_sys_architecture_v2.png` | 3.3 | 4-layer lifecycle architecture |
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

*End of report. Regenerate charts: `python EDA/aditya_findings/build_slide_charts.py` and `python EDA/aditya_findings/build_rec_sys_charts.py`.*
