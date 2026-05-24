# LushProtein — Final Feedback & Roadmap

**Purpose:** Consolidate midterm professor feedback, LushProtein (LP) founder feedback, and class lecture requirements into an actionable finals workplan.  
**Does not modify:** `README.md`, `FINDINGS.md`, `presentation.md`, `data_usage.md`, `data_quality_checks.md`

---

## 1. Midterm Professor Feedback → Response

| Feedback | Status | Deliverable |
|----------|--------|-------------|
| **LTV by cohort & channel + explain calculation** | ✅ Implemented | `FINAL_LTV_AND_BUSINESS_VALUE.md`, `12_ltv_by_acq_cohort.csv`, `12_ltv_by_first_channel.csv`, `12_ltv_by_cohort_channel.csv` |
| **Business value: potential + conservative + show math** | ✅ Implemented | `12_business_value_scenarios.csv`, `FINAL_LTV_AND_BUSINESS_VALUE.md` |
| **Deciling analysis (class slides)** | ✅ Exists + extended | `07_lens1_decile_table.csv`, `12_vtd_decile_cumulative_categories.csv` |
| **Cumulative categories by VTD decile** | ✅ New | `12_vtd_decile_cumulative_categories.csv` |
| **Cohort analysis — VERY IMPORTANT** | ✅ Exists + extended | Lenses 3–5 outputs; acquisition by year in `12_acquisition_by_year.csv` |
| **Don't blindly push 2nd purchase — target who** | ✅ New | `12_loyal_customer_profile.csv`, `12_loyal_vs_one_and_done.csv` |
| **Identify what makes loyal customers loyal** | ✅ New | Section 5 in `FINAL_INSTRUCTOR_REPORT.md` |
| **Margin of SKUs** | ⚠️ Partial | 65% null COGS; `12_sku_margin_coverage.csv` + 40% proxy documented |
| **LTV definition, POS** | ✅ Documented | LTV = sum revenue; POS = order `Source = 'pos'` |
| **Cohort by acquisition / promotion year** | ✅ | `acq_year` on customers; `10_lens4_discount_intensity.csv` |

---

## 2. LushProtein Founder Feedback → Response

| LP Feedback | Finding | Action taken |
|-------------|---------|--------------|
| **On-site vs off-site discounting** | POS is **`Source = 'pos'`** in **customer transaction** files, NOT in Discounts CSV | `12_pos_vs_web_orders.csv`, `12_pos_vs_web_customer_outcomes.csv` |
| **Discounts dataset has POS label** | ❌ **Not found** — Discounts export has `Context` = all/customer/segment only; no POS codes | Documented in `FINAL_DATA_QUALITY_REPORT.md` |
| **Factor margin + cost of action plans** | COGS sparse | Gross profit = LTV uplift × 40% proxy; SKU cost join where available |
| **Focus 2022+ (2021 product shift)** | Confirmed lean/clear dominate post-2021 | Finals filter + SKU analysis from 2022 |
| **Ignore July & November** | Promo months | Excluded from finals-eligible cohort |
| **Remove Better Elite Whey** | Handle: `better-whey-protein-elite` (333 line items, 200 customers) | Excluded in script 12 |
| **Drop 51%+ discount analysis for finals** | LP: market experiments/gifting | Excluded from finals-eligible cohort |
| **Serving sizes / reorder speed** | Variant Title encodes servings (e.g. "25 servings", "500g Pack (20 Serv)") | Flavor-SKU level in `12_sku_flavor_revenue_2022plus.csv`; reorder interval analysis = **TODO** |
| **Product/flavor level (not just categories)** | Founder priority | `12_sku_flavor_revenue_2022plus.csv` — handle + variant + SKU |
| **Discontinued products** | draft/archived in master | `12_discontinued_products_not_in_recent_orders.csv` |
| **Identify loyal repeaters, target them** | Loyal profile vs one-and-done | `12_loyal_vs_one_and_done.csv` |

---

## 3. POS Verification (Critical)

**LP assumption:** Discounts dataset labels POS for on-site codes.  
**Actual data:**

| Dataset | Column | POS signal |
|---------|--------|------------|
| **Customer transactions** | `Source` | Value **`pos`** (419 orders, 397 customers); confirmed via `Browser: User Agent` = `Shopify POS/...` |
| **Discounts export** | `Name`, `Context`, `Type` | **No POS codes found** in 367 rows |

**On-site vs off-site comparison (verified):**

| Metric | POS (on-site) | Web (off-site) |
|--------|---------------|----------------|
| Orders | 419 | 5,046 |
| % orders discounted | **99.3%** | 52.3% |
| Avg order value | S$59 | S$83 |
| First-order customers | 363 | 2,743 |
| Repeat rate (first-order cohort) | **17.9%** | **29.0%** |
| Avg LTV (first-order cohort) | **S$78** | **S$124** |
| % subscribed | **1.9%** | **21.0%** |

**Conclusion:** On-site POS discounting is operational (events/pop-ups), heavily discounted, and produces **weaker** long-term customers than web. Not recommended as a scalable acquisition lever.

---

## 4. Class Concepts to Feature in Final Deck

From `Combined_Slides.pdf` (Customer-Base Audit):

1. **Five lenses** — show at least one chart per lens used
2. **Decile concentration** — D1 = 65.9% revenue (Lens 1)
3. **Revenue = Customers × AOF × AOV** — Lens 1 decomposition
4. **Cohort retention curves** — Lens 3 / monthly heatmap
5. **Vintage comparison at same age** — Lens 4 (`10_lens4_year1_comparison.csv`)
6. **Base health scorecard** — Lens 5 (4/5 KPIs in ALERT)
7. **VTD decile × product breadth** — new finals chart

---

## 5. Remaining TODO for Final Presentation

| Priority | Task | Owner suggestion |
|----------|------|------------------|
| P0 | Build finals slides using **2022+ filtered** numbers | All |
| P0 | Add **LTV cohort × channel** table to deck | Aditya / analytics |
| P0 | Replace generic “push 2nd purchase” with **loyal customer targeting** narrative | Aditya |
| P1 | Chart: VTD decile × cumulative categories | Viz team |
| P1 | Chart: POS vs web outcomes | Viz team |
| P1 | Chart: Top 10 SKU/flavor combos (2022+) | Viz team |
| P2 | Reorder interval by serving size (creatine 50 serv vs lean 25 serv) | New script |
| P2 | True margin using COGS where available | Enhance script 12 |
| P2 | Cost of action plans (email/SMS CAC estimates from LP) | Business case |

---

## 6. File Index (New Finals Artifacts)

| File | Description |
|------|-------------|
| `FINAL_INSTRUCTOR_REPORT.md` | Main instructor-facing EDA report |
| `FINAL_LTV_AND_BUSINESS_VALUE.md` | LTV definitions + scenario math |
| `FINAL_DATA_QUALITY_REPORT.md` | Extended DQ for finals |
| `FINAL_FEEDBACK_ROADMAP.md` | This document |
| `AGENT_HANDOFF_PROMPT.md` | Context for AI agents |
| `EDA/12_finals_deep_dive.py` | Finals analysis script |
| `EDA/outputs/12_*.csv` | All finals CSV outputs |
| `deliverables/LushProtein_Orders_STTM.csv` | Source-to-target mapping (orders) |

---

*Last updated: May 2026*
