# Recommendation B — Use Your Product Lineup to Cross-Sell, on a Schedule

**Script:** `run_recommendation_b.py`  
**One sentence:** After a customer's **1st order ships**, nudge them toward a **2nd product category on order 2** — and after **order 2**, push toward a **3rd category by order 3**.

---

## Phase 1 timing — read this first

This is the #1 source of confusion. Here is the exact sequence:

| When | What fires | What you recommend | Goal |
|------|------------|-------------------|------|
| **Day 14 after order 1 ships** | Klaviyo flow CS-01 / CS-02 / CS-03 | The **other protein category** they have NOT bought yet | 2nd category on **order 2** |
| **Day 7 after order 2 ships** | Klaviyo flow CS-04 (add to flows) | 3rd category (Collagen, Accessories add-on, or 2nd flavour) | 3rd category by **order 3** |
| **At checkout (order 1)** | Shopify bundle widget | Clear + Lean starter bundle | Same-order cross-sell |

**It is NOT "wait until order 2 then recommend."**  
The email fires **after order 1** so the recommendation lands **before they place order 2**.

### The 3 Klaviyo flows (Phase 1)

| Flow | Trigger | Delay from order 1 | Recommend for order 2 |
|------|---------|-------------------|------------------------|
| **CS-01 Clear → Lean** | 1st order contained Clear Protein | 14 days | Lean Protein (TMT or Taro 1kg) |
| **CS-02 Lean → Clear** | 1st order contained Lean Protein | 14 days | Clear Protein (Peach or White Grape 500g) |
| **CS-03 Collagen → Protein** | 1st order was Collagen, no protein SKU | 21 days | Clear or Lean starter 500g |

File: `outputs/klaviyo_cross_sell_flows.csv`

### Shopify bundle (same time as order 1)

**Clear + Lean starter** on PDP and cart — for buyers who haven't tried both.

- True bundle GP: **S$73.60** per conversion (COGS-backed)
- 5% bundle discount costs S$3.68 — net GP still **S$69.92**

---

## Size of prize — explained plainly

The scenarios in `bundle_roi_scenarios.csv` and `pitch_analysis/outputs/prize_scenarios_explained.csv` use this formula:

```
Annual GP uplift = POOL x CONVERSION RATE x GP UPLIFT PER CUSTOMER
```

### What does POOL mean?

**Pool = the number of customers eligible for that action today** (not revenue, not orders).

| Scenario | Pool | Plain English |
|----------|------|---------------|
| **8% single-cat → 2nd category** | **2,514** | Customers who have **only ever bought 1 product category** (e.g. Clear only, never Lean) |
| **5% single-cat → 3 categories** | **2,514** | Same people — but the goal is deeper: add Lean + Collagen, not just one more |
| **8% middle decile → 2nd category** | **1,309** | Customers in profit deciles 5–7 (middle spenders) who are moveable but not yet VIP |
| **5% single-cat → bundle** | **2,514** | Same single-category pool — how many buy the Clear+Lean bundle |

### What does conversion rate mean?

**Conversion rate = what % of that pool you realistically convert in year 1** (conservative).

Example: 8% of 2,514 = **201 customers** add a 2nd category.

### Worked example — the biggest prize (category ladder)

From `pitch_analysis/outputs/category_ladder_gp.csv`:

| Categories ever bought | Customers | Avg GP | Repeat rate |
|------------------------|-----------|--------|-------------|
| 1 category only | 2,514 (59%) | **S$59** | 17% |
| 2 categories | 1,216 (28%) | **S$79** | 30% |
| 3 categories | 410 (10%) | **S$144** | 55% |

**If 5% of single-category buyers (126 customers) reach 3 categories:**
- GP uplift per customer: S$144 − S$59 = **S$85**
- Annual GP uplift: 126 × S$85 = **S$10,693**

**If 8% add just a 2nd category (201 customers):**
- GP uplift per customer: S$79 − S$59 = **S$20**
- Annual GP uplift: 201 × S$20 = **S$3,969**

This is the **largest growth lever** in the 4,290-customer pool — bigger than stopping discount leakage (Rec A).

---

## Proof (figures in `outputs/`)

| Figure | What it proves |
|--------|----------------|
| `fig_co_purchase_heatmap_d1.png` | Clear↔Lean co-purchase is 53–65% among best buyers |
| `fig_sole_vs_cross_d1.png` | Only 28% of D1 stay in one category |
| `fig_breadth_by_order.png` | Category breadth jumps at order 3 — time the 3rd-category nudge there |
| `fig_bundle_roi.png` | Bundle scenarios with true COGS |
| `../pitch_analysis/outputs/fig_category_ladder.png` | Each category added = more GP + higher repeat |

---

## Phase 2 — SKU-level (built)

| Output | Use |
|--------|-----|
| `../recommendation_systems/outputs/sku_association_rules.csv` | PDP "Frequently bought together" |
| `../recommendation_systems/outputs/first_to_second_sku_matrix.csv` | Exact SKU for order 2 email |
| `../pitch_analysis/INTEGRATION_DEMO.md` | Mockups for website + email |

**Top pairs:** Peach ↔ White Grape Clear (36% confidence), Taro ↔ TMT Lean (36%)

---

## Regenerate

```bash
python EDA/aditya_findings/Recommendation_B/run_recommendation_b.py
python EDA/aditya_findings/build_pitch_analysis.py
```
