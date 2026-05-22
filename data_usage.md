# LushProtein — Data Usage and Pipeline Reference

**Project:** ISSS603 Science of Customer Analytics · SMU Sem 5
**Data Period:** 2019–2026 (analysis focused on 2020–2025)
**Markets:** Singapore (SG) + Malaysia (MY) + Hong Kong (HK), all converted to SGD
**FX Rates Applied:** 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average, 2020–2026)
**Last Verified:** 21 May 2026 — full pipeline re-run, all 62 verification checks PASS, zero hardcoded values confirmed across all EDA and visualization scripts

---

## Table of Contents

1. [Dataset Inventory and Status](#1-dataset-inventory-and-status)
2. [Dataset 1 — Customer Transactions](#2-dataset-1--customer-transactions)
3. [Dataset 2 — Product Master](#3-dataset-2--product-master)
4. [Dataset 3 — Discounts](#4-dataset-3--discounts)
5. [Dataset 4 — Campaigns](#5-dataset-4--campaigns-not-analyzed)
6. [Dataset 5 — Recharge Subscription Data](#6-dataset-5--recharge-subscription-data)
7. [Analysis Pipeline — Script by Script](#7-analysis-pipeline--script-by-script)
8. [Verified Master Numbers](#8-verified-master-numbers)
9. [What Each Finding Relies On](#9-what-each-finding-relies-on)

---

## 1. Dataset Inventory and Status

| # | Folder | File | Size | Rows | Status | Used In |
|---|---|---|---|---|---|---|
| 1 | `1.customer_transaction` | 7 yearly Excel files | ~40 MB total | 153,828 raw → 27,350 orders | ✅ **Primary source** | All EDA scripts |
| 2 | `2.product_master` | `2_1.products_master_20260505.xlsx` | 35 KB | 167 variants | ✅ **Loaded, limited use** | `01_load_and_merge`, `02_data_quality` |
| 3 | `3.Discounts` | `3_1.discounts_export_20260505.csv` | 42 KB | 367 codes | ✅ **Loaded, standalone use** | `01_load_and_merge`, `05_channel_discount` |
| 4 | `4.Campaigns` | `4_1.Sessions by referrer_20260505.csv` | 52 MB | 137,033 sessions | ⚠️ **Defined but NOT analyzed** | None — see Section 5 |
| 5a | `5.Recharge_data` | `5_1.orders_combined_20260505.xlsx` | 74 KB | 1,215 orders | ✅ **Loaded, subscription revenue** | `06_subscription_churn` |
| 5b | `5.Recharge_data` | `5_2.order_items_checkout_20260505.xlsx` | 87 KB | 1,094 items | ✅ **Loaded, first-checkout SKUs** | `04_product_analysis`, `06_subscription_churn` |
| 5c | `5.Recharge_data` | `5_3.subscribers_reactivated_20260505.xlsx` | 6 KB | 50 records | ✅ **Loaded, win-back analysis** | `06_subscription_churn` |
| 5d | `5.Recharge_data` | `5_4.subscriptions_churned_20260505.xlsx` | 41 KB | 526 records | ✅ **Loaded, cancellation reasons** | `06_subscription_churn` |
| 5e | `5.Recharge_data` | `5_5.order_items_recurring_20260505.xlsx` | 54 KB | 650 items | ✅ **Loaded, renewal SKU loyalty** | `04_product_analysis`, `06_subscription_churn` |

**Additional reference files (not part of EDA):**
- `LushProtein_Data_Glossary_20260505.xlsx` — Column-level documentation for all datasets
- `LushProtein_Source_to_Target_Mapping_Exercise.xlsx` — STM deliverable (customer transactions only)
- `Combined_Slides.pdf` — Course lecture reference for EDA methodology

---

## 2. Dataset 1 — Customer Transactions

**Source:** Shopify order export, 7 annual files (2020–2026)
**Why used:** This is the complete purchase history of every customer across all three LushProtein markets. It is the only dataset that links customers, orders, revenue, channel, and product together.

### What is extracted

| Output Table | Filter Applied | Rows | Purpose |
|---|---|---|---|
| `orders.parquet` | `Top Row == 1` (one row per order) | 27,350 | Primary unit for all customer/revenue analysis |
| `lines.parquet` | `Line: Type == 'Line Item'` | 50,963 | Product category and SKU-level analysis |
| `customers.parquet` | Derived: one row per customer | 13,780 | LTV, retention, RFM, cohort analysis |

### FX Conversion (applied before saving)

```python
# EDA/01_load_and_merge.py
FX_RATES_TO_SGD = {"SG": 1.0, "MY": 1/3.30, "HK": 1/6.10}
# Rates = 5-year average (2020–2026): 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD
# Applied to: Price: Total, Price: Total Discount, Price: Total Shipping, Line: Price
# After conversion: Currency column set to "SGD" for all 27,350 orders
```

**Converted:** 11,309 MY orders (÷3.30) + 2 HK orders (÷6.10)
**SG orders:** 16,041 — no change

### Columns in `orders.parquet`

| Column | Type | Source | Notes |
|---|---|---|---|
| `order_id` | str | `ID` | Shopify order ID |
| `customer_id` | str | `Customer: ID` | Shopify customer ID (13-digit) |
| `order_date` | datetime (UTC) | `Processed At` | Converted to SGT for display |
| `store` | str | Derived from `Name` prefix | "SG", "MY", "HK" |
| `Currency` | str | Set to "SGD" after FX | Always "SGD" post-conversion |
| `Price: Total` | float | FX-converted | Net revenue in SGD |
| `Price: Total Discount` | float | FX-converted | Discount amount in SGD |
| `channel` | str | Derived | Tags + UTM → 7 channel types |
| `is_subscription` | bool | Tags | "Subscription" or "Yotpo Subscriptions" in Tags |
| `has_discount` | bool | Derived | `Price: Total Discount > 0` |
| `product_category` | str | `Line: Product Handle` | Lean Protein, Clear Protein, Collagen, etc. |

### Known gaps in this dataset

| Gap | Detail | Impact |
|---|---|---|
| No discount code column | `Price: Total Discount` exists but no "which code was used" | Cannot link individual orders to specific promo codes |
| `Line: Variant Cost` not extracted | Field exists in raw data but not in parquet | No per-SKU margin analysis |
| UTM gaps | 94.9% of orders have no UTM Source | Channel classification falls back to Tags-based logic |

### Market revenue breakdown (2020–2025, SGD)

| Year | SG Store | MY Store (SGD equiv.) | HK | Combined |
|---|---|---|---|---|
| 2020 | S$286,181 | S$170,771 | – | **S$456,952** |
| 2021 | S$406,908 | S$441,022 | – | **S$847,930** ← Peak |
| 2022 | S$385,076 | S$362,510 | – | **S$747,587** |
| 2023 | S$101,135 | S$80,902 | – | **S$182,038** |
| 2024 | S$150,308 | S$134,663 | – | **S$284,971** |
| 2025 | S$399,216 | S$9,617 | S$319 | **S$409,152** |

> MY market was near-equal to SG at peak (2021) and has since collapsed. 2025 is 97% SG-driven.

---

## 3. Dataset 2 — Product Master

**Source:** Shopify product catalogue export (`2.product_master`)
**Why loaded:** To cross-reference product handles from the order data with clean titles, SKU classifications, and pricing.

### What it contains

| Field | Coverage | Used? | Notes |
|---|---|---|---|
| `Handle` | 57 unique handles | ✅ | Used to classify product category in `00_config.py` |
| `Variant SKU` | 56 unique SKUs | ⚠️ Partially | Saved to `products.parquet` but not joined to orders |
| `Status` | active/draft/archived | ✅ | Used in `02_data_quality.py` to count active SKUs |
| `Cost per item` | Available for 58/167 variants (35%) | ❌ Not used | COGS not used due to 65% nulls — 40% margin proxy used instead |
| `Price / Singapore` | All variants | ❌ Not used | Could validate FX conversion; not implemented |
| `Price / Malaysia` | All variants | ❌ Not used | Same as above |

### Why product master is not the primary classification source

The `classify_product()` function in `EDA/00_config.py` maps product **handle keywords** (e.g., "lean-protein", "collagen") to categories directly from the order line items. This is more reliable than joining to the product master because:
- Some older SKUs (2020–2022) appear in orders but are archived or absent from the current master
- The handle-based classification handles all variants without needing a join

### Active SKU count (as of May 2026)

```
active:   34 SKUs
draft:    22 SKUs
archived:  1 SKU
```

---

## 4. Dataset 3 — Discounts

**Source:** Shopify discounts export (`3.Discounts`)
**Why loaded:** To classify the types of promotions LushProtein runs and identify potentially misleading codes (e.g., 100% affiliate codes).

### What it contains

| Field | Detail |
|---|---|
| Total codes | 367 |
| Active | 149 |
| Expired | 218 |
| Codes with zero uses | 204 (55%) — drafts/tests, never deployed |
| Total recorded redemptions | ~2,700+ across all codes |

### Key codes identified

| Code | Value | Uses | Category | Note |
|---|---|---|---|---|
| Default program - DO NOT DELETE | -15% | 317 | Subscription | Recharge subscription recurring discount |
| Buy 2 Save 5% | -5% | 272 | Bundle | Volume incentive |
| AFFCOUPON | -10% | 261 | Affiliate | Standard affiliate commission code |
| welcome10 | -10% | 154 | Welcome | New customer acquisition |
| BDAY40 | -40% | 147 | Event | Birthday/loyalty |
| SGAFF100 | **-100%** | 88 | Affiliate | ⚠️ 100% discount — affiliate pays full cost |

### Critical limitation: Cannot link codes to individual orders

The Shopify order export **does not include a "discount code used" column**. The `Price: Total Discount` in the orders table tells us the amount discounted but not which code was applied.

**What this means for the analysis:**
- Discount taxonomy (code classification) is a **standalone** table-level analysis
- Discount sensitivity analysis uses amount/depth (0%, 1–5%, etc.) — **this is valid**
- We cannot identify which specific customers used `SGAFF100` or `welcome10`

### Why `SGAFF100` (100% discount) is real and not data error

The `SGAFF100` code is a standard affiliate arrangement: the affiliate receives the product free (funded by their commission). It is NOT a data error. However, these 88 orders **inflate the "50%+ discounted" cohort** with zero-revenue orders that distort LTV comparisons. These orders should be treated as marketing cost, not zero-LTV customers.

---

## 5. Dataset 4 — Campaigns (NOT Analyzed)

**Source:** `4_1.Sessions by referrer_20260505.csv` (52 MB, 137,033 rows)
**Why defined in config:** The `CAMPAIGNS_FILE` path is set in `EDA/00_config.py` as a placeholder.
**Why NOT loaded or analyzed:** See below.

### What the dataset contains

```
Columns: Referrer source, Referrer name, Session city, UTM campaign,
         UTM medium, UTM source, Landing page path, Landing page URL,
         Online store visitors, Sessions

Total sessions recorded: 246,909
Total unique visitors:   220,244
Date range:              NO DATE COLUMN — 5 years aggregated into totals
```

### Top-level statistics (descriptive only)

| UTM Source | Sessions | % of Identified |
|---|---|---|
| facebook | 58,322 | 65% |
| meta | 15,706 | 18% |
| affiliate | 4,798 | 5% |
| shopify_email | 4,608 | 5% |
| snowball | 3,879 | 4% |

**Top cities by session volume:**

| City | Sessions |
|---|---|
| Singapore | 30,506 (12%) |
| Kuala Lumpur | 23,048 (9%) |
| Petaling Jaya | 7,518 (3%) |

### Why it is NOT suitable for the core analysis

| Limitation | Why it matters |
|---|---|
| **No date column** | 5 years of traffic collapsed into cumulative totals. Cannot trend by month or year. |
| **No customer ID or order ID** | Cannot compute true conversion rates (sessions → orders). Cannot join to any customer behavior. |
| **Pre-aggregated dimensions** | Each row is a unique combination of UTM + city + landing page. Not order-level data. |
| **No market separation** | Sessions from SG and MY are mixed together without a market field. |

### What it IS useful for (descriptive narrative only)

> "Approximately 65% of identified acquisition sessions came from Facebook/Meta paid social, consistent with the order-level UTM data. Singapore (12%) and Kuala Lumpur (9%) are the top session cities, reflecting the primary markets."

### Why the order-level UTM is better

The `Browser: UTM Source` field in the customer transaction files provides UTM source **at the order level with a customer ID attached**. This enables the channel quality analysis (repeat rate by channel, LTV by channel) that the campaigns file cannot support. The `classify_channel()` function in `EDA/00_config.py` uses this field, supplemented by order Tags.

---

## 6. Dataset 5 — Recharge Subscription Data

**Source:** 5 Excel files exported from the Recharge subscription platform
**Why used:** Recharge is the subscription management layer sitting on top of Shopify. It provides subscription-specific data (churn, cancellation reasons, recurring SKUs) that Shopify does not capture.

### Files and their purpose

| File | Rows | Date Range | What it provides | How used |
|---|---|---|---|---|
| `5_1.orders_combined` | 1,215 | Apr 2025–Apr 2026 | Subscription order history (checkout + recurring) | Subscription order type breakdown in `06` |
| `5_2.order_items_checkout` | 1,094 | Same | Line items of first-subscription checkouts | Top SKUs at onboarding in `04`, `06` |
| `5_3.subscribers_reactivated` | 50 | Same | Customers who re-subscribed after cancelling | Win-back rate and timing in `06` |
| `5_4.subscriptions_churned` | 526 | Same | Cancelled subscriptions with reasons | Cancellation reasons and churn cycle in `06` |
| `5_5.order_items_recurring` | 650 | Same | Line items of renewal subscription orders | SKU loyalty ratio (checkout vs. recurring) in `04` |

### Critical limitations

**1. Temporal coverage: Apr 2025–Apr 2026 only**

The Recharge exports cover exactly one year. LushProtein has had subscriptions since at least 2021. The 520 subscribers in the 2021–2024 period whose Recharge data was not exported are identified only via their Shopify order Tags.

```
Shopify ever-subscribed customers (Tags-based): 1,095  (all time, 2020–2026)
Recharge unique customers in export:              575  (Apr 2025–Apr 2026 only)
Gap:                                              520  (earlier subscribers, no Recharge detail)
```

**2. Customer ID systems do not match**

Recharge uses its own 8-digit customer IDs. Shopify uses 13-digit IDs. These cannot be joined on `customer_id`.

```
Recharge customer ID example: 237412247    (8 digits, Recharge internal)
Shopify customer ID example:  6423777902847 (13 digits, Shopify internal)
```

The correct join key is `shopify_order_id` (96% match rate — the 4% gap is orders from the Apr 1–7 2026 window between export dates, per the Data Glossary).

**3. Subscription LTV — how it is correctly calculated**

The subscriber vs. non-subscriber LTV comparison does NOT use Recharge data. It uses the Shopify `customers.parquet` table, where `ever_subscribed` is derived from Shopify order Tags. This captures all 1,095 ever-subscribed customers across the full 2020–2026 period.

```python
# EDA/06_subscription_churn.py — Section A
# Uses: cust.groupby("ever_subscribed").agg(avg_ltv=("total_revenue","mean"))
# Source: customers.parquet (Shopify tags, full history)
# NOT from Recharge customer table
```

**4. Recharge revenue currency**

No explicit currency column in the Recharge export. Average order value = S$81. Given that Recharge is deployed on the SG Shopify store and the avg order value is consistent with SGD pricing for protein supplements (S$60–100/tub), the figures are treated as SGD. FX conversion is NOT applied to Recharge tables.

---

## 7. Analysis Pipeline — Script by Script

### Data Loading

| Script | Input | Output | What it does |
|---|---|---|---|
| `EDA/00_config.py` | — | Config constants | FX rates, product classification, channel classification, analysis date |
| `EDA/01_load_and_merge.py` | 7 order Excel files + all ancillary files | 10 Parquet files | Merges all raw data, applies FX conversion, builds customer summary |

### Core EDA Scripts

| Script | Parquet tables used | CSV outputs | Key findings produced |
|---|---|---|---|
| `02_data_quality.py` | orders, lines, customers, discounts, products | `02_data_quality_report.txt`, orders/country/channel/revenue CSVs | Table dimensions, null rates, payment status, product/discount overviews |
| `03_customer_retention.py` | orders, customers | `03_cohort_retention_heatmap.csv`, `03_rfm_segments.csv`, `03_time_to_second_purchase.csv` | Repeat rates, 60-day retention, time-to-2nd-purchase distribution, RFM segmentation |
| `04_product_analysis.py` | orders, lines, customers, rc_checkout, rc_recurring | `04_cross_product_ltv.csv`, `04_product_revenue_summary.csv`, `04_sku_popularity.csv` | Cross-sell LTV staircase, product revenue mix, SKU loyalty ratios |
| `05_channel_discount.py` | orders, customers, discounts | `05_channel_quality.csv`, `05_discount_sensitivity.csv`, `05_discount_code_taxonomy.csv` | Channel repeat/LTV comparison, first-order discount depth vs LTV, code taxonomy |
| `06_subscription_churn.py` | customers, rc_orders, rc_checkout, rc_churned, rc_recurring, rc_reactivated | `06_sub_vs_onetime_ltv.csv`, `06_churn_reasons.csv`, `06_churn_by_product.csv`, `06_reactivation_analysis.csv` | Sub vs non-sub LTV, churn by product, cancellation reasons, win-back rate |

### 5-Lens Customer-Base Audit (Bruce, Fader & Ross)

| Script | Lens | Key output |
|---|---|---|
| `07_lens1_heterogeneity.py` | Lens 1: How different are customers? | Decile table, distribution charts, top-10% = 66% of revenue |
| `08_lens2_period_decomposition.py` | Lens 2: Why did revenue move? | Annual waterfall (New/Retained/Lost), decile migration |
| `09_lens3_cohort_evolution.py` | Lens 3: How does one cohort evolve? | VTD curves, inter-purchase time distribution, one-and-done rate |
| `10_lens4_vintage_comparison.py` | Lens 4: Are newer cohorts better or worse? | 60d/180d/365d retention by acquisition year, channel and discount drift |
| `11_lens5_base_health.py` | Lens 5: How healthy is the full base? | 5-KPI health scorecard, composition waterfall |

### Visualizations

| Script | Charts produced | Based on |
|---|---|---|
| `01_revenue_and_volume.py` | Revenue + discount trend, monthly trend, orders/customers by year | Verified from `02_orders_by_year.csv` |
| `02_retention_overview.py` | Retention by channel, 60-day cohort heatmap, time-to-2nd-purchase | `03_cohort_retention_heatmap.csv`, `03_time_to_second_purchase.csv` |
| `03_product_and_crosssell.py` | Cross-sell LTV staircase, product revenue mix, SKU loyalty | `04_cross_product_ltv.csv`, `04_sku_popularity.csv` |
| `04_subscription_churn.py` | Subscriber vs one-time LTV, churn by cycle, cancellation reasons | `06_sub_vs_onetime_ltv.csv`, `06_churn_reasons.csv` |
| `05_discount_channel.py` | Discount depth vs LTV, marketplace vs website, RFM segments | `05_channel_quality.csv`, `03_rfm_segments.csv` |

---

## 8. Verified Master Numbers

All numbers below confirmed by re-running the full pipeline on **19 May 2026**.
**Scope: SG + MY + HK combined in SGD (1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD, 5-year average 2020–2026)**

### Business at a Glance

| Metric | Verified Value | How Computed |
|---|---|---|
| Unique customers (2020–2026) | **13,780** | `len(customers.parquet)` |
| Total orders (2020–2026) | **27,350** | `len(orders.parquet)` |
| Repeat customers | **4,459** | `cust['is_repeat'].sum()` |
| Overall repeat purchase rate | **32.4%** | `4,459 / 13,780` |
| 60-day retention rate | **18.3%** | Cohort-level: eligible cohorts only (first order ≤ Apr 2026 − 60d) |
| Avg 60-day cohort retention | **18.1%** | Average of monthly cohort `retention_60d` values |
| Median days to 2nd order | **49 days** | `cust[is_repeat]['days_to_second'].median()` |
| Subscriber avg LTV (SGD) | **S$532** | `cust[ever_subscribed==True]['total_revenue'].mean()` |
| Non-subscriber avg LTV (SGD) | **S$200** | `cust[ever_subscribed==False]['total_revenue'].mean()` |
| Subscriber LTV uplift | **+166%** | `(532 / 200) - 1` |
| Ever-subscribed customers | **1,095 (7.9%)** | Derived from Shopify order Tags |

### Annual Revenue and Discounting

| Year | Revenue (SGD) | Orders | % Orders Discounted | Discounts as % of Gross |
|---|---|---|---|---|
| 2020 | **S$456,952** | 2,847 | 0.0% | 0.0% |
| 2021 | **S$847,930** | 6,259 | 0.0% | 0.0% ← Revenue peak |
| 2022 | **S$747,587** | 3,710 | 15.2% | 3.9% |
| 2023 | **S$182,038** | 2,253 | 59.3% | 15.1% |
| 2024 | **S$284,971** | 4,261 | 69.2% | 30.9% |
| 2025 | **S$409,152** | 6,407 | 49.6% | 35.2% |

> **Note:** Previous figures (e.g. S$1.86M in 2021) were incorrect — they mixed MYR and SGD without conversion. The correct combined peak is **S$848K** in 2021.

### Channel Quality

| Channel | Customers | Repeat Rate | Avg LTV (SGD) | % Subscribed |
|---|---|---|---|---|
| Subscription | 4,275 | **40.9%** | S$343 | 18.8% |
| Direct / Organic | 6,920 | 33.5% | S$198 | 3.8% |
| **Marketplace** | **2,126** | **14.4%** | **S$115** | **0.0%*** |
| Paid Social | 382 | 19.4% | S$71 | 6.0% |
| Email | 48 | 12.5% | S$50 | 2.1% |

*Marketplace notes: (1) **0% subscribed** = Shopify subscriptions only — Shopee/Lazada auto-delivery systems are not tracked in Shopify. (2) **14.4% repeat rate** = 306 customers with 2+ Shopify-visible orders ÷ 2,126 marketplace-first customers. Repeat purchases made exclusively on Shopee/Lazada without syncing to Shopify are not captured. There are 3,268 total marketplace-tagged Shopify orders across 2,126 customers (avg 1.54 orders/customer), confirming that repeat marketplace purchases do partially appear in Shopify via the integration. The relative channel comparison is valid as all channels are measured on the same Shopify-data basis.

### Cross-Sell LTV Staircase

| Products Bought | Customers | Repeat Rate | Avg LTV (SGD) |
|---|---|---|---|
| 1 product | 9,537 | 23.6% | S$170 |
| 2 products | 2,679 | 39.7% | S$230 |
| 3 products | 1,052 | **65.5%** | **S$470** |
| 4+ products | 512 | **88.7%** | **S$743** |

### Subscription Analysis

| Metric | Non-Subscriber | Subscriber | Uplift |
|---|---|---|---|
| Customers | 12,685 | 1,095 | — |
| Repeat rate | 28.7% | 74.4% | +159% |
| Avg LTV (SGD) | S$200 | S$532 | **+166%** |
| Avg orders | 1.74 | 4.86 | +179% |
| Avg lifespan | 93 days | 399 days | +329% |

**Churn data (Recharge, Apr 2025–Apr 2026):**

| Metric | Value |
|---|---|
| Total churned subscriptions | 526 |
| Peak churn cycle | Cycle 1 (30–60 days): 110 churns |
| #1 cancellation reason | "I already have more than I need" (143, 27%) |
| Reactivated customers | 50 |

### First-Order Discount Depth vs LTV

> Source: `EDA/outputs/05_discount_depth_bins.csv` — computed from `orders.parquet` + `customers.parquet`. Discount depth = `Price: Total Discount / Price: Total` on the customer's first order. Bins, counts, and rates all read dynamically (zero hardcoded values).

| First Order Discount | Customers | Repeat Rate | Avg LTV (SGD) |
|---|---|---|---|
| **Full price (0%)** | **9,398** | **36.4%** | **S$274** |
| 1–5% off | 186 | 17.7% | S$109 |
| 6–10% off | 395 | 26.1% | S$135 |
| 11–20% off | 1,250 | 25.5% | S$120 |
| 21–30% off | 458 | 25.5% | S$158 |
| 31–50% off | 1,189 | 23.0% | S$150 |
| **51%+ off** | **430** | **21.9%** | **S$92** |

> Full-price buyers: **−40% repeat rate drop** and **−66% LTV drop** vs 51%+ off buyers (S$274 vs S$92). Any discount hurts; a floor forms at ~22–26% RR regardless of depth. The 1–5% tier is small (n=186) and noisy.

### RFM Segments

| Segment | Customers | % of Base | Avg LTV (SGD) | Priority |
|---|---|---|---|---|
| Loyal | 4,359 | 31.6% | S$157 | Medium — cross-sell opportunity |
| Hibernating | 3,321 | 24.1% | S$112 | Low — mostly one-and-done |
| **At Risk** | **2,351** | **17.1%** | **S$514** | 🔴 **Urgent — highest LTV going dormant** |
| **Champions** | **1,828** | **13.3%** | **S$397** | 🔴 **Urgent — protect** |
| Can't Lose | 1,218 | 8.8% | S$66 | Low — very inactive |
| Promising | 688 | 5.0% | S$58 | Low — recent first-timers |

### Health Scorecard (Lens 5)

| KPI | Value | Status | Benchmark |
|---|---|---|---|
| Overall Repeat Rate | 32.4% | 🔴 ALERT | >35% |
| YoY Retention (latest year) | 7.8% | 🔴 ALERT | >40% |
| Avg 60-Day Cohort Retention | 18.1% | 🔴 ALERT | >20% |
| Acquisition Dependency | 51.9% | 🔴 ALERT | <50% (lower = better) |
| Top 20% Revenue Concentration | 78.1% | ✅ OK | <80% |

### Cohort Quality Decline (Lens 4)

| Cohort | Customers | 60d Retention | 365d Retention | Avg Y1 Revenue (SGD) |
|---|---|---|---|---|
| 2020 | 1,696 | 14.3% | **38.0%** | S$334 |
| 2021 | 3,334 | 15.0% | 28.1% | S$212 |
| 2022 | 1,462 | 13.8% | 25.9% | S$241 |
| 2023 | 873 | 13.5% | 25.8% | S$107 |
| 2024 | 2,015 | **16.1%** | 28.1% | S$99 |

> 365-day retention declined from 38% (2020 cohort) to 25.8% (2022–2023 cohorts). 2024 shows slight improvement. Y1 revenue per customer fell from S$334 to S$99 over the same period.

---

## 9. What Each Finding Relies On

| Presentation Finding | Primary Data Source | Parquet Table | Reliability | Limitation |
|---|---|---|---|---|
| 13,780 customers, 32.4% repeat | `1.customer_transaction` | `customers.parquet` | High | None |
| 18.1% 60-day retention | `1.customer_transaction` | `customers.parquet` + cohort calc | High | None |
| Revenue peaked S$848K in 2021 | `1.customer_transaction` + FX | `orders.parquet` | High | Fixed FX rate (±10% historical error) |
| 69.2% of 2024 orders discounted | `1.customer_transaction` | `orders.parquet` | High | None |
| Discount → lower LTV/repeat | `1.customer_transaction` | `orders.parquet` + `customers.parquet` | Medium-High | Correlation, not proven causation |
| Marketplace LTV gap (S$115 vs S$198) | `1.customer_transaction` | `customers.parquet` | Medium-High | Marketplace subscription tracking gap |
| Cross-sell LTV staircase | `1.customer_transaction` | `lines.parquet` + `customers.parquet` | Medium | Selection bias (loyal customers buy more naturally) |
| Subscriber LTV +166% | `1.customer_transaction` (Tags) | `customers.parquet` | High | Tags-based; 520 historical subscribers have no Recharge detail |
| Peak churn at Cycle 1 | `5.Recharge_data` | `rc_churned.parquet` | Medium | Apr 2025–Apr 2026 only; may not represent earlier behavior |
| #1 churn reason = stockpile | `5.Recharge_data` | `rc_churned.parquet` | Medium | Same temporal limitation |
| Discount code taxonomy | `3.Discounts` | `discounts.parquet` | Low-Medium | Standalone table; cannot link to individual orders |
| Facebook = 65% of web sessions | `4.Campaigns` | NOT in parquet | Low | No date, no customer ID — descriptive only |
