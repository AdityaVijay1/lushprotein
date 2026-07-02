# LushProtein — Customer Analytics Project (ISSS603)

**Course:** ISSS603 Science of Customer Analytics · SMU × LushProtein capstone  
**Markets:** Singapore, Malaysia, Hong Kong — analysis figures in **SGD**  
**FX assumption:** 1 SGD = 3.30 MYR · 1 SGD = 6.10 HKD (5-year average, 2020–2026)

---

## Quick start 

This repository contains **reproducible Python analysis** for LushProtein’s finals cohort and **Solution 2** (four-layer recommendation engine). Choose one path:

| Goal | What to run | 
|------|-------------|
| **Full pipeline from raw data only** | `solution2_standalone_from_raw.ipynb` (project root) 
| **Solution 2 on pre-built finals** | `solution2_recommendation_engine.ipynb` (project root) 
| **Profit decile analysis** | `EDA/lushprotein_decile.ipynb` 
| **Batch scripts (EDA + Solution 2)** | See [§5 Batch script pipelines](#5-batch-script-pipelines) 
**Prerequisites:** Python 3.10+, Jupyter (for notebooks). Dependencies auto-install in the standalone notebook; otherwise:

```bash
pip install -r requirements-solution2.txt
```

**Important:** The five raw data folders are **not committed to git** (PII). Place them at project root before running from raw data — see [§3 Data setup](#3-data-setup).

---

## Table of contents

1. [Project overview](#1-project-overview)
2. [Final deliverables map](#2-final-deliverables-map)
3. [Data setup](#3-data-setup)
4. [Repository structure](#4-repository-structure)
5. [Batch script pipelines](#5-batch-script-pipelines)
6. [Reproducible notebooks](#6-reproducible-notebooks)
7. [Finals cohort & filters](#7-finals-cohort--filters)
8. [Solution 2 — key results](#8-solution-2--key-results)
9. [Mid-term EDA findings (summary)](#9-mid-term-eda-findings-summary)
10. [Charts & output index](#10-charts--output-index)
11. [Data quality & traceability](#11-data-quality--traceability)
12. [Team & references](#12-team--references)

---

## 1. Project overview

**Company:** LushProtein — DTC sports nutrition (founded 2013)  
**Hero products:** Lean Protein, Clear Protein, Collagen Glow

**Core business problem:** Acquisition works; retention does not. On the **finals cohort** (post founder feedback filters):

| Metric | Value |
|--------|-------|
| Finals-eligible customers | **5,694** |
| Finals orders | **8,955** |
| One-and-done rate | **77.3%** |
| Single-category buyers | **65%** |
| Subscriber repeat rate | **62%** |
| Non-subscriber repeat rate | **17%** |

**Solution 2 (this repo’s primary recommendation):** A **four-layer recommendation engine** — rule-based cold start (L1), market basket analysis (L2), timed post-purchase cross-sell + samples (L3), item-item collaborative filtering (L4). Phase 1 focuses on **Layer 3** (7-row timing lookup, no ML required).

**Full narrative:** `EDA/report_details/Final_report.md` · `EDA/report_details/xLP.pdf`

---

## 2. Final deliverables map

| Deliverable | Location |
|-------------|----------|
| **Final report (Part A + B)** | `EDA/report_details/Final_report.md`, `EDA/report_details/xLP.pdf` |
| **Reproducible notebooks** | `solution2_standalone_from_raw.ipynb`, `solution2_recommendation_engine.ipynb`, `EDA/lushprotein_decile.ipynb` |
| **Python analysis scripts** | `EDA/` (pipeline), `EDA/aditya_findings/` (Solution 2) |
| **Cleaned finals datasets** | `EDA/outputs_finals/` (+ `manifest.json`) |
| **Presentation charts** | `EDA/aditya_findings/outputs/charts/` |
| **Layer 3 timing table** | `EDA/aditya_findings/outputs/cross_sell_timing_and_samples.csv` |
| **CRM treatment tiers** | `EDA/aditya_findings/outputs/crm_treatment_tiers.csv` |
| **Slide content & script** | `EDA/aditya_findings/final_slides_rec.md`, `EDA/aditya_findings/aditya_scriptV2.md` |
| **Individual reflective report** | `EDA/aditya_findings/individual_report/ReflectiveReport.pdf` |
| **Mid-term materials** | `Group1_ISSS603_midterm_presentation.pdf`, `DATA_QUALITY_REPORT_FINAL.md` |
| **Data glossary** | `LushProtein_Data_Glossary_20260505.xlsx` (local; not in git) |

---

## 3. Data setup

### 3.1 Raw data folders (required for standalone notebook)

Place these folders at **project root** (same level as `EDA/`):

```
LushProtein_Project_Data_20260505/
├── 1.customer_transaction/     # 1_*.xlsx — Shopify orders (2020–2026)
├── 2.product_master/           # products_master xlsx — SKUs, prices, Cost per item
├── 3.Discounts/                # discounts CSV export
├── 4.Campaigns/                # Sessions by referrer CSV (reference)
└── 5.Recharge_data/            # 5 Recharge xlsx files (subscriptions)
```

These folders are listed in `.gitignore` because they contain customer PII. The repo includes **pre-built parquet outputs** in `EDA/outputs/` and `EDA/outputs_finals/` so reviewers can run Solution 2 without raw files.

### 3.2 Data sources

| # | Folder | Description |
|---|--------|-------------|
| 1 | `1.customer_transaction` | Shopify order exports. Use `Top Row == 1` for order-level; `Line: Type == 'Line Item'` for line items. |
| 2 | `2.product_master` | Product catalogue — SKU, price, **Cost per item** (used for COGS in standalone notebook). |
| 3 | `3.Discounts` | Promotional codes and redemption counts. |
| 4 | `4.Campaigns` | Pre-aggregated web traffic by referrer (no order-level join). |
| 5 | `5.Recharge_data` | Subscription orders, checkout/recurring items, churn, reactivation. |

**FX rule:** All revenue converted to SGD at load time (`01_load_and_merge.py` / standalone notebook).

**COGS rule:** Finals margin enrichment uses `EDA/aditya_findings/20260616-COGS_Data_Request_LushProtein (1).xlsx` (founder-provided, June 2026). The standalone notebook uses product master `Cost per item` when the LP COGS file is not present.

---

## 4. Repository structure

```
LushProtein_Project_Data_20260505/
│
├── 1.customer_transaction/          # RAW (gitignored) — Shopify orders
├── 2.product_master/                # RAW (gitignored)
├── 3.Discounts/                     # RAW (gitignored)
├── 4.Campaigns/                     # RAW (gitignored)
├── 5.Recharge_data/                 # RAW (gitignored)
│
├── solution2_standalone_from_raw.ipynb      # ★ Raw → clean → Solution 2 (self-contained)
├── solution2_recommendation_engine.ipynb     # ★ Solution 2 on outputs_finals/
├── requirements-solution2.txt
│
├── standalone_outputs/              # Generated by standalone notebook (parquet + manifest)
│
├── EDA/
│   ├── 00_config.py                 # Paths, product/channel classifiers, FX rates
│   ├── 01_load_and_merge.py         # Raw Excel → EDA/outputs/*.parquet
│   ├── 02–12_*.py                   # Mid-term + 5-Lens + finals deep-dive scripts
│   ├── 13_build_finals_datasets.py  # DQ + LP filters → outputs_finals/
│   ├── run_eda.py                   # Orchestrator (scripts 01–12)
│   ├── trace_datasets.py            # Data lineage report (raw → parquet)
│   │
│   ├── outputs/                     # Mid-term parquet cache + CSVs
│   ├── outputs_finals/              # ★ Finals cohort (primary analysis base)
│   │   ├── manifest.json            # Row counts + filter documentation
│   │   ├── orders.parquet, lines.parquet, customers.parquet
│   │   └── README.md
│   │
│   ├── lushprotein_decile.ipynb     # Profit + frequency deciles (D1–D5)
│   ├── customer_eda.ipynb           # Exploratory notebook
│   │
│   ├── aditya_findings/             # ★ Solution 2 analysis scripts & outputs
│   │   ├── _shared.py               # COGS, decile pool, chart helpers
│   │   ├── run_all.py               # Run full Solution 2 script pipeline
│   │   ├── enrich_finals_with_margin.py
│   │   ├── build_crm_tiers_and_timing.py
│   │   ├── build_rec_sys_charts.py
│   │   ├── calc_slide_data.py
│   │   ├── recommendation_systems/  # MBA, item-CF, 4-layer export
│   │   ├── Recommendation_A/        # Customer tier / incentive analysis
│   │   ├── Recommendation_B/      # Cross-sell co-purchase matrix
│   │   └── outputs/charts/          # Presentation PNGs
│   │
│   ├── category_analysis/           # Category behaviour by decile
│   ├── decile_analysis/             # D1 profile scripts
│   └── report_details/              # Final report markdown + PDF
│
├── visualizations/                  # Mid-term chart scripts → charts/
└── README.md                        # This file
```

---

## 5. Batch script pipelines

Run all commands from **project root** unless noted.

### 5.1 Mid-term EDA (full historical base)

```bash
cd EDA
python 01_load_and_merge.py          # ~60s — builds EDA/outputs/*.parquet
python run_eda.py --skip-load        # scripts 02–12
cd ../visualizations
python run_visualizations.py         # mid-term PNG charts
```

### 5.2 Finals cohort (founder-filtered)

Requires `EDA/outputs/` from step 5.1:

```bash
cd EDA
python 13_build_finals_datasets.py   # → EDA/outputs_finals/
python aditya_findings/enrich_finals_with_margin.py   # COGS + deciles on customers
```

Expected primary row counts (see `outputs_finals/manifest.json`):

| File | Rows |
|------|------|
| `customers.parquet` | 5,694 |
| `orders.parquet` | 8,955 |
| `lines.parquet` | 14,448 |

### 5.3 Solution 2 analysis (scripts)

Requires `outputs_finals/` + `lushprotein_decile.ipynb` export (`decile_customer_table.csv`):

```bash
# From project root:
python EDA/aditya_findings/run_all.py
```

This runs: margin enrichment → Recommendation A/B → MBA → 4-layer recommenders → CRM tiers & timing → presentation charts.

**Regenerate charts only:**

```bash
python EDA/aditya_findings/build_rec_sys_charts.py
python EDA/aditya_findings/build_presentation_charts.py
```

### 5.4 Data traceability

```bash
python EDA/trace_datasets.py         # Prints raw → parquet lineage for all 5 sources
```

---

## 6. Reproducible notebooks

### 6.1 `solution2_standalone_from_raw.ipynb` (recommended for full traceability)

**Input:** Only the five raw data folders at project root.  
**Output:** `standalone_outputs/` (parquet + `manifest.json` + timing CSV)

| Section | What it does |
|---------|--------------|
| Cell 0 | Auto-installs all Python dependencies |
| Part A | Load & merge Shopify + Recharge + product master |
| Part B | DQ + LP filters → finals cohort (same logic as `13_build_finals_datasets.py`) |
| Part C | COGS from product master `Cost per item` |
| Parts D–H | Solution 2 metrics: problem statement, L1–L4 |

**Run:** Open from project root → Run All. First cell installs packages if missing.

### 6.2 `solution2_recommendation_engine.ipynb` (fast path)

**Input:** Pre-built `EDA/outputs_finals/` (committed in repo).  
**Output:** Validates manifest, reproduces presentation numbers inline, optional script regeneration.

Set `RUN_REGENERATE = True` in Section 8 to rerun `EDA/aditya_findings/` scripts.

### 6.3 `EDA/lushprotein_decile.ipynb`

Rebuilds profit and order-frequency deciles (D1–D5) on the finals pool. Exports `decile_customer_table.csv` required by `build_crm_tiers_and_timing.py`.

---

## 7. Finals cohort & filters

Authoritative documentation: `EDA/outputs_finals/README.md` and `manifest.json`.

| Layer | ID | Rule |
|-------|-----|------|
| **1 — DQ** | DQ-02 | `Price: Total = 0` AND zero discount |
| | DQ-03 | Zero revenue, positive discount (free fulfilment) |
| | DQ-04 | Wholesale tag OR order > S$5,000 |
| **2 — LP customer** | LP-F03 | Lifetime `first_order_date >= 2022-01-01` (entire customer excluded if pre-2022) |
| | LP-F01 | Exclude `better-whey-protein-elite` buyers |
| | LP-F02 | Exclude Jul/Nov **acquisition** months |
| | LP-F04 | Exclude 51%+ first-order discount depth |
| **0 — Window** | | Orders `>= 2022-01-01` on retained customers |
| **3 — Order/SKU** | | Drop Jul/Nov order months; drop elite handle from lines |

**Do not use** `outputs_finals/do_not_use_these/*` for analysis — those are DQ-only reference snapshots without LP filters.

---

## 8. Solution 2 — key results

Full write-up: `EDA/report_details/Final_report.md` Part B.

### Four-layer architecture

| Layer | Method | Primary output |
|-------|--------|----------------|
| **L1** | Rule-based cold start (category co-purchase) | `Recommendation_B/outputs/co_purchase_matrix_all.csv` |
| **L2** | Same-order SKU market basket analysis | `recommendation_systems/outputs/sku_association_rules.csv` |
| **L3** | Timed post-purchase email + physical sample | `outputs/cross_sell_timing_and_samples.csv` (7 rows) |
| **L4** | Item-item collaborative filtering | `recommendation_systems/outputs/recommender_04_item_similarity_matrix.csv` |

### Category ladder (repeat rate by categories ever purchased)

| Categories | Repeat rate (approx.) |
|------------|----------------------|
| 1 | 13% |
| 2 | 30% |
| 3+ | 63% |

### Layer 3 timing example (Clear Protein first purchase)

| Field | Value |
|-------|-------|
| Cross-sell target | Lean Protein |
| Email day after delivery | 14 |
| Physical sample day | 44 |
| Median reorder window | 54 days |

Charts: `EDA/aditya_findings/outputs/charts/rec_sys_why_4_layers.png`, `slide1_problem_statement.png`, `rec_sys_l3_timing_detail.png`

---

## 9. Mid-term EDA findings (summary)

*Full mid-term analysis on the unfiltered 2020–2026 base (13,780 customers, 27,350 orders). Superseded by finals cohort for final recommendations but retained for historical context.*

| Metric | Mid-term base |
|--------|---------------|
| Overall repeat rate | 32.4% |
| 60-day retention | 18.3% |
| Median days to 2nd order | 49 days |
| Subscriber LTV uplift | +166% vs non-subscriber |

**Top findings (mid-term):**

1. Deep discounting reduces cohort quality (full-price 36.4% repeat vs 51%+ off at 21.9%)
2. Cross-sell is the highest LTV lever (3-product buyers: 65.5% repeat, S$470 LTV)
3. Marketplace channel underperforms Direct/Organic on repeat and LTV
4. Subscription churn peaks at cycle 1 (30–60 days); top reason: “already have more than I need”

Detailed tables and chart references preserved in sections below and in `DATA_QUALITY_REPORT_FINAL.md`.

---

## 10. Charts & output index

### Solution 2 / finals presentation

`EDA/aditya_findings/outputs/charts/` — regenerate via `build_rec_sys_charts.py` + `build_presentation_charts.py`

| File | Description |
|------|-------------|
| `slide1_problem_statement.png` | 77.3% one-and-done, category ladder |
| `rec_sys_why_4_layers.png` | Four-layer architecture overview |
| `rec_sys_l1_cold_start.png` | Layer 1 co-purchase rules |
| `rec_sys_l2_mba_rules.png` | Layer 2 association rules |
| `rec_sys_l3_timing_detail.png` | Layer 3 email + sample timeline |
| `rec_sys_l4_item_cf_heatmap.png` | Layer 4 item similarity |
| `r2_category_ladder.png` | Repeat rate by category breadth |
| `r2_cross_sell_timeline_clear.png` | Clear Protein customer journey |

### Mid-term visualizations

`visualizations/charts/` — regenerate with `python visualizations/run_visualizations.py`

Key files: `01a_revenue_discount_trend.png`, `03a_cross_product_ltv.png`, `04b_churn_by_cycle.png`, `05a_discount_depth_impact.png`

### Part A report charts

`EDA/report_details/charts/` — filter layers, missing values, one-time buyer rate

---

## 11. Data quality & traceability

| Resource | Purpose |
|----------|---------|
| `DATA_QUALITY_REPORT_FINAL.md` | Mid-term DQ report |
| `data_quality_checks.md` | DQ issue register |
| `EDA/outputs_finals/manifest.json` | Finals filter manifest + row counts |
| `EDA/trace_datasets.py` | Executable lineage: raw files → parquet |
| `ERD_VERIFICATION.md` | Entity relationship notes |
| `LushProtein_Source_to_Target_Mapping_ExerciseV1.xlsx` | Source-to-target mapping (local) |

**Key grain rules (same file, different filters):**

- `Top Row == 1` → one row per **order**
- `Line: Type == 'Line Item'` → one row per **line item**
- `store` is **derived** from order `Name` prefix (LP/LPSG=SG, LPMY=MY, LPHK=HK)

---
**Course:** ISSS603 Applied Data Science for Customer Insights, Singapore Management University  
**Industry partner:** LushProtein  
**Group:** Group 1


*Last updated: July 2026 · ISSS603 Science of Customer Analytics · SMU × LushProtein*
