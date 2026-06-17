# Feedback on External Rec F & G Proposals

**Date:** June 17, 2026  
**Validation script:** `run_rec_f_g_analysis.py`  
**Data:** 4,290-customer pool · true COGS on 74.7% of revenue

---

## Bottom line

The other chatbot correctly identified the two gaps you felt — **product-side entry SKU narrative** and **customer-side decile × category actionability**. The *frameworks* are good. The *prize math* for both F and G is **3–10× too optimistic** when run against your actual data.

| Rec | Framework | Data-backed? | Validated prize | Pitch tier |
|-----|-----------|--------------|-----------------|------------|
| **F** — Gateway flavor routing | ✅ Yes | ✅ Quadrants work | **~S$1K/yr** (not S$4K) | **Sharpen** Rec C/E — not a lead |
| **G** — Middle decile cross-sell window | ⚠️ Partially | ⚠️ Pool is 88, not 774 | **~S$269/yr** (not S$2.5K) | **Fold into Rec C/B** — not standalone |

**You already have two clear, data-backed pitch insights:** **Rec C** (category ladder, S$11–17K) and **Rec D** (subscribe repeaters, S$2–4K + compounding). Rec F sharpens *how* to execute C/E at the SKU level. Rec G is a timing nuance on C, not a third hero.

---

## Rec F — Gateway Flavor Playbook

### What we agree with

1. **The quadrant framework is the right product narrative.** Entry SKUs are not equal. Segmenting by first-order volume × repeat rate produces actionable merchandising rules.
2. **The story direction is correct.** Route paid/organic traffic to high-repeat entry SKUs; deprioritize high-volume, low-repeat traps from top-of-funnel.
3. **Specific SKU calls match the data:**
   - **Clear Peach 500g** — 412 first-buyers, **27% repeat** → **Gateway Hero** ✅
   - **Lean TMT 1kg** (barcode handle) — 192 first-buyers, **35% repeat** → **Gateway Hero** ✅ (fastest replenishment signal in range)
   - **Clear Shaker White** — 228 first-buyers, **21% repeat** → **Acquisition Trap** ✅ (aligns with Rec E)
4. **Strategic value is real even when prize is small.** Reordering featured products costs near-zero. This permanently changes the acquisition playbook.

### What we disagree with or would refine

1. **Prize math is overstated (~S$4K → ~S$1K).**
   - Chatbot assumed loyal-tier conversion (3+ orders) on top of repeat lift — not directly measurable from first-SKU repeat rates alone.
   - Validated scenario: 200 customers shifted (5% of ~4K new acq/yr) × 6.4pp incremental repeat (halfway trap→hero) × S$79 GP per new repeater = **S$1,009/yr**.
   - The loyal LTV gap (S$720) math is directionally interesting but speculative without cohort tracking.

2. **SKU handle duplication inflates trap count.** The same physical product appears under multiple variant handles:
   - Lean TMT **barcode handle** → Gateway Hero (35% repeat)
   - Lean TMT **"1 x 1kg Pack"** legacy handle → Acquisition Trap (12.6% repeat, 182 buyers)
   - Clear Peach **barcode** → Gateway Hero (27%)
   - Clear Peach **"1 x 500g"** handle → Acquisition Trap (7.2% repeat)
   
   **Action for LP meeting:** Ask which handle is the canonical Shopify product. Consolidate analysis by barcode, not variant title, before changing ad landing pages.

3. **Hidden Gems are under-promoted but small.** 17 SKUs with high repeat, low volume (e.g. Collagen 300g at 34% on n=76). Worth featuring in email/PDP, but not acquisition-scale volume.

4. **Rec F overlaps Rec E.** Shaker-led acquisition is already Rec E. F adds granularity (which protein flavours to feature), not a new strategic layer.

### Recommended positioning in deck

> "Don't just fix acquisition *category* (stop shaker-led — Rec E). Fix acquisition *flavour*: feature Clear Peach and Lean TMT as default entry points; pull shaker promos to cart-add only."

**Tier:** Product execution detail under Rec C + E. Prize ~S$1K direct + permanent merchandising benefit.

---

## Rec G — Middle Decile Cross-Sell Window

### What we agree with

1. **Middle deciles are under-served.** D5–D7 = **1,309 customers**, **70.5% still at 1 category**, avg **1.35 categories** vs D1 at 2.3.
2. **Category ladder economics are real.** 1-cat → 2-cat = **+S$20 GP** and **17% → 30% repeat** (from `category_ladder_gp.csv`).
3. **Collagen T9 index (111) supports Collagen as 2nd category** for protein-first buyers.
4. **Timing precision (post order 2, pre order 3) is a valid CRM design choice** — different from Rec B's day-14-after-order-1 trigger.

### What we disagree with

1. **Addressable pool is ~9× smaller than claimed.**

   | Segment | Chatbot estimate | Validated count |
   |---------|------------------|-----------------|
   | D5–D7 total | ~1,290 | **1,309** ✅ |
   | 1-category share | 60% → ~774 | **70.5% → 923** (all 1-cat middle decile) |
   | **1-cat AND 2+ orders** | **774** | **88** ❌ |

   Why the gap: D5–D7 avg orders = **1.16**. Most middle-decile customers have only **one order**. The "bought twice but never cross-sold" segment is tiny (88), not 774.

2. **Prize math collapses (~S$2.5K → ~S$269).**
   - 88 pool × 8% convert = 7 customers × S$20 GP uplift = S$138
   - Plus 30% follow-on to 3-cat: 2 customers × S$65 = S$130
   - **Total ~S$269/yr** — not material as a standalone recommendation.

3. **Rec G is largely redundant with Rec C.** Rec C already targets 2,514 single-category buyers (the real pool). Rec G adds segment filter (middle decile) + timing (post order 2) but shrinks the pool to 88.

4. **The sharper sub-story within G:** **21 "stuck repeaters"** — D5–D7, 1 category, **3+ orders**. These customers proved repeat intent but never cross-sold. That's a CRM list, not a S$2.5K prize.

### Recommended positioning in deck

Do **not** pitch Rec G as a standalone recommendation. Instead:

- **Rec C** owns the category ladder (2,514 pool, S$11–17K).
- **Rec B** owns timing (day 14 post order 1; day 7 post order 2).
- **Rec G insight** becomes one bullet: *"Prioritise the 88 middle-decile customers who ordered 2+ times on one category — they're warm but stuck. A second cross-sell email after order 2 ships is cheap insurance."*

---

## How F & G fit the existing stack (revised)

| Rec | Role | Validated prize | Layer |
|-----|------|-----------------|-------|
| **C** | Climb category ladder | **S$11–17K** | **Lead — customer** |
| **D** | Subscribe repeaters | **S$2–4K** | **Lead — product/replenishment** |
| B | Execute C (day 14 / day 7 flows) | — | Tactical |
| E | Fix acquisition category mix | S$4K | Product |
| A | VIP guardrail | S$14K protected | Defensive |
| **F** | Gateway flavour routing | **~S$1K** | Product sharpen (under C/E) |
| **G** | Middle decile post-order-2 | **~S$269** | Segment nuance (under C/B) |

**What F and G add that was missing:** connecting specific products to specific segments at specific journey moments. That's valuable for execution detail — but it does not replace C + D as the two hero insights.

---

## Your two pitch-ready insights (confirmed)

### Insight 1 — Customer: "Most customers never leave one category"

- **59%** of customers (2,514) bought only one category ever
- GP **S$59** vs **S$144** at 3 categories; repeat **17%** vs **55%**
- **Fix:** Rec B flows + Clear↔Lean bundle → **S$10,693 GP/yr** (5% reach 3 cats)

### Insight 2 — Product: "Repeaters aren't on Subscribe & Save"

- **689** customers ordered 2+ times, never subscribed
- Subscribers repeat **62%** vs **19%**; GP gap **S$66/customer**
- **Fix:** 48-day post-order-2 flow on Peach Clear / TMT Lean → **S$2,262 GP/yr** (5% convert)

Rec F (which flavours to feature) and Rec G (which segment to hit post-order-2) make these two insights *executable* — they don't replace them.

---

## Regenerate validation

```bash
python EDA/aditya_findings/rec_f_g_validation/run_rec_f_g_analysis.py
```

**Outputs:** `outputs/flavor_quadrant.csv`, `fig_flavor_quadrant.png`, `fig_middle_decile_pool.png`, prize scenarios
