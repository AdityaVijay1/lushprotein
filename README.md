# LushProtein — Customer Analytics Project

**Markets:** Singapore + Malaysia + Hong Kong — all figures in SGD
**FX Applied:** 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD (5-year average rate, 2020–2026)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Data Sources](#3-data-sources)
4. [How to Run the EDA](#4-how-to-run-the-eda)
5. [EDA Findings](#5-eda-findings)
   - [5.1 Business at a Glance](#51-business-at-a-glance)
   - [5.2 Revenue and the Discount Problem](#52-revenue-and-the-discount-problem)
   - [5.3 Channel Quality](#53-channel-quality)
   - [5.4 Cross-Product LTV](#54-cross-product-ltv)
   - [5.5 Subscription Analysis](#55-subscription-analysis)
   - [5.6 Time-to-Second-Purchase](#56-time-to-second-purchase)
   - [5.7 Discount Sensitivity](#57-discount-sensitivity)
   - [5.8 RFM Customer Segments](#58-rfm-customer-segments)
   - [5.9 Prioritised Findings](#59-prioritised-findings)
6. [Data Quality Report](#6-data-quality-report)
7. [Entity Relationship Diagram — Notes](#7-entity-relationship-diagram--notes)
8. [Source-to-Target Mapping — Orders](#8-source-to-target-mapping--orders)
9. [Mid-Term Presentation Slide Guide](#9-mid-term-presentation-slide-guide)
10. [Charts Index](#10-charts-index)

---

## 1. Project Overview

**Company:** LushProtein
**Industry:** Direct-to-consumer (DTC) sports nutrition
**Founded:** 2013
**Core Markets:** Singapore, Malaysia; early presence in Hong Kong, Australia, Indonesia
**Go-to-market:** Digital-first DTC supported by community fitness events (Hyrox, pop-ups)

**Hero Products:**
| Product | Description |
|---|---|
| Lean Protein | Whey protein with prebiotics and probiotics; bubble tea-inspired flavours |
| Clear Protein | Refreshing fruity clear protein drink |
| Collagen Glow | Pure collagen peptides for hair, skin, and nails |

**The Core Business Problem:**
LushProtein successfully acquires new customers but retains very few. Currently **75% of first-time buyers never make a second purchase**. Repeat purchase rate sits at ~25–32%. High customer acquisition costs mean the business only breaks even after multiple orders, so retention is the primary driver of profitability and growth.

**The Single Most Important Metric:**
Getting first-time buyers to make a **second purchase within 60 days**. The second purchase is the strongest predictor of long-term customer lifetime value (LTV).

---

## 2. Repository Structure

```
LushProtein_Project_Data_20260505/
|
├── data/                            # Medallion Data Lake (canonical data)
│   ├── bronze/                      # Raw source catalog + supplemental refs
│   ├── silver/                      # Cleaned merged tables (was EDA/outputs/)
│   ├── gold/                        # Finals cohort + analytics (was EDA/outputs_finals/)
│   └── pipeline/                    # Bronze→Silver→Gold orchestrators
|
├── 1.customer_transaction/          # Bronze: Shopify order exports (gitignored)
├── 2.product_master/                # Bronze: product catalogue
├── 3.Discounts/                     # Bronze: promotional codes
├── 4.Campaigns/                     # Bronze: traffic data (not yet loaded)
├── 5.Recharge_data/                 # Bronze: subscription platform data
|
├── EDA/                             # Python analysis scripts (logic layer)
│   ├── 00_config.py                 # Paths — SILVER_DIR, GOLD_DIR, medallion
│   ├── 01_load_and_merge.py         # Bronze → Silver
│   ├── 02–12_*.py                   # Silver exports
│   ├── 13_build_finals_datasets.py  # Silver → Gold
│   ├── outputs/                     # Junction → data/silver/
│   ├── outputs_finals/              # Redirect → data/gold/ (see README there)
│   ├── decile_analysis/             # Gold analytics scripts
│   ├── category_analysis/           # Gold analytics scripts
│   └── aditya_findings/             # Gold analytics + recommendations
|
├── visualizations/                  # Presentation charts (reads Silver/Gold exports)
```

**Medallion docs:** `data/README.md` · **Run full pipeline:** `python data/pipeline/run_full_pipeline.py`

### Legacy structure (pre-medallion)

```
├── EDA/outputs/                     # → now data/silver/ (junction)
├── EDA/outputs_finals/              # → now data/gold/
```

---

## 3. Data Sources

| # | Folder | File(s) | Rows | Description |
|---|---|---|---|---|
| 1 | `1.customer_transaction` | 7 yearly Excel files (2020–2026) | 153,828 total rows (all line types) | Every Shopify order. Each row is one line type (Line Item, Transaction, Shipping Line, Discount, etc.) within an order. |
| 2 | `2.product_master` | `2_1.products_master_20260505.xlsx` | 167 | Full product catalogue — every SKU with price, COGS, and per-market availability. |
| 3 | `3.Discounts` | `3_1.discounts_export_*.csv` | 367 | All promotional codes with redemption counts, value type, and status. |
| 4 | `4.Campaigns` | `4_1.Sessions by referrer_*.csv` | 137,034 | Pre-aggregated web traffic by UTM and referrer. No date column; five years collapsed. |
| 5 | `5.Recharge_data` | 5 files (orders, checkout items, recurring items, churned subs, reactivated subs) | ~3,500 combined | Subscription platform data — first-purchase and renewal orders, cancellation reasons. |

**Key filtering rules:**
- Use `Top Row == 1` for **one row per order** (order-level analysis)
- Use `Line: Type == 'Line Item'` for **product-level analysis** (all line items)
- All revenue is FX-converted to SGD at load time — `Price: Total` in `orders.parquet` is always in SGD (1 SGD = 3.30 MYR, 1 SGD = 6.10 HKD, 5-year average 2020–2026)

---

## 4. How to Run the EDA

**Requirements:** Python 3.x, `pandas`, `openpyxl`, `pyarrow`, `matplotlib`, `seaborn`

```bash
pip install pandas openpyxl pyarrow matplotlib seaborn
```

**Step 1 — Build the Parquet cache (run once, ~60 seconds)**
```bash
cd EDA
python 01_load_and_merge.py
```

**Step 2 — Run all EDA analyses**
```bash
python run_eda.py --skip-load
```

**Step 3 — Generate all charts**
```bash
cd ../visualizations
python run_visualizations.py
```

Charts are saved to `visualizations/charts/` as PNG files at 150 dpi.

---

## 5. EDA Findings

### 5.1 Business at a Glance

| Metric | Value |
|---|---|
| Unique customers (2020–2026) | 13,780 |
| Total orders | 27,350 |
| Overall repeat purchase rate | **32.4%** |
| 60-day retention rate | **18.3%** |
| Median days to 2nd order | 49 days |
| Subscriber avg LTV vs non-subscriber | **+166%** (S$532 vs S$200, combined SGD) |
| Ever-subscribed customers | 1,095 (7.9% of all customers) |

> **What this means:** Nearly 6 in 10 first-time buyers never return within 60 days — the window when product biology begins delivering results and when almost all loyalty decisions are made. The overall 32.4% repeat rate includes late returners; the 60-day rate is the operationally critical number.

---

### 5.2 Revenue and the Discount Problem

| Year | Revenue (SGD, combined) | % Orders Discounted | Discounts as % of Gross |
|---|---|---|---|
| 2020 | **S$456,952** | 0% | 0% |
| 2021 | **S$847,930** | 0% | 0% ← Peak |
| 2022 | **S$747,587** | 15.2% | 3.9% |
| 2023 | **S$182,038** | 59.3% | 15.1% |
| 2024 | **S$284,971** | 69.2% | 30.9% |
| 2025 | **S$409,152** | 49.6% | 35.2% |

> **FX note:** All figures are SG + MY + HK combined in SGD (1 SGD = 3.30 MYR, 5-year average 2020–2026). Previous figures (S$1.86M in 2021) mixed MYR as SGD — those were incorrect.

Revenue peaked at **S$848K in 2021 across both SG and MY markets with zero discounting**. MY was near-equal to SG at peak (S$441K vs S$407K) and has since collapsed. Since 2022, discount rates climbed to 69% of orders in 2024 while combined revenue has not recovered. The 2023 collapse coincides with the first aggressive discounting campaigns.

> **Chart:** `01a_revenue_discount_trend.png`

---

### 5.3 Channel Quality

| Channel | Customers | Repeat Rate | Avg LTV (SGD) | % Subscribed (Shopify) |
|---|---|---|---|---|
| Subscription | 4,275 | **40.9%** | S$343 | 18.8% |
| Direct / Organic | 6,920 | **33.5%** | S$198 | 3.8% |
| Paid Social | 382 | 19.4% | S$71 | 6.0% |
| Affiliate | 26 | 19.2% | S$94 | 3.8% |
| **Marketplace** | **2,126** | **14.4%** | **S$115** | **0.0%*** |
| Email | 48 | 12.5% | S$50 | 2.1% |

> **\* Marketplace metric notes:**
> - **0% subscribed** = Shopify subscriptions only. Shopee/Lazada operate independent auto-delivery systems not tracked in Shopify.
> - **14.4% repeat rate** = customers with 2+ Shopify-visible orders ÷ 2,126 marketplace-first customers (306 repeaters). Repeat purchases made exclusively on Shopee/Lazada without syncing to Shopify are not captured. Evidence of partial sync: there are 3,268 total marketplace-tagged Shopify orders for 2,126 customers (avg 1.54/customer) — if only first-time orders were synced, the count would be exactly 2,126. All channels are compared on the same Shopify-data basis, making the relative comparison valid.

**Marketplace is a structural problem.** 2,126 customers (15% of base) deliver:
- 1.7× lower LTV than Direct/Organic (S$115 vs S$198)
- 2.3× lower repeat rate (14.4% vs 33.5%)
- No confirmed Shopify subscription conversion


> **Charts:** `02a_retention_by_channel.png`, `05b_marketplace_vs_website.png`

---

### 5.4 Cross-Product LTV

| Products Purchased | Customers | Repeat Rate | Avg LTV (SGD) |
|---|---|---|---|
| 1 product | 9,537 | 23.6% | S$170 |
| 2 products | 2,679 | 39.7% | S$230 |
| 3 products | 1,052 | **65.5%** | **S$470** |
| 4+ products | 512 | **88.7%** | **S$743** |

**Cross-selling is the single highest-ROI retention lever in the dataset.** Moving a customer from 1 to 3 product categories:
- Raises repeat rate from 23.6% → 65.5% (+178%)
- Raises avg LTV from S$170 → S$470 (+176%)

**Top cross-purchase combinations (all customers — computed dynamically from `lines.parquet`):**
1. Lean Protein (104 customers — single-product)
2. Lean Protein + Other (80 customers)
3. Clear Protein (76 customers — single-product)
4. Accessories + Clear Protein + Lean Protein (69 customers) — highest multi-product combo

This is a supply-side insight, not a demand-side problem: customers who are exposed to multiple products become loyal. The implication is a strong cross-sell sequence after first purchase.

> **Charts:** `03a_cross_product_ltv.png`, `03d_top_product_combos.png`

---

### 5.5 Subscription Analysis

**Subscriber vs Non-Subscriber Comparison:**

| Metric | Subscriber | Non-Subscriber | Uplift |
|---|---|---|---|
| Repeat rate | **74.4%** | 28.7% | +159% |
| Avg LTV (SGD) | **S$532** | S$200 | **+166%** |
| Avg orders | 4.86 | 1.74 | +179% |
| Avg lifespan (days) | 399 | 93 | +329% |

**Subscription churn is high and concentrated early:**

| Subscription Cycle (~30 days each) | Cancellations |
|---|---|
| Cycle 0 (< 30 days) | 60 |
| **Cycle 1 (30–60 days)** | **110** (peak churn) |
| Cycle 2 (60–90 days) | 101 |
| Cycle 3 (90–120 days) | 81 |
| Total in first 60 days | **244 of 526** = **46.4% of all cancellations** |

**Raw subscription churn rate: 64.7%** (347 of 536 checkout subscribers eventually cancelled)

**Top cancellation reasons:**

| Reason | Count | % |
|---|---|---|
| I already have more than I need | 143 | **31.9%** |
| Other reason | 131 | 29.2% |
| I no longer use this product | 88 | 19.6% |
| Created by accident | 40 | 8.9% |
| This is too expensive | 19 | 4.2% |
| I need it sooner | 14 | 3.1% |
| Want a different product | 5 | 1.1% |

> **Key insight:** The #1 cancellation reason ("already have more than I need") is not a product dissatisfaction problem — it is a **cadence mismatch**. A 30-day delivery interval accumulates product faster than many customers consume it, leading to stockpiling and cancellation. The fix is a flexible 45/60-day interval option and a prominent skip-delivery flow — not a retention email.
>
> **Win-back rate:** 43 of 347 churned subscribers reactivated (12.4%). Median time to reactivation: 112 days.

> **Charts:** `04a_subscriber_vs_onetime.png`, `04b_churn_by_cycle.png`, `04c_cancellation_reasons.png`, `04d_churn_tenure_distribution.png`

---

### 5.6 Time-to-Second-Purchase

Of 13,780 total customers, **4,459 (32.4%) ever placed a second order.**

| Days Window | Repeaters in Window | Cumulative % of All Repeaters |
|---|---|---|
| 0–7 days | 336 | 7.5% |
| 8–14 days | 222 | 12.5% |
| 15–30 days | 568 | 25.3% |
| 31–60 days | 692 | 40.8% |
| **61–90 days** | **461** | **51.1%** |
| 91–180 days | 603 | 64.6% |
| 181–365 days | 450 | 74.7% |
| 365+ days | 463 | 85.1% |

**Key percentiles:**
- P25: 11 days
- **P50 (median): 49 days**
- P75: 141 days
- P90: 376 days

> **What this means:** ~41% of customers who ever come back do so within 60 days. After 60 days without a second order, the probability of natural repurchase declines sharply. The first 60 days after first purchase is the retention-critical window — aligned with product biology (a standard serving lasts ~4–8 weeks).

> **Chart:** `02c_time_to_second_purchase.png`

---

### 5.7 Discount Sensitivity

| First-Order Discount Depth | Customers | Repeat Rate | Avg LTV (SGD) |
|---|---|---|---|
| **Full price (0%)** | **9,398** | **36.4%** | **S$274** |
| 1–5% off | 186 | 17.7% | S$109 |
| 6–10% off | 395 | 26.1% | S$135 |
| 11–20% off | 1,250 | 25.5% | S$120 |
| 21–30% off | 458 | 25.5% | S$158 |
| 31–50% off | 1,189 | 23.0% | S$150 |
| **51%+ off** | **430** | **21.9%** | **S$92** |

Source: `EDA/outputs/05_discount_depth_bins.csv` — all values dynamically computed.

Full-price first-order customers repeat at **36.4%** with **S$274 avg LTV**.
Customers acquired at 51%+ discount repeat at only **21.9%** with **S$92 avg LTV** — a **+66% repeat rate advantage and +198% LTV advantage for full-price buyers**.

Any discount immediately pulls the repeat rate into the low-to-mid 20s. The LTV damage is consistent across all discount depths — from S$274 (full price) down to S$92 (51%+). The 1–5% tier is small (n=186) and noisy but confirms the pattern.

> **Bottom line:** Every promotional campaign that uses deep discounts (>20% off) is acquiring cohorts that are materially less loyal and less profitable over time. The brand is spending margin to attract weaker customers.

> **Chart:** `05a_discount_depth_impact.png`

---

### 5.8 RFM Customer Segments

RFM scores each customer on Recency (how recently they bought), Frequency (how often), and Monetary value (how much they spent), producing 1–4 scores on each dimension.

| Segment | Customers | % of Base | Avg LTV (SGD) | Avg Orders | Priority Action |
|---|---|---|---|---|---|
| Loyal | 4,359 | 31.6% | S$157 | 1.9 | Cross-sell to second product |
| Hibernating | 3,321 | 24.1% | S$112 | 1.0 | Low-cost reactivation attempt |
| **At Risk** | **2,351** | **17.1%** | **S$514** | 3.4 | **Win-back NOW — highest LTV going quiet** |
| **Champions** | **1,828** | **13.3%** | **S$397** | 3.2 | **Protect — early access, loyalty perks** |
| Can't Lose | 1,218 | 8.8% | S$66 | 1.0 | Final re-engagement attempt |
| Promising | 688 | 5.0% | S$58 | 1.0 | Nurture to 2nd order |
| New | 15 | 0.1% | S$67 | 1.0 | Welcome sequence |

**At Risk (2,351 customers, S$514 avg LTV)** — These customers have proven they will spend significantly but have gone quiet. They represent the highest-urgency reactivation opportunity in the base.

> **Chart:** `05c_rfm_segments.png`

---

### 5.9 Prioritised Findings

| Rank | Finding | Key Evidence | Confidence | Suggested Experiment |
|---|---|---|---|---|
| 1 | **Deep discounting destroys cohort quality** | Full-price: 36.4% repeat, S$274 LTV vs 51%+ off: 21.9% repeat, S$92 LTV (+66% RR, +198% LTV advantage for full-price buyers) | High | Cap new-customer discount at 15%; remove 50%+ deals |
| 2 | **Cross-sell is the #1 LTV lever** | 3-product buyers: 65.5% repeat, S$470 LTV (+176% vs 1-product) | High | Post-purchase cross-sell email at Day 21 post-first-order |
| 3 | **At Risk segment = urgent high-value opportunity** | 2,351 customers, S$514 avg LTV, currently dormant | High | Targeted win-back with strongest offer |
| 4 | **Subscription cadence causes stockpile churn** | 27% cancel "already have too much"; peak churn at Cycle 1 (30–60 days) | High | Add 45/60-day interval option + skip-delivery button |
| 5 | **Marketplace cannibalises LTV** | 14.4% repeat vs 33.5% direct; 1.7× LTV gap (S$115 vs S$198) | Medium | Reduce marketplace SKU range; redirect paid budget to own site |

---

## 6. Data Quality Report

*This section supports Deliverable 1: Mid-Term PDF Report.*

### 6.1 Discrepancies Found

| ID | Issue | Location | Magnitude | Counter-Measure |
|---|---|---|---|---|
| DQ-01 | **94.9% null rate on `Browser: UTM Source`** | orders — all years | 25,941 of 27,350 orders have no UTM | Channel classified using `Tags` field as fallback (marketplace keywords, subscription tags). UTM-only analysis limited to 5.1% of orders with data. |
| DQ-02 | **62.3% null rate on `Tags` column** | orders — all years | 17,034 orders with no tag | Nulls treated as "Direct / Organic" after excluding marketplace and subscription signals. Flagged as classification limitation. |
| DQ-03 | **3.9% null rate on `Shipping: Country`** | orders | 1,065 orders | Excluded from country-level analysis only. Retained in all other analyses. |
| DQ-04 | **1,617 orders with `Price: Total = 0`** (free/gifted orders) | orders | 5.9% of all orders | Retained in order counts but excluded from revenue and LTV calculations. |
| DQ-05 | **4.3% Recharge orders unmatched to Shopify** (export-timing gap) | Recharge ↔ Shopify join on `shopify_order_id` | 52 of 1,215 Recharge orders | Documented as timing gap — Shopify exported Mar 31, Recharge Apr 7. Not a data error. Excluded from joined analyses. |
| DQ-06 | **Mixed currencies: SGD (59%), MYR (41%), HKD (<1%)** | `Price: Total` — orders | 11,311 orders in MYR/HKD | **FX conversion applied at load time**: 1 SGD = 3.30 MYR, 1 SGD = 6.10 HKD. All `Price: Total` and discount columns converted to SGD before saving to Parquet. Currency = "SGD" for all orders post-conversion. Fixed rates introduce ≤10% historical error; directional findings unaffected. |
| DQ-07 | **49.3% of Top Row orders have unclassifiable product category** | `Line: Product Handle` on Top Row filter | 13,484 of 27,350 classified as "Unknown" | Top Row captures only the first line item. Multi-item orders may have hero products on non-top rows. Product analysis uses Lines table (50,963 rows, all line items) instead. |
| DQ-08 | **Old SKUs (pre-2022) absent from product master** | `2_1.products_master` | Affects product name lookups for early cohorts | Product classification done by handle keyword matching (not master join) to maintain continuity across all years. |
| DQ-09 | **Affiliate codes replaced with synthetic IDs (AFFILIATE_001–009)** | `3.Discounts` — code names | 7 codes anonymised | Grouped into "Affiliate" category. PII removed by data provider before delivery. |
| DQ-10 | **45.4% of discount codes have 0 uses (draft/test codes)** | `3.Discounts` | 204 of 367 codes never used | Filtered to `Times Used In Total > 0` (163 active codes) for all discount analyses. |

### 6.2 Data-Quality Checks Performed

| Check | Method | Result |
|---|---|---|
| Duplicate order IDs | Grouped by `order_id` after `Top Row == 1` filter | 0 duplicates — **clean** |
| Null primary keys | Count of null `customer_id` and `order_id` | 0 nulls — **clean** |
| Negative prices | Count of `Price: Total < 0` | 0 rows — **clean** |
| Date range validity | Min/max of `Processed At` | 2020-01-01 to 2026-03-31 — **expected** |
| Recharge join coverage | Left join Recharge → Shopify on `shopify_order_id` | 95.7% match rate — 4.3% gap explained by export timing |
| Multi-currency isolation | Group by `Currency` before revenue aggregation | SGD / MYR / HKD isolated correctly |
| Subscription tag consistency | Cross-check `Tags='Subscription Order'` vs Recharge data | Recharge: 536 checkout subscribers; Shopify tags: 1,095 ever-subscribed. Difference explained by multi-period subscriptions and Yotpo Subscriptions app. |

---

## 7. Entity Relationship Diagram — Notes

*This section supports Deliverable 2: ERD in draw.io.*

Draw 9 entities. Place **Customer** at the centre. Radiating out: Orders (one-to-many), Lines (via Orders, one-to-many), Products (many Lines reference one Product via SKU). Recharge tables cluster separately, bridged through `shopify_order_id → order_id`. Campaigns is a standalone entity (no FK join possible).

| Entity | Primary Key | Key Foreign Keys | Relationship |
|---|---|---|---|
| customers *(derived)* | `customer_id` | — | 1 customer → many orders |
| orders *(1_1 to 1_7)* | `order_id` (ID) | `customer_id` | 1 order → many lines |
| lines *(from orders)* | `order_id` + `Line: ID` | `order_id`, `Line: SKU` → products | Many lines → 1 order |
| products_master | `Variant SKU` (variant), `Handle` (product) | — | 1 product → many lines |
| discounts | `Name` (code string) | Linked to orders via `Tags` (no hard FK) | 1 code → many orders |
| campaigns | Composite (all 8 dimension columns) | None (standalone) | Pre-aggregated; no order join |
| rc_orders | `recharge_order_id` | `shopify_order_id` → orders.order_id, `customer_id` | 1 Recharge order → 1 Shopify order |
| rc_checkout / rc_recurring | `recharge_order_id` + `product_sku` | `recharge_order_id` → rc_orders | Many items → 1 Recharge order |
| rc_churned | `subscription_id` | `customer_id`, `product_id` | Many churned subs → 1 customer |
| rc_reactivated | `customer_id` | `customer_id` → customers | Subset of previously churned customers |

---

## 8. Source-to-Target Mapping — Orders

*This section supports Deliverable 3: Source-to-Target Mapping (Excel).*

The `LushProtein_Source_to_Target_Mapping_Exercise.xlsx` file has Sheet 2 (products_master) completed as a reference example. Fill in Sheet 1 (1.orders) using the mapping below.

**Three non-obvious transformation rules the marker will look for:**
1. `Top Row == 1` filter for order-level grain vs `Line: Type == 'Line Item'` for product-level grain — same file, different row filters, different analytical grain
2. `store` is a **derived column** from the `Name` prefix — it does not exist as a raw column
3. `Price: Total` must never be summed across SGD and MYR — currency must be isolated first

| target_column | target_data_type | pk_fk | source_column | source_data_type | transformation | notes / business rule |
|---|---|---|---|---|---|---|
| `order_id` | STRING (id) | PK | `ID` | id (13-digit) | Filter `Top Row = 1`; cast STRING | Shopify order PK. 13-digit numeric. Join target for all FKs. |
| `order_name` | STRING | — | `Name` | text | Direct copy | Human-readable order number. Prefix encodes store: LP=SG, LPSG=SG subscription, LPMY=Malaysia, LPHK=Hong Kong |
| `order_date` | DATETIME | — | `Processed At` | datetime+tz | Parse to UTC; convert to Asia/Singapore for display | Use `Processed At` not `Created At` — reflects actual payment processing time |
| `customer_id` | STRING (id) | FK → customers | `Customer: ID` | id (13-digit) | Filter `Top Row = 1`; cast STRING | Links to customer entity. 0% null after Top Row filter. |
| `store` | STRING (cat) | — | `Name` (derived) | text | CASE: starts with LPMY→MY, LPHK→HK, LPSG/LP→SG | **Derived column** — does not exist as a raw field. |
| `currency` | STRING (cat) | — | `Currency` | text | Direct copy | SGD (55%), MYR (45%), HKD (<1%). Never aggregate across currencies. |
| `total_price` | DECIMAL | — | `Price: Total` | decimal | Direct copy | Total charged including shipping. In order currency. |
| `total_discount` | DECIMAL | — | `Price: Total Discount` | decimal | Direct copy; fill null → 0 | 5.9% of orders have total = 0 (free/gifted orders). |
| `total_shipping` | DECIMAL | — | `Price: Total Shipping` | decimal | Direct copy; fill null → 0 | — |
| `payment_status` | STRING (cat) | — | `Payment: Status` | text | Direct copy; filter to paid / partially_refunded | Values: paid (99.6%), partially_refunded (0.4%) |
| `fulfillment_status` | STRING (cat) | — | `Order Fulfillment Status` | text | Direct copy | fulfilled / partial / null. Exclude restocked rows. |
| `tags` | STRING | — | `Tags` | text (comma-list) | Direct copy; parse for subscription / marketplace signals | 62.3% null. Key values: Subscription Order, FIRST_ORDER, shopee, lazada, Recurring Order #N |
| `utm_source` | STRING | — | `Browser: UTM Source` | text | Direct copy | 94.9% null. Present only for paid/tracked traffic. |
| `utm_medium` | STRING | — | `Browser: UTM Medium` | text | Direct copy | Companion to utm_source |
| `utm_campaign` | STRING | — | `Browser: UTM Campaign` | text | Direct copy | Campaign name string |
| `shipping_country` | STRING | — | `Shipping: Country` | text | Direct copy | 3.9% null. Top values: Malaysia (52%), Singapore (41%) |
| `cancelled_at` | DATETIME | — | `Cancelled At` | datetime | Parse datetime; null = not cancelled | 89.2% null (most orders fulfilled) |
| `line_id` | STRING (id) | PK (line-level) | `Line: ID` | id | Filter `Line: Type = 'Line Item'` | Line-level PK. Use for product analysis. |
| `line_product_handle` | STRING | FK → products | `Line: Product Handle` | text (slug) | Filter `Line: Type = 'Line Item'`; direct copy | URL slug. Join to products_master on Handle. |
| `line_sku` | STRING | FK → products | `Line: SKU` | text | Filter `Line: Type = 'Line Item'`; cast STRING | Variant-level FK. Join to products_master on Variant SKU. |
| `line_title` | STRING | — | `Line: Title` | text | Direct copy | Product display name on the order |
| `line_quantity` | INT | — | `Line: Quantity` | int | Cast INT | Units purchased for this line |
| `line_price` | DECIMAL | — | `Line: Price` | decimal | Direct copy | Price per unit before line-level discount |
| `line_discount` | DECIMAL | — | `Line: Discount` | decimal | Direct copy; fill null → 0 | Line-level discount amount |
| `line_total` | DECIMAL | — | `Line: Total` | decimal | Direct copy | Actual revenue for this line after discount |

---

## 9. Mid-Term Presentation Slide Guide

*This section supports Deliverable 4: Mid-Term Group Presentation Slides.*

Recommended 14-slide structure:

| Slide | Title | What to Show | Chart to Use |
|---|---|---|---|
| 1 | Title Slide | Team name, company, date | — |
| 2 | Project Overview | LushProtein products, core problem (75% churn), key metric (2nd purchase in 60 days) | — |
| 3 | Data Sources Overview | 9 tables, row counts, date range, ERD thumbnail | ERD from draw.io |
| 4 | Data Quality Findings | Top 5 DQ issues (DQ-01 through DQ-05), counter-measures applied | — |
| 5 | Business at a Glance | 5 KPI numbers: customers, repeat rate, 60-day retention, median days to 2nd order, sub LTV uplift | `01a_revenue_discount_trend.png` |
| 6 | Revenue and the Discount Problem | Revenue peaked 2021 at zero discounting; 49.6% of orders discounted in 2025 (35.2% of gross revenue); revenue not recovered | `01a_revenue_discount_trend.png` + `01b_monthly_revenue_2024_2026.png` |
| 7 | Not All Customers Are Equal | Channel quality — Marketplace vs Direct LTV and repeat rate gap | `02a_retention_by_channel.png` + `05b_marketplace_vs_website.png` |
| 8 | The Cross-Sell Opportunity | LTV staircase (1 → 4 products). +171% LTV uplift. | `03a_cross_product_ltv.png` |
| 9 | Subscription: High Value, High Churn | Sub vs non-sub metrics; churn by cycle; top cancellation reason | `04a_subscriber_vs_onetime.png` + `04b_churn_by_cycle.png` + `04c_cancellation_reasons.png` |
| 10 | Discount Depth Destroys Loyalty | Full-price (36.4% RR, S$274 LTV) vs 51%+ off (21.9% RR, S$92 LTV) — +66% RR and +198% LTV for full-price buyers | `05a_discount_depth_impact.png` |
| 11 | Customer Segments (RFM) | RFM pie + priority action table; At Risk and Can't Lose are urgent | `05c_rfm_segments.png` |
| 12 | Time-to-Second-Purchase | Distribution histogram; ~41% of repeaters return within 60 days | `02c_time_to_second_purchase.png` |
| 13 | Top Findings and Proposed Experiments | Findings table (ranked 1–6) with suggested experiments | — |
| 14 | Next Steps | Further analyses to run; what experiments to propose for final submission | — |

**Highest-impact charts for visual storytelling:**
- `03a_cross_product_ltv.png` — the LTV staircase (most striking visual)
- `04b_churn_by_cycle.png` — the churn danger zone
- `05a_discount_depth_impact.png` — the LTV V-drop by discount depth
- `02a_retention_by_channel.png` — channel side-by-side comparison

---

## 10. Charts Index

All charts are in `visualizations/charts/`. Regenerate with `python run_visualizations.py`.

| File | Description |
|---|---|
| `01a_revenue_discount_trend.png` | Annual revenue bars with discount rate overlay (dual axis) |
| `01b_monthly_revenue_2024_2026.png` | Month-by-month revenue line with annotated spikes |
| `01c_orders_customers_by_year.png` | Orders vs unique customers side-by-side by year |
| `02a_retention_by_channel.png` | Repeat rate + LTV horizontal bars per channel |
| `02b_retention_by_product.png` | Repeat rate, avg LTV, median days to 2nd by hero product |
| `02c_time_to_second_purchase.png` | Days-to-2nd-purchase histogram with cumulative line and 60-day marker |
| `02d_cohort_60d_retention.png` | Monthly cohort 60-day retention coloured by performance tier |
| `03a_cross_product_ltv.png` | LTV staircase bars + repeat rate line by product breadth |
| `03b_product_revenue_mix.png` | Revenue donut + avg unit price comparison |
| `03c_sku_loyalty.png` | Checkout vs recurring customer counts per SKU with loyalty ratio |
| `03d_top_product_combos.png` | Most common cross-category purchase combinations |
| `04a_subscriber_vs_onetime.png` | Subscriber vs non-subscriber metric comparison (indexed) |
| `04b_churn_by_cycle.png` | Cancellations by subscription cycle with 30–60 day danger zone shaded |
| `04c_cancellation_reasons.png` | Horizontal bar of cancellation reasons with themed annotations |
| `04d_churn_tenure_distribution.png` | How long customers subscribed before cancelling |
| `05a_discount_depth_impact.png` | Repeat rate + LTV drop by first-order discount depth |
| `05b_marketplace_vs_website.png` | Indexed channel comparison + country order mix donut |
| `05c_rfm_segments.png` | RFM bubble chart + priority action bar |
| `05d_discount_code_taxonomy.png` | Discount code redemptions by type (donut) |

---

*Last updated: May 2026 · ISSS603 Science of Customer Analytics · SMU*
