# LushProtein — Final Instructor Report (EDA & Data Due Diligence)

**Course:** ISSS603 Science of Customer Analytics · SMU  
**Client:** LushProtein (SG, MY, HK)  
**Audience:** Instructors — data understanding and preparation assessment  
**Scope:** Combined markets, SGD (FX at load: 1 SGD = 3.30 MYR | 1 SGD = 6.10 HKD)  
**Analysis window (finals focus):** 2022+ with documented exclusions (see Section 2)

> This document is **new for the final submission**. It supplements (does not replace) `README.md`, `FINDINGS.md`, and `data_quality_checks.md`.

---

## 1. Executive Summary

We analysed **27,350 orders** and **13,780 unique customers** (2020–Q1 2026) using the **Customer-Base Audit** five-lens framework (Bruce, Fader & Ross, 2022).

**Core diagnosis:** LushProtein’s base is heterogeneous — the top 10% of customers by spend generate ~**66%** of revenue (Lens 1 decile). Retention is weak at the critical 60-day window (**18.1%** cohort retention). Acquisition quality declined from 2020–2024 vintages (Lens 4), coinciding with marketplace and discount mix shifts.

**Finals pivot (per LP + professor feedback):**
- Move from “everyone should repeat” → **identify who to target** (loyal vs one-and-done profiles)
- Report **LTV by acquisition cohort and channel** with explicit formulas
- Quantify opportunities with **conservative and potential** scenarios including **margin proxy**
- Analyse **on-site (POS) vs off-site (web)** discounts — POS is in order `Source`, not the Discounts export
- Product analysis at **SKU / flavor level**; exclude `better-whey-protein-elite` and 51%+ acquisition experiments

---

## 2. Finals Analysis Filters (LP + Professor Guidance)

| Filter | Rationale | Impact |
|--------|-----------|--------|
| **Focus 2022+** | 2021 product portfolio shift (lean/clear replace legacy whey) | Primary narrative starts post-relaunch |
| **Exclude July & November acquisitions** | Birthday sale + Black Friday — atypical discount intensity | Removes **2,818** customers from finals-eligible cohort |
| **Exclude first-order 51%+ discount depth** | LP: experimental/gifting acquisition, not structural pricing | Removes **1,240** customers |
| **Exclude `better-whey-protein-elite` buyers** | Unsustainable bulk orders; distorts product analysis | Removes **200** customers |
| **Finals-eligible pool** | All filters + acq ≥ 2022-01-01 | **5,761 customers** |

Script: `EDA/12_finals_deep_dive.py` → `EDA/outputs/12_*.csv`

---

## 3. Exploratory Data Analysis

### 3.1 Distributions & Coverage

| Entity | Rows | Date range | Notes |
|--------|------|------------|-------|
| Orders (Top Row=1) | 27,350 | 2020-01 – 2026-03 | Paid/fulfilled; restocked excluded |
| Line items | 50,963 | Same | `Line: Type = Line Item` |
| Customers | 13,780 | — | `customer_id.nunique()` |
| Product master variants | 167 | Snapshot May 2026 | 34 active SKUs |
| Discount codes | 367 (163 used) | — | **No order-level code join** |
| Recharge subscriptions | ~1 year window | Apr 2025 – Apr 2026 | Partial subscription history |

**Spend distribution (Lens 1):** Mean customer spend **S$226** vs median **S$67** (3.4× skew). **82.7%** of customers are below mean spend. **67.6%** are one-time buyers.

### 3.2 Key Summary Statistics (All Markets, SGD)

| Metric | Value | Source |
|--------|-------|--------|
| Overall repeat rate | 32.4% | `customers.parquet` |
| 60-day cohort retention | 18.1% | `03_cohort_retention_heatmap.csv` |
| Median days to 2nd order | 49 days | `customers.parquet` |
| Subscriber LTV / Non-subscriber | S$532 / S$200 (+166%) | `customers.parquet` |
| 2025 orders discounted | 49.6% | `02_orders_by_year.csv` |
| 2025 discount as % of gross | 35.2% | `02_orders_by_year.csv` |

### 3.3 Five-Lens Outputs (Class Framework)

| Lens | Question | Key output files |
|------|----------|------------------|
| **L1** | How different are customers? | `07_lens1_decile_table.csv`, `07_lens1_decomposition.csv` |
| **L2** | What changed period-on-period? | `08_lens2_overlap_all_years.csv`, `08_lens2_decile_migration.csv` |
| **L3** | How does one cohort evolve? | `09_lens3_cohort_annual.csv`, `09_lens3_vtd_decile_table.csv` |
| **L4** | Are new cohorts better/worse? | `10_lens4_year1_comparison.csv`, `10_lens4_discount_intensity.csv` |
| **L5** | How healthy is the base? | `11_lens5_health_scorecard.csv`, `11_lens5_cohort_revenue_matrix.csv` |

**VTD decile × cumulative categories (finals):** `12_vtd_decile_cumulative_categories.csv`  
Top decile (D10): avg LTV **S$1,488**, **89.5%** repeat, **1.47** avg unique product handles, **3.6** avg flavor-SKU combinations.

---

## 4. Data Issues, Impact & Mitigation

| ID | Issue | Impact | Mitigation | Evidence |
|----|-------|--------|------------|----------|
| DQ-01 | 94.9% null UTM | Channel under-attribution | `classify_channel()` uses Tags + Name | `05_channel_quality.csv` |
| DQ-02 | Mixed currencies | Revenue inflation if ignored | FX at load in `01_load_and_merge.py` | All parquet in SGD |
| DQ-03 | 65% null COGS | No true SKU margin for most variants | 40% gross margin proxy; join where `Cost per item` exists | `12_sku_margin_coverage.csv` |
| DQ-04 | No discount code on orders | Cannot link code taxonomy to outcomes | Use discount **amount** bins; POS via `Source` | `12_pos_vs_web_orders.csv` |
| DQ-05 | 100%-off orders (1,283) | Distorts discount/LTV ratios | Flagged; excluded from finals 51%+ cohort | `data_quality_checks.md` DQ-06 |
| DQ-06 | Marketplace repeat undercount | Conservative channel gap | Footnote on cross-email Shopee repurchase | Slide 10 caveat |
| DQ-07 | Recharge 1-year window | Incomplete subscription history | Shopify Tags for `ever_subscribed`; Recharge for churn detail | `06_subscription_churn.py` |
| DQ-08 | POS not in parquet originally | Missed on-site analysis | `Source` column merged in script 12 | `12_pos_vs_web_*.csv` |

Full log: `FINAL_DATA_QUALITY_REPORT.md` (extends `data_quality_checks.md`).

---

## 5. Consumer Behaviour Hypotheses (Emerging)

1. **Loyalty is concentrated, not broad.** Top decile drives ~65% of revenue; one-and-done customers dominate count (9,321 vs 2,349 loyal 3+ order repeaters).

2. **What makes loyal customers different** (`12_loyal_vs_one_and_done.csv`):

   | Segment | n | Avg LTV | % Subscribed | Avg unique handles | % Full-price first order |
   |---------|---|---------|--------------|-------------------|--------------------------|
   | Loyal (3+ orders, repeat) | 2,349 | S$835 | 25.4% | 1.72 | **78.5%** |
   | One-and-done | 9,321 | S$81 | 3.0% | 0.83 | 57.4% |

3. **POS (on-site) discounts are not a growth lever.** 99.3% of POS orders are discounted vs 52.3% web; POS first-order customers: **17.9%** repeat, **S$78** LTV, **1.9%** subscribed vs web **29.0%**, **S$124**, **21.0%**.

4. **Cross-sell and subscription correlate with VTD decile** — product breadth rises monotonically from D1→D10 (see `12_vtd_decile_cumulative_categories.csv`).

5. **Acquisition cohort quality fell post-2021** — 2025 acq cohort avg LTV **S$103** vs 2022 **S$276** (unfiltered; finals-filtered in `12_ltv_by_acq_cohort_finals_filtered.csv`).

---

## 6. Opportunities & Business Value

| Opportunity | Target segment | Conservative | Potential | Script output |
|-------------|----------------|--------------|-----------|---------------|
| Cross-sell (→2 products) | 1-product finals pool | S$17.6K gross / S$7.0K profit | Same at 10% conv | `12_business_value_scenarios.csv` |
| Cross-sell (→3 products) | 1-product pool | S$44.1K gross / S$17.6K profit | 5% conversion | Same |
| Retention win-back | 2024–25 no 2nd order | S$78.7K (10%) | S$118.1K (15%) | Same |
| Subscription conversion | Non-subscribers | S$210.6K (5%) | S$526.5K (12.5%) | Same |
| Marketplace → direct LTV | 2,126 marketplace | S$8.8K (5%) | S$26.4K (15%) | Same |

**Margin method:** `gross_profit = LTV_uplift × 40%` where SKU-level COGS unavailable. When `Cost per item` present, use `(Price − Cost) × quantity` at line level (future enhancement).

Full formulas: `FINAL_LTV_AND_BUSINESS_VALUE.md`

---

## 7. Supporting Evidence & Charts

| Finding | Primary CSV | Chart |
|---------|-------------|-------|
| Decile concentration | `07_lens1_decile_table.csv` | Lens 1 decile (class slides) |
| Cohort retention | `03_cohort_retention_heatmap.csv` | `02d_cohort_60d_retention.png` |
| Vintage decline | `10_lens4_year1_comparison.csv` | `01a_revenue_discount_trend.png` |
| Loyal vs one-and-done | `12_loyal_vs_one_and_done.csv` | TBD finals slide |
| POS vs web | `12_pos_vs_web_orders.csv` | TBD finals slide |
| SKU/flavor mix | `12_sku_flavor_revenue_2022plus.csv` | TBD finals slide |
| VTD × categories | `12_vtd_decile_cumulative_categories.csv` | TBD finals slide |

---

## 8. Pipeline & Reproducibility

```bash
python EDA/run_eda.py              # scripts 01–12
python visualizations/run_visualizations.py
```

**New finals script:** `EDA/12_finals_deep_dive.py`  
**STTM deliverable:** `deliverables/LushProtein_Orders_STTM.csv` (paste into `LushProtein_Source_to_Target_Mapping_ExerciseV1.xlsx`)

---

*Prepared for ISSS603 final submission · May 2026*
