# LushProtein — LTV Methodology & Business Value Calculations

**Audience:** Professors + final presentation team  
**Currency:** SGD (FX applied once at load in `01_load_and_merge.py`)

---

## 1. LTV Definition

### Primary definition (used throughout pipeline)

```
LTV (customer) = SUM(Price: Total) across all paid, non-restocked orders
                 for that customer_id, after FX conversion to SGD
```

| Step | Detail |
|------|--------|
| Grain | One row per **customer_id** in `customers.parquet` |
| Revenue field | `total_revenue` = sum of order-level `Price: Total` |
| FX | MYR ÷ 3.30, HKD ÷ 6.10 at load time |
| Exclusions | Unpaid orders, restocked fulfillments dropped at load |
| Time horizon | Full observation window (2020 – Q1 2026); not truncated at 12 months unless noted |

### Gross profit LTV (when margin needed)

```
Gross_Profit_LTV = LTV × MARGIN_RATE
MARGIN_RATE = 0.40  (40% proxy — used because 65% of product master COGS is null)
```

**SKU-level margin (where available):**
```
Line_Gross_Margin = (Line: Total) − (Cost per item × Line: Quantity)
```
Join: `Line: SKU` → `products_master.Variant SKU`  
Coverage: **58/167** variants have `Cost per item` → see `12_sku_margin_coverage.csv`

### POS (Point of Sale)

```
On-site order  ⇔  Source = 'pos'  in customer transaction export
Off-site order ⇔  Source = 'web'  (primary owned-site channel)
```

Verified by `Browser: User Agent` containing `Shopify POS` on POS rows.  
**Not** identified via Discounts export (no POS codes there).

---

## 2. LTV by Acquisition Cohort

**Cohort key:** `acq_year = YEAR(first_order_date)`

| Acq year | Customers | Avg LTV | Median LTV | Repeat rate | % Subscribed |
|----------|-----------|---------|------------|-------------|--------------|
| 2020 | 1,696 | S$618 | S$130 | 52.8% | 4.3% |
| 2021 | 3,334 | S$252 | S$62 | 39.1% | 3.0% |
| 2022 | 1,462 | S$276 | S$83 | 36.7% | 4.8% |
| 2023 | 873 | S$128 | S$70 | 29.2% | 18.6% |
| 2024 | 2,015 | S$125 | S$65 | 30.9% | 14.4% |
| 2025 | 3,524 | S$103 | S$51 | 21.9% | 7.7% |

Source: `12_ltv_by_acq_cohort.csv`

**Finals-filtered cohorts (2022+, excl. Jul/Nov, 51%+, elite whey):** `12_ltv_by_acq_cohort_finals_filtered.csv`

**Formula:**
```python
cust.groupby("acq_year").agg(
    customers=("customer_id", "count"),
    avg_ltv=("total_revenue", "mean"),
    repeat_rate=("is_repeat", "mean"),
)
```

---

## 3. LTV by First Channel

| First channel | Customers | Repeat rate | Avg LTV | Median LTV | % Subscribed |
|---------------|-----------|-------------|---------|------------|--------------|
| Subscription | 4,275 | 40.9% | S$343 | — | 18.8% |
| Direct / Organic | 6,920 | 33.5% | S$198 | — | 3.8% |
| Marketplace | 2,126 | 14.4% | S$115 | — | 0.0%* |
| Paid Social | 382 | 19.4% | S$71 | — | 6.0% |

*Shopify subscriptions only.

**Formula:**
```python
# first_channel = channel of customer's earliest order by order_date
cust.groupby("first_channel").agg(avg_ltv=("total_revenue", "mean"), ...)
```

Source: `12_ltv_by_first_channel.csv` (same numbers as `05_channel_quality.csv`)

---

## 4. LTV by Cohort × Channel

Cross-tab for professor requirement: `12_ltv_by_cohort_channel.csv`

Example use: compare 2024 Direct/Organic avg LTV vs 2024 Marketplace avg LTV at same acquisition age.

---

## 5. Business Value Scenarios

**General formula:**
```
Gross_LTV_Uplift = Pool × Conversion_Rate × Uplift_per_Customer
Gross_Profit_Uplift = Gross_LTV_Uplift × 0.40
```

### 5.1 Cross-sell (finals-filtered 1-product pool)

| Scenario | Pool | Rate | Uplift/customer | Gross LTV | Gross profit (40%) |
|----------|------|------|-----------------|-----------|-------------------|
| →2-product (conservative) | 2,941 | 10% | S$60 (S$230−S$170) | **S$17,565** | **S$7,026** |
| →3-product (conservative) | 2,941 | 5% | S$300 (S$470−S$170) | **S$44,051** | **S$17,620** |

### 5.2 Retention win-back (2024–25, no 2nd order)

| Scenario | Pool | Rate | Value/customer | Gross LTV | Gross profit |
|----------|------|------|----------------|-----------|--------------|
| Conservative | 2,346 | 10% | S$336* | **S$78,741** | **S$31,496** |
| Potential | 2,346 | 15% | S$336* | **S$118,112** | **S$47,245** |

*Avg LTV of repeaters in finals-eligible pool.

### 5.3 Subscription conversion

| Scenario | Pool (non-subs) | Rate | Uplift (S$532−S$200) | Gross LTV | Gross profit |
|----------|-----------------|------|----------------------|-----------|--------------|
| Conservative | 12,685 | 5% | S$332 | **S$210,603** | **S$84,241** |
| Potential | 12,685 | 12.5% | S$332 | **S$526,507** | **S$210,603** |

### 5.4 Marketplace → direct LTV gap

| Scenario | Pool | Rate | Gap (Direct−Marketplace LTV) | Gross LTV | Gross profit |
|----------|------|------|------------------------------|-----------|--------------|
| Conservative | 2,126 | 5% | S$83 | **S$8,806** | **S$3,523** |
| Potential | 2,126 | 15% | S$83 | **S$26,419** | **S$10,568** |

Source: `12_business_value_scenarios.csv`

**Note:** Scenarios are **directional**, not additive. Overlapping customers across programs mean total upside < sum of rows.

---

## 6. Acquisition Rate by Year

```
New_Customers(year) = COUNT customers WHERE acq_year = year
Pct_of_Base = New_Customers / 13,780
```

Source: `12_acquisition_by_year.csv`

Use with Lens 4 vintage tables to show **quality vs quantity** of annual acquisition.

---

## 7. What Changed from Midterm Slide Numbers

| Midterm slide | Finals adjustment |
|---------------|-------------------|
| K$528 subscription upside | Still valid at 12.5% non-sub conversion; now split conservative (5%) vs potential (12.5%) |
| K$219 retention | Recalculated on filtered pool: 2,346 × 10–15% × S$336 |
| 51%+ discount story | **Removed from finals narrative** per LP — still in historical EDA, excluded from eligible cohort |
| S$190 vs S$198 website LTV | Unchanged; document which aggregation you cite |

---

*Script: `EDA/12_finals_deep_dive.py` · Outputs: `EDA/outputs/12_*.csv`*
