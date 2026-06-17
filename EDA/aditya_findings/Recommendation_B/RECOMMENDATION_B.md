# Recommendation B — Use Your Product Lineup to Cross-Sell, on a Schedule

**Script:** `run_recommendation_b.py`  
**One sentence:** After a customer's 2nd order, email them the complementary protein — Clear buyers get Lean, Lean buyers get Clear — and sell a Clear+Lean starter bundle.

---

## The problem (in plain English)

Most value is not from getting a 2nd order — it's from getting a **2nd product category**. D1 buyers average **2.2+ categories**; middle deciles are stuck at **1.4–1.6**. Cross-sell happens naturally for the best buyers (only **28%** of D1 stay in one category) but nobody is **triggering** it for everyone else.

---

## Phase 1 — Do now (category MBA, no new analysis)

### 3 Klaviyo flows

File: `outputs/klaviyo_cross_sell_flows.csv`

| Flow | Trigger | Delay | Evidence |
|------|---------|-------|----------|
| **Clear → Lean** | 2nd order, bought Clear first | 14 days | **53%** of D1 Clear buyers also buy Lean |
| **Lean → Clear** | 2nd order, bought Lean first | 14 days | **65%** of D1 Lean buyers also buy Clear |
| **Collagen → Protein** | 1st order Collagen, no protein | 21 days | **30.5%** Collagen repeat rate |

### 1 Shopify bundle

**Clear + Lean starter** — modest 5% bundle discount (not stackable with site promos)

- True bundle GP: **S$73.60** per conversion (COGS-backed)
- Bundle discount cost: **S$3.68** — still **S$69.92 net GP**

---

## Phase 2 — Next sprint (SKU MBA)

Script: `recommendation_systems/sku_market_basket.py`

| Output | Purpose |
|--------|---------|
| `sku_association_rules.csv` | PDP "Frequently bought together" |
| `first_to_second_sku_matrix.csv` | Post-purchase "next best SKU" |

**Top SKU pairs (same order):**
- Peach Clear ↔ White Grape Clear (36% confidence, lift 2.5×)
- Taro Lean ↔ Thai Milk Tea Lean (36% confidence)
- Lean TMT → Clear shaker (25% confidence)

**Expected yield:** +2–3% attach on repeat orders; flavour bundles beat generic "shop now"

---

## Proof (figures in `outputs/`)

### Figure 1: `fig_co_purchase_heatmap_d1.png`
D1 co-purchase rates — Clear↔Lean is the core engine

### Figure 2: `fig_sole_vs_cross_d1.png`
Only **28%** of D1 stay in one category — cross-sell is the norm for best buyers

### Figure 3: `fig_breadth_by_order.png`
Category breadth jumps at **order 3** — target cross-sell there, not order 2

### Figure 4: `fig_cross_sell_flows.png`
Data-backed evidence for each Klaviyo flow

### Figure 5: `fig_bundle_roi.png`
Bundle scenarios: **S$8.8K + S$7.2K** GP uplift (conservative)

---

## Size of prize

| Scenario | Pool | Conv. rate | GP uplift |
|----------|------|------------|-----------|
| 5% single-cat → bundle | 2,514 | 5% | **S$8,788** |
| 8% middle decile → 2nd category | 1,287 | 8% | **S$7,199** |
| Flows + bundle (conservative) | All | — | **S$15,000** |

**Execution:** Medium — 3 Klaviyo flows + 1 Shopify bundle. **4–6 weeks.**

---

## Regenerate

```bash
python EDA/aditya_findings/Recommendation_B/run_recommendation_b.py
```
