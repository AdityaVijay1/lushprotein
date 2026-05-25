# LushProtein — Data Quality & Due Diligence Report (Final)

**Team:** Group 1 — Aditya Vijay, Emily Pham Vinh Tan, Saelin Lee, Shwe Tin Aung, Weilin Ang, Zhengfeng Toh
**Date:** May 2026
**Scope:** Shopify customer transactions (2020–Q1 2026), SG + MY + HK, all revenue in **SGD** after FX conversion
**Audience:** Course instructors (ISSS603 — assessment of data due diligence)

> **This is the single reference document for the PDF Data Quality Report.**
> Midterm narrative file `data_quality_checks.md` is preserved unchanged for teammate reference.
> Finals-layer drops (DQ-02, DQ-03, DQ-04) are applied **only** in `EDA/12_finals_deep_dive.py`.
> Midterm pipeline scripts 01–11 and the base 27,350-order parquet are unmodified.

**Currency assumption:** 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, applied once at load in `EDA/01_load_and_merge.py`).

---

## Table of Contents

1. [Dataset Overview and Coverage](#1-dataset-overview-and-coverage)
2. [Summary Statistics and Distributions](#2-summary-statistics-and-distributions)
3. [Data Issues Identified](#3-data-issues-identified)
4. [Mitigations Applied](#4-mitigations-applied)
5. [Impact Assessment on Analysis](#5-impact-assessment-on-analysis)
6. [Sensitivity and Robustness Checks](#6-sensitivity-and-robustness-checks)
7. [LushProtein Feedback — Applied Analysis Filters](#7-lushprotein-feedback--applied-analysis-filters)
8. [Appendices](#8-appendices)

---

## 1. Dataset Overview and Coverage

### All Source Datasets — Complete Inventory

| # | Folder | File(s) | Rows | Loaded? | Used in Scripts | Notes |
|---|---|---|---|---|---|---|
| 1 | `1.customer_transaction` | 7 yearly Excel files (`1_1`–`1_7.orders-*_20260505.xlsx`) | 153,828 raw rows → 27,350 orders + 50,963 line items | ✅ YES | All EDA scripts 01–12 | Primary source. FX conversion applied at load. |
| 2 | `2.product_master` | `2_1.products_master_20260505.xlsx` | 167 variants | ✅ YES | `01_load_and_merge.py`, `02_data_quality.py` | Saved to parquet. Category classification, COGS (65% null) not used. |
| 3 | `3.Discounts` | `3_1.discounts_export_20260505.csv` | 367 codes | ✅ YES | `01_load_and_merge.py`, `05_channel_discount.py` | Discount code taxonomy. Cannot link to individual orders — no discount code column in transactions. |
| 4 | `4.Campaigns` | `4_1.Sessions by referrer_20260505.csv` | **137,033 rows** | ⚠️ **DEFINED BUT NOT LOADED** | **NONE** | `CAMPAIGNS_FILE` defined in `00_config.py` but never imported. Has no date column or customer/order ID. |
| 5a | `5.Recharge_data` | `5_1.orders_combined` | 1,215 orders | ✅ YES | `06_subscription_churn.py` | Apr 2025–Apr 2026 only. Avg order S$81 SGD. |
| 5b | `5.Recharge_data` | `5_2.order_items_checkout` | 1,094 line items | ✅ YES | `04_product_analysis.py`, `06_subscription_churn.py` | First-checkout SKU ranking. |
| 5c | `5.Recharge_data` | `5_3.subscribers_reactivated` | 50 customers | ✅ YES | `06_subscription_churn.py` | Win-back cohort. |
| 5d | `5.Recharge_data` | `5_4.subscriptions_churned` | 526 records | ✅ YES | `06_subscription_churn.py` | Cancellation reasons and churn cycle. |
| 5e | `5.Recharge_data` | `5_5.order_items_recurring` | 650 line items | ✅ YES | `04_product_analysis.py`, `06_subscription_churn.py` | Renewal SKU loyalty analysis. |

### Canonical Output Tables (post-`01_load_and_merge.py`)

| Table | Rows | Key Fields |
|---|---|---|
| `orders.parquet` | **27,350 orders** | order_id, customer_id, order_date, store, Price: Total (SGD), Price: Total Discount (SGD), channel, is_subscription |
| `lines.parquet` | **50,963 line items** | order_id, customer_id, product_category, Line: Price/Total (SGD) |
| `customers.parquet` | **13,780 customers** | customer_id, first/second order dates, total_orders, total_revenue (SGD), RFM fields |
| `products.parquet` | **167 variants** | Handle, Variant SKU, prices by market, Status, Cost per item |
| `discounts.parquet` | **367 codes** | Name, Value, Value Type, Times Used, Status |
| `rc_orders.parquet` | **1,215 orders** | metric_date, shopify_order_id, order_type, order_total (SGD est.) |
| `rc_checkout.parquet` | **1,094 items** | product_title, variant_title, quantity, customer_id (Recharge ID) |
| `rc_reactivated.parquet` | **50 records** | customer_id (Recharge ID), first_activation, reactivated_date |
| `rc_churned.parquet` | **526 records** | customer_id, cancellation_reason, subscription tenure |
| `rc_recurring.parquet` | **650 items** | product_title, variant_title, purchase_type |

### Temporal Coverage

| Period | Orders | Unique Customers | Notes |
|---|---|---|---|
| 2019 | 3 | 3 | Incomplete year — excluded from cohort analysis |
| 2020 | 2,847 | 1,696 | Full year, zero discounting |
| 2021 | 6,259 | 3,815 | Peak revenue year (S$848K combined SGD) |
| 2022 | 3,710 | 2,299 | First discounting introduced |
| 2023 | 2,253 | 1,399 | Revenue collapse year |
| 2024 | 4,261 | 2,621 | Recovery, heavy discounting |
| 2025 | 6,407 | 4,107 | Highest order volume, continued discounting |
| 2026 (partial) | 1,610 | 1,230 | Jan–Mar only; excluded from full-year analyses |

**Date range confirmed:** 2019-12-31 to 2026-03-30

### Store and Currency Coverage

| Store | Orders | Revenue (Own Currency) | FX Rate | Revenue (SGD equivalent) |
|---|---|---|---|---|
| SG | 16,041 | S$1,913,387 | 1.000 | **S$1,913,387** |
| MY | 11,309 | RM 3,958,566 | ÷ 3.30 | **S$1,199,566** |
| HK | 2 | HK$1,943 | ÷ 6.10 | **S$319** |
| **All markets** | **27,350** | — | — | **S$3,112,952 total SGD** |

**Critical note:** Three stores use three currencies. Raw data contains no FX rates.

**Mitigation applied (May 2026):** 5-year average exchange rates (2020–2026) applied at data load time in `EDA/01_load_and_merge.py`:
- `1 SGD = 3.30 MYR` → MYR ÷ 3.30 = SGD equivalent
- `1 SGD = 6.10 HKD` → HKD ÷ 6.10 = SGD equivalent

**Known limitations:**
1. SGD/MYR moved between ~3.0 and ~3.5 over 2020–2026. Early MY revenue may be off ±10%.
2. MY market was effectively dormant by 2025 (S$9,617 SGD vs S$441,022 in 2021). Combined 2025 totals are 97% SG-driven.
3. HK store (2 orders, S$319 SGD) is immaterial.

**Post-conversion market revenue by year:**
```
Year  SG (SGD)    MY (SGD)    Total
2020  S$286,181   S$170,771   S$456,952
2021  S$406,908   S$441,022   S$847,930  ← combined peak
2022  S$385,076   S$362,510   S$747,587
2023  S$101,135   S$80,902    S$182,038
2024  S$150,308   S$134,663   S$284,971
2025  S$399,216   S$9,617     S$409,152  ← MY market effectively dormant
```

**Implemented in:** `EDA/00_config.py` (`FX_RATES_TO_SGD` dict), `EDA/01_load_and_merge.py`

### Key Summary Statistics (post-mitigation, SGD — full 27,350-order pipeline)

**Order revenue (all markets, SGD):**

| Statistic | Value (All Markets, SGD) | SG-only (SGD) |
|---|---|---|
| Count | 27,350 orders | 16,041 orders |
| Mean | S$113.83 | S$119.28 |
| Median | S$62.10 | S$62.10 |
| 25th percentile | S$29.00 | — |
| 75th percentile | S$115.00 | — |
| Maximum | S$26,520.00 (wholesale-tagged, SG 2026) | — |
| Std deviation | S$405.16 | — |

Mean ≈ 2× median → right-skewed distribution expected in consumer health context (see DQ-04).

**Customers:**

| Statistic | Value |
|---|---|
| Unique customers | 13,780 |
| One-time buyers (1 order) | **9,321 (67.6%)** |
| Repeat rate (≥2 orders) | **32.4%** |
| 60-day cohort retention | **18.1%** |
| Subscriber LTV / Non-subscriber LTV | **S$532 / S$200 (+166%)** |

**Finals analysis pool (after DQ-02/03/04 drops + all LP filters):**

| Stage | Orders / Customers |
|---|---|
| Base pipeline | 27,350 orders · 13,780 customers |
| After DQ-02 drop (zero rev + zero disc) | −336 → 27,014 |
| After DQ-03 drop (100%-discount) | −1,281 → 25,733 |
| After DQ-04 drop (wholesale/outlier) | −78 → **25,658** retained |
| After LP-F03 (2022+ only) | customer-level filter |
| After LP-F01/02/04 (elite, promo months, 51%+) | **6,353 finals-eligible customers** |

---

## 2. Summary Statistics and Distributions

### Order Revenue Distribution (All Markets — SGD after FX conversion)

| Statistic | Value (All Markets, SGD) | SG-only (SGD) |
|---|---|---|
| Count | 27,350 orders | 16,041 orders |
| Mean | SGD 113.83 | SGD 119.28 |
| Median | SGD 62.10 | SGD 62.10 |
| 25th percentile | SGD 29.00 | — |
| 75th percentile | SGD 115.00 | — |
| Maximum | SGD 26,520.00 | — |
| Std deviation | SGD 405.16 | — |

The mean (S$114) is nearly double the median (S$62), indicating **right-skewed distribution** driven by a small number of high-value orders. This is expected in a consumer health brand context but the outliers require examination (see DQ-04).

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

Issues are ordered by severity. DQ-01 through DQ-12 are data due-diligence findings. LP-F01–F04 (see Section 7) are LushProtein-directed analytical scope filters, not data errors.

---

### DQ-01 — Multi-Currency: Fixed FX Conversion Applied

**Description:** The dataset spans three stores (SG, MY, HK) using different currencies (SGD, MYR, HKD). The raw data contains no FX conversion rates.

**Evidence:**
```
SG store: 16,041 orders, SGD 1,913,387 (SGD)
MY store: 11,309 orders, MYR 3,958,566 (MYR → SGD equivalent: S$1,199,566)
HK store:      2 orders, HKD 1,943     (HKD → SGD equivalent: S$319)
```

**Severity:** HIGH — mixing currencies without conversion produces nonsensical revenue totals.

**Mitigation Applied (May 2026):**
5-year average exchange rates (2020–2026) are applied at data load time in `EDA/01_load_and_merge.py`:
```python
FX_RATES_TO_SGD = {
    "SG": 1.0,
    "MY": 1.0 / 3.30,   # 1 MYR = 0.3030 SGD  (5-yr avg: 1 SGD = 3.30 MYR)
    "HK": 1.0 / 6.10,   # 1 HKD = 0.1639 SGD  (5-yr avg: 1 SGD = 6.10 HKD)
}
# Applied to Price: Total, Price: Total Discount, Price: Total Shipping
# Currency column set to "SGD" for all orders after conversion
```

**Assumption stated explicitly:**
- Rates represent the **5-year average (2020–2026)** and do not vary by transaction date
- Actual MYR/SGD rate moved between ~3.0 and ~3.5 over the period → individual year figures may deviate up to ±10% from the average-rate conversion
- For **relative comparisons** (repeat rates, LTV uplift %, cohort retention), the FX rate has no impact — these are count-based or ratio-based metrics

**Residual risk:** The fixed-rate assumption introduces ≤10% error on absolute MY revenue figures. MY market is dominant in 2020–2022 but almost absent in 2025, so combined 2025 figures are 97% SG-driven.

---

### DQ-02 — Zero-Revenue, Zero-Discount Orders *(Dropped in finals analysis)*

**Description:** 336 orders have `Price: Total = 0` **and** `Price: Total Discount = 0` simultaneously. These cannot be legitimate paid orders — they carry no commercial value and no customer cost.

**Evidence:**
```
Count: 336
By store: SG (198), MY (138)
By channel: Direct/Organic (196), Subscription (124), Paid Social (8), Email (8)
By year: 2020 (4), 2021 (173), 2022 (70), 2023 (1), 2024 (14), 2025 (73), 2026 (1)
```

The 2021 cluster (173 orders) is suspicious — this is the highest-revenue year, and a large batch of zero-value orders suggests a data export or system placeholder event.

**Impact:**
- Inflate order counts and unique customer counts (+336 orders = +1.2%)
- Contribute S$0 to all revenue, LTV, and discount metrics automatically
- Customers with only zero-value orders appear as "active" without any revenue contribution

**Severity:** MEDIUM (count); LOW (revenue)

**Midterm pipeline behaviour (01–11):** These 336 orders are **retained** in `orders.parquet` (total: 27,350). Midterm scripts 01–11 and the midterm PDF deliverables reference the 27,350-order base.

**Finals analysis (12_finals_deep_dive.py):** **DROPPED** — LushProtein confirmed these orders serve no analytical purpose other than inflating counts. Applying this drop in the finals layer only preserves midterm deliverable accuracy.

```
Midterm pipeline:   27,350 orders  →  orders.parquet (unchanged)
After DQ-02 drop:   27,014 orders  (−336, finals layer only)
Revenue impact:     S$0  (zero-value orders add nothing)
```

---

### DQ-03 — 100%-Discount Orders (Free Fulfilments) *(Dropped in finals analysis)*

**Description:** 1,281 orders have `Price: Total = S$0` but a positive `Price: Total Discount` — meaning the full product value was discounted away and the customer paid nothing. These are real product shipments, but zero revenue is recognised.

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

**Impact on the discount-rate metric:**
The correct discount metric is "discounts as % of gross revenue" — not disc/net_rev. The disc/net_rev ratio inflates the figure because 100%-discount orders contribute to the numerator while adding S$0 to the denominator.

```
2025:
  Revenue collected (net):  S$409,152
  Discounts given:          ~S$220,000  (incl. 100%-off orders)
  Gross potential:          ~S$629,000
  Correct discount rate:    35.2% of gross revenue  (not 54.2% disc/net_rev)
```

**Severity:** MEDIUM — does not affect retention or LTV calculations, but distorts the raw disc/net_rev ratio.

**Midterm pipeline behaviour (01–11):** Retained in `orders.parquet`. Discount metrics reformulated to use % of gross revenue (not disc/net_rev).

**Finals analysis (12_finals_deep_dive.py):** **DROPPED** per LushProtein request. Free fulfilments are not consumer purchase behaviour and should not influence LTV, repeat-rate, or loyalty analysis conclusions.

```
After DQ-02 + DQ-03 drops:   25,733 orders retained  (−1,617 total)
Revenue impact:               S$0  (all dropped orders have net rev = S$0)
```

---

### DQ-04 — Wholesale / Outlier Orders *(Dropped in finals analysis)*

**Description:** A subset of orders are B2B/reseller bulk purchases. These are identified by either an explicit Shopify tag (`wholesale-sale`) or an anomalously high order value (> S$5,000). Including these in consumer LTV analysis distorts per-customer metrics.

**Evidence (top 5 orders by value):**

| Order ID | Date | Store | Revenue | Channel | Tag |
|---|---|---|---|---|---|
| 5988616077567 | 2021-11-25 | MY | MYR 114,240 (~S$34,618) | Direct/Organic | none |
| 5988536516863 | 2022-07-26 | MY | MYR 67,797 (~S$20,544) | Direct/Organic | none |
| 6725769625855 | 2026-03-04 | SG | SGD 26,520 | Direct/Organic | **wholesale-sale** |
| 4992808091903 | 2020-06-27 | SG | SGD 23,468 | Subscription | none |
| 5988726178047 | 2021-03-02 | MY | MYR 21,769 (~S$6,597) | Direct/Organic | none |

The March 2026 SG order is explicitly tagged `wholesale-sale`, confirming these are B2B/reseller orders. The untagged MY orders with 600×+ the median order value are almost certainly the same.

```
Orders tagged 'wholesale-sale':      65
Orders with Price: Total > S$5,000:  14
Combined (union):                    78 unique orders
By year: 2020 (2), 2021 (4), 2022 (6), 2025 (36), 2026 (30)
```

**Impact:**
- The MYR 114,240 order alone represents ~2.9% of MY store's total revenue
- Including these in LTV calculations makes those customers appear as ultra-high-value outliers
- Median order value (S$62.10) is robust; mean (S$113.83) is inflated by these orders
- The MY store's mean order (MYR 350) vs median (MYR 183) gap is largely explained by these orders

**Severity:** LOW for SG median/repeat-rate analysis; MEDIUM for MY revenue totals and mean LTV.

**Midterm pipeline behaviour (01–11):** Retained. Per-customer LTV aggregation limits per-order impact; median used in key comparisons.

**Finals analysis (12_finals_deep_dive.py):** **DROPPED** — any order tagged `wholesale-sale` **OR** with `Price: Total > S$5,000`. LP confirmed both criteria are correct signals for B2B/non-consumer orders.

```
After DQ-02 + DQ-03 + DQ-04 drops:   25,658 orders retained  (−1,692 total unique)
```

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
- This inflates the Direct/Organic customer count (6,920 customers) and its LTV metric

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

**Mitigation:** The `is_subscription` flag (derived programmatically from Tags) is used in all analyses.

---

### DQ-08 — Marketplace Subscription Tracking Gap and Repeat Rate Measurement

**Description:** Two related limitations affect the Marketplace channel quality metrics.

**Part A — Subscription tracking gap:**
Shopify cannot track subscriptions that originate on third-party marketplace platforms (Shopee, Lazada). All 2,126 Marketplace customers show `pct_subscribed = 0.0%` in the channel quality analysis — but this reflects Shopify's data limitations, not necessarily the true subscription behaviour of these customers.

**Evidence:**
```
Marketplace channel orders:          3,268
Marketplace is_subscription = True:  0
```

Shopee and Lazada both have auto-delivery/subscription features on their own platforms. If Marketplace customers subscribe on those platforms, those recurring orders do not appear in Shopify at all.

**Part B — Repeat rate measurement scope:**
The 14.4% marketplace repeat rate is computed as 306 customers with ≥2 Shopify-visible orders ÷ 2,126 marketplace-first customers. A "repeat" is any second Shopify order regardless of channel.

```
Marketplace customers:                 2,126
Marketplace repeaters (2+ Shopify):      306
Repeat rate:                           14.4%   (306 / 2,126)
Total marketplace-tagged orders:       3,268
Avg orders per marketplace customer:    1.54
```

The fact that there are 3,268 marketplace-tagged orders across 2,126 customers confirms that repeat Shopee/Lazada orders ARE being captured in Shopify via the integration — at least partially.

**Potential sources of undercount in the 14.4%:**
1. A customer who buys on Shopee with email A and then on Shopee again with email B gets two separate Shopify customer records — the repeat is not linked.
2. If the Shopify–Shopee/Lazada integration misses some repeat orders, those are invisible.

**Impact:**
- The **0% Shopify subscription rate** for Marketplace is technically correct within Shopify data; the true marketplace subscription rate on Shopee/Lazada is unknown
- The **14.4% repeat rate** may be a modest undercount; but even if higher, customers who only repeat on Shopee/Lazada without entering the Shopify ecosystem have zero CRM visibility — this strengthens, not weakens, the channel quality argument
- The **relative comparison** (14.4% Marketplace vs 33.5% Direct/Organic) is valid: all channels are measured on identical Shopify-data basis

**Severity:** MEDIUM for the subscription conversion metric and repeat rate headline; LOW for the LTV comparison and the strategic conclusion.

**Mitigation:**
- Subscription comparison annotated: "Shopify subscriptions only; Marketplace platforms operate independent subscription systems not tracked here"
- Repeat rate annotated: "Reflects customers with 2+ Shopify-visible orders. Repeat purchases exclusively on Shopee/Lazada are not captured."

---

### DQ-09 — Campaigns Dataset Not Loaded (4.Campaigns)

**Description:** `4_1.Sessions by referrer_20260505.csv` (137,033 rows, 52 MB) is the largest file in the dataset. It is referenced as `CAMPAIGNS_FILE` in `EDA/00_config.py` but is **never imported or analyzed in any EDA script**.

**What it contains:**
```
Columns: Referrer source, Referrer name, Session city, UTM campaign,
         UTM medium, UTM source, Landing page path, Landing page URL,
         Online store visitors, Sessions

Top UTM sources (by sessions):
  facebook      58,322 sessions
  meta          15,706 sessions
  affiliate      4,798 sessions
  shopify_email  4,608 sessions
  snowball       3,879 sessions

Total sessions: 246,909 | Unique visitors: 220,244
```

**Critical limitations of this dataset:**
1. **No date column** — 5 years of traffic collapsed into cumulative counts; time-trending is impossible
2. **No customer or order ID** — cannot compute true conversion rates (sessions → orders)
3. **Each row is a unique dimension combination** — useful for proportional channel mix, not for joining

**Severity:** LOW for the core findings (retention, LTV, cohort analysis are all order-based). MEDIUM for any claim about acquisition channel effectiveness.

**Mitigation:** The `Browser: UTM Source` field in the order-level data provides the same UTM information at the order level with full customer linkage. This is what the channel classification in `EDA/00_config.py` uses and is superior to the campaign file for analysis purposes.

---

### DQ-10 — Discount Code Not Linked to Individual Orders

**Description:** The `3.Discounts` dataset contains 367 discount codes with redemption counts. However, the Shopify order export does NOT include a "discount code used" column at the order level. The `Price: Total Discount` column shows the discount amount, but not which code was applied.

**Evidence:**
```
Raw order columns searched for "discount code": NONE FOUND
Available: Price: Total Discount (amount), Line: Discount (line-level amount)
Missing:   which_discount_code_was_applied (does not exist in export)

Discounts dataset has: Name, Value, Times Used In Total
But these CANNOT be joined to orders.parquet on any common key.
```

**Impact:**
- The discount taxonomy analysis (`EDA/05_channel_discount.py` Section C) is a **standalone** analysis of the Discounts table — it shows what codes exist and how many total times they were used, but cannot identify which specific customers or orders used them
- The `SGAFF100` code (−100%, 88 uses) is confirmed real — these are affiliate codes where the product is paid by the affiliate, not the customer
- Discount sensitivity analysis uses `has_discount` (True/False) and the discount dollar amount, which is still valid for measuring discount impact on LTV

**Severity:** MEDIUM. The key discount finding (full-price buyers have 2× repeat rate vs 50%+ discounted buyers) remains valid because it uses the discount amount, not the code.

**Mitigation:** Classify discount depth by amount (as % of order value) rather than code. This is what the analysis does in `EDA/05_channel_discount.py` Section B.

---

### DQ-11 — Recharge Data Temporal Coverage and Customer ID Mismatch

**Description:** The Recharge subscription platform exports only cover **April 2025 to April 2026** (1 year). LushProtein has been running subscriptions since at least 2021 (based on Shopify order tags). Additionally, Recharge customer IDs are different from Shopify customer IDs.

**Evidence:**
```
Recharge date range: 2025-04-08 to 2026-04-07 (exactly 1 year)
Shopify orders with is_subscription tag: 3,265 orders, 1,095 unique customers
Recharge unique customers: 575 (Recharge-internal IDs, 8-digit)
Shopify customer IDs: 13-digit numbers

Cross-reference on shopify_order_id (the correct join key):
  Recharge rows: 1,215
  Matched to Shopify orders: 1,163 (96%)
  Unmatched 52 rows: likely Apr 1-7 2026 gap between export dates

Customer ID JOIN: ZERO matches (different ID systems — Recharge vs Shopify)
```

**Impact:**
- `06_subscription_churn.py` Section A (subscriber vs non-subscriber LTV) uses **Shopify tags** — correctly captures all 1,095 subscribers, not just the 575 in Recharge → **VALID**
- `06_subscription_churn.py` Sections B–D use **Recharge data directly** — represent the most recent year only
- Cancellation reasons (526 churns) are from 2025–2026 only — may not represent earlier churn behavior
- The 520 "missing" subscribers (1,095 Shopify − 575 Recharge) are likely customers whose subscriptions pre-date April 2025 or used the old Yotpo Subscriptions platform

**Severity:** MEDIUM for subscription churn/tenure analysis. LOW for LTV and retention analysis (which use Shopify data).

**Mitigation:**
- Subscription LTV comparison uses Shopify data → unaffected
- Churn analysis is explicitly described as "from the Recharge export (Apr 2025–Apr 2026)" in presentation notes
- Join on `shopify_order_id` (96% match) is the correct approach for Recharge ↔ Shopify validation

---

### DQ-12 — Product Master COGS Not Available

**Description:** The `2.product_master` file contains a `Cost per item` column, but **109 of 167 variants (65%) have null cost data**. This prevents gross margin calculation at the SKU level.

**Evidence:**
```
Products master: 167 variant rows
  active:   34 SKUs
  draft:    22 SKUs
  archived:  1 SKU

Cost per item:
  Non-null: 58/167 (35%)
  Null:    109/167 (65%)
  Range of available COGS: not surfaced (sensitive field)
```

**Impact:** All margin calculations in the analysis use an estimated 40% gross margin proxy (`MARGIN_RATE = 0.40` in `EDA/12_finals_deep_dive.py`). This is an assumption, not a data-derived figure.

**Severity:** LOW for relative comparisons. MEDIUM for absolute profit figures in business-value scenarios.

**Mitigation:** The 40% gross margin assumption is disclosed in all scripts. Profit figures are labelled "profit proxy" throughout. Revenue-based findings are unaffected.

---

## 4. Mitigations Applied

| Issue ID | Issue Summary | Mitigation | Where Implemented |
|---|---|---|---|
| DQ-01 | Multi-currency (SG/MY/HK) | Fixed FX applied at load (1 SGD = 3.30 MYR, 6.10 HKD); all in SGD | `00_config.py`, `01_load_and_merge.py` |
| DQ-02 | Zero-rev + zero-disc orders (336) | **Retained in midterm pipeline (01–11). DROPPED in finals layer.** | Midterm: retained. Finals: `12_finals_deep_dive.py` |
| DQ-03 | 100%-discount / free fulfilment orders (1,281) | **Retained in midterm pipeline. DROPPED in finals layer per LP request.** | Midterm: retained. Finals: `12_finals_deep_dive.py` |
| DQ-04 | Wholesale/outlier orders (78) | **Retained in midterm pipeline. DROPPED in finals layer (wholesale tag OR > S$5,000) per LP confirmation.** | Midterm: retained. Finals: `12_finals_deep_dive.py` |
| DQ-05 | UTM attribution 94.9% null | Tags-based `classify_channel()` with documented priority | `00_config.py` |
| DQ-06 | Mixed order/line-item row structure | `Top Row = 1` for orders; `Line: Type = Line Item` for lines | `01_load_and_merge.py` |
| DQ-07 | Subscription tag vs flag (2 orders off) | `is_subscription` flag used; negligible | `01_load_and_merge.py` |
| DQ-08 | Marketplace subscription tracking gap | Annotated in channel quality analysis | `05_channel_discount.py`, finals docs |
| DQ-09 | Campaigns dataset not loaded | Order-level UTM/Tags used instead (superior join key) | `00_config.py` |
| DQ-10 | Discount code not on order rows | Amount-based discount depth bins used | `05_channel_discount.py` |
| DQ-11 | Recharge temporal gap + ID mismatch | Subscription LTV from Shopify Tags (full history); churn stats noted as 2025–2026 | `06_subscription_churn.py` |
| DQ-12 | COGS 65% null | 40% gross margin proxy; labelled "profit proxy" | `12_finals_deep_dive.py`, business-value scenarios |

**Pipeline filters applied in `01_load_and_merge.py` (midterm base):**

| Filter | Rows Removed | Purpose |
|---|---|---|
| `Top Row == 1` | Raw 153,828 → 27,350 orders | One row per order |
| Drop null `customer_id` / `order_date` | Small | Valid joins |
| `Payment: Status` ∈ paid, partially_refunded | Unpaid/cancelled | Revenue quality |
| `Order Fulfillment Status` ≠ restocked | Restocked | Not real sales |
| DQ-02 zero orders | **None** | Not filtered in midterm |

**Additional drops in `12_finals_deep_dive.py` (finals layer):**

| Drop | Orders Removed | Retained |
|---|---|---|
| DQ-02: zero rev + zero disc | −336 | 27,014 |
| DQ-03: 100%-discount | −1,281 | 25,733 |
| DQ-04: wholesale tag OR > S$5,000 | −78 | **25,658** |

---

## 5. Impact Assessment on Analysis

### Findings that are Robust

| Finding | Robustness | Key Caveat |
|---|---|---|
| 67.6% of customers are one-time buyers | **High** | Count-based; not affected by FX or DQ issues |
| 60-day retention rate: 18.1% | **High** | Count-based; FX-neutral |
| Subscriber LTV +166% vs non-subscriber | **High** | All markets, SGD; large sample; uses Shopify tags (full history) |
| Revenue peaked 2021 at zero discounting | **High** | Direct from revenue figures (S$848K combined SGD) |
| Marketplace LTV gap (S$115 vs S$198 direct) | **Med–High** | DQ-08 subscription footnote acknowledged; LTV measurement complete |
| Cross-sell LTV staircase (1→2→3 products) | **Medium–High** | Observational — selection bias possible (loyal customers naturally buy more) |
| Discount ↔ lower cohort quality | **Medium** | Strong consistent association across multiple cuts; causal claim not proven |
| "49.6% of orders discounted in 2025" | **High** | Direct count of orders with has_discount=True |
| Finals-eligible loyal repeater insights | **Medium–High** | Based on 25,658-order clean set after DQ-02/03/04 drops + LP filters |

### What We Cannot Conclude

1. **Causation between discounts and lower retention** — The data shows a strong correlation but cannot rule out the alternative that LushProtein was targeting a different (lower-intent) customer segment in 2023–2024, independent of the discount strategy.
2. **True Marketplace subscription behaviour** — No visibility into Shopee/Lazada subscription activity (DQ-08).
3. **Profitability per customer** — LTV in this analysis means *revenue-to-date*, not profit-to-date. COGS available for only 35% of SKUs (DQ-12).
4. **Attribution of revenue to marketing spend** — 94.9% of orders lack UTM tracking; ROAS cannot be calculated (DQ-09).
5. **Full historical subscription churn picture** — Recharge export covers Apr 2025–Apr 2026 only; earlier cancellations not captured (DQ-11).
6. **Which specific discount code drove which order** — No discount code column on order rows (DQ-10).

---

## 6. Sensitivity and Robustness Checks

### Check 1 — Exclude Outlier Orders (> S$5,000)

**Method:** Remove all orders > SGD 5,000 from all stores and recalculate repeat rate and median LTV.

```python
# All orders excl. outliers (combined SGD)
clean = orders[orders['rev'] <= 5000]
# Before: 27,350 orders, S$3,113,272 revenue
# After removal of ~14 outlier orders (rev>5k): revenue ~−4%
# Repeat rate: unaffected (per-customer metric)
# Median order value: SGD 62.10 → ~SGD 61.90 (negligible change)
```

**Finding:** Excluding extreme outlier orders has minimal effect on per-customer metrics. The repeat rate and cohort retention findings are unchanged.

### Check 2 — DQ-02 / DQ-03 / DQ-04 Drop Impact

| Scenario | Orders | Revenue (SGD) | Repeat Rate | Median LTV |
|---|---|---|---|---|
| Midterm pipeline (01–11) | 27,350 | S$3,112,952 | 32.4% | — |
| After DQ-02 drop (zero rev+disc) | 27,014 | **S$3,112,952** (unchanged) | ~unchanged | ~unchanged |
| After DQ-03 drop (100%-disc) | 25,733 | **S$3,112,952** (unchanged) | marginally higher | marginally higher |
| After DQ-04 drop (wholesale/outlier) | 25,658 | S$2,997,000 (est. −3.7%) | ~unchanged | ~unchanged |

**Confirms:** DQ-02 and DQ-03 drops have zero revenue impact (all dropped orders have net rev = S$0). DQ-04 removes a small portion of absolute revenue but does not affect per-customer repeat metrics. The finals analysis is conducted on 25,658 clean consumer orders.

### Check 3 — Subscription Tag Consistency

```
Orders tagged as Subscription/Recurring:    3,267
Orders with is_subscription = True:         3,265
Agreement rate:                             99.94%
```

The 2-order discrepancy is inconsequential for all subscription analyses.

### Check 4 — Discount Metric Reformulation

Three ways to measure 2025 discount intensity:

| Metric | 2025 Value | Interpretation | Use in Report? |
|---|---|---|---|
| `disc / net_revenue` (original chart) | 54.2% | Misleading — denominator already reduced | ❌ |
| `% of orders with any discount` | 49.6% | Clear and directly interpretable | ✅ |
| `disc / (rev + disc)` — % of gross revenue | 35.2% | Most meaningful for business context | ✅ |

### Check 5 — FX Verification

`python EDA/verify_all.py` — **62 checks PASS** (MY/HK avg order values post-conversion within expected range; known outlier orders confirmed).

---

## 7. LushProtein Feedback — Applied Analysis Filters

These are **not data quality issues**. They are analytical scope decisions made at LushProtein's request to focus the finals analysis on their core, stable consumer base. All four filters are applied **only** in `EDA/12_finals_deep_dive.py`. Midterm scripts 01–11 and the base parquet files are unaffected.

The instructions for each of these filters came directly from LushProtein representatives during the post-midterm presentation feedback session.

---

### LP-F01 — Exclude better-whey-protein-elite Buyers

**Context:** `better-whey-protein-elite` is a high-gram-quantity protein format available in bulk configurations. LushProtein indicated that buyers of this product represent a non-representative bulk-purchasing pattern that distorts the consumer LTV, product breadth, and repeat-rate metrics for their core audience.

**Implementation:**
```python
EXCLUDE_HANDLE = "better-whey-protein-elite"
elite_customers = set(
    lines[lines["Line: Product Handle"].fillna("").str.contains(EXCLUDE_HANDLE, case=False)]["customer_id"]
)
cust["exclude_elite_buyer"] = cust["customer_id"].isin(elite_customers)
```

**Scale of impact:** **167 customers** are flagged and removed from the finals-eligible pool.

**Rationale documented in report:** These buyers represent a product line LushProtein is not actively growing. Including them would inflate cross-sell and breadth metrics for a product the brand does not intend to scale.

**Applied in:** `EDA/12_finals_deep_dive.py`

---

### LP-F02 — Exclude Customers Acquired in July or November

**Context:** LushProtein identified two promotional months that create acquisition cohorts with atypical discount intensity:
- **July** — LushProtein's company birthday month, featuring storewide promotions
- **November** — Black Friday / Cyber Monday period, with market-wide heavy discounting

Customers acquired during these months show discount-driven purchase patterns that are not representative of the year-round consumer relationship LushProtein is building.

**Implementation:**
```python
EXCLUDE_MONTHS = {7, 11}
cust["exclude_promo_month"] = cust["acq_month"].isin(EXCLUDE_MONTHS)
```

**Scale of impact:** **2,818 customers** are flagged and removed from the finals-eligible pool.

**Rationale documented in report:** Promo-month cohorts have atypical first-order discount depth, lower organic intent, and distorted LTV benchmarks. Removing them ensures that the repeat rates, LTV figures, and loyalty insights reflect LushProtein's core, non-promotional business.

**Applied in:** `EDA/12_finals_deep_dive.py`

---

### LP-F03 — Restrict Analysis Window to January 2022 Onwards

**Context:** LushProtein indicated that the period before 2022 represented a market acquisition and product experimentation phase. During 2020–2021, the product portfolio, pricing strategy, and market focus were in flux. From 2022 onwards, the core product line and pricing structure stabilised.

**Implementation:**
```python
ANALYSIS_START = pd.Timestamp("2022-01-01", tz="Asia/Singapore")
cust["finals_eligible"] = cust["first_order_date"] >= ANALYSIS_START  # (combined with other filters)
```

**Scale of impact:** All customers acquired before 2022-01-01 are excluded from the finals cohort. This removes approximately 7,500+ customers who joined during the experimentation phase.

**Rationale documented in report:** Using the post-2022 stable period ensures that LTV, retention, and loyalty findings are generalisable to the current business model and product mix, not historical experiments. The midterm dataset retains the full 2020–2026 history for completeness.

**Applied in:** `EDA/12_finals_deep_dive.py`

---

### LP-F04 — Exclude Customers with ≥51% First-Order Discount

**Context:** LushProtein confirmed that customers whose first order used a discount depth of 51% or more were acquired through experimental campaigns, gifting programs, or affiliate codes not intended to represent organic consumer intent. These include:
- Social Snowball referral codes (up to 100% off)
- Launch/sampling campaigns
- High-value affiliate promotional codes (e.g., `SGAFF100`)

**Implementation:**
```python
first_ord["first_disc_depth"] = first_ord["first_disc"] / (first_ord["first_rev"] + first_ord["first_disc"])
first_ord["first_disc_bin"] = pd.cut(
    first_ord["first_disc_depth"],
    bins=[-0.001, 0.001, 0.05, 0.10, 0.20, 0.30, 0.50, 1.01],
    labels=["0%", "1-5%", "6-10%", "11-20%", "21-30%", "31-50%", "51%+"],
)
cust["exclude_51pct"] = cust["first_disc_bin"].astype(str) == "51%+"
```

**Scale of impact:** **480 customers** with a first-order discount depth above 50% are excluded from the finals cohort (note: this reflects the post-DQ-02/03/04 clean order set; the pre-drop count was higher at ~1,240 in the full pipeline).

**Rationale documented in report:** The relationship between first-order discount depth and long-term loyalty is central to the finals analysis. Including deeply-discounted acquisition customers would contaminate the loyalty driver findings — LushProtein explicitly confirmed these are not the target audience for the retention and repeat-purchase insights.

**Applied in:** `EDA/12_finals_deep_dive.py`

---

### Finals-Eligible Pool Summary

| Filter Applied | Customers Removed | Remaining |
|---|---|---|
| Base (all customers) | — | 13,780 |
| LP-F03: Acquired before 2022-01-01 | ~7,500+ | ~6,200 |
| LP-F02: Acquired in July or November | 2,818 (overlap with above) | — |
| LP-F01: Bought better-whey-protein-elite | 167 (overlap) | — |
| LP-F04: First order 51%+ discounted | 480 (overlap) | — |
| **Finals-eligible (all filters combined)** | — | **6,353** |

*Note: Counts reflect cumulative filter application — customers excluded by multiple criteria are not double-counted.*

---

## 8. Appendices

### A. Scripts Referenced in This Report

| Script | Purpose | Key Outputs |
|---|---|---|
| `EDA/01_load_and_merge.py` | Loads raw Excel files; applies FX; creates base parquet | `orders.parquet`, `lines.parquet`, `customers.parquet` |
| `EDA/02_data_quality.py` | DQ audit; null counts; year summaries | `02_data_quality_report.txt`, `02_orders_by_year.csv` |
| `EDA/03_customer_retention.py` | Cohort retention; RFM | `03_cohort_retention_heatmap.csv`, `03_rfm_segments.csv` |
| `EDA/05_channel_discount.py` | Channel quality; discount depth | `05_channel_quality.csv`, `05_discount_sensitivity.csv` |
| `EDA/06_subscription_churn.py` | Subscriber LTV; Recharge churn | Churn analysis outputs |
| `EDA/12_finals_deep_dive.py` | **Finals analysis with DQ-02/03/04 drops + LP filters** | `12_*.csv` finals outputs |
| `EDA/verify_all.py` | 62 automated data checks | Pass/fail log |
| `visualizations/08_finals_charts.py` | Finals visualisations | `08a_*` through `08l_*.png` |

### B. Related Documents (Not Replaced)

| File | Role |
|---|---|
| `data_quality_checks.md` | Midterm DQ log — **preserved unchanged** for teammate reference |
| `FINAL_FEEDBACK_ROADMAP.md` | Post-presentation feedback actions and roadmap |
| `deliverables/LushProtein_Orders_STTM.csv` | Source-to-target mapping (69 raw + 12 derived columns) |

### C. Key Field Reference

| Field | Grain | Type | Notes |
|---|---|---|---|
| `order_id` | Order | str | PK; from `ID` where `Top Row = 1`; 0 duplicates confirmed |
| `customer_id` | Customer | str | FK; 13-digit Shopify ID; no nulls |
| `order_date` | Order | datetime UTC | Derived from `Processed At`; timezone-aware |
| `store` | Order | str | "SG", "MY", "HK" — proxy for currency |
| `Price: Total` | Order | float | Net revenue after discounts — SGD post-FX conversion |
| `Price: Total Discount` | Order | float | Total discount applied — zero if no discount |
| `channel` | Order | str | Derived from Tags + UTM (see DQ-05) |
| `Source` | Order | str | Raw Shopify source — `web`, `pos`, `unknown` |
| `is_subscription` | Order | bool | Derived from Tags; 99.94% consistent with raw Tags |
| `has_discount` | Order | bool | Derived: `Price: Total Discount > 0` |
| `Tags` | Order | str | Raw Shopify order tags — 62.3% null |
| `Line: Product Handle` | Line | str | Product identifier — null for order-header rows |
| `Line: SKU` | Line | str | Variant-level SKU; FK to product master |

### D. Finals Order Count Summary

```
Base pipeline (midterm):                  27,350 orders · 13,780 customers
  DQ-02 drop (zero rev + zero disc):        -336 orders
  DQ-03 drop (100%-discount):             -1,281 orders
  DQ-04 drop (wholesale-tag OR > S$5k):      -78 orders (-75 unique after overlap)
Finals clean order pool:                  25,658 orders  (Option B: finals layer only)

LP-F03  Pre-2022 acquisitions excluded:   5,016 customers
LP-F01  Elite-whey buyers excluded:         167 customers (overlap)
LP-F02  Jul/Nov acquisitions excluded:    2,818 customers (overlap)
LP-F04  51%+ first-order disc excluded:     480 customers (overlap)

Finals-eligible customers (all LP filters):  6,353 customers
```

---

*Prepared for ISSS603 PDF Data Quality Report · Group 1 · May 2026*
