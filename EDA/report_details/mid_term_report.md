# ISSS603 Applied Data Science for Customer Insights
## Mid-Term Report — Group 1 (SMU x LushProtein)

**Group Members:** Aditya Vijay, Ang Wei Lin, Aung Shwe Tin, Lee Sae Lin, Pham Vinh Tan Emily, Toh Zheng Feng

---

## 1. Introduction

Dataset covers various operational aspects of LushProtein from December 2019 to March 2026, including customer transactions, product offerings, discounts, campaigns, and subscription data.

### 1.1 Temporal Coverage

**Period of analysis:** 2019-12-31 to 2026-03-30

| Period | Orders | Unique Customers | Notes |
|--------|--------|-----------------|-------|
| 2019 | 3 | 3 | Incomplete year — excluded from cohort analysis |
| 2020 | 2,847 | 1,696 | Full year, zero discounting |
| 2021 | 6,259 | 3,815 | Peak revenue year (S$848K) |
| 2022 | 3,710 | 2,299 | First discounting introduced |
| 2023 | 2,253 | 1,399 | Revenue collapse year |
| 2024 | 4,261 | 2,621 | Recovery, heavy discounting |
| 2025 | 6,407 | 4,107 | Highest order volume, continued discounting |
| 2026 (Partial) | 1,610 | 1,230 | Jan–Mar only; excluded from full-year analysis |

### 1.2 Store and Currency Coverage

| Store | Orders | Revenue (Own Currency) | FX Rate | Revenue (SGD) |
|-------|--------|----------------------|---------|--------------|
| SG | 16,041 | SGD $1,913,068 | 1.00 | S$1,913,068 |
| MY | 11,309 | RM $3,958,566 | 3.30 | S$1,199,566 |
| HK | 2 | HK$1,943 | 6.10 | S$319 |
| **All markets** | **27,350** | — | — | **S$3,112,952** |

**FX methodology:** 5-year average exchange rates (2020–2026) applied at data load time. Introduces measurement error of up to ±10% in absolute revenue figures; direction and relative magnitude of all findings are unaffected.

**Known limitations:**
- SGD/MYR moved between ~3.0 and ~3.5 over 2020–2026; early-year MY revenue may be off by up to 10%
- MY market was effectively dormant by 2025 (S$9,617 vs S$441,022 in 2021), so combined totals are dominated by SG data in recent years
- HK store (2 orders, S$319) is immaterial

---

## 2. Summary Statistics and Distributions

### 2.1 Order Revenue Distribution (All Markets — in SGD after FX conversion)

| Statistics | All Markets (SGD) | SG Only (SGD) | MY Only (SGD equiv.) |
|------------|------------------|--------------|---------------------|
| Count | 27,530 | 16,039 | 11,309 |
| Mean | $113.83 | $119.28 | $106.07 |
| Median | $59.90 | $62.10 | $55.48 |
| Std Dev | $413.76 | $405.16 | $425.60 |
| 25th pctile | $29.40 | $29.00 | $29.70 |
| 75th pctile | $108.41 | $115.00 | $96.67 |
| 90th pctile | $202.48 | $206.66 | — |
| Maximum | $34,618 | S$26,520 | $34,618 |

The mean (S$114) is nearly double the median (S$60), indicating a strongly right-skewed distribution driven by a small number of high-value wholesale/reseller orders. Per-customer LTV is therefore reported as a median in key comparisons. The largest single order is a MY wholesale order of MYR 114,240 (≈ S$34,618).

### 2.2 Order per Customer Distribution

| Statistics | All Markets | SG Market Only |
|------------|------------|---------------|
| Mean | 1.98 | 1.8 |
| Median | 1 | 1 |
| 75th percentile | 2 | 2 |
| 90th percentile | 4 | 3 |
| Maximum | 667 | 667 |
| # Unique customers | 13,780 | 8,920 |
| # With exactly 1 order | 9,321 (67.6%) | 6,454 (72.4%) |
| # With >10 orders | 268 (1.9%) | 111 (1.2%) |
| # With >20 orders | 35 (0.3%) | — |

67.6% of all-markets customers — and 72.4% of SG-only customers — made exactly one purchase. The extreme maximum of 667 orders belongs to a single customer, almost certainly a reseller or test account.

### 2.3 Discount Distribution (All Discounted Orders)

- 9,024 orders carried any discount (33% of total)
- Discount depth = Discount Price / (Total Price + Discount Price)
- Notable anomaly: 14.5% spike at 90–100% off (1,308 orders) — these represent real product shipments (referral rewards, PR samples, subscription welcome gifts) at zero customer cost

### 2.4 LTV Analysis by Acquisition Year and Channel

| Channel | 2022 | 2023 | 2024 | 2025 | 2026 |
|---------|------|------|------|------|------|
| Direct / Organic | S$216 | S$105 | S$92 | S$73 | S$79 |
| Subscription | S$292 | S$190 | S$134 | S$173 | S$110 |
| Marketplace | S$128 | S$74 | S$57 | S$131 | S$139 |
| Paid Social | — | — | — | S$70 | S$84 |

Subscription-acquired customers consistently generate the highest LTV across most cohorts (peaking at S$292 in 2022). Customer quality appears to be declining across traditional acquisition channels in newer cohorts. Marketplace repeat rate (14.4%) remains well below Direct/Organic (33.5%).

### 2.5 Missing Value Summary

| Column | Null Count | % Missing | Notes |
|--------|-----------|-----------|-------|
| Tags | 17,026 | 62.3% | Expected behaviour |
| Browser: UTM Source | 25,945 | 94.9% | Most orders lack UTM tracking |
| Browser: UTM Medium | 25,945 | 94.9% | Same as above |
| Browser: UTM Campaign | 25,978 | 95.0% | Same as above |
| Browser: Referrer Domain | 22,383 | 81.8% | Expected for direct/organic traffic |
| Line: Product Handle | 13,484 | 49.3% | Order-header rows without line items |
| Shipping: Country | 1,055 | 3.9% | Some orders missing shipping destination |
| Order Fulfilment Status | 207 | 0.8% | Minor gap |
| second_order_date | 9,321 | 67.6% | Expected: 67.6% of customers are one-time buyers |

---

## 3. Data Issues and Discrepancies

### 3.1 Mixed Currencies
Raw data contains no FX conversion rates at point of sale. Applied 5-year average rates: 1 SGD = 3.3 MYR, 1 SGD = 6.1 HKD.

### 3.2 Zero Revenue and Zero Discount Orders
336 orders simultaneously record S$0 in both "Price: Total" and "Price: Total Discount". Likely caused by data import or system error. **Removed from analysis.**

### 3.3 100%-Discount Orders
1,281 orders record "Price: Total" = S$0 but a positive "Price: Total Discount". Confirmed with LushProtein as complimentary packages for marketing promotions (influencer collaborations, etc.). **Excluded from final analysis** as they do not reflect consumer purchase behaviour.

### 3.4 Outlier / Wholesale Orders
78 B2B/outlier orders identified: 65 tagged `wholesale-sale` + 14 orders with Price: Total > S$5,000 (one order meets both criteria). **Excluded from finals analysis**; retained in midterm EDA base of 27,350 orders.

### 3.5 Missing Values in UTM Attributions
94.9% of orders lack UTM source/medium/campaign data. Fallback rule applied using Shopify order tags and product handles:
- Marketplace channels identified via server-side Shopify tags (highly reliable)
- Subscription orders cross-referenced using tags + `is_subscription` flag (99.9% consistency: 3,263/3,265 matches)
- Remaining untracked traffic presented as "Direct/Own Channels"

### 3.6 Line-Item vs Order-Level Row Structure
Raw Shopify export mixes order-header rows with line-item rows. 13,484 rows (49.3%) have null "Line: Product Handle". Built two separate tables:
1. Order-level metrics (Top Row = 1 only) — 27,350 orders
2. Line-level metrics (Line: Type = 'Line Item') — 50,963 line items

### 3.7 Subscription Tag vs Flag Consistency
3,267 orders tagged as subscription-related vs 3,265 with `is_subscription = true`. Discrepancy of 2 orders (0.06%). **Using `is_subscription` flag consistently** across all data models.

### 3.8 Marketplace Subscription Tracking Gap and Repeat Rate Measurement
- Shopify cannot ingest third-party platform data → 0.0% subscription rate for all 2,126 marketplace customers (platform limitation, not true behaviour)
- 14.4% marketplace repeat rate = 306 customers with 2+ Shopify-visible orders / 2,126 marketplace-first customers (likely an undercount)
- Comparison against 33.5% Direct/Organic rate remains valid as both use the same baseline

### 3.9 Unused Campaigns Dataset
"4_1. Sessions by referrer_20260505.csv" (246,909 sessions) not used: no date columns (5 years collapsed into static totals) and no customer/order IDs. Order-level Browser: UTM Source used instead for channel classification.

### 3.10 Discount Code Not Linked to Individual Orders
367 discount codes tracked in the Discounts dataset but cannot be linked to individual orders — no connecting field in Shopify export. Discount analysis uses the binary "has discount" variable and discount depth (% of order value) instead.

### 3.11 Temporal Coverage Gaps and Customer ID Mismatches in Recharge Data
- Recharge export covers April 2025 – April 2026 only (subscriptions run since at least 2021)
- Recharge uses 8-digit customer IDs with zero matches to 13-digit Shopify IDs
- Joined on `shopify_order_id`: matched 1,163 of 1,215 Recharge rows (52 unmatched = early April 2026 date discrepancy)
- Result: 1,095 unique subscription customers in Shopify vs only 575 in Recharge
- Churn findings represent a one-year window only (2025–2026)

### 3.12 Product Master COGS Not Available
65% of variant rows in `2.product_master` have null "Cost per item". Only 58 of 167 variants contain active cost data. **Workaround:** Fixed 40% gross margin assumption applied (`MARGIN_RATE = 0.40`). All profit figures labelled "profit proxy."

---

## 4. Follow-Up Analysis to the Midterm Presentation

### 4.1 LTV Definition

**Primary:** LTV (customer) = Sum(Price: Total) — total revenue per customer across all paid, non-restocked orders after FX conversion to SGD

**Gross Profit LTV:** LTV × 0.40 (40% margin proxy, used because 65% of product master COGS is null)

### 4.2 Business Value Calculations

(See final report Part B for updated prize model on finals cohort.)

---

## 5. Applied Analysis Filters — LushProtein Feedback

Following the midterm presentation, LushProtein provided guidance on which customer segments to include in the finals analysis, focused on the company's current target market and business model.

**Four filters applied:**

1. **Better Whey Protein Elite exclusion** — customers purchasing this product tend to buy in bulk and do not represent the broader customer base
2. **July and November acquisition exclusion** — these months contain major promotional campaigns (anniversary, Black Friday) that attract more promotion-driven customers
3. **Post-January 2022 only** — pre-2022 years were a period of product and pricing experimentation
4. **>50% first-purchase discount exclusion** — customers acquired via referral programmes or sampling campaigns may bias retention and LTV analysis

**Final customer pool (mid-term estimate — superseded by manifest):**

| Cohort Filtering Stage | Customers Remaining | Notes |
|-----------------------|--------------------|-|
| Total customer base | 13,780 | All paid, non-restocked customers |
| Acquired on or after 1 Jan 2022 | ~6,200 | Removes ~7,500 pre-2022 customers |
| Additional business-rule filters applied | 6,353 | Mid-term estimate |
| **Authoritative finals cohort (June 2026)** | **5,694** | See `outputs_finals/manifest.json` |

---
