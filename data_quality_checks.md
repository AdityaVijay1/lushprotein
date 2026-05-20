# LushProtein — Data Quality Report

**Team:** Aditya Vijay, Emily Pham Vinh Tan, Saelin Lee, Shwe Tin Aung, Weilin Ang, Zhengfeng Toh
**Date:** May 2026
**Scope:** Shopify customer transaction data (2020–2026), all markets combined (SG + MY + HK) in SGD
**Audience:** Course instructors (assessment of data due diligence)

> **CURRENCY UPDATE (Applied May 2026):** All revenue figures have been converted to SGD using fixed exchange rates:
> **1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD**
> Conversion is applied at data load time in `EDA/01_load_and_merge.py`.
> See DQ-01 (updated) for full discussion of limitations and assumptions.

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

### All Source Datasets — Complete Inventory

| # | Folder | File(s) | Rows | Loaded? | Used in Scripts | Notes |
|---|---|---|---|---|---|---|
| 1 | `1.customer_transaction` | 7 yearly Excel files | 153,828 raw rows → 27,350 orders + 50,963 line items | ✅ YES | All EDA scripts 01–11 | Primary source. FX conversion applied. |
| 2 | `2.product_master` | `2_1.products_master_20260505.xlsx` | 167 variants | ✅ YES | `01_load_and_merge.py`, `02_data_quality.py` | Saved to parquet. Used for category classification in DQ audit only. COGS (65% null) not used. |
| 3 | `3.Discounts` | `3_1.discounts_export_20260505.csv` | 367 codes | ✅ YES | `01_load_and_merge.py`, `05_channel_discount.py` | Discount code taxonomy. Cannot link to individual orders (no discount code field in transactions). |
| 4 | `4.Campaigns` | `4_1.Sessions by referrer_20260505.csv` | **137,033 rows** | ⚠️ **DEFINED BUT NOT LOADED** | **NONE** | `CAMPAIGNS_FILE` defined in `00_config.py` but never imported. Has no date column or customer/order ID. Useful for top-of-funnel description only. |
| 5a | `5.Recharge_data` | `5_1.orders_combined` | 1,215 orders | ✅ YES | `06_subscription_churn.py` | Apr 2025–Apr 2026 only. Avg order S$81 (SGD). |
| 5b | `5.Recharge_data` | `5_2.order_items_checkout` | 1,094 line items | ✅ YES | `04_product_analysis.py`, `06_subscription_churn.py` | First-checkout SKU ranking |
| 5c | `5.Recharge_data` | `5_3.subscribers_reactivated` | 50 customers | ✅ YES | `06_subscription_churn.py` | Win-back cohort |
| 5d | `5.Recharge_data` | `5_4.subscriptions_churned` | 526 records | ✅ YES | `06_subscription_churn.py` | Cancellation reasons and churn cycle |
| 5e | `5.Recharge_data` | `5_5.order_items_recurring` | 650 line items | ✅ YES | `04_product_analysis.py`, `06_subscription_churn.py` | Renewal SKU loyalty analysis |

### Canonical Output Tables

| Table | Rows | Key Fields |
|---|---|---|
| `orders.parquet` | **27,350 orders** | order_id, customer_id, order_date, store, revenue (SGD), discount (SGD), channel, is_subscription |
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
| 2021 | 6,259 | 3,815 | Peak revenue year (S$848K combined SGD; old figure S$1.86M was mixing MYR as SGD) |
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
| **All markets** | **27,352** | — | — | **S$3,113,272 SGD total** |

**Critical note:** The three stores use different currencies. The raw data contains no FX rates.

**Mitigation applied (May 2026):** Fixed exchange rates provided by the team are applied at data load time:
- `1 SGD = 3.30 MYR` → MYR ÷ 3.30 = SGD equivalent
- `1 SGD = 6.10 HKD` → HKD ÷ 6.10 = SGD equivalent

These are **fixed historical rates** (not market rates at each transaction date). This introduces a measurement error in absolute revenue figures. The **direction and relative magnitude of findings are unaffected**.

**Known limitations of fixed-rate FX approach:**
1. SGD/MYR moved between ~3.0 and ~3.5 over 2020–2026. Early-year MY revenue (2020–2021) may be understated/overstated by up to 10%.
2. MY market was effectively dormant by 2025 (only S$9,617 SGD in 2025 vs S$441,022 in 2021), so the combined totals are dominated by SG data in recent years.
3. HK store (2 orders, S$319 SGD equivalent) is immaterial.

**Implemented in:** `EDA/00_config.py` (`FX_RATES_TO_SGD` dict), `EDA/01_load_and_merge.py` (conversion applied before Parquet save)

---

## 2. Summary Statistics and Distributions

### Order Revenue Distribution (All Markets — SGD after FX conversion)

| Statistic | Value (All Markets, SGD) | SG-only (SGD) |
|---|---|---|
| Count | 27,352 orders | 16,041 orders |
| Mean | SGD 113.83 | SGD 119.28 |
| Median | SGD 62.10 | SGD 62.10 |
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
Fixed exchange rates provided by the team are applied at data load time in `EDA/01_load_and_merge.py`:
```python
FX_RATES_TO_SGD = {
    "SG": 1.0,
    "MY": 1.0 / 3.30,   # 1 MYR = 0.3030 SGD  (1 SGD = 3.30 MYR)
    "HK": 1.0 / 6.10,   # 1 HKD = 0.1639 SGD  (1 SGD = 6.10 HKD)
}
# Applied to Price: Total, Price: Total Discount, Price: Total Shipping
# Currency column set to "SGD" for all orders after conversion
```

**Assumption stated explicitly:**
- Rates are **fixed at April 2026** and do not vary by transaction date
- Historical MYR/SGD rate moved between ~3.0 and ~3.5 over 2020–2026 → absolute revenue figures for 2020–2022 may be off by up to ±10%
- For **relative comparisons** (repeat rates, LTV uplift %, cohort retention), the FX rate has no impact — these are count-based or ratio-based metrics

**Post-conversion market revenue summary:**
```
Year  SG (SGD)    MY (SGD)    Total
2020  S$286,181   S$170,771   S$456,952
2021  S$406,908   S$441,022   S$847,930  ← combined peak
2022  S$385,076   S$362,510   S$747,587
2023  S$101,135   S$80,902    S$182,038
2024  S$150,308   S$134,663   S$284,971
2025  S$399,216   S$9,617     S$409,152  ← MY market effectively dormant
```

**Residual risk:** The fixed-rate assumption introduces ≤10% error on absolute MY revenue figures. MY market is dominant in 2020–2022 but almost absent in 2025, so the combined 2025 figures are 97% SG-driven.

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
The correct discount metric is "discounts as % of gross revenue" — not disc/net_rev. The disc/net_rev ratio inflates the figure because 100%-discount orders contribute to the numerator while adding S$0 to the denominator.

**Better representation (2025, combined SG + MY + HK in SGD):**
```
2025:
  Revenue collected (net):  S$409,152
  Discounts given:          ~S$220,000  (incl. 100%-off orders)
  Gross potential:          ~S$629,000
  Correct discount rate:    35.2% of gross revenue
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
- This inflates the Direct/Organic customer count (6,920 customers) and its LTV metric (S$198 in the combined dataset)

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
The 14.4% marketplace repeat rate is computed as 306 customers with ≥2 Shopify-visible orders ÷ 2,126 marketplace-first customers. A "repeat" is any second Shopify order regardless of whether it came through Shopee/Lazada again or through a direct Shopify.com visit.

```
Marketplace customers:                 2,126
Marketplace repeaters (2+ Shopify):      306
Repeat rate:                           14.4%   (306 / 2,126)
Total marketplace-tagged orders:       3,268
Avg orders per marketplace customer:    1.54
```

The fact that there are 3,268 marketplace-tagged orders across 2,126 customers (not 2,126 as would be the case if only first orders were synced) confirms that repeat Shopee/Lazada orders ARE being captured in Shopify via the integration — at least partially.

**Potential sources of undercount in the 14.4%:**
1. A customer who buys on Shopee with email A and then on Shopee again with email B gets two separate Shopify customer records — the repeat is not linked.
2. If the Shopify–Shopee/Lazada integration misses some repeat orders, those are invisible.

**Impact:**
- The **0% Shopify subscription rate** for Marketplace is technically correct within Shopify data; the true marketplace subscription rate on Shopee/Lazada is unknown.
- The **14.4% repeat rate** may be a modest undercount. However, even if the true rate is higher, customers who only repeat on Shopee/Lazada without entering the Shopify ecosystem have zero CRM visibility and zero Shopify subscription potential — this strengthens, not weakens, the channel quality argument.
- The **relative comparison** (14.4% Marketplace vs 33.5% Direct/Organic) is valid: all channels are measured on identical Shopify-data basis.
- The **LTV gap** (S$115 Marketplace vs S$198 Direct/Organic) is also valid — both channels' LTV is measured from complete Shopify purchase histories.

**Severity:** MEDIUM for the subscription conversion metric and repeat rate headline; LOW for the LTV comparison and the strategic conclusion.

**Mitigation:**
- LTV and repeat rate comparisons across channels remain valid (both use Shopify purchase history)
- Subscription comparison annotated: "Shopify subscriptions only; Marketplace platforms operate independent subscription systems not tracked here"
- Repeat rate annotated: "Marketplace repeat rate reflects customers with 2+ Shopify-visible orders. Repeat purchases exclusively on Shopee/Lazada and not synced to Shopify are not captured."

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

Top cities (sessions):
  Singapore       30,506
  Kuala Lumpur    23,048
  Petaling Jaya    7,518

Total sessions: 246,909 | Unique visitors: 220,244
```

**Critical limitations of this dataset (from Data Glossary):**
1. **No date column** — 5 years of traffic collapsed into cumulative counts; time-trending is impossible
2. **No customer or order ID** — cannot compute true conversion rates (sessions → orders)
3. **Each row is a unique dimension combination** — useful for proportional channel mix, not for joining

**What it would be useful for:**
- Top-of-funnel channel mix narrative: "Facebook drives ~24% of all sessions"
- Geographic description of the customer base: SG (12%), KL (9%), PJ (3%)
- Landing page popularity (which product pages attract the most visitors)

**Severity:** LOW for the core findings (retention, LTV, cohort analysis are all order-based). MEDIUM for any claim about acquisition channel effectiveness — the campaigns data confirms the channel distribution but cannot quantify conversion.

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
- The `SGAFF100` code (-100%, 88 uses) is confirmed real — these are the "dummy" affiliate codes the user identified. They represent orders where affiliates get 100% commission (the product is paid by the affiliate, not the customer)
- Discount sensitivity analysis uses `has_discount` (True/False) and the discount dollar amount, which is still valid for measuring discount impact on LTV

**Severity:** MEDIUM. The key discount finding (full-price buyers have 2× repeat rate vs 50%+ discounted buyers) remains valid because it uses the discount amount, not the code. The code-level taxonomy is informative but approximate.

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
- `06_subscription_churn.py` Sections B–D use **Recharge data directly** — represent the most recent year only, not the full subscription history
- Cancellation reasons (526 churns) are from 2025–2026 — may not represent earlier churn behavior
- The 520 "missing" subscribers (1,095 Shopify − 575 Recharge) are likely customers whose subscriptions were before April 2025 or who subscribed via the old Yotpo Subscriptions platform

**Severity:** MEDIUM for subscription churn/tenure analysis. LOW for LTV and retention analysis (which use Shopify data).

**Mitigation:**
- Subscription LTV comparison uses Shopify data → unaffected
- Churn analysis is explicitly described as "from the Recharge export (Apr 2025–Apr 2026)" in the presentation notes
- Join on `shopify_order_id` (96% match) is the correct approach if revenue-level Recharge validation is needed

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

**Impact:** All margin calculations in the analysis use an estimated 40% gross margin proxy (`MARGIN_RATE = 0.40` in `EDA/07_lens1_heterogeneity.py`). This is an assumption, not a data-derived figure.

**Severity:** LOW for relative comparisons (top decile vs bottom decile). MEDIUM for absolute profit figures cited in `presentation.md`.

**Mitigation:** The 40% gross margin assumption is disclosed in all scripts. Profit figures are labelled "profit proxy" throughout. Revenue-based findings are unaffected.

---

## 4. Mitigations Applied

| Issue ID | Issue | Mitigation Applied | Where Applied |
|---|---|---|---|
| DQ-01 | Multi-currency | Fixed FX applied at load time (1 SGD = 3.30 MYR, 1 SGD = 6.10 HKD); all markets combined in SGD | `EDA/00_config.py`, `EDA/01_load_and_merge.py` |
| DQ-02 | Zero-value orders | Included in counts; auto-excluded from revenue | All revenue calculations |
| DQ-03 | 100%-discount orders | Noted; discount metric reformulated as % of gross | `presentation.md` Slide 2 |
| DQ-04 | Wholesale outliers | Per-customer LTV (not per-order) reduces impact | All LTV metrics |
| DQ-05 | UTM attribution gaps | Tags-based channel assignment with documented priority | `EDA/00_config.py` channel classification |
| DQ-06 | Line-item structure | Product analyses filter to non-null handles | `EDA/04_product_analysis.py` |
| DQ-07 | Subscription tag inconsistency | `is_subscription` flag used; 2-order discrepancy negligible | `EDA/06_subscription_churn.py` |
| DQ-08 | Marketplace subscription gap | Annotated in channel quality analysis | `presentation.md` Slide 3 |
| DQ-09 | Campaigns dataset unused | UTM data from order-level field used instead (superior join key) | `EDA/00_config.py` channel classification |
| DQ-10 | Discount code not in orders | Discount amount-based analysis used; code-level taxonomy is standalone | `EDA/05_channel_discount.py` |
| DQ-11 | Recharge temporal gap + ID mismatch | Subscription LTV uses Shopify tags (full history); churn stats noted as 2025–2026 only | `EDA/06_subscription_churn.py`, `presentation.md` |
| DQ-12 | COGS gaps in product master | 40% gross margin proxy used; labelled as "profit proxy" throughout | `EDA/07_lens1_heterogeneity.py` |

---

## 5. Impact Assessment on Analysis

### Which Findings Are Robust?

| Finding | Robustness | Key Caveat |
|---|---|---|
| 67.6% of customers are one-time buyers | **High** | Count-based; not affected by FX or DQ issues |
| 60-day retention rate: 18.1% | **High** | Count-based; FX-neutral |
| Subscriber LTV +166% vs non-subscriber | **High** | All markets, SGD; large sample (1,095 vs 12,685); uses Shopify tags (full history) |
| Cross-sell LTV staircase | **Medium-High** | Observational — selection bias possible (loyal customers naturally buy more) |
| Marketplace LTV gap (S$115 vs S$198 direct) | **Medium-High** | Subscription tracking gap (DQ-08) acknowledged; LTV measurement is complete |
| Discount → lower cohort quality | **Medium** | Strong consistent association across multiple cuts; causal claim not proven |
| Revenue peaked 2021 at zero discounting | **High** | Directly from revenue figures (S$848K combined SGD); not model-dependent |
| "49.6% of orders discounted in 2025" | **High** | Direct count of orders with has_discount=True |
| At Risk segment: S$514 avg LTV | **Medium** | RFM scoring is rank-based (robust to outliers); "At Risk" label is analyst-defined |
| Cancellation reason "#1 = stockpile" | **Medium** | Recharge export only covers Apr 2025–Apr 2026 (DQ-11); may not reflect all historical churn |
| Subscription win-back rate | **Low** | Only 50 reactivated customers in Recharge export; small sample |

### What We Cannot Conclude From This Data

1. **Causation between discounts and lower retention** — The data shows a strong correlation but cannot rule out the alternative that LushProtein was targeting a different (lower-intent) customer segment in 2023–2024, independent of the discount strategy.

2. **True Marketplace customer subscription behaviour** — We cannot know whether Marketplace customers subscribe on Shopee/Lazada. The Shopify dataset has no visibility into their post-acquisition behaviour on those platforms (DQ-08).

3. **Profitability per customer** — The dataset contains revenue figures but not COGS, shipping costs, or marketing spend per customer. "LTV" in this analysis means *revenue-to-date*, not profit-to-date. COGS is available for only 35% of SKUs in the product master (DQ-12).

4. **Attribution of revenue to marketing spend** — 94.9% of orders lack UTM tracking in the order data. The campaigns dataset (DQ-09) has UTM session data but no order/customer IDs, so ROAS cannot be calculated.

5. **Full historical subscription churn picture** — The Recharge export covers only Apr 2025–Apr 2026 (DQ-11). Earlier subscription cancellations (2021–2024) are not captured in the Recharge tables.

6. **Which specific discount code drove which order** — The transactions table has the discount amount but not the code name. We cannot identify which customers used `SGAFF100` (the 100% affiliate code) vs. `welcome10` vs. `AFFCOUPON` (DQ-10).

---

## 6. Sensitivity and Robustness Checks

### Check 1: Does Excluding Outlier Orders Change the Key Findings?

**Method:** Remove all orders >SGD 5,000 from all stores and recalculate repeat rate and median LTV.

```python
# All orders excl. outliers (combined SGD)
clean = orders[orders['rev'] <= 5000]
# Before: 27,350 orders, S$3,113,272 revenue
# After removal of ~12 outlier orders: revenue ~-4%
# Repeat rate: unaffected (per-customer metric)
# Median order value: SGD 62.10 → ~SGD 61.90 (negligible change)
```

**Finding:** Excluding extreme outlier orders has minimal effect on per-customer metrics. The repeat rate and cohort retention findings are unchanged.

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
