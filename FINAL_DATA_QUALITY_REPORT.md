# LushProtein — Final Data Quality Report

**Audience:** ISSS603 instructors  
**Extends:** `data_quality_checks.md` (original midterm log — not modified)  
**Focus:** Due diligence, impact, mitigation, and evidence for finals scope

---

## 1. Dataset Inventory & Coverage

| # | Dataset | Raw rows | Analytical rows | Used in finals? |
|---|---------|----------|-----------------|-----------------|
| 1 | Customer transactions (7 Excel files) | 153,828 | 27,350 orders / 50,963 lines | ✅ Primary |
| 2 | Product master | 167 variants | 167 | ✅ Margin/SKU (partial COGS) |
| 3 | Discounts export | 367 codes | 163 active | ⚠️ Taxonomy only — no order join |
| 4 | Campaigns (UTM sessions) | 137,033 | — | ❌ No date/customer ID |
| 5 | Recharge subscription | ~1 year | 575 orders | ⚠️ Churn detail only |

---

## 2. Critical Issues for Finals Analysis

### DQ-F01 — No discount code on order rows
**Severity:** HIGH  
**Description:** Orders have `Price: Total Discount` (amount) but no `discount_code` column. Cannot link `3.Discounts` codes to customer outcomes.  
**Impact:** Cannot compare specific promo codes (welcome10 vs POS codes) at order level — only discount depth bins and POS `Source`.  
**Mitigation:** Use first-order discount depth bins; POS identified via `Source='pos'`.  
**Evidence:** `05_discount_depth_bins.csv`, `12_pos_vs_web_orders.csv`

### DQ-F02 — POS is in orders, not Discounts export
**Severity:** MEDIUM (documentation)  
**Description:** LP believed Discounts CSV labels POS codes. Verified: **zero** POS references in 367 discount codes. POS orders identified via `Source='pos'` in transaction export (419 orders).  
**Impact:** On-site vs off-site analysis must use order `Source`, not Discounts join.  
**Mitigation:** Documented in `FINAL_FEEDBACK_ROADMAP.md`; merged in `12_finals_deep_dive.py`.

### DQ-F03 — 65% null COGS in product master
**Severity:** HIGH for margin analysis  
**Description:** `Cost per item` populated for 58/167 variants only.  
**Impact:** Cannot compute true SKU margin for majority of flavors.  
**Mitigation:** 40% gross margin proxy for business value; flag rows with/without cost in `12_sku_margin_coverage.csv`.  
**Sensitivity:** Repeat rate and cohort findings are count-based — unaffected.

### DQ-F04 — Mixed currencies pre-FX
**Severity:** CRITICAL (resolved)  
**Description:** 41% of orders originally in MYR, <1% HKD.  
**Mitigation:** Fixed FX at load (`FX_RATES_TO_SGD` in `00_config.py`). Never re-convert downstream.  
**Evidence:** `verify_all.py` MY/HK avg order value checks.

### DQ-F05 — 100%-off / gifting orders
**Severity:** MEDIUM  
**Description:** 1,283 orders with S$0 revenue and full discount (affiliate gifts, experiments).  
**Impact:** Inflates discount totals; LP asked to exclude 51%+ acquisition experiments from finals.  
**Mitigation:** Finals cohort excludes first-order depth ≥51%; flag in reports.

### DQ-F06 — better-whey-protein-elite bulk distortion
**Severity:** MEDIUM (product analysis)  
**Description:** 333 line items, 200 customers — unsustainable bulk product per LP.  
**Mitigation:** Excluded from finals-eligible cohort and SKU rankings in script 12.

### DQ-F07 — July & November promo months
**Severity:** MEDIUM (cohort quality)  
**Description:** Birthday (July) and Black Friday (November) drive atypical discount depth.  
**Mitigation:** Customers acquired in months 7 and 11 excluded from finals-eligible pool (2,818 customers).

### DQ-F08 — Marketplace repeat rate undercount
**Severity:** LOW–MEDIUM  
**Description:** Shopee repurchase with different email creates new customer_id.  
**Impact:** 14.4% marketplace repeat is conservative.  
**Mitigation:** Footnote in all channel comparisons; strategic finding unchanged.

### DQ-F09 — Recharge covers ~1 year only
**Severity:** MEDIUM  
**Description:** Historical subscription patterns before Apr 2025 estimated from Shopify Tags.  
**Mitigation:** `ever_subscribed` from Tags; churn cycles from Recharge export only.

### DQ-F10 — UTM 94.9% null
**Severity:** HIGH for attribution  
**Mitigation:** `classify_channel()` uses Tags (marketplace, subscription) as primary signal.

---

## 3. Mitigation Evidence (Before / After)

| Check | Before mitigation | After mitigation |
|-------|-------------------|------------------|
| MY customer LTV | Inflated ~3.3× (MYR as SGD) | Corrected S$532 sub LTV |
| Currency mix in charts | Misleading totals | All SGD in parquet |
| Channel unknown | 94.9% null UTM | Tags-based classification |
| POS analysis | Not in parquet | Source merged in script 12 |
| Elite whey SKUs | Skewed product mix | Excluded from finals pool |

Run: `python EDA/verify_all.py` (62 checks)

---

## 4. Join & Grain Rules

| Analytical grain | Filter | PK |
|------------------|--------|-----|
| Order-level | `Top Row == 1` | `order_id` |
| Line-level | `Line: Type == 'Line Item'` | `line_id` |
| Customer-level | Aggregate orders | `customer_id` |

**Never:** Sum `Price: Total` across currencies before FX.  
**Never:** Count orders when metric requires unique customers.

---

## 5. Data Readiness for Final Deliverables

| Requirement | Ready? | Gap |
|-------------|--------|-----|
| LTV by cohort & channel | ✅ | — |
| Decile + VTD categories | ✅ | — |
| POS vs web | ✅ | — |
| SKU/flavor level | ✅ | — |
| True SKU margin | ⚠️ | Need LP to fill COGS |
| Reorder interval by serving size | ❌ | TODO script |
| Action plan cost (email/SMS) | ❌ | Need LP cost inputs |

---

*See also: `FINAL_INSTRUCTOR_REPORT.md`, `FINAL_FEEDBACK_ROADMAP.md`*
