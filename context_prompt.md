# LushProtein Project — Agent Handoff Prompt



Copy everything below the line into a new Cursor/agent session to restore full project context.



---



## SYSTEM CONTEXT



You are assisting **Group 1, ISSS603 Science of Customer Analytics (SMU)**, on the **LushProtein** client project — a direct-to-consumer protein supplement brand in **Singapore, Malaysia, and Hong Kong**.



**Workspace:**

`C:\Users\adity\Documents\Aditya SMU\SMU Sem 5\Lush Protein SMU X\LushProtein_Project_Data_20260505\`



**Git branch:** `aditya_changes`



**Course framework:** Bruce, Fader & Ross — *Customer-Base Audit* (2022) — **Five Lenses** on the customer×time face of the data cube. Class slides: `Combined_Slides.pdf`.



---



## PROJECT GOAL



Analyse 5 years of Shopify transactional data (2020–2026) to:

1. Demonstrate **rigorous data due diligence** (instructor report)

2. Identify **who** LushProtein's loyal customers are (not just "push everyone to 2nd purchase")

3. Quantify opportunities with **LTV by cohort & channel**, **conservative vs potential business value**, and **margin**

4. Deliver final presentation + supporting docs for LP founder feedback



---



## NON-NEGOTIABLE RULES



1. **FX:** All revenue/LTV in **SGD**. Applied ONCE at load: `1 SGD = 3.30 MYR`, `1 SGD = 6.10 HKD` in `EDA/00_config.py`. Never re-convert downstream.

2. **No hardcoded business metrics** in EDA/viz scripts — load from `EDA/outputs/` CSVs/parquet.

3. **Customer counts** = `customer_id.nunique()`, not order counts.

4. **Correct subscriber LTV = S$532** (not old wrong S$1,063).

5. **Do not modify** these midterm docs unless asked: `README.md`, `FINDINGS.md`, `presentation.md`, `data_usage.md`, `data_quality_checks.md`.

6. **Use NEW finals docs** for updates: `FINAL_*.md` files in repo root.

7. **SKU / flavor analysis:** Keep each SKU separate — never group across SKUs (founder requirement).



---



## FINALS-SPECIFIC FILTERS (LP + Professor)



| Filter | Reason |

|--------|--------|

| **Analysis focus 2022+** | 2021 product portfolio shift (lean/clear protein) |

| **Exclude July & November acquisitions** | Birthday + Black Friday promo distortion |

| **Exclude first-order 51%+ discount depth** | LP: experimental/gifting, not structural pricing |

| **Exclude `better-whey-protein-elite`** | Unsustainable bulk orders |

| **Finals-eligible pool:** 5,761 customers | After all filters, acq ≥ 2022-01-01 |



Script: `EDA/12_finals_deep_dive.py` → `EDA/outputs/12_*.csv`



---



## KEY DATA FACTS



| Metric | Value |

|--------|-------|

| Unique customers | 13,780 |

| Total orders | 27,350 |

| Repeat rate | 32.4% |

| 60-day cohort retention | 18.1% |

| Subscriber / non-subscriber LTV | S$532 / S$200 (+166%) |

| POS orders (`Source='pos'`) | 419 (99.3% discounted; weak repeat) |

| Web orders (`Source='web'`) | 5,046 |

| Top decile (D10) share of LTV | ~66% |



**POS clarification:** On-site = order `Source='pos'` in **customer transaction** files. **NOT** in Discounts CSV (no POS codes found there).



**LTV definition:** `SUM(Price: Total)` per customer in SGD. Gross profit proxy = LTV × 40% (COGS 65% null).



---



## REPO STRUCTURE



```

EDA/

  00_config.py          # FX, product categories, channel classifier

  01_load_and_merge.py  # Raw → parquet (ENTRY POINT)

  02–06                 # Core EDA (quality, retention, product, channel, churn)

  07–11                 # Five-lens scripts

  12_finals_deep_dive.py # Finals analysis (LTV, SKU, loyal tiers, POS, discontinued)

  run_eda.py            # Runs 01–12

  outputs/              # All CSV + parquet outputs



visualizations/

  08_finals_charts.py   # Finals charts 08a–08l (load from 12_*.csv only)

  run_visualizations.py # Runs 01–08



deliverables/

  LushProtein_Orders_STTM.csv  # Source-to-target mapping for Excel exercise



FINAL_INSTRUCTOR_REPORT.md      # Main instructor EDA report

FINAL_FEEDBACK_ROADMAP.md       # All feedback + response status + product focus

FINAL_LTV_AND_BUSINESS_VALUE.md # LTV formulas + scenario math

FINAL_DATA_QUALITY_REPORT.md    # Extended DQ log (extends midterm report)

AGENT_HANDOFF_PROMPT.md         # Duplicate of this file at repo root

context_prompt.md               # This file — session handoff



Combined_Slides.pdf             # Class lecture slides (lenses, deciles)

Mid-term Report - Group 1.pdf   # Midterm instructor report (needs finals update)

Group1_ISSS603_midterm_presentation.pdf  # Midterm deck

```



Raw data (gitignored): `1.customer_transaction/` through `5.Recharge_data/`



---



## PIPELINE



```bash

python EDA/run_eda.py

python visualizations/run_visualizations.py

# or finals only:

python EDA/12_finals_deep_dive.py

python visualizations/08_finals_charts.py

```



---



## FINALS VISUALIZATIONS (08a–08l) — ALL COMPLETE ✅



Run: `python visualizations/08_finals_charts.py` → `visualizations/charts/`



| Chart | File | What it shows |

|-------|------|---------------|

| **08a** | `08a_vtd_decile_product_breadth.png` | **Heatmap:** product breadth + LTV metrics by VTD decile (D1–D10) |

| **08b** | `08b_pos_vs_web_outcomes.png` | POS vs web: repeat rate, LTV, subscription |

| **08c** | `08c_top10_sku_flavor_revenue.png` | Top 10 SKUs by revenue — **each SKU separate** |

| **08d** | `08d_loyal_vs_one_and_done.png` | **What makes loyal different** — factor gap chart (cross-sell, sub, full-price) |

| **08e** | `08e_first_flavor_repeat_rate.png` | First-purchase SKU → repeat rate (n≥30, excl. unknown tags) |

| **08f** | `08f_discontinued_products_history.png` | Archived/draft products at SKU level |

| **08g** | `08g_ltv_cohort_channel_heatmap.png` | Avg LTV by acquisition year × first channel |

| **08h** | `08h_business_value_scenarios.png` | Conservative vs potential gross profit uplift |

| **08i** | `08i_loyal_repeater_target_tiers.png` | Customer targeting tiers (Tier 1–4) |

| **08j** | `08j_reorder_interval_by_sku.png` | Median reorder days by SKU |

| **08k** | `08k_loyal_repeater_first_flavors.png` | Entry SKUs of loyal customers (excl. unknown/shakers) |
| **08l** | `08l_loyal_repeater_entry_drivers.png` | P(loyal) by acquisition channel + first-purchase SKU |



**Chart design notes (May 2026 refresh):**

- Larger figsizes, dynamic height for horizontal bar charts

- SKU-level unique y-labels (fixes duplicate-label overlap bugs in 08c/08f)

- 08a converted from cramped dual-axis bar chart → **heatmap**

- 08e excludes `unknown` flavor tags and 100% repeat outliers

- 08k excludes unknown (1,579 customers) and shaker accessories



---



## PRODUCT / FLAVOR FOCUS (Founder Priority)



**Method:** Each row = `Handle + Variant Title + SKU` — never grouped.



**Top revenue SKUs (2022+, filtered):**

- Clear Protein Peach `0724999807814` — S$46K, 532 customers

- Lean Thai Milk Tea `LEAN-THA-1KG-V1` — S$35K, 282 customers

- Clear White Grape `0724999807807` — S$29K, 366 customers



**Discontinued products:**

- `prime-whey-isolate` — **only archived** SKU family (~S$84K historical)

- `better-whey` — **draft**, phased out (~S$232K total, NOT same as `better-whey-protein-elite`)



**Loyal repeater — what makes them come back (not just who they are):**

| Factor | Loyal | One-and-done | Lift |
|--------|-------|--------------|------|
| 3+ product handles | 27.5% | 4.6% | **5.9×** |
| Ever subscribed | 25.4% | 3.0% | **8.4×** |
| First order full-price | 78.5% | 57.4% | 1.4× |
| P(loyal) via Subscription channel | 23.3% | — | vs 4.9% Marketplace |
| Median days to 2nd (loyal vs 2-order) | 49d | — | Same as 2-order (48d) |

**Key insight:** Cross-sell + subscription separate loyal from stalled 2-order customers — not speed to 2nd purchase alone.

**Targeting tiers:**

| Tier | n | Avg LTV | Action |
|------|---|---------|--------|
| Tier 1: Loyal + Sub | 596 | S$888 | Protect & upsell |
| Tier 2: Loyal Non-Sub | 1,753 | S$817 | Convert to subscription |
| Tier 3: 2-order | 2,110 | S$190 | Push to 3rd order + cross-sell |
| Tier 4: One-and-done | 9,321 | S$81 | Low priority |

**Charts:** `08d` (factor gaps), `08l` (entry channel/SKU), `08i` (tiers), `08k` (entry flavors)



---



## KEY CSV OUTPUTS (`EDA/outputs/12_*.csv`)



| File | Description |

|------|-------------|

| `12_ltv_by_acq_cohort.csv` | LTV by acquisition year |

| `12_ltv_by_cohort_channel.csv` | LTV cross-tab cohort × channel |

| `12_vtd_decile_cumulative_categories.csv` | VTD decile × product breadth |

| `12_sku_flavor_revenue_2022plus.csv` | SKU/flavor revenue (separate SKUs) |

| `12_first_flavor_loyalty_min30.csv` | First flavor → repeat (n≥30) |

| `12_discontinued_products_history.csv` | Archived/draft product sales history |

| `12_reorder_interval_by_sku.csv` | Median reorder days by SKU |

| `12_loyal_repeater_behavioral_drivers.csv` | Factor gaps: loyal vs one-and-done |
| `12_loyal_repeater_rate_by_factor.csv` | P(loyal) by channel, product, discount depth |
| `12_loyal_rate_by_first_sku_min30.csv` | P(loyal) by first-purchase SKU (n≥30) |
| `12_loyal_repeater_reorder_skus.csv` | SKUs loyal customers keep reordering |
| `12_loyal_repeater_return_pathway.csv` | Return speed: loyal vs 2-order |
| `12_loyal_repeater_target_tiers.csv` | Targeting tiers |

| `12_loyal_repeater_top_first_flavors.csv` | Entry flavors of loyal customers |

| `12_loyal_vs_one_and_done.csv` | Segment comparison |

| `12_pos_vs_web_customer_outcomes.csv` | POS vs web metrics |

| `12_business_value_scenarios.csv` | Conservative vs potential value |

| `12_customers_enriched.csv` | Customer export with `target_tier`, `loyal_repeater` |



---



## BUSINESS VALUE SCENARIOS (from `12_business_value_scenarios.csv`)



| Opportunity | Conservative gross profit | Potential gross profit |

|-------------|---------------------------|------------------------|

| Cross-sell →3 products (5%) | S$17,620 | — |

| Retention win-back (10%) | S$31,496 | S$47,245 (15%) |

| Sub conversion | S$84,241 (5%) | S$210,603 (12.5%) |

| Marketplace LTV gap | S$3,523 (5%) | S$10,568 (15%) |



---



## LTV BY CHANNEL (for deck — explains S$190 vs S$198)



- `06a`: Direct/Organic alone = **S$198**

- `05b`: "Own Website" blend (Direct + Paid Social + Email + Affiliate) = **S$190**

- Marketplace = **S$115** in both



---



## DELIVERABLES COMPLETED (Post-Midterm)



| Deliverable | File |

|-------------|------|

| Instructor finals report | `FINAL_INSTRUCTOR_REPORT.md` |

| Feedback roadmap + TODO | `FINAL_FEEDBACK_ROADMAP.md` |

| LTV & business value math | `FINAL_LTV_AND_BUSINESS_VALUE.md` |

| Extended DQ report | `FINAL_DATA_QUALITY_REPORT.md` |

| Source-to-target mapping | `deliverables/LushProtein_Orders_STTM.csv` |

| Finals deep-dive script | `EDA/12_finals_deep_dive.py` |

| Finals charts (11) | `visualizations/08_finals_charts.py` |



---



## REMAINING WORK (Priority)



| Priority | Task | Status |

|----------|------|--------|

| P0 | Build finals slides using 2022+ filtered numbers | 🔲 Team |

| P0 | Add LTV cohort×channel to deck (`08g`) | 🔲 Team |

| P0 | Replace generic 2nd-purchase push with loyal targeting (Section 8 of roadmap) | 🔲 Team |

| P0 | Update `Mid-term Report - Group 1.pdf` → final instructor report | 🔲 Team — use `FINAL_*.md` |

| P1 | All 11 finals charts | ✅ Done (refreshed May 2026) |

| P2 | True SKU margin (need LP COGS — 35% coverage) | 🔲 Pending LP |

| P2 | Action plan cost estimates (email/SMS CAC) | 🔲 Pending LP |

| P2 | Export Tier 1–2 CRM list | 🔲 Privacy review |



---



## WHEN MAKING CHANGES



- Read surrounding code conventions before editing

- Minimize scope — focused diffs only

- Run `12_finals_deep_dive.py` after filter logic changes

- Run `08_finals_charts.py` after CSV changes

- Update `FINAL_*.md` not legacy midterm docs

- Never commit unless user asks



---



## TASK FOR THIS SESSION



[Describe your specific task here — e.g. "Build finals slide on loyal customer profiling" or "Update mid-term report Section 3 with DQ findings"]



---



*Last updated: May 2026 — all P1 charts complete; 08a heatmap; SKU-level chart fixes*

