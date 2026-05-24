# LushProtein — Final Feedback & Roadmap

**Purpose:** Consolidate midterm professor feedback, LushProtein (LP) founder feedback, and class lecture requirements into an actionable finals workplan.  
**Does not modify:** `README.md`, `FINDINGS.md`, `presentation.md`, `data_usage.md`, `data_quality_checks.md`

---

## 1. Midterm Professor Feedback → Response

| Feedback | Status | Deliverable |
|----------|--------|-------------|
| **LTV by cohort & channel + explain calculation** | ✅ Done | `FINAL_LTV_AND_BUSINESS_VALUE.md`, `12_ltv_by_*.csv`, `08g_ltv_cohort_channel_heatmap.png` |
| **Business value: potential + conservative + show math** | ✅ Done | `12_business_value_scenarios.csv`, `08h_business_value_scenarios.png` |
| **Deciling analysis (class slides)** | ✅ Done | `07_lens1_decile_table.csv`, `08a_vtd_decile_product_breadth.png` |
| **Cumulative categories by VTD decile** | ✅ Done | `12_vtd_decile_cumulative_categories.csv`, `08a_vtd_decile_product_breadth.png` |
| **Cohort analysis — VERY IMPORTANT** | ✅ Done | Lenses 3–5; `12_acquisition_by_year.csv`, `08g_ltv_cohort_channel_heatmap.png` |
| **Don't blindly push 2nd purchase — target who** | ✅ Done | `12_loyal_repeater_target_tiers.csv`, `08i_loyal_repeater_target_tiers.png` |
| **Identify what makes loyal customers loyal** | ✅ Done | `12_loyal_vs_one_and_done.csv`, `08d_loyal_vs_one_and_done.png`, Section 7 below |
| **Margin of SKUs** | ⚠️ Partial | `12_sku_margin_coverage.csv` — 35% COGS coverage; 40% proxy elsewhere |
| **LTV definition, POS** | ✅ Done | Documented; `08b_pos_vs_web_outcomes.png` |
| **Cohort by acquisition / promotion year** | ✅ Done | `12_ltv_by_acq_cohort.csv`, `10_lens4_discount_intensity.csv` |

---

## 2. LushProtein Founder Feedback → Response

| LP Feedback | Status | Deliverable |
|-------------|--------|-------------|
| **On-site vs off-site discounting** | ✅ Done | `12_pos_vs_web_*.csv`, `08b_pos_vs_web_outcomes.png` |
| **Discounts dataset has POS label** | ❌ Not in data | POS = `Source='pos'` in **order export** only |
| **Factor margin + cost of action plans** | ⚠️ Partial | `08h_business_value_scenarios.png` uses 40% gross profit proxy |
| **Focus 2022+** | ✅ Done | All `12_*` SKU/flavor outputs filter 2022+ |
| **Ignore July & November** | ✅ Done | Excluded in `finals_eligible` flag |
| **Remove Better Elite Whey** | ✅ Done | `better-whey-protein-elite` excluded from finals pool |
| **Drop 51%+ discount from finals narrative** | ✅ Done | Excluded from `finals_eligible` |
| **Serving sizes / reorder speed** | ✅ Done | `12_reorder_interval_by_sku.csv`, `08j_reorder_interval_by_sku.png` |
| **Product/flavor level (SKU separate)** | ✅ Done | See **Section 7** + `08c`, `08e`, `08k` |
| **Discontinued products** | ✅ Done | See **Section 8** + `08f_discontinued_products_history.png` |
| **Identify loyal repeaters, target them** | ✅ Done | See **Section 9** + `08i`, `08k` |

---

## 3. POS Verification (On-site vs Off-site)

| Dataset | Column | POS signal |
|---------|--------|------------|
| **Customer transactions** | `Source` | Value **`pos`** (419 orders); confirmed via `Shopify POS` user agent |
| **Discounts export** | All columns | **No POS codes found** |

| Metric | POS (on-site) | Web (off-site) |
|--------|---------------|----------------|
| Orders | 419 | 5,046 |
| % orders discounted | **99.3%** | 52.3% |
| First-order customers | 363 | 2,743 |
| Repeat rate | **17.9%** | **29.0%** |
| Avg LTV | **S$78** | **S$124** |
| % subscribed | **1.9%** | **21.0%** |

**Chart:** `visualizations/charts/08b_pos_vs_web_outcomes.png`

---

## 4. Class Concepts → Charts

| Class concept | Chart file |
|---------------|------------|
| Lens 1 decile concentration | `07_lens1` outputs + `08a_vtd_decile_product_breadth.png` |
| Lens 3 cohort / VTD | `09_lens3_vtd_decile_table.csv` + `08a` |
| Lens 4 vintage comparison | `10_lens4_year1_comparison.csv` |
| Lens 5 base health | `11_lens5_health_scorecard.csv` |
| LTV cohort × channel | `08g_ltv_cohort_channel_heatmap.png` |
| Business value scenarios | `08h_business_value_scenarios.png` |

---

## 5. Finals Visualizations — ALL COMPLETE ✅

Run: `python visualizations/08_finals_charts.py`

| Chart | File | What it shows |
|-------|------|---------------|
| **08a** | `08a_vtd_decile_product_breadth.png` | Avg unique products + % 3+ products by VTD decile; cumulative LTV line |
| **08b** | `08b_pos_vs_web_outcomes.png` | POS vs web: repeat rate, LTV, subscription |
| **08c** | `08c_top10_sku_flavor_revenue.png` | Top 10 SKU/flavor by revenue (2022+, filtered) — **each SKU separate** |
| **08d** | `08d_loyal_vs_one_and_done.png` | **What makes loyal different** — cross-sell, subscription, full-price factor gaps |
| **08e** | `08e_first_flavor_repeat_rate.png` | First-purchase flavor → repeat rate (min 30 customers, SKU kept separate) |
| **08f** | `08f_discontinued_products_history.png` | Archived/draft products with historical revenue |
| **08g** | `08g_ltv_cohort_channel_heatmap.png` | Avg LTV by acquisition year × first channel (2022+) |
| **08h** | `08h_business_value_scenarios.png` | Conservative vs potential gross profit uplift |
| **08i** | `08i_loyal_repeater_target_tiers.png` | Customer targeting tiers by LTV |
| **08j** | `08j_reorder_interval_by_sku.png` | Median reorder days by SKU (serving-size aware) |
| **08k** | `08k_loyal_repeater_first_flavors.png` | Top entry flavors among loyal repeaters |
| **08l** | `08l_loyal_repeater_entry_drivers.png` | P(loyal) by acquisition channel + first-purchase SKU |

---

## 6. Product / Flavor Focus (Founder Priority)

### Methodology — SKU and flavor kept separate

Each row is uniquely identified by:
```
Handle + Variant Title + SKU  (never grouped across SKUs)
```

Example — Clear Protein Peach exists as **three separate SKUs**:
- `0724999807814` — 500g Pack (20 Serv) / Peach
- `CLEAR-PEA-500G-V2` — 1 x 500g Pack (20 servings) / Peach
- Different pack sizes = different reorder cadence

**Data files:**
- `12_sku_flavor_revenue_2022plus.csv` — revenue by handle/variant/SKU
- `12_first_flavor_loyalty_all.csv` — first-purchase flavor → repeat/LTV (all customers)
- `12_first_flavor_loyalty_2022plus_filtered.csv` — finals-filtered
- `12_first_flavor_loyalty_min30.csv` — flavors with n≥30 for reliable repeat rates

### Top revenue SKUs (2022+, finals filters)

| Product / Flavor | SKU | Customers | Revenue (SGD) |
|------------------|-----|-----------|---------------|
| Clear Protein / Peach | 0724999807814 | 532 | S$46,450 |
| Lean Protein / Thai Milk Tea | LEAN-THA-1KG-V1 | 282 | S$35,520 |
| Clear Protein / White Grape | 0724999807807 | 366 | S$29,375 |
| Clear Protein / Peach | CLEAR-PEA-500G-V2 | 239 | S$28,313 |
| Lean Protein / Taro | LEAN-TAR-1KG-V1 | 216 | S$26,200 |

**Chart:** `08c_top10_sku_flavor_revenue.png`

### First-purchase flavor → loyalty (min 30 customers)

High repeat-rate entry flavors (examples — see full CSV):
- **better-whey / Cocoa Dinosaur** (SKU 0724999807937): 100% repeat among n=41 (legacy product — interpret with caution)
- **collagen-glow / Natural**: 58.8% repeat, n=34
- **lean-protein / Thai Milk Tea**: 34.8% repeat, n=230
- **clear-protein / White Grape**: 32.6% repeat, n=285

**Chart:** `08e_first_flavor_repeat_rate.png`

### Reorder cadence by serving size

Variant Title encodes servings (e.g. "25 servings", "20 Serv", "50 servings"):
- Lean Protein 1kg (25 servings): median reorder ~45–60 days
- Creatine 250g (50 servings): longer median gap
- Clear Protein 500g (20 servings): ~30–45 days

**Data:** `12_reorder_interval_by_sku.csv`  
**Chart:** `08j_reorder_interval_by_sku.png`

---

## 7. Discontinued Products (Founder Question)

### Only 1 **archived** product in master: `prime-whey-isolate`

| Product | Status | Historical orders | Customers | Revenue (SGD) | Last sale |
|---------|--------|-------------------|-----------|---------------|-----------|
| **prime-whey-isolate** | **archived** | 762+ (all SKUs) | 388 | **~S$84,471** | May 2025 |
| **better-whey** (all flavors/SKUs) | **draft** | 2,946 | 1,705 | **~S$232,409** | Sep 2025 |
| super-omega-3 | draft | 228 | 134 | S$10,226 | Mar 2025 |
| green-tea-extract-capsules | draft | 150 | 125 | S$3,971 | Sep 2025 |

**Key insight for LP:** The discontinued/archived whey line (`prime-whey-isolate`) still generated significant revenue through 2025. **`better-whey`** is draft (being phased out) but remains the largest historical discontinued-category product — **not the same as `better-whey-protein-elite`** (which is excluded as bulk/distortion).

**Data:** `12_discontinued_products_history.csv` (full SKU-level history)  
**Chart:** `08f_discontinued_products_history.png`

---

## 8. Loyal Repeaters — What Makes Them Come Back (Founder Priority)

### Definition
```
Loyal repeater = is_repeat AND total_orders >= 3
```
**2,349 loyal repeaters** vs **9,321 one-and-done** (overall ~17% of customers become loyal).

### The question: what factors keep them coming back?

Analysis compares loyal repeaters vs one-and-done on **behavioral**, **acquisition**, and **product entry** factors.  
**Data:** `12_loyal_repeater_behavioral_drivers.csv`, `12_loyal_repeater_rate_by_factor.csv`, `12_loyal_rate_by_first_sku_min30.csv`, `12_loyal_repeater_reorder_skus.csv`  
**Charts:** `08d_loyal_vs_one_and_done.png` (factor gaps), `08l_loyal_repeater_entry_drivers.png` (entry channel + SKU)

---

### Factor 1 — Cross-sell / product breadth (strongest differentiator)

| Factor | Loyal | One-and-done | Lift |
|--------|-------|--------------|------|
| **3+ unique product handles** | **27.5%** | 4.6% | **5.9×** |
| **2+ unique product handles** | **43.6%** | 19.0% | **2.3×** |
| Avg unique handles | **1.72** | 0.83 | — |
| Avg unique flavor-SKUs | **3.68** | 1.44 | — |

**Insight:** Loyal customers don't just reorder the same tub — they **expand across products**. Cross-sell is the biggest behavioural gap vs one-and-done.

**What loyal customers keep reordering:** Clear Protein Peach, White Grape, Lean Thai Milk Tea (`12_loyal_repeater_reorder_skus.csv`).

---

### Factor 2 — Subscription (retention mechanism)

| Factor | Loyal | One-and-done | Lift |
|--------|-------|--------------|------|
| **Ever subscribed** | **25.4%** | 3.0% | **8.4×** |

**Insight:** Subscription is both a driver and an outcome — loyal customers are 8× more likely to subscribe. Converting Tier 2 (loyal non-sub, n=1,753) is the highest-value action.

---

### Factor 3 — Acquisition quality (how they arrived)

| First channel | P(become loyal) | vs baseline (~17%) |
|---------------|-----------------|---------------------|
| **Subscription** | **23.3%** | 1.4× |
| Direct / Organic | 17.6% | 1.0× |
| Marketplace | **4.9%** | 0.3× |
| Paid Social | 6.8% | 0.4× |

| First-order discount | P(become loyal) |
|---------------------|-----------------|
| **Full-price (0%)** | **21.3%** |
| 51%+ (experimental) | 7.0% |

| Factor | Loyal | One-and-done |
|--------|-------|--------------|
| First order full-price | **78.5%** | 57.4% |

**Insight:** Customers acquired via **subscription channel** or at **full price** are far more likely to become loyal. Marketplace and deep-discount acquisition rarely produce loyal repeaters.

---

### Factor 4 — Entry product / flavor (what they bought first)

Among active SKUs (n≥30, excl. unknown tags), highest P(loyal):

| First-purchase SKU | P(loyal) | n |
|--------------------|----------|---|
| Collagen Glow Natural 300g | **41.2%** | 34 |
| Lean Thai Milk Tea 1kg | **17.8%** | 230 |
| Soy Protein Natural 1kg | **17.1%** | 82 |

**Chart:** `08l_loyal_repeater_entry_drivers.png`  
**Note:** Legacy `better-whey` SKUs show very high P(loyal) but are draft/discontinued — use for historical context only.

---

### Factor 5 — Return speed (pathway, not acquisition filter)

| Segment | Median days to 2nd order | % returned within 60 days |
|---------|--------------------------|---------------------------|
| Loyal (3+ orders) | 49 days | **55.9%** |
| 2-order (stalled) | 48 days | 55.4% |

**Insight:** Speed to 2nd order **does not** separate loyal from 2-order customers (both ~49 days). What separates them is **3rd order + product breadth + subscription** — not just getting a 2nd purchase quickly.

---

### Targeting tiers (who to act on)

| Tier | Customers | Avg LTV | Action |
|------|-----------|---------|--------|
| **Tier 1: Loyal + Subscribed** | 596 | **S$888** | Protect, upsell new flavors |
| **Tier 2: Loyal Non-Sub** | 1,753 | **S$817** | Convert to subscription; cross-sell |
| **Tier 3: 2-order** | 2,110 | S$190 | Push to 3rd order + cross-sell (critical threshold) |
| **Tier 4: One-and-done** | 9,321 | S$81 | Low priority unless high P(loyal) entry SKU |

**Chart:** `08i_loyal_repeater_target_tiers.png`

---

### Deck narrative (for final presentation)

> **Loyalty is not random — it follows a pattern.** Loyal repeaters cross-sell (3+ products, 5.9× lift), subscribe (8.4× lift), and typically enter at full price via subscription or direct channels. Marketplace and deep-discount buyers rarely become loyal. The lever is not "push everyone to a 2nd purchase" — it's **cross-sell + subscription conversion after the 2nd order**, steering acquisition toward high-P(loyal) SKUs like Lean Thai Milk Tea and Collagen Glow.

---

## 9. Remaining TODO

| Priority | Task | Status |
|----------|------|--------|
| P0 | Build finals slides using 2022+ filtered numbers | 🔲 Team |
| P0 | Add LTV cohort × channel table to deck | 🔲 Use `08g` + `12_ltv_by_cohort_channel.csv` |
| P0 | Replace generic 2nd-purchase push with loyal targeting narrative | 🔲 Use Section 8 |
| P1 | Chart: VTD decile × cumulative categories | ✅ `08a` |
| P1 | Chart: POS vs web outcomes | ✅ `08b` |
| P1 | Chart: Top 10 SKU/flavor (2022+) | ✅ `08c` |
| P1 | Chart: Loyal vs one-and-done | ✅ `08d` |
| P1 | Chart: First-flavor repeat rate | ✅ `08e` |
| P1 | Chart: Discontinued products | ✅ `08f` |
| P1 | Chart: LTV cohort × channel heatmap | ✅ `08g` |
| P1 | Chart: Business value scenarios | ✅ `08h` |
| P1 | Chart: Loyal repeater tiers | ✅ `08i` |
| P1 | Chart: Reorder interval by SKU | ✅ `08j` |
| P1 | Chart: Loyal first flavors | ✅ `08k` |
| P2 | True margin using COGS where available | 🔲 Need LP to fill product master COGS |
| P2 | Cost of action plans (email/SMS CAC) | 🔲 Need LP cost inputs |
| P2 | Export Tier 1–2 customer list for CRM (if LP approves) | 🔲 Privacy review |

---

## 10. File Index

### Analysis scripts
| File | Description |
|------|-------------|
| `EDA/12_finals_deep_dive.py` | All finals analysis (sections 1–11) |
| `visualizations/08_finals_charts.py` | All finals charts (08a–08k) |

### Key CSV outputs (`EDA/outputs/12_*.csv`)

| File | Description |
|------|-------------|
| `12_ltv_by_acq_cohort.csv` | LTV by acquisition year |
| `12_ltv_by_cohort_channel.csv` | LTV cross-tab cohort × channel |
| `12_vtd_decile_cumulative_categories.csv` | VTD decile × product breadth |
| `12_sku_flavor_revenue_2022plus.csv` | SKU/flavor revenue (separate SKUs) |
| `12_first_flavor_loyalty_min30.csv` | First flavor → repeat (n≥30) |
| `12_discontinued_products_history.csv` | Archived/draft product sales history |
| `12_reorder_interval_by_sku.csv` | Median reorder days by SKU |
| `12_loyal_repeater_target_tiers.csv` | Targeting tiers |
| `12_loyal_repeater_top_first_flavors.csv` | Entry flavors of loyal customers |
| `12_loyal_vs_one_and_done.csv` | Segment comparison |
| `12_business_value_scenarios.csv` | Conservative vs potential value |

### Documentation
| File | Description |
|------|-------------|
| `FINAL_INSTRUCTOR_REPORT.md` | Instructor EDA report |
| `FINAL_LTV_AND_BUSINESS_VALUE.md` | LTV + scenario math |
| `FINAL_DATA_QUALITY_REPORT.md` | Extended DQ |
| `FINAL_FEEDBACK_ROADMAP.md` | This document |
| `AGENT_HANDOFF_PROMPT.md` | Agent context |
| `deliverables/LushProtein_Orders_STTM.csv` | Source-to-target mapping |

---

## 11. Re-run Commands

```bash
python EDA/12_finals_deep_dive.py
python visualizations/08_finals_charts.py
# or full pipeline:
python EDA/run_eda.py
python visualizations/run_visualizations.py
```

---

*Last updated: May 2026 — all P1 visualization tasks complete*
