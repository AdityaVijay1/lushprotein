# LushProtein — Findings & Recommendations (Product × Customer)

**Author:** Aditya · Group 1 · ISSS603  
**Sources:** `category_analysis/` + `decile_analysis/` + **LP COGS (June 2026)**  
**Cohort:** 4,290 customers · S$552K revenue · **true margin where COGS available (70.5% weighted)**  
**Date:** June 2026

> **Deck = one story + two recommendations (Section 2).** Everything else is PDF / Q&A.

---

## 1. The one narrative (pitch to the founder)

**10% of your customers generate 41% of your true gross profit.** They are not just "more frequent" — they buy **bigger baskets** (S$326 avg GP vs S$5 for worst decile) and **more categories** (2.2+ vs 1.6).

At the same time, you're probably **over-discounting** these people. A 10% site-wide sale on your best 429 customers costs **S$14K in GP** they would have spent anyway. And half your "loyal" frequent buyers aren't actually your most profitable.

**The story:** *Find your best customers, stop discounting them, and use your product range (Clear + Lean, flavours, 2nd category by order 3) to turn everyone else into better buyers.*

---

## 2. Lead with these two recommendations

### Recommendation A — Stop treating your best customers like strangers

**What it means:** Export `klaviyo_crm_tiers.csv` → tag customers in Klaviyo/Shopify:

| Tier | Who | Count | What to do |
|------|-----|-------|------------|
| **VIP** | Best profit + best frequency | **245** | Early access, bundles, subscription. **No % off.** |
| **Profit D1** | High spend, not frequent | **184** | Premium upsell (1kg packs). **No blanket promos.** |
| **Freq D1** | Frequent, lower spend | **184** | Replenishment reminders only. |
| **Standard** | Everyone else | **3,677** | Normal acquisition/win-back. |

**Why (one number):** 10% discount on profit D1 = **S$14K GP lost/yr** (true COGS). VIPs alone hold **26% of all GP**.

**Product depth:** D1 over-indexes on **Lean** (index 275) and **Clear** (265). True margin on hero SKUs = **~70%**, not 40%. Upsell 1kg / hero flavours — not shakers as lead.

**Size of prize:** **S$18–20K GP/yr** (leakage stopped + VIP retention)

**Execution:** **High** — CSV export → Klaviyo tags. **2–4 weeks.**

**Slide figures:** `Recommendation_A/outputs/fig_gp_by_decile_true.png`, `fig_discount_erosion.png`

**Full doc:** `Recommendation_A/RECOMMENDATION_A.md`

---

### Recommendation B — Use your product lineup to cross-sell, on a schedule

**What it means:**

**Phase 1 (now):**
- 3 Klaviyo flows: **Clear→Lean**, **Lean→Clear**, **Collagen→protein** (trigger: after 2nd order)
- 1 Shopify bundle: **Clear + Lean starter** (5% bundle discount, not stackable)
- Tag tiers from Rec A so VIPs get bundles, not % off

**Phase 2 (next sprint):**
- Plug `sku_association_rules.csv` into PDP
- Plug `first_to_second_sku_matrix.csv` into post-purchase emails

**Why (one number):** Only **28%** of D1 stay in one category. **65%** of D1 Lean buyers also buy Clear. Category breadth jumps at **order 3**.

**Product depth:** Top SKU pairs: **Peach ↔ White Grape Clear** (36% confidence), **Taro ↔ TMT Lean** (36%). Bundle true GP = **S$73.60**/conversion.

**Size of prize:** **S$15–16K GP/yr** conservative (flows + bundle scenarios in `bundle_roi_scenarios.csv`)

**Execution:** **Medium** — 3 flows + 1 bundle. **4–6 weeks.**

**Slide figures:** `Recommendation_B/outputs/fig_co_purchase_heatmap_d1.png`, `fig_breadth_by_order.png`

**Full doc:** `Recommendation_B/RECOMMENDATION_B.md`

---

## 3. LP COGS data — how we use it

**File:** `20260616-COGS_Data_Request_LushProtein (1).xlsx`

| Metric | Before (40% proxy) | After (LP COGS) |
|--------|-------------------|-----------------|
| Revenue with known margin | 31% | **74.7%** |
| SKUs with unit cost | 28 | **129** |
| Weighted gross margin | 40% assumed | **70.5%** measured |
| D1 % of profit | 44% | **41%** (still hyper-concentrated) |
| D1 avg GP | S$228 (proxy) | **S$326** (true hybrid) |
| Margin leakage (10% on D1) | ~S$24K (estimated) | **S$14K** (true GP base) |

**Method:** True GP on COGS-covered lines + 40% proxy on remainder. See `margin_analysis/MARGIN_ANALYSIS.md`.

**What changed:** Profit decile ranks are **54% stable** — story holds, numbers are sharper. Hero proteins are **more profitable** than we assumed. Accessories margin may be lower — validates "shaker as add-on, not lead."

---

## 4. Market basket analysis

### Phase 1 — Done (category level)

| Asset | Location |
|-------|----------|
| Co-purchase matrix (D1) | `Recommendation_B/outputs/co_purchase_matrix_d1.csv` |
| 3 Klaviyo flow specs | `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv` |
| Bundle ROI | `Recommendation_B/outputs/bundle_roi_scenarios.csv` |

### Phase 2 — Done (SKU level)

| Asset | Location |
|-------|----------|
| Top 20 association rules | `recommendation_systems/outputs/sku_association_rules.csv` |
| Next-order matrix | `recommendation_systems/outputs/first_to_second_sku_matrix.csv` |
| 4 recommender comparison | `recommendation_systems/outputs/recommender_system_comparison.csv` |

**Expected yield (Phase 2):** +2–3% attach on repeat orders; flavour bundles (Peach + TMT) outperform generic links.

---

## 5. Four recommendation systems

| # | System | Deploy where | Effort | Lift |
|---|--------|--------------|--------|------|
| 1 | **Rule-based** | Klaviyo flows | Low | 5–8% |
| 2 | **Association rules** | PDP bundles | Low-Med | 2–4% |
| 3 | **Sequential next-best** | Post-purchase email | Medium | 3–5% |
| 4 | **Item-based CF** | Logged-in "You may also like" | Med-High | 2–3% |

**Item-based CF chosen over user-based** because 67% one-and-done = sparse user vectors; item similarity works from first purchase.

**Full doc:** `recommendation_systems/RECOMMENDER_SYSTEMS.md`

---

## 6. Hierarchical clustering — yes, but not as primary recommender

**5 clusters** on purchase profiles confirm:
- **Casual_Clear** = 3,712 customers (86%) — cross-sell target for Rec B
- **Premium** clusters = 9% of customers, ~40%+ of GP — protect via Rec A

**Use for:** Segment validation, appendix. **Not for:** Product recommendations (use the 4 systems above).

**Full doc:** `recommendation_systems/HIERARCHICAL_CLUSTERING.md`

---

## 7. Findings catalog (prioritised by size of prize)

### Customer concentration
| Finding | Evidence | Action |
|---------|----------|--------|
| GP hyper-concentrated | D1 = **41% true GP**, 43% revenue | VIP programme |
| Profit ≠ frequency | 245 both, 184 profit-only, 184 freq-only | Two playbooks |
| 69× GP gap | D1 S$326 vs D10 S$5 (true COGS) | Don't discount D1 |
| 21 whales | First 10% revenue = 21 customers | Founder outreach |

### Product × category
| Finding | Evidence | Action |
|---------|----------|--------|
| Hero proteins | Lean index 275, Clear 265 | Lead acquisition with Clear/Lean |
| Cross-sell is norm for D1 | 72% multi-category | Trigger for everyone at order 3 |
| Clear↔Lean pair | 53–65% D1 co-purchase | Bundle + flows |
| Collagen quality entry | 30.5% repeat | Collagen→protein flow |
| Accessories weak lead | VTD index ~68 | 30-day protein upsell |

### Margin (new — COGS)
| Finding | Evidence | Action |
|---------|----------|--------|
| True margin > proxy | **70.5%** weighted on covered SKUs | Stop assuming 40% everywhere |
| Discount erosion quantified | 10% on D1 = **S$14K GP** | Exclude D1 from site-wide promos |
| Bundle still profitable | S$73.60 GP after 5% bundle discount | Clear+Lean starter bundle |

---

## 8. Combined yield (both recommendations)

| Source | Conservative GP/yr |
|--------|-------------------|
| Rec A — stop margin leakage | **S$14–20K** |
| Rec B — cross-sell flows + bundle | **S$15–16K** |
| **Combined** | **S$29–36K GP** |

---

## 9. What goes on slides vs PDF

| Deck (5–6 slides) | PDF / appendix |
|-------------------|----------------|
| Narrative: 10% → 41% GP | Full decile tables |
| Rec A: CRM tiers + S$14K leakage | COGS coverage, rank stability |
| Rec B: cross-sell heatmap + order 3 | SKU association rules, 4 recommenders |
| Combined yield: S$29–36K | Hierarchical clustering, full EDA |
| Next step: deploy Klaviyo tags | `customers_decile_table.csv` definitions |

---

## 10. Regenerate everything

```bash
python EDA/aditya_findings/run_all.py
```

Or step by step:
```bash
python EDA/aditya_findings/margin_analysis/run_margin_analysis.py
python EDA/aditya_findings/Recommendation_A/run_recommendation_a.py
python EDA/aditya_findings/Recommendation_B/run_recommendation_b.py
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
python EDA/aditya_findings/recommendation_systems/hierarchical_clustering.py
```

---

## 11. Folder index

| Folder | Contents |
|--------|----------|
| `margin_analysis/` | COGS integration, true profit deciles, leakage |
| `Recommendation_A/` | CRM tiers, Klaviyo export, discount erosion proof |
| `Recommendation_B/` | Cross-sell flows, bundle ROI, co-purchase heatmaps |
| `recommendation_systems/` | SKU MBA, 4 recommenders, clustering |
| `20260616-COGS_Data_Request_LushProtein (1).xlsx` | LP margin data |

---

*Lead with Rec A + Rec B. Same story: protect the profit core, grow through product structure — not blanket promos.*
