# Rec F & G — Validated Analysis

**Date:** June 17, 2026  
**Pool:** 4,290 finals-eligible customers (excl. 100% marketplace)  
**Script:** `run_rec_f_g_analysis.py`

---

## Rec F: Entry SKU Quadrant Analysis

### Method

- Source: `EDA/outputs/12_first_flavor_loyalty_min30.csv` (first-purchase SKU → repeat rate, n≥30)
- Loyal overlay: `12_loyal_repeater_top_first_flavors.csv`
- Median split on **first-buyer volume** and **repeat rate** → four quadrants

### Quadrant summary

| Quadrant | SKUs | Avg repeat | Total first-buyers | Action |
|----------|------|------------|-------------------|--------|
| **Gateway Hero** | 13 | **27.6%** | 1,544 | Default featured / ad landing SKU |
| **Hidden Gem** | 17 | **39.6%** | 597 | Grow awareness — email/PDP feature |
| **Acquisition Trap** | 17 | **14.9%** | 1,816 | Remove from top-of-funnel promos |
| **Laggard** | 12 | **13.7%** | 448 | Deprioritize |

### Top Gateway Heroes (high volume + high repeat)

| Entry SKU | First-buyers | Repeat | Notes |
|-----------|-------------|--------|-------|
| Clear Protein Peach 500g | 412 | **27%** | #1 revenue SKU; 54-day reorder cycle |
| Clear Protein White Grape 500g | 260 | **25%** | 54-day cycle; co-purchase with Peach |
| Lean Protein TMT 1kg | 192 | **35%** | Fastest reorder (35 days); highest repeat among volume SKUs |
| Plant Protein Cocoa Dinosaur 480g | 105 | **28%** | Strong repeat, moderate volume |
| Collagen Glow 300g | 76 | **34%** | High repeat; aligns with T9 index 111 |
| Better Whey Cocoa Dinosaur 1kg | 74 | **27%** | Solid gateway |
| Soy Protein Unflavoured 1kg | 84 | **24%** | Niche but sticky |

### Top Acquisition Traps (high volume + low repeat)

| Entry SKU | First-buyers | Repeat | Notes |
|-----------|-------------|--------|-------|
| Clear Shaker White | 228 | **21%** | Rec E overlap — shaker-led acquisition |
| Lean TMT "1 x 1kg" legacy handle | 182 | **13%** | Same product, different handle — data artefact |
| Clear White Grape "1 x 500g" legacy | 161 | **11%** | Legacy handle trap |
| Lean Taro "1 x 1kg" | 160 | **15%** | Low repeat flavour |
| Creatine 250g | 148 | **16%** | Supplement-only entry |
| Clear Peach "1 x 500g" legacy | 125 | **7%** | Legacy handle — worst repeat among volume SKUs |

### Hidden Gems (low volume + high repeat)

High-repeat SKUs with below-median first-buyer counts. Candidates for email features and logged-in PDP recommendations:

- Collagen variants (34–40% repeat on n=30–76)
- Plant Protein flavours (28–40% repeat)
- Discovery Sampler 6-pack (24% repeat on n=54)

### Reorder interval signals (from prior analysis)

| SKU | Reorder cycle | Quadrant |
|-----|---------------|----------|
| Lean TMT 1kg | **35 days** | Gateway Hero |
| Clear Peach 500g | **54 days** | Gateway Hero |
| Clear White Grape 500g | **54 days** | Gateway Hero |

Fast reorder + high repeat = strongest Subscribe & Save candidates (links to Rec D).

### Rec F prize scenario (validated)

| Assumption | Value |
|------------|-------|
| Annual new acquirers | 4,000 |
| % shifted trap → hero | 5% (200 customers) |
| Trap avg repeat | 14.9% |
| Hero avg repeat | 27.6% |
| Incremental lift assumed | 6.4pp (halfway) |
| GP per new repeater | S$79 (Tier-2 LTV × 66.5% margin) |
| **Annual GP uplift** | **S$1,009** |

Conservative by design. Compounding repeat benefit over 2–3 years is real but not quantified here.

### Chart

`outputs/fig_flavor_quadrant.png` — scatter of volume vs repeat, coloured by quadrant, bubble size = revenue.

---

## Rec G: Middle Decile Cross-Sell Window

### Method

- Filter: `profit_decile_true` in D5, D6, D7
- Addressable: 1 category ever **AND** 2+ total orders
- GP uplift from `pitch_analysis/outputs/category_ladder_gp.csv`

### Segment breakdown

| Segment | N | Avg categories | Avg orders | % 1-category |
|---------|---|----------------|------------|--------------|
| D5–D7 all | **1,309** | 1.35 | 1.16 | **70.5%** |
| D5–D7, 1-cat, 2+ orders (**Rec G pool**) | **88** | 1.0 | 2.31 | 100% |
| — exactly 2 orders | 67 | 1.0 | 2.0 | 100% |
| — 3+ orders (stuck repeaters) | 21 | 1.0 | 3.29 | 100% |

### Why the pool is only 88

Middle decile customers average **1.16 orders**. Most have placed only one order and are already captured by Rec C's day-14-after-order-1 cross-sell. The Rec G pool is the subset who:

1. Came back for a 2nd (or 3rd+) order — proved repeat intent
2. Still bought within a single category — cross-sell failed

This is a **high-intent, failed-cross-sell** list, not the broad middle decile.

### Category ladder economics (Rec G uses these)

| Categories | Customers (all pool) | Avg GP | Repeat |
|------------|---------------------|--------|--------|
| 1 | 2,514 | S$59 | 17% |
| 2 | 1,216 | S$79 | 30% |
| 3 | 410 | S$144 | 55% |

Uplift 1→2: **+S$20 GP**, **+13pp repeat**

### Rec G prize scenario (validated)

| Assumption | Value |
|------------|-------|
| Pool | 88 (D5–D7, 1-cat, 2+ orders) |
| Conversion to 2nd category | 8% → 7 customers |
| GP uplift per convert (1→2 cat) | S$19.74 |
| Year 1 direct GP | S$138 |
| 30% follow-on to 3-cat | 2 customers × S$65 = S$130 |
| **Year 1 total GP** | **S$269** |

### Comparison to Rec C prize (same ladder, bigger pool)

| Scenario | Pool | 5–8% convert | Year 1 GP |
|----------|------|--------------|-----------|
| Rec C: 5% of 2,514 reach 3-cat | 2,514 | 126 | **S$10,693** |
| Rec C: 8% of 2,514 add 2nd cat | 2,514 | 201 | **S$3,969** |
| Rec G: 8% of 88 add 2nd cat | 88 | 7 | **S$269** |

Rec G is a **precision retargeting layer** on Rec C, not a separate opportunity.

### Chart

`outputs/fig_middle_decile_pool.png` — D5–D7 category distribution + addressable pool funnel.

---

## Combined recommendation map

```
Acquisition (new customers)
├── Rec E: Fix category mix (stop shaker-led)
├── Rec F: Feature Gateway Hero flavours (Peach, TMT, Collagen)
└── Rec B: Day 14 cross-sell email → order 2

Repeat journey (existing customers)
├── Rec C: Category ladder (2,514 single-cat pool) ← LEAD
├── Rec G: Post-order-2 retry for 88 stuck middle decile ← nuance
└── Rec D: Subscribe & Save at 48 days post-order-2 ← LEAD

Defensive
└── Rec A: Exclude profit D1 from blanket promos
```

---

## Data files

| File | Contents |
|------|----------|
| `outputs/flavor_quadrant.csv` | All entry SKUs with quadrant assignment |
| `outputs/rec_f_prize_scenario.csv` | Rec F prize assumptions |
| `outputs/rec_g_segment_breakdown.csv` | Middle decile segment counts |
| `outputs/rec_g_prize_scenario.csv` | Rec G prize assumptions |
| `outputs/fig_flavor_quadrant.png` | Rec F scatter chart |
| `outputs/fig_middle_decile_pool.png` | Rec G pool funnel |

---

## Open questions for LP (feeds into meeting prep)

1. **Canonical SKU handles:** Which Shopify product/variant is the "real" Clear Peach 500g and Lean TMT 1kg? Legacy "1 x Pack" handles show 7–13% repeat vs 27–35% on barcode handles.
2. **Featured product logic:** How are homepage/ads landing products chosen today? Data suggests shaker and legacy handles may be over-featured.
3. **Klaviyo flow inventory:** Is there already a post-order-2 email? If yes, what's the conversion rate? (Validates Rec G pool size and conversion assumptions.)
4. **CAC by entry SKU:** We have repeat rates but not acquisition cost per flavour — needed to fully rank Gateway Heroes.
