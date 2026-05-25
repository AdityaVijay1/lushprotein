# LushProtein — Full Project Context Prompt

> Paste this entire file into a new Cursor session to restore complete project context.
> Last updated: **May 26, 2026**

---

## 1. WHO IS THE CLIENT AND WHAT IS THE PROBLEM?

**LushProtein** is a direct-to-consumer (DTC) protein supplement brand operating across **Singapore (SG), Malaysia (MY), and Hong Kong (HK)** via a Shopify storefront. Their primary products are flavoured protein powders (Clear Protein, Lean Protein, Soy Protein), creatine, and collagen supplements.

**The core business problem:**
- 67.6% of customers buy exactly once and never come back ("one-and-done")
- The founder wants to understand **who the loyal repeaters are**, **what makes them come back**, and **how to grow that segment**
- There is no systematic understanding of which products drive loyalty, which acquisition channels produce the best long-term customers, or what the actual economic value of improving retention looks like

**What LushProtein wants from this project:**
1. Understand their customer base rigorously — retention rates, LTV by channel and cohort, discount impact
2. Identify loyal repeaters and the *factors* that create them (subscription, cross-sell, entry product, channel)
3. Get SKU- and flavor-level product insights — the founder cares deeply about specific products, NOT category aggregates
4. Know which products are discontinued (archived vs draft), their historical value, and reorder patterns
5. Quantify business value opportunities (conservative and potential) with real math
6. Understand the data quality issues in their Shopify export and how they were handled

---

## 2. ACADEMIC CONTEXT

**Course:** ISSS603 Science of Customer Analytics — SMU, Semester 5
**Team:** Group 1 — Aditya Vijay, Emily Pham Vinh Tan, Saelin Lee, Shwe Tin Aung, Weilin Ang, Zhengfeng Toh
**Framework:** Bruce, Fader & Ross — *Customer-Base Audit* (2022) — **Five Lenses** on the customer×time face of the data cube
- Lens 1: Heterogeneity (VTD decile concentration)
- Lens 2: Activity/inactivity
- Lens 3: VTD stability across cohorts
- Lens 4: Vintage comparison (acquisition year quality)
- Lens 5: Base health scorecard

**Deliverables:**
- Midterm PDF report (data quality + EDA) — submitted May 2026
- Finals presentation to LP founder + instructor — in progress
- Finals written report — in progress

**Workspace:**
`C:\Users\adity\Documents\Aditya SMU\SMU Sem 5\Lush Protein SMU X\LushProtein_Project_Data_20260505\`
**Git branch:** `aditya_changes`

---

## 3. THE DATA

### Source datasets
| # | Folder | Contents | Used? |
|---|--------|----------|-------|
| 1 | `1.customer_transaction/` | 7 yearly Shopify order Excel exports (2020–2026); 153,828 raw rows → **27,350 orders + 50,963 line items** | ✅ Primary |
| 2 | `2.product_master/` | `2_1.products_master_20260505.xlsx` — 167 variants, SKU names, prices, status (active/draft/archived), COGS (65% null) | ✅ |
| 3 | `3.Discounts/` | 367 discount codes with redemption counts; **cannot be joined to orders** (no discount code column in order export) | ✅ Standalone only |
| 4 | `4.Campaigns/` | 137,033 session rows by referrer; **no date, no customer/order ID** — cannot join to orders | ❌ Not loaded |
| 5 | `5.Recharge_data/` | 5 files covering Apr 2025–Apr 2026 subscription data (1,215 orders, churn reasons, reactivations) | ✅ |

### Three currencies — one critical issue
All three stores export revenue in their local currency (SGD, MYR, HKD). **Fixed FX rates applied at load:**
- `1 SGD = 3.30 MYR` | `1 SGD = 6.10 HKD` — 5-year average (2020–2026)
- Applied ONCE in `EDA/01_load_and_merge.py`; never re-converted downstream
- **All revenue figures in this project are in SGD**

### Canonical analytical tables (after `01_load_and_merge.py`)
| Table | Rows | What it is |
|-------|------|------------|
| `orders.parquet` | **27,350** | 1 row per order — revenue (SGD), channel, discount, date, store, customer |
| `lines.parquet` | **50,963** | 1 row per line item — SKU, product handle, variant, line revenue |
| `customers.parquet` | **13,780** | 1 row per customer — total_orders, total_revenue, first channel, RFM fields |
| `products.parquet` | **167 variants** | Handle, SKU, status, prices by market, COGS |

---

## 4. KEY FINDINGS (What We Know)

### 4.1 The retention problem
| Metric | Value |
|--------|-------|
| One-time buyers | **9,321 (67.6%)** |
| Repeat rate (≥2 orders) | **32.4%** |
| 60-day cohort retention | **18.1%** |
| Customers with 10+ orders | 268 (1.9%) |
| Max orders (one customer) | 667 — likely reseller |

Revenue is **right-skewed**: mean S$226, median S$67. Top decile (D10) holds ~66% of total LTV.

### 4.2 Revenue history and the discount problem
| Year | Orders | Revenue (SGD) | Notes |
|------|--------|---------------|-------|
| 2020 | 2,847 | S$457K | Zero discounting |
| 2021 | 6,259 | **S$848K peak** | Zero discounting |
| 2022 | 3,710 | S$748K | Discounting introduced |
| 2023 | 2,253 | S$182K | Revenue collapse |
| 2024 | 4,261 | S$285K | Recovery; heavy discounting |
| 2025 | 6,407 | S$409K | Highest order volume; heavy discounting continues |

**The association:** Revenue peaked when there was zero discounting. As discount depth increased, per-cohort quality (LTV, repeat rate) declined. This is a correlation — not proven causation — but the pattern is consistent across multiple analytical cuts.

### 4.3 LTV by acquisition channel (full customer base, clean order set)
| Channel | Customers | Avg LTV | Repeat rate | Sub rate |
|---------|-----------|---------|-------------|---------- |
| Subscription | 4,275 | **S$315** | 39.3% | 18.8% |
| Direct / Organic | 6,920 | S$185 | 30.9% | 3.8% |
| Marketplace (Shopee/Lazada) | 2,126 | S$115 | 14.3% | 0.0%* |
| Paid Social | 382 | S$71 | 17.8% | 6.0% |

*Marketplace 0% subscription reflects Shopify's data limits — Shopee/Lazada subscriptions run on their own platforms and don't show in Shopify.

### 4.4 Loyal repeaters — who they are and what drives them
**Definition:** Loyal repeater = customer with 3+ total orders.

| Factor | Loyal (3+ orders) | One-and-done | Lift |
|--------|-------------------|--------------|------|
| 2+ unique product handles | 40.6% | 16.9% | **2.4×** |
| Ever subscribed | 26.0% | 3.4% | **7.7×** |
| First order full-price | 81.5% | 60.1% | 1.4× |
| 3+ unique product handles | 24.6% | 4.1% | **5.9×** |
| First order via web (not POS) | 99.4% | 96.2% | ~1× |

**Key insight:** Subscription and cross-sell (buying multiple product types) are the strongest predictors of loyalty. Speed to second purchase is NOT a differentiator — loyal customers and 2-order customers both return within ~49–54 days of their first order.

### 4.5 Targeting tiers (full customer base)
| Tier | Customers | Avg LTV | Avg orders | Recommended action |
|------|-----------|---------|------------|--------------------|
| **Tier 1:** Loyal + Subscribed | **581** | **S$907** | 7.6 | Protect; VIP offers |
| **Tier 2:** Loyal, not subscribed | **1,651** | **S$804** | 5.3 | Convert to subscription |
| **Tier 3:** 2-order customers | **1,972** | **S$185** | 2.0 | Push 3rd order + introduce 2nd product |
| **Tier 4:** One-and-done | **8,597** | **S$80** | 1.0 | Low ROI; win-back only if recent |
| Other (DQ-dropped orders) | 979 | S$0 | 0 | Excluded |

Total loyal repeaters (Tier 1 + 2): **2,232 customers**

### 4.6 On-site (POS) vs web customers
| Metric | POS first-order | Web first-order |
|--------|-----------------|-----------------|
| Customers | 370 | 2,717 |
| Repeat rate | 11.6% | 27.7% |
| Avg LTV | S$78 | S$126 |
| % subscribed | 1.9% | 21.3% |

POS customers are almost entirely discounted (99.3% of POS orders have a discount) and have weak long-term outcomes.

### 4.7 Top revenue SKUs (2022+, finals-filtered, each SKU separate)
| Handle | Variant | SKU | Revenue | Customers |
|--------|---------|-----|---------|-----------|
| clear-protein | 500g Pack / Peach | `0724999807814` | S$45,811 | 532 |
| lean-protein | 1kg Pack / Thai Milk Tea | `LEAN-THA-1KG-V1` | S$33,210 | 275 |
| clear-protein | 500g Pack / White Grape | `0724999807807` | S$28,904 | 362 |
| clear-protein | 500g Pack / Peach (v2) | `CLEAR-PEA-500G-V2` | S$27,106 | 237 |
| lean-protein | 1kg Pack / Taro | `LEAN-TAR-1KG-V1` | S$20,888 | 205 |
| micronized-creatine | 250g Pack | `CRE-UNF-250G-V1` | S$11,525 | 192 |

### 4.8 Discontinued products
- `prime-whey-isolate` — **Status: archived** (intentionally delisted; product page hidden; no new orders possible) — ~S$84K historical revenue
- `better-whey` — **Status: draft** (unpublished; staging only; phased out) — ~S$232K historical revenue across multiple SKUs
- **NOTE:** `better-whey` (draft) is NOT the same as `better-whey-protein-elite` (active but excluded from finals analysis per LP)

**Shopify status definitions:**
- `archived` = product delisted; customer-facing page removed; no new purchases
- `draft` = product not published to storefront; internal only; effectively discontinued for customers

### 4.9 Reorder intervals (median days between repurchases, same SKU)
| SKU / Flavor | Repeat buyers | Median reorder days |
|-------------|---------------|---------------------|
| clear-protein / Peach 500g | 81 | **54 days** |
| clear-protein / White Grape 500g | 48 | **54 days** |
| collagen-glow / Unflavoured | 40 | **42 days** |
| lean-protein / Thai Milk Tea 1kg | 39 | **35 days** |
| creatine / 250g | 37 | **66 days** |

### 4.10 Business value scenarios (gross profit uplift, 40% margin proxy)
| Opportunity | Conservative | Potential |
|-------------|-------------|-----------|
| Cross-sell: 5% of 1-product → 3-product | S$17,752 | — |
| Retention win-back (2024–25 lapsed) | S$40,727 (10%) | S$61,091 (15%) |
| Subscription conversion | S$88,375 (5%) | S$220,937 (12.5%) |
| Marketplace LTV gap improvement | S$2,964 (5%) | S$8,892 (15%) |

---

## 5. DATA QUALITY — WHAT WE FOUND AND HOW IT'S HANDLED

### 5.1 Overview
Full detail in `DATA_QUALITY_REPORT_FINAL.md` (914 lines). Summary of key issues:

| ID | Issue | Severity | How handled |
|----|-------|----------|-------------|
| DQ-01 | Three currencies in one export | HIGH | Fixed FX at load in `01_load_and_merge.py` |
| DQ-02 | 336 zero-revenue, zero-discount orders | MEDIUM | Retained in midterm; **DROPPED in finals layer** |
| DQ-03 | 1,281 orders where full value discounted (free gifts/referrals) | MEDIUM | Retained in midterm; **DROPPED in finals layer** |
| DQ-04 | 78 wholesale/bulk orders (tagged `wholesale-sale` or >S$5K) | MEDIUM | Retained in midterm; **DROPPED in finals layer** |
| DQ-05 | 94.9% of orders missing UTM source | MEDIUM | Tags-based `classify_channel()` fallback |
| DQ-06 | Raw export mixes order-header rows and line-item rows | HIGH | `Top Row=1` filter for orders; `Line: Type=Line Item` for lines |
| DQ-07 | 2 orders: subscription tag vs flag mismatch | LOW | Negligible; use `is_subscription` flag |
| DQ-08 | Marketplace 0% subscription; 14.4% repeat may undercount | MEDIUM | Annotated in all channel slides |
| DQ-09 | Campaigns file (137K sessions) has no date/customer ID | LOW | Not loaded; order-level UTM used instead |
| DQ-10 | Discount code not on order rows (cannot join to Discounts export) | MEDIUM | Amount-based discount depth bins used |
| DQ-11 | Recharge export covers Apr 2025–Apr 2026 only; different IDs | MEDIUM | Shopify tags for subscriber LTV (full history) |
| DQ-12 | COGS null for 65% of SKUs in product master | MEDIUM | 40% gross margin proxy; labelled "profit proxy" |

**DQ-13 (POS not in Discounts export): REMOVED from report** — LP mentioned it without clarifying which dataset; POS analysis via `Source='pos'` in order export is valid and not a data quality issue.

### 5.2 Option B — Finals-layer drops
To preserve midterm deliverable integrity, the three problematic order types are dropped **only** in `EDA/12_finals_deep_dive.py`. The base `orders.parquet` (27,350 orders) is never modified.

```
DQ-02 drop: −336 orders (zero rev + zero disc)
DQ-03 drop: −1,281 orders (100%-discount free fulfilments)
DQ-04 drop: −78 orders (wholesale-sale tag OR Price: Total > S$5,000)
─────────────────────────────────────────
Finals clean order pool: 25,658 orders
```

After drops, `total_orders`, `total_revenue`, and `is_repeat` in the `cust` dataframe are **rebuilt** from the clean orders so all downstream stats reflect the consumer-only pool.

### 5.3 LushProtein Feedback Filters (LP-F01 to LP-F04)
These are **analytical scope decisions from LP** — NOT data errors. Applied only in `12_finals_deep_dive.py`:

| Label | Filter | Customers removed | Reason |
|-------|--------|-------------------|--------|
| LP-F01 | Exclude `better-whey-protein-elite` buyers | 167 | Bulk product; not core consumer |
| LP-F02 | Exclude Jul/Nov acquisitions | 2,818 | Birthday + BFCM promo distortion |
| LP-F03 | Analysis window: 2022-01-01+ | 5,016 | Pre-2022 = market experimentation phase |
| LP-F04 | Exclude first-order 51%+ discount | 480 | Acquisition experiments, not organic buyers |
| | **Finals-eligible customers** | | **6,353** |

---

## 6. WORK DONE — COMPLETE HISTORY

### Midterm (pre-presentation, completed)
- **Scripts 01–11:** Full EDA pipeline — data loading, quality checks, retention, product analysis, channel/discount, subscription churn, Five-Lens analysis
- **`data_quality_checks.md`:** Detailed midterm DQ log (preserved unchanged for reference)
- **`FINDINGS.md`:** Midterm narrative findings
- **`presentation.md`:** Midterm presentation script
- **`Mid-term Report - Group 1.pdf`:** Submitted PDF report

### Post-midterm (all completed as of May 26, 2026)

**Analytics:**
- `EDA/12_finals_deep_dive.py` — Full finals analysis script. Includes Option B DQ drops (DQ-02/03/04), LP-F01–F04 filters, LTV by cohort/channel, SKU-level analysis, loyal repeater factor analysis, discontinued product history, reorder intervals, business value scenarios, targeting tiers
- Loyal repeater factor analysis — 5 behavioral drivers compared between loyal and one-and-done segments (`12_loyal_repeater_behavioral_drivers.csv`)
- Targeting tier framework — 4 tiers with Tier 1 (Loyal+Sub) through Tier 4 (One-and-done)

**Visualizations (12 charts, all regenerated May 26 2026):**
- `visualizations/08_finals_charts.py` — generates `08a` through `08l`
- 08a: VTD decile heatmap (product breadth + LTV metrics)
- 08b: POS vs web customer outcomes
- 08c: Top 10 SKUs by revenue (SKU-level, no grouping)
- 08d: Loyal vs one-and-done factor gap chart
- 08e: First-purchase SKU → repeat rate (n≥30)
- 08f: Discontinued products SKU history
- 08g: LTV by cohort × channel heatmap
- 08h: Business value scenarios (conservative vs potential)
- 08i: Customer targeting tiers
- 08j: Reorder intervals by SKU
- 08k: Entry SKUs of loyal customers
- 08l: P(loyal) by acquisition channel + first SKU

**Documentation:**
- `DATA_QUALITY_REPORT_FINAL.md` — Single reference for PDF DQ report (914 lines). Detailed depth matching `data_quality_checks.md` style. DQ-01–12 full write-ups; DQ-02/03/04 updated to show finals drops; DQ-13 removed; Section 7 = LP Feedback Filters LP-F01 to LP-F04
- `FINAL_FEEDBACK_ROADMAP.md` — All professor and LP feedback mapped to deliverables and status
- `FINAL_INSTRUCTOR_REPORT.md` — Finals EDA narrative for instructors
- `FINAL_LTV_AND_BUSINESS_VALUE.md` — LTV formulas and scenario math explained
- `context_prompt.md` — This file

**Deliverables:**
- `deliverables/LushProtein_Orders_STTM.csv` — Source-to-target mapping: 69 raw Shopify columns + 12 derived analytical fields
- `deliverables/LushProtein_Orders_Combined_20260505.csv` — All 7 raw Excel files combined (153,828 rows, 69 columns)
- `deliverables/build_orders_sttm.py` — Script that built the STTM programmatically

---

## 7. REPO STRUCTURE

```
EDA/
  00_config.py            FX rates, channel classifier, product categories
  01_load_and_merge.py    Raw Excel → parquet; FX conversion; base tables (NEVER modify for DQ)
  02_data_quality.py      DQ audit; null counts; year summaries
  03_customer_retention.py Cohort retention; RFM; time-to-second-purchase
  04_product_analysis.py  Product mix; cross-sell; category transitions
  05_channel_discount.py  Channel quality; discount depth; sensitivity
  06_subscription_churn.py Subscriber LTV; Recharge churn analysis
  07_lens1_heterogeneity.py Decile analysis; VTD concentration
  08_lens2_activity.py    Activity/inactivity patterns
  09_lens3_vtd.py         VTD stability across cohorts
  10_lens4_vintage.py     Vintage (acquisition year) comparison
  11_lens5_health.py      Base health scorecard
  12_finals_deep_dive.py  FINALS SCRIPT — DQ drops + LP filters + all finals outputs
  run_eda.py              Runs 01–12 in sequence

  outputs/                All CSV + parquet outputs
    orders.parquet        27,350 orders (base — never overwritten)
    lines.parquet         50,963 line items
    customers.parquet     13,780 customers
    12_*.csv              Finals-specific outputs

visualizations/
  08_finals_charts.py     12 finals charts (08a–08l); reads from 12_*.csv
  run_visualizations.py   Runs all viz scripts
  charts/                 Generated PNG files

deliverables/
  LushProtein_Orders_STTM.csv
  LushProtein_Orders_Combined_20260505.csv
  build_orders_sttm.py

DATA_QUALITY_REPORT_FINAL.md  ← SINGLE REFERENCE for DQ PDF report
FINAL_FEEDBACK_ROADMAP.md
FINAL_INSTRUCTOR_REPORT.md
FINAL_LTV_AND_BUSINESS_VALUE.md
FINAL_DATA_QUALITY_REPORT.md   ← redirect pointer to DATA_QUALITY_REPORT_FINAL.md
data_quality_checks.md         ← MIDTERM; preserved unchanged

context_prompt.md              ← this file
Combined_Slides.pdf            Class lecture slides
Mid-term Report - Group 1.pdf  Submitted midterm PDF
```

Raw data (gitignored): `1.customer_transaction/` through `5.Recharge_data/`

---

## 8. PIPELINE — HOW TO RUN

```bash
# Full pipeline (takes ~5 min):
python EDA/run_eda.py
python visualizations/run_visualizations.py

# Finals only (most common; ~2 min):
python EDA/12_finals_deep_dive.py
python visualizations/08_finals_charts.py
```

**PowerShell note:** Use `;` not `&&` to chain commands.

**After any change to filter logic or customer stats** → rerun `12_finals_deep_dive.py` then `08_finals_charts.py`.

---

## 9. KEY CSV OUTPUTS (`EDA/outputs/12_*.csv`)

| File | What it contains |
|------|-----------------|
| `12_ltv_by_acq_cohort.csv` | LTV, repeat rate, avg orders by acquisition year |
| `12_ltv_by_first_channel.csv` | LTV, repeat rate, sub rate by first channel |
| `12_ltv_by_cohort_channel.csv` | LTV cross-tab: acquisition year × first channel |
| `12_vtd_decile_cumulative_categories.csv` | VTD decile × product breadth, cum % LTV |
| `12_sku_flavor_revenue_2022plus.csv` | Revenue + customers per SKU (2022+, separate per SKU) |
| `12_sku_margin_coverage.csv` | SKUs with COGS from product master |
| `12_first_flavor_loyalty_min30.csv` | First-purchase SKU → repeat rate (n≥30) |
| `12_discontinued_products_history.csv` | Archived/draft products: revenue, customers, date range |
| `12_reorder_interval_by_sku.csv` | Median reorder days per SKU/flavor |
| `12_loyal_repeater_target_tiers.csv` | Tier 1–4 + Other: count, avg LTV, avg orders |
| `12_loyal_repeater_behavioral_drivers.csv` | 5 factor comparisons: loyal vs one-and-done |
| `12_loyal_repeater_rate_by_factor.csv` | P(loyal) by channel, first product, discount depth |
| `12_loyal_rate_by_first_sku_min30.csv` | P(loyal) by first-purchase SKU (n≥30) |
| `12_loyal_repeater_reorder_skus.csv` | SKUs loyal customers keep reordering |
| `12_loyal_repeater_top_first_flavors.csv` | Entry flavors for loyal customers (top 20) |
| `12_loyal_vs_one_and_done.csv` | Full factor comparison table |
| `12_pos_vs_web_customer_outcomes.csv` | POS vs web: repeat rate, LTV, subscription |
| `12_business_value_scenarios.csv` | Conservative + potential GP scenarios |
| `12_customer_enriched_finals.csv` | Customer export: target_tier, loyal_repeater, vtd_decile |

---

## 10. NON-NEGOTIABLE RULES

1. **FX:** All revenue/LTV in **SGD**. Applied ONCE at load via `FX_RATES_TO_SGD` in `EDA/00_config.py`. Never re-convert.
2. **No hardcoded metrics** in scripts — always load from `EDA/outputs/` CSVs/parquet.
3. **Customer counts** = `customer_id.nunique()`, not order counts.
4. **Subscriber LTV = S$532** — the old S$1,063 figure was wrong (was double-counting pre-FX conversion).
5. **Never modify** midterm docs: `README.md`, `FINDINGS.md`, `presentation.md`, `data_usage.md`, `data_quality_checks.md`.
6. **Never overwrite** `orders.parquet`, `lines.parquet`, `customers.parquet` — these are the midterm base (27,350 orders). DQ drops apply only in `12_finals_deep_dive.py`.
7. **SKU/flavor analysis** — keep every SKU separate; never group across handles or variants (founder requirement).
8. **DQ report** — update `DATA_QUALITY_REPORT_FINAL.md`, not `data_quality_checks.md`. The midterm DQ log is preserved.
9. **PowerShell** — use `;` not `&&` to chain commands.
10. **Never commit** unless the user explicitly asks.

---

## 11. REMAINING WORK

| Priority | Task | Owner |
|----------|------|-------|
| P0 | Build finals presentation slides using 2022+ filtered numbers | Team |
| P0 | Update `Mid-term Report - Group 1.pdf` → finals version; use `DATA_QUALITY_REPORT_FINAL.md` as basis | Team |
| P0 | Add loyal targeting narrative (replace "push everyone to 2nd purchase") | Team |
| P1 | All 12 finals charts | ✅ Done May 26 2026 |
| P1 | `DATA_QUALITY_REPORT_FINAL.md` | ✅ Done May 26 2026 |
| P2 | True SKU margin calculations — need LP to provide COGS for remaining 65% of SKUs | Pending LP |
| P2 | Action plan cost estimates (email/SMS campaign CAC) | Pending LP |
| P2 | Export Tier 1–2 CRM list (581 + 1,651 loyal customers) for targeted outreach | Privacy review |

---

## 12. TASK FOR THIS SESSION

[Replace this line with your specific task — e.g. "Build the finals slide on loyal customer profiling using 08d, 08i, and 08k" or "Add Section 3 DQ findings to the finals report PDF"]

---

*Team: Group 1 · ISSS603 SMU · May 2026 · Git branch: aditya_changes*
