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

---

## FINALS-SPECIFIC FILTERS (LP + Professor)

| Filter | Reason |
|--------|--------|
| **Analysis focus 2022+** | 2021 product portfolio shift (lean/clear protein) |
| **Exclude July & November acquisitions** | Birthday + Black Friday promo distortion |
| **Exclude first-order 51%+ discount depth** | LP: experimental/gifting, not structural pricing |
| **Exclude `better-whey-protein-elite`** | Unsustainable bulk orders |
| **Finals-eligible pool:** 5,761 customers | After all filters, acq ≥ 2022-01-01 |

Script: `EDA/12_finals_deep_dive.py`

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
  12_finals_deep_dive.py # NEW — finals analysis
  run_eda.py            # Runs 01–12
  outputs/              # All CSV + parquet outputs

visualizations/         # Chart scripts (load from outputs only)
deliverables/
  LushProtein_Orders_STTM.csv  # Source-to-target mapping for Excel exercise

FINAL_INSTRUCTOR_REPORT.md      # Main instructor EDA report
FINAL_FEEDBACK_ROADMAP.md       # All feedback + response status
FINAL_LTV_AND_BUSINESS_VALUE.md # LTV formulas + scenario math
FINAL_DATA_QUALITY_REPORT.md    # Extended DQ log
AGENT_HANDOFF_PROMPT.md         # This file

Combined_Slides.pdf             # Class lecture slides (lenses, deciles)
Group1_ISSS603_midterm_presentation.pdf  # Finalized midterm deck
```

Raw data (gitignored): `1.customer_transaction/` through `5.Recharge_data/`

---

## PIPELINE

```bash
python EDA/run_eda.py
python visualizations/run_visualizations.py
```

---

## TOP FINDINGS (Midterm — refine for finals)

1. Deep discounting / cohort quality decline (2022+ narrative; de-emphasise 51%+ per LP)
2. Cross-sell = biggest LTV lever (SKU/flavor level for finals)
3. Target **loyal customer profile** vs one-and-done (not blanket 2nd-purchase push)
4. Subscription high value, cadence mismatch churn
5. Marketplace vs owned-site channel gap
6. **NEW:** POS on-site discounts underperform web for LTV/repeat/subscription

---

## BUSINESS VALUE SCENARIOS (from `12_business_value_scenarios.csv`)

| Opportunity | Conservative gross profit | Potential gross profit |
|-------------|---------------------------|------------------------|
| Cross-sell →3 products (5%) | S$17,620 | — |
| Retention win-back (10%) | S$31,496 | S$47,245 (15%) |
| Sub conversion | S$84,241 (5%) | S$210,603 (12.5%) |
| Marketplace LTV gap | S$3,523 (5%) | S$10,568 (15%) |

---

## REMAINING WORK (Priority)

1. Finals slides with 2022+ filtered numbers + lens/decile charts
2. Viz: VTD decile × categories, POS vs web, top SKU/flavors
3. Reorder interval by serving size (Variant Title parsing)
4. True margin where COGS exists; LP to supply missing costs
5. Action plan cost estimates from LP

---

## WHEN MAKING CHANGES

- Read surrounding code conventions before editing
- Minimize scope — focused diffs only
- Run `12_finals_deep_dive.py` after filter logic changes
- Update `FINAL_*.md` not legacy midterm docs
- Never commit unless user asks

---

## TASK FOR THIS SESSION

[Describe your specific task here — e.g. "Build finals slide on loyal customer profiling" or "Add reorder interval analysis by serving size"]

---

*End of handoff prompt*
