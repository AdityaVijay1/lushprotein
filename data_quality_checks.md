# LushProtein — Data Quality Report

**Team:** Aditya Vijay, Emily Pham Vinh Tan, Saelin Lee, Shwe Tin Aung, Weilin Ang, Zhengfeng Toh
**Date:** May 2026
**Scope:** Shopify customer transaction data (2020–2026)
**Audience:** Course instructors (assessment of data due diligence)

---

## Table of Contents

1. [Dataset Overview and Coverage](#1-dataset-overview-and-coverage)
2. [Summary Statistics and Distributions](#2-summary-statistics-and-distributions)
3. [Data Issues Identified](#3-data-issues-identified)
4. [Mitigations Applied](#4-mitigations-applied)
5. [Impact Assessment on Analysis](#5-impact-assessment-on-analysis)
6. [Sensitivity and Robustness Checks](#6-sensitivity-and-robustness-checks)

---

## 1. Dataset Overview and Coverage

### Source Data

The raw data consists of Shopify order export files across multiple stores. After loading and merging in `EDA/01_load_and_merge.py`, the canonical dataset contains:

| Table | Rows | Key Fields |
|---|---|---|
| `orders.parquet` | **27,350 orders** | order_id, customer_id, order_date, store, revenue, discount, channel, is_subscription |
| `customers.parquet` | **13,780 customers** | customer_id, first/second order dates, total_orders, total_revenue, RFM fields |

### Temporal Coverage

| Period | Orders | Unique Customers | Notes |
|---|---|---|---|
| 2019 | 3 | 3 | Incomplete year — excluded from cohort analysis |
| 2020 | 2,847 | 1,696 | Full year, zero discounting |
| 2021 | 6,259 | 3,815 | Peak revenue year (S$1.86M SGD) |
| 2022 | 3,710 | 2,299 | First discounting introduced |
| 2023 | 2,253 | 1,399 | Revenue collapse year |
| 2024 | 4,261 | 2,621 | Recovery, heavy discounting |
| 2025 | 6,407 | 4,107 | Highest order volume, continued discounting |
| 2026 (partial) | 1,610 | 1,230 | Jan–Mar only; excluded from full-year analyses |

**Date range confirmed:** 2019-12-31 to 2026-03-30

### Store and Currency Coverage

| Store | Orders | Revenue (Own Currency) | Currency |
|---|---|---|---|
| SG | 16,039 | S$1,913,068 | SGD |
| MY | 11,309 | RM 3,958,566 | MYR |
| HK | 2 | HK$1,943 | HKD |

**Critical note:** The three stores use different currencies. **No FX conversion was available in the raw data.** Revenue figures across stores cannot be combined meaningfully.

**Mitigation:** All customer-level analyses (LTV, retention, RFM, cohort quality) are **restricted to SGD (SG store) orders only.** This is documented in `EDA/00_config.py` as the `SGD_STORE` constant.

---

## 2. Summary Statistics and Distributions

### Order Revenue Distribution (SG Store — SGD)

| Statistic | Value |
|---|---|
| Count | 16,039 orders |
| Mean | SGD 119.28 |
| Median | SGD 62.10 |
| 25th percentile | SGD 29.00 |
| 75th percentile | SGD 115.00 |
| Maximum | SGD 26,520.00 |
| Std deviation | SGD 405.16 |

The mean (S$119) is nearly double the median (S$62), indicating **right-skewed distribution** driven by a small number of high-value orders. This is expected in a consumer health brand context but the outliers require examination (see DQ-04).

### Order Revenue Distribution (MY Store — MYR)

| Statistic | Value |
|---|---|
| Count | 11,309 orders |
| Mean | MYR 350.04 |
| Median | MYR 183.07 |
| Maximum | MYR 114,240.00 |
| Std deviation | MYR 1,404.48 |

The MY store shows even higher skew — the maximum order of MYR 114,240 is likely a wholesale/bulk order and is more than 600× the median.

### Orders Per Customer Distribution

| Statistic | Value |
|---|---|
| Mean | 1.98 orders |
| Median | 1.0 orders |
| 75th percentile | 2.0 orders |
| Maximum | 667 orders |
| Customers with exactly 1 order | **9,321 (67.6%)** |
| Customers with 10+ orders | 268 (1.9%) |
| Customers with 20+ orders | 35 (0.3%) |

**Key insight:** 67.6% of customers made exactly one purchase. The extreme max (667 orders) is one customer, likely a reseller or test account.

### Discount Distribution (All Discounted Orders)

| Discount Depth | Count | % of Discounted Orders |
|---|---|---|
| 0–5% off | 871 | 10.2% |
| 5–10% off | 997 | 11.7% |
| 10–15% off | 1,161 | 13.6% |
| 15–20% off | 734 | 8.6% |
| 20–30% off | 2,159 | 25.3% |
| 30–40% off | 886 | 10.4% |
| 40–50% off | 167 | 2.0% |
| 50–60% off | 284 | 3.3% |
| 60–70% off | 329 | 3.9% |
| 70–80% off | 96 | 1.1% |
| 80–90% off | 31 | 0.4% |
| 90–100% off | **1,308** | **15.3%** |

The **15.3% of discounted orders at 90–100% off** is a notable spike that warrants its own issue entry (see DQ-03).

### Missing Values Summary

| Column | Null Count | % Missing | Notes |
|---|---|---|---|
| `Tags` | 17,026 | 62.3% | Many orders have no tag — this is normal; tags are manually or programmatically applied |
| `Browser: UTM Source` | 25,945 | 94.9% | Most orders lack UTM tracking (see DQ-05) |
| `Browser: UTM Medium` | 25,945 | 94.9% | Same as above |
| `Browser: UTM Campaign` | 25,978 | 95.0% | Same as above |
| `Browser: Referrer Domain` | 22,383 | 81.8% | Expected for direct/organic traffic |
| `Line: Product Handle` | 13,484 | 49.3% | Order-header rows without line items (see DQ-06) |
| `Shipping: Country` | 1,055 | 3.9% | Some orders missing shipping destination |
| `Order Fulfillment Status` | 207 | 0.8% | Minor gap |
| `second_order_date` (customers) | **9,321** | **67.6%** | Expected: 67.6% of customers are one-time buyers |

---

## 3. Data Issues Identified

### DQ-01 — Multi-Currency Without FX Conversion

**Description:** The dataset spans three stores (SG, MY, HK) using different currencies (SGD, MYR, HKD). The raw data contains no FX conversion rates, and the `Price: Total` field represents each store's local currency.

**Evidence:**
```
SG store: 16,039 orders, SGD 1,913,068 (SGD)
MY store: 11,309 orders, MYR 3,958,566 (MYR)
HK store:      2 orders, HKD 1,943     (HKD)
```

**Impact:** Combining revenue across stores without FX conversion would overstate or understate total revenue depending on exchange rates. At the time of writing, 1 MYR ≈ 0.30 SGD, so the MY revenue is approximately SGD 1.19M — but this conversion is not applied in the data.

**Severity:** HIGH — mixing currencies directly would produce nonsensical aggregate revenue figures.

**Mitigation:** All customer-level and revenue analyses are restricted to the SG store only. This is explicitly set in `EDA/00_config.py`:
```python
SGD_STORE = "SG"
# All retention, LTV, cohort and RFM analyses filter: orders[orders['store'] == SGD_STORE]
```

**Residual risk:** The SG store analysis excludes ~41% of all orders. Patterns found in SG may not generalise to MY/HK markets.

---

### DQ-02 — Zero-Revenue, Zero-Discount Orders

**Description:** 336 orders have `Price: Total = 0` and `Price: Total Discount = 0` simultaneously. These cannot be legitimate paid orders.

**Evidence:**
```
Count: 336
By store: SG (198), MY (138)
By channel: Direct/Organic (196), Subscription (124), Paid Social (8), Email (8)
By year: 2020 (4), 2021 (173), 2022 (70), 2023 (1), 2024 (14), 2025 (73), 2026 (1)
```

The 2021 cluster (173 orders) is suspicious — this is the highest-revenue year, and a large batch of zero-value orders in one year suggests a data export or system issue.

**Impact:**
- These orders inflate order counts and unique customer counts
- They contribute S$0 to revenue but appear as "orders placed"
- Customers with only zero-value orders would incorrectly appear as "active"

**Severity:** MEDIUM — significant in count (336) but zero revenue impact.

**Mitigation:** These orders are included in order-count metrics (for completeness) but contribute zero to all revenue-based metrics automatically. For retention analysis, a customer with only zero-value orders would not appear as a repeat buyer in a meaningful sense unless they also have non-zero orders.

**Before/After comparison:**
```
Total orders (incl. zero-value): 27,350
Total orders (excl. zero-value): 27,014  (difference: 336 = 1.2%)
Total revenue: unaffected (zero-value orders contribute S$0)
```

---

### DQ-03 — 100%-Discount Orders (Free Fulfillments)

**Description:** 1,281 orders have `Price: Total = S$0` but a positive `Price: Total Discount` — meaning the full product value was discounted away and the customer paid nothing.

**Evidence:**
```
Count: 1,281 orders
Total discount value applied: S$277,697
By year:
  2022:  4 orders
  2023: 38 orders
  2024: 448 orders
  2025: 741 orders
  2026:  52 orders
By channel:
  Direct / Organic: 975
  Subscription: 273
  Email: 21
  Marketplace: 12
  Affiliate: 2
```

**Likely causes (not dummy codes):**
- **Referral rewards:** LushProtein ran a social referral program (Social Snowball tags visible in order data). Referral reward orders are typically free products shipped to the referring customer.
- **Subscription welcome gifts:** First subscription orders sometimes come with a complimentary product.
- **Influencer/PR shipments:** Products sent to influencers with no charge.

These are **real product shipments** — not test/dummy entries. They represent actual cost-of-goods incurred by the business, but no revenue recognised.

**Impact on the "discount rate" metric:**
The headline "54.3% discount rate" in the original analysis is computed as `disc_amount / net_revenue`. This metric is inflated by 100%-discount orders because they add S$277,697 to the discount numerator while contributing S$0 to the revenue denominator.

**Better representation:**
```
2025 (% of gross revenue given as discounts):
  Revenue collected:   S$432,896
  Discounts given:     S$234,875  (incl. 100%-off orders)
  Gross potential:     S$667,771
  Discount %:          S$234,875 / S$667,771 = 35.2%
```

**Severity:** MEDIUM — does not affect retention or LTV calculations (zero-revenue orders are excluded from LTV). Does affect interpretation of the discount rate metric.

**Mitigation:** Use "% of orders with any discount" (49.6% in 2025) and "discounts as % of gross revenue" (35.2% in 2025) instead of the `disc/net_rev` ratio.

---

### DQ-04 — Outlier / Wholesale Orders

**Description:** 45 orders exceed SGD/MYR 5,000 in a single order — far above the median of SGD 62 / MYR 183.

**Evidence (top 5 orders):**

| Order ID | Date | Store | Revenue | Channel |
|---|---|---|---|---|
| 5988616077567 | 2021-11-25 | MY | MYR 114,240 | Direct/Organic |
| 5988536516863 | 2022-07-26 | MY | MYR 67,797 | Direct/Organic |
| 6725769625855 | 2026-03-04 | SG | SGD 26,520 | Direct/Organic (tagged: wholesale-sale) |
| 4992808091903 | 2020-06-27 | SG | SGD 23,468 | Subscription |
| 5988726178047 | 2021-03-02 | MY | MYR 21,769 | Direct/Organic |

The March 2026 SG order is explicitly tagged `wholesale-sale`, confirming these are B2B/reseller orders, not individual consumer purchases.

**Impact:**
- The MYR 114,240 order alone represents ~2.9% of MY store's total revenue
- If included in customer LTV calculations, these customers would appear as ultra-high-value outliers
- The MY store's mean order value (MYR 350) vs median (MYR 183) gap is largely explained by these orders

**Severity:** LOW for SG analysis (only 10 SG orders affected), MEDIUM for MY analysis.

**Mitigation:**
- All LTV and retention analyses use per-customer averages, which reduces the per-order outlier effect
- The 5-lens cohort analysis uses the median (not mean) for key comparisons where stated
- The wholesale-tagged SGD 26,520 SG order is included but is in 2026 (partial year excluded from full-year analyses)

---

### DQ-05 — UTM Attribution Gaps (Channel Classification)

**Description:** 94.9% of orders (25,945 of 27,350) are missing `Browser: UTM Source`. Channel classification is therefore based on order Tags, product handles, and a fallback rule — not direct UTM attribution.

**Evidence:**
```
Orders missing UTM Source:   25,945 (94.9%)
Orders missing UTM Medium:   25,945 (94.9%)
Orders missing UTM Campaign: 25,978 (95.0%)
```

**Channel classification logic** (from `EDA/00_config.py`):
```python
# Priority order:
# 1. Tags contain 'Subscription' → channel = 'Subscription'
# 2. Tags contain 'shopee'       → channel = 'Marketplace'
# 3. Tags contain 'lazada'       → channel = 'Marketplace'
# 4. UTM Source = 'facebook'     → channel = 'Paid Social'
# 5. Default                     → channel = 'Direct / Organic'
```

**Impact:**
- "Direct / Organic" is the default fallback — it includes all orders without any tracking tag
- Some paid search or paid social traffic that was not UTM-tagged will be misclassified as Direct/Organic
- This inflates the Direct/Organic customer count (6,920 customers) and its LTV metric (S$583)

**Severity:** MEDIUM — the Direct/Organic LTV figure may be overstated if it includes untracked paid traffic.

**Mitigation:**
- Marketplace channels (Shopee/Lazada) are identified via Tags, which are reliable (Tags are applied server-side by Shopify apps at order creation)
- Subscription orders are identified via Tags + `is_subscription` flag, which match in 3,263 of 3,265 cases (99.9% consistency)
- For the presentation, Direct/Organic findings are presented as "Direct/Own channels" to acknowledge the attribution ambiguity

---

### DQ-06 — Line-Item vs Order-Level Row Structure

**Description:** The raw Shopify export mixes order-header rows and order-line-item rows. 13,484 rows (49.3%) have a null `Line: Product Handle`, indicating they are order-level summary rows without an associated product.

**Evidence:**
```
Rows with null Line: Product Handle: 13,484 (49.3% of rows)
```

**Impact:**
- If all 27,350 rows are treated as distinct orders, some customers will appear to have made more orders than they actually did
- Product-level analyses (cross-sell, SKU loyalty) cannot use rows with null product handles

**Mitigation:**
- Order-level analyses (revenue, channel, retention) use `order_id` deduplication
- Product-level analyses filter to rows where `Line: Product Handle IS NOT NULL`
- The order count of 27,350 in the customer table is based on deduplicated `order_id` counts, not row counts

---

### DQ-07 — Subscription Tag vs Flag Consistency

**Description:** There is a minor inconsistency between the `Tags`-based subscription identification and the computed `is_subscription` boolean flag.

**Evidence:**
```
Orders tagged as Subscription/Recurring:    3,267
Orders flagged is_subscription = True:      3,265
Discrepancy (tagged but not flagged):           2
Discrepancy (flagged but not tagged):           0
```

**Impact:** Negligible. 2 orders out of 3,267 (0.06%) are misclassified. This has no meaningful effect on subscription analyses.

**Mitigation:** The `is_subscription` flag (derived programmatically from Tags) is used in all analyses. No further action required.

---

### DQ-08 — Marketplace Subscription Tracking Gap

**Description:** Shopify cannot track subscriptions that originate on third-party marketplace platforms (Shopee, Lazada). All 2,126 Marketplace customers show `pct_subscribed = 0.0%` in the channel quality analysis — but this reflects Shopify's data limitations, not necessarily the true subscription behaviour of these customers.

**Evidence:**
```
Marketplace channel orders:          3,268
Marketplace is_subscription = True:  0
```

**Impact:**
- The "0% subscription conversion from Marketplace" finding is technically correct within Shopify data
- However, Shopee and Lazada both have auto-delivery/subscription features on their own platforms
- If Marketplace customers subscribe on Shopee/Lazada, those recurring orders would not appear in Shopify at all — they would be entirely absent from the dataset

**Severity:** MEDIUM for the subscription conversion metric; LOW for the LTV and repeat rate metrics (which track all Shopify purchases regardless of origin channel).

**Mitigation:**
- LTV and repeat rate comparisons across channels remain valid (both use Shopify purchase history)
- Subscription conversion comparison must be annotated: "Shopify subscriptions only; Marketplace platforms operate independent subscription systems not tracked here"

---

## 4. Mitigations Applied

| Issue ID | Issue | Mitigation Applied | Where Applied |
|---|---|---|---|
| DQ-01 | Multi-currency | SG store only for all customer-level analysis | `EDA/00_config.py`, all lens scripts |
| DQ-02 | Zero-value orders | Included in counts; auto-excluded from revenue | All revenue calculations |
| DQ-03 | 100%-discount orders | Noted; discount metric reformulated as % of gross | `presentation.md` Slide 2 |
| DQ-04 | Wholesale outliers | Per-customer LTV (not per-order) reduces impact | All LTV metrics |
| DQ-05 | UTM attribution gaps | Tags-based channel assignment with documented priority | `EDA/00_config.py` channel classification |
| DQ-06 | Line-item structure | Product analyses filter to non-null handles | `EDA/04_product_analysis.py` |
| DQ-07 | Subscription tag inconsistency | `is_subscription` flag used; 2-order discrepancy negligible | `EDA/06_subscription_churn.py` |
| DQ-08 | Marketplace subscription gap | Annotated in channel quality analysis | `presentation.md` Slide 3 |

---

## 5. Impact Assessment on Analysis

### Which Findings Are Robust?

| Finding | Robustness | Key Caveat |
|---|---|---|
| 67.6% of customers are one-time buyers | **High** | Based on complete order counts; not affected by any DQ issue |
| 60-day retention rate: 18.1% | **High** | SG-only; uses deduplicated order dates |
| Subscriber LTV +186% vs non-subscriber | **High** | SG-only; large sample (1,095 vs 12,685) |
| Cross-sell LTV staircase | **Medium-High** | Observational — selection bias possible (loyal customers naturally buy more) |
| Marketplace LTV gap (S$117 vs S$583) | **Medium-High** | Subscription tracking gap acknowledged; LTV measurement is complete |
| Discount → lower cohort quality | **Medium** | Direct causal claim not proven; association is strong and consistent across multiple cuts |
| Revenue peaked 2021 at zero discounting | **High** | Directly from raw revenue figures; not model-dependent |
| "54.3% discount rate" | **Low (misleading)** | Reformulated to 35.2% of gross revenue and 49.6% of orders discounted |
| At Risk segment: S$1,072 avg LTV | **Medium** | RFM scoring is rank-based (robust to outliers); "At Risk" segment label is analyst-defined |

### What We Cannot Conclude From This Data

1. **Causation between discounts and lower retention** — The data shows a strong correlation but cannot rule out the alternative that LushProtein was targeting a different (lower-intent) customer segment in 2023–2024, independent of the discount strategy.

2. **True Marketplace customer subscription behaviour** — We cannot know whether Marketplace customers subscribe on Shopee/Lazada. The Shopify dataset has no visibility into their post-acquisition behaviour on those platforms.

3. **Profitability per customer** — The dataset contains revenue figures but not COGS, shipping costs, or marketing spend per customer. "LTV" in this analysis means *revenue-to-date*, not profit-to-date.

4. **Attribution of revenue to marketing spend** — 94.9% of orders lack UTM tracking, making it impossible to calculate ROAS or attribute revenue to specific campaigns.

---

## 6. Sensitivity and Robustness Checks

### Check 1: Does Excluding Outlier Orders Change the Key Findings?

**Method:** Remove all orders >SGD 5,000 from SG store and recalculate repeat rate and median LTV.

```python
# SG orders excl. outliers
sg_clean = orders[(orders['store']=='SG') & (orders['rev'] <= 5000)]
# sg_clean: 16,029 orders (10 removed)
# Revenue change: SGD 1,913,068 → SGD 1,827,948  (-4.5%)
# Repeat rate: unaffected (per-customer metric)
# Median order value: SGD 62.10 → SGD 61.90  (negligible change)
```

**Finding:** Excluding 10 outlier SG orders has minimal effect on per-customer metrics. The repeat rate and cohort retention findings are unchanged.

### Check 2: Does Including vs Excluding Zero-Value Orders Change Order Counts?

```
Total orders: 27,350
Excl. zero-rev/zero-disc orders: 27,014 (−336, −1.2%)
This does not change any per-customer LTV, repeat rate, or retention metric
because zero-value orders contribute S$0 to revenue.
```

### Check 3: Subscription Tag Consistency

```
Orders tagged as Subscription/Recurring:    3,267
Orders with is_subscription = True:         3,265
Agreement rate:                             3,263 / 3,265 = 99.94%
```

The 2-order discrepancy is inconsequential for all subscription analyses.

### Check 4: Discount Metric Reformulation

Three ways to measure the 2025 discount intensity:

| Metric | 2025 Value | Interpretation |
|---|---|---|
| `disc / net_revenue` (original chart) | 54.2% | Misleading — denominator already reduced |
| `% of orders with any discount` | 49.6% | Clear and directly interpretable |
| `disc / (rev + disc)` i.e. % of gross revenue | 35.2% | Most meaningful for business context |

**Recommendation:** Present the 35.2% and 49.6% figures in the deck. Retire the 54.2% ratio.

---

## Appendix A — Scripts That Generated This Report

| Script | Purpose |
|---|---|
| `EDA/01_load_and_merge.py` | Loads raw Excel files, merges, creates `orders.parquet` and `customers.parquet` |
| `EDA/02_data_quality.py` | Generates `02_data_quality_report.txt`, `02_orders_by_year.csv`, `02_revenue_by_month.csv` |
| `EDA/03_customer_retention.py` | Produces `03_cohort_retention_heatmap.csv`, `03_time_to_second_purchase.csv`, `03_rfm_segments.csv` |
| `EDA/05_discount_channel.py` | Produces `05_channel_quality.csv`, `05_discount_sensitivity.csv` |
| `EDA/06_subscription_churn.py` | Produces subscription churn analysis |
| `EDA/10_lens4_vintage_comparison.py` | Cohort quality comparison across acquisition years |

## Appendix B — Column Reference for Key Fields

| Column | Type | Notes |
|---|---|---|
| `order_id` | int64 | Shopify order ID — unique (0 duplicates confirmed) |
| `customer_id` | int64 | Shopify customer ID — no nulls |
| `order_date` | datetime (UTC) | Timezone-aware; all converted to UTC for consistency |
| `store` | string | "SG", "MY", "HK" — proxy for currency |
| `Price: Total` | float | Net revenue after discounts — in store's local currency |
| `Price: Total Discount` | float | Total discount applied — zero if no discount |
| `channel` | string | Derived from Tags + UTM (see DQ-05) |
| `is_subscription` | bool | Derived from Tags; 99.94% consistent with raw Tags |
| `has_discount` | bool | Derived: `Price: Total Discount > 0` |
| `Tags` | string | Raw Shopify order tags — 62.3% null |
| `Line: Product Handle` | string | Product identifier — null for order-header rows |
