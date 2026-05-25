# LushProtein — Data Quality & Due Diligence Report (Final)

**Team:** Group 1 — Aditya Vijay, Emily Pham Vinh Tan, Saelin Lee, Shwe Tin Aung, Weilin Ang, Zhengfeng Toh  
**Date:** May 2026  
**Audience:** Course instructors (ISSS603) — assessment of data understanding and preparation  
**Scope:** Shopify customer transactions (2020–Q1 2026), SG + MY + HK, all revenue in **SGD** after FX conversion  

> **This is the single reference document for the PDF Data Quality Report.**  
> It consolidates `data_quality_checks.md` (midterm, preserved unchanged) and post-feedback extensions from `FINAL_DATA_QUALITY_REPORT.md`.  
> **Midterm narrative files** (`FINDINGS.md`, `presentation.md`) are not modified.

**Currency assumption:** 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, applied once at load in `EDA/01_load_and_merge.py`).

---

## Table of Contents

1. [Dataset Overview, Coverage & EDA Summary](#1-dataset-overview-coverage--eda-summary)
2. [Data Issues & Discrepancies](#2-data-issues--discrepancies)
3. [Mitigations Applied](#3-mitigations-applied)
4. [Impact on Analysis](#4-impact-on-analysis)
5. [Sensitivity & Robustness Evidence](#5-sensitivity--robustness-evidence)
6. [Finals Analysis Filters (Post-Feedback)](#6-finals-analysis-filters-post-feedback)
7. [Appendices](#7-appendices)

---

## 1. Dataset Overview, Coverage & EDA Summary

### 1.1 Source data inventory

| # | Folder | File(s) | Raw rows | Loaded? | Used in analysis |
|---|--------|---------|----------|---------|------------------|
| 1 | `1.customer_transaction` | 7 yearly Excel (`1_1`–`1_7.orders-*_20260505.xlsx`) | 153,828 | ✅ | **Primary** — all EDA scripts 01–12 |
| 2 | `2.product_master` | `2_1.products_master_20260505.xlsx` | 167 variants | ✅ | Category lookup; COGS 65% null |
| 3 | `3.Discounts` | `3_1.discounts_export_20260505.csv` | 367 codes | ✅ | Taxonomy only — **no order join** |
| 4 | `4.Campaigns` | `4_1.Sessions by referrer_20260505.csv` | 137,033 | ❌ | Defined in config, never loaded |
| 5 | `5.Recharge_data` | 5 files (orders, checkout, churn, etc.) | ~1 year | ✅ | Churn detail; LTV uses Shopify tags |

**Canonical analytical tables** (after `01_load_and_merge.py`):

| Table | Rows | Grain | Key fields |
|-------|------|-------|------------|
| `orders.parquet` | **27,350** | 1 row / order (`Top Row = 1`) | order_id, customer_id, order_date, store, Price: Total (SGD), channel, is_subscription, Source |
| `lines.parquet` | **50,963** | 1 row / line item | order_id, Line: SKU, Line: Total (SGD), product_category |
| `customers.parquet` | **13,780** | 1 row / customer | total_orders, total_revenue, first_channel, RFM, days_to_second |

### 1.2 Temporal and store coverage

| Period | Orders | Unique customers | Notes |
|--------|--------|------------------|-------|
| 2020 | 2,847 | 1,696 | Full year; zero discounting |
| 2021 | 6,259 | 3,815 | Peak revenue (~S$848K combined SGD) |
| 2022 | 3,710 | 2,299 | Discounting introduced |
| 2023 | 2,253 | 1,399 | Revenue collapse |
| 2024 | 4,261 | 2,621 | Recovery; heavy discounting |
| 2025 | 6,407 | 4,107 | Highest order volume |
| 2026 (partial) | 1,610 | 1,230 | Jan–Mar only |

**Date range:** 2019-12-31 to 2026-03-30. **2019** excluded from cohort analyses (3 orders only).

| Store | Orders | Revenue (SGD, post-FX) |
|-------|--------|------------------------|
| SG | 16,041 | S$1,913,387 |
| MY | 11,309 | S$1,199,566 |
| HK | 2 | S$319 |

### 1.3 Key summary statistics (post-mitigation, SGD)

**Order revenue (all markets):**

| Statistic | Value |
|-----------|-------|
| Count | 27,350 orders |
| Mean | S$113.83 |
| Median | S$62.10 |
| Max | S$26,520 (wholesale-tagged, SG 2026) |

Mean ≈ 2× median → right-skewed distribution (expected; see DQ-04).

**Customers:**

| Statistic | Value |
|-----------|-------|
| Unique customers | 13,780 |
| One-time buyers (1 order) | **9,321 (67.6%)** |
| Repeat rate (≥2 orders) | **32.4%** |
| 60-day cohort retention | **18.1%** |
| Subscriber LTV / Non-subscriber | **S$532 / S$200** (+166%) |

**Discount depth (discounted orders only):**

| Depth | % of discounted orders |
|-------|----------------------|
| 20–30% | 25.3% |
| 90–100% | **15.3%** (see DQ-03) |

**Missingness (order-level):**

| Column | % missing | Notes |
|--------|-----------|-------|
| `Browser: UTM Source` | 94.9% | Channel uses Tags fallback (DQ-05) |
| `Tags` | 62.3% | Normal — not all orders tagged |
| `Line: Product Handle` | 49.3% on raw rows | Order-header rows (DQ-06) |

---

## 2. Data Issues & Discrepancies

Issues are ordered by severity. **DQ-01–DQ-12** = midterm due diligence. **DQ-13–DQ-15** = post-feedback / finals.

---

### DQ-01 — Multi-currency (CRITICAL → resolved)

**Issue:** SG (SGD), MY (MYR), HK (HKD) in one export with no transaction-date FX.

**Impact:** Summing raw `Price: Total` mixes currencies → inflated/wrong totals (MYR treated as SGD overstated MY ~3.3×).

**Mitigation:** Fixed rates at load in `00_config.py` / `01_load_and_merge.py`; `Currency` set to SGD for all orders.

**Evidence (post-FX):**

| Year | SG (SGD) | MY (SGD) | Combined |
|------|----------|----------|----------|
| 2021 | S$407K | S$441K | **S$848K peak** |
| 2025 | S$399K | S$10K | S$409K (97% SG) |

**Residual risk:** ±10% on absolute MY year-level revenue; **no impact** on repeat rates, retention %, or channel ratios.

---

### DQ-02 — Zero-revenue, zero-discount orders ⚠️ *Clarification below*

**Issue:** **336 orders** have `Price: Total = 0` **and** `Price: Total Discount = 0` (not paid orders, not 100%-off gifts).

**Evidence:** SG 198, MY 138; spike in 2021 (173 orders). Likely export/system placeholders or non-revenue events.

**Impact:**
- Inflate **order counts** and possibly `total_orders` per customer (+336 orders = **+1.2%**)
- Contribute **S$0** to revenue, LTV, and discount-dollar totals

**Severity:** MEDIUM (count); LOW (revenue)

#### ✅ DQ-02 clarification — Are zero orders included or excluded?

| Question | Answer |
|----------|--------|
| **Are they in `orders.parquet`?** | **YES — all 336 are included** (27,350 total orders in pipeline) |
| **Are they dropped in `01_load_and_merge.py`?** | **NO** — there is no filter removing zero-revenue orders |
| **What does mitigation mean?** | They stay in the dataset for **completeness and order-count metrics**, but contribute **$0 automatically** to revenue-based metrics (`total_revenue`, LTV, discount sums) because `Price: Total = 0` |
| **What does the "before/after" table mean?** | A **sensitivity illustration only** — shows what counts *would* be if you *chose* to exclude them. It is **not** what the pipeline does |

```
Pipeline (actual):     27,350 orders  →  all retained in orders.parquet
Sensitivity (hypothetical):  27,014 orders  →  if zero-rev/zero-disc removed (−336)
Revenue (either case):  unchanged — zero orders add S$0
```

**Repeat-rate edge case:** A customer with *only* zero-value orders would still count as having 1+ "orders" in `total_orders`, but would not meaningfully appear as a revenue-generating repeater unless they also have paid orders.

**We did not exclude DQ-02 orders** in the main pipeline. Finals filters (Section 6) address different issues (51%+ first-order discount, promo months, elite whey) — not DQ-02.

---

### DQ-03 — 100%-discount orders (free fulfillments)

**Issue:** **1,281 orders** with `Price: Total = S$0` but **positive** `Price: Total Discount` (full product value discounted away).

**Causes:** Referral rewards, subscription gifts, influencer/PR shipments — real shipments, zero revenue.

**Impact:** Inflates `discount / net_revenue` ratio; does **not** inflate LTV (S$0 revenue).

**Mitigation:** Report **49.6% of orders discounted** and **35.2% discounts as % of gross revenue** (2025), not misleading disc/net_rev (54.2%).

---

### DQ-04 — Wholesale / outlier orders

**Issue:** 45 orders > S$5,000 (e.g. MYR 114,240 in 2021; S$26,520 SG wholesale-tagged 2026).

**Impact:** Skews mean order value; limited effect on median or per-customer LTV.

**Mitigation:** Per-customer LTV aggregation; median used where stated; sensitivity Check 1 (Section 5).

---

### DQ-05 — UTM attribution gaps

**Issue:** 94.9% missing `Browser: UTM Source`.

**Impact:** "Direct / Organic" is default fallback — may include untracked paid traffic.

**Mitigation:** `classify_channel()` prioritises Tags (marketplace, subscription) then UTM; documented in `00_config.py`.

---

### DQ-06 — Order vs line-item row structure

**Issue:** Raw export mixes order-header and line rows; 49.3% of raw rows lack `Line: Product Handle`.

**Impact:** Row-count ≠ order-count if not deduplicated.

**Mitigation:** Orders: `Top Row = 1` + `order_id`. Lines: `Line: Type = 'Line Item'`. Product analyses filter non-null handles.

---

### DQ-07 — Subscription tag vs flag (negligible)

**Issue:** 2 of 3,267 subscription-tagged orders not flagged `is_subscription`.

**Mitigation:** Use programmatic `is_subscription` flag (99.94% agreement).

---

### DQ-08 — Marketplace subscription & repeat measurement

**Issue A:** 0% Shopify subscription rate for Marketplace — Shopee/Lazada subs not in Shopify.  
**Issue B:** 14.4% repeat rate may undercount cross-email Shopee repurchases.

**Mitigation:** Footnotes on all channel slides; LTV/repeat comparisons valid on identical Shopify basis.

---

### DQ-09 — Campaigns file not loaded

**Issue:** 137K session rows; no date, no customer/order ID — cannot join to orders.

**Mitigation:** Order-level UTM + Tags used instead (superior for conversion analysis).

---

### DQ-10 — Discount code not on order rows

**Issue:** No `discount_code` column in transactions; cannot join to `3.Discounts`.

**Mitigation:** Discount **depth** from `Price: Total Discount` amount (valid for LTV vs discount analysis).

---

### DQ-11 — Recharge temporal gap & ID mismatch

**Issue:** Recharge export Apr 2025–Apr 2026 only; Recharge customer ID ≠ Shopify customer ID.

**Mitigation:** Subscriber LTV from Shopify Tags (full history); churn reasons labelled 2025–2026 only; join Recharge↔Shopify on `shopify_order_id` (96% match).

---

### DQ-12 — Product master COGS gaps

**Issue:** `Cost per item` null for **109/167 variants (65%)**.

**Mitigation:** 40% gross margin **proxy** for business-value scenarios; labelled "profit proxy"; SKU coverage in `12_sku_margin_coverage.csv`.

---

### DQ-13 — POS not in Discounts export (post-feedback)

**Issue:** LP expected POS codes in `3.Discounts`. Verified: **zero** POS references in 367 codes.

**Evidence:** POS identified via `Source = 'pos'` in order export — **419 orders**, 99.3% discounted.

**Mitigation:** On-site vs off-site analysis uses order `Source`, not Discounts join (`12_pos_vs_web_*.csv`).

---

### DQ-14 — better-whey-protein-elite bulk distortion (post-feedback)

**Issue:** Unsustainable bulk product per LP — 200 customers, distorts product mix.

**Mitigation:** Excluded from finals-eligible cohort and SKU rankings (`12_finals_deep_dive.py`).

---

### DQ-15 — July & November promo months (post-feedback)

**Issue:** Birthday (July) and Black Friday (November) create atypical acquisition discount intensity.

**Mitigation:** Customers acquired in months 7 and 11 excluded from finals-eligible pool (**2,818 customers**).

---

## 3. Mitigations Applied

| ID | Issue | Mitigation | Where implemented |
|----|-------|------------|-------------------|
| DQ-01 | Multi-currency | FX to SGD at load | `00_config.py`, `01_load_and_merge.py` |
| DQ-02 | Zero-rev/zero-disc orders | **Retained in pipeline**; $0 contribution to revenue metrics | `01_load_and_merge.py` (no drop filter) |
| DQ-03 | 100%-off orders | Reformulated discount metrics | `05_channel_discount.py`, finals narrative |
| DQ-04 | Outliers | Per-customer LTV; median comparisons | All LTV scripts |
| DQ-05 | UTM null | Tags-based `classify_channel()` | `00_config.py` |
| DQ-06 | Row structure | Top Row / Line Item filters | `01_load_and_merge.py` |
| DQ-07 | Tag inconsistency | `is_subscription` flag | `01_load_and_merge.py` |
| DQ-08 | Marketplace limits | Footnotes | Channel analysis, finals docs |
| DQ-09 | Campaigns unused | Order-level UTM/Tags | `00_config.py` |
| DQ-10 | No discount code | Amount-based depth bins | `05_channel_discount.py` |
| DQ-11 | Recharge gap | Shopify tags for LTV; date scope on churn | `06_subscription_churn.py` |
| DQ-12 | COGS null | 40% margin proxy | `07_lens1`, `12_business_value_scenarios.csv` |
| DQ-13 | POS location | `Source='pos'` in orders | `12_finals_deep_dive.py` |
| DQ-14 | Elite whey | Exclude from finals pool | `12_finals_deep_dive.py` |
| DQ-15 | Promo months | Exclude Jul/Nov acquisitions | `12_finals_deep_dive.py` |

### Pipeline filters actually applied (`01_load_and_merge.py`)

| Filter | Rows removed | Purpose |
|--------|--------------|---------|
| `Top Row == 1` | Raw 153,828 → 27,350 orders | One row per order |
| Drop null `customer_id` / `order_date` | Small | Valid joins |
| `Payment: Status` ∈ paid, partially_refunded | Unpaid/cancelled | Revenue quality |
| `Order Fulfillment Status` ≠ restocked | Restocked | Not real sales |
| **DQ-02 zero orders** | **None** | **Not filtered** |

---

## 4. Impact on Analysis

### Findings that are robust

| Finding | Robustness | Main caveat |
|---------|------------|-------------|
| 67.6% one-time buyers | **High** | Count-based |
| 18.1% 60-day retention | **High** | FX-neutral |
| Subscriber LTV +166% | **High** | Shopify tags, full history |
| 2021 peak at zero discounting | **High** | Post-FX revenue |
| Marketplace LTV gap (S$115 vs S$198) | **Med–High** | DQ-08 footnote |
| Discount ↔ lower cohort quality | **Medium** | Correlation, not proven causation |

### What we cannot conclude

1. Causal effect of discounts on retention (confounding by segment/targeting).  
2. True Marketplace subscription rate on Shopee/Lazada.  
3. Per-customer **profit** (COGS 65% null).  
4. ROAS / marketing attribution (no order-level spend).  
5. Which **discount code** drove which order (DQ-10).  
6. Full pre-2025 churn reasons (Recharge 1-year window).

---

## 5. Sensitivity & Robustness Evidence

### Check 1 — Exclude outlier orders (> S$5,000)

Removing ~12 extreme orders: revenue −~4%; **repeat rate unchanged**; median order value S$62.10 → ~S$61.90.

### Check 2 — DQ-02 zero orders (hypothetical exclusion)

| Metric | With zero orders (pipeline) | If excluded (sensitivity only) |
|--------|----------------------------|------------------------------|
| Order count | **27,350** | 27,014 (−1.2%) |
| Total revenue | S$3,112,952 | **Identical** (S$0 contribution) |
| Per-customer LTV | Unchanged | Unchanged |

**Confirms:** DQ-02 orders are **in** the pipeline; exclusion is optional and immaterial for revenue findings.

### Check 3 — Subscription tag consistency

3,267 tagged vs 3,265 flagged → **99.94%** agreement.

### Check 4 — Discount metric reformulation (2025)

| Metric | Value | Use in report? |
|--------|-------|----------------|
| disc / net_revenue | 54.2% | ❌ Misleading |
| % orders with any discount | 49.6% | ✅ |
| discounts / gross revenue | 35.2% | ✅ |

### Check 5 — FX verification

`python EDA/verify_all.py` — **62 checks PASS** (MY/HK avg order values post-conversion).

---

## 6. Finals Analysis Filters (Post-Feedback)

Separate from DQ-02. Applied in `12_finals_deep_dive.py` for LP/professor-requested narrative (2022+ focus):

| Filter | Customers removed | Rationale |
|--------|-------------------|-----------|
| Acquisition before 2022-01-01 | (focus window) | Product portfolio shift |
| Acquired in **July or November** | 2,818 | Birthday + BFCM distortion |
| First-order discount **≥51%** | 1,240 | Experimental/gifting per LP |
| Bought **better-whey-protein-elite** | 200 | Bulk distortion per LP |
| **Finals-eligible pool** | **5,761** | After all filters |

Midterm metrics (27,350 orders, 13,780 customers) remain valid for full-history due diligence.

---

## 7. Appendices

### A. Scripts

| Script | Output |
|--------|--------|
| `01_load_and_merge.py` | `orders.parquet`, `lines.parquet`, `customers.parquet` |
| `02_data_quality.py` | `02_data_quality_report.txt`, yearly summaries |
| `05_channel_discount.py` | Channel quality, discount depth |
| `06_subscription_churn.py` | Churn, subscriber LTV |
| `12_finals_deep_dive.py` | `12_*.csv` finals outputs |
| `verify_all.py` | 62 automated checks |

### B. Related documents (not replaced)

| File | Role |
|------|------|
| `data_quality_checks.md` | Midterm DQ log — **preserved** |
| `FINAL_INSTRUCTOR_REPORT.md` | Finals EDA narrative |
| `deliverables/LushProtein_Orders_STTM.csv` | Source-to-target mapping (69 raw + 12 derived columns) |

### C. Key field reference

| Field | Grain | Notes |
|-------|-------|-------|
| `order_id` | Order | PK; from `ID` where Top Row = 1 |
| `customer_id` | Customer | FK; 13-digit Shopify ID |
| `order_date` | Order | Derived from `Processed At` |
| `Price: Total` | Order | Net revenue SGD post-FX |
| `channel` | Order | Derived — see DQ-05 |
| `Source` | Order | Raw — `web`, `pos`, etc. (DQ-13) |
| `Line: SKU` | Line | FK to product master |

---

*Prepared for ISSS603 PDF Data Quality Report · Group 1 · May 2026*
