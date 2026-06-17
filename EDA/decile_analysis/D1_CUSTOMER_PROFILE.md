# What Makes a D1 Customer? — Identification & Conversion Playbook

**Pool:** 4,290 customers (finals, excl. 100% marketplace)  
**Profit D1:** 368 customers (9% of pool) · **357** avg true GP  
**Data:** True COGS hybrid + `outputs_finals/` enriched parquets  
**Script:** `run_d1_profile_analysis.py`

> **Meeting prep:** How Rec C (cross-sell) and Rec D (subscription) systematically create D1 customers — see `../aditya_findings/FOUNDER_MEETING_PREP.md` Section 3.

---

## 1. Executive summary — the D1 fingerprint

A **profit D1 customer** is not simply "someone who orders a lot." They are identifiable by a **combination** of:

1. **Premium basket** — high $/unit (S$61 vs S$8 for D10)
2. **Multi-category shopping** — 2.5 categories ever vs 1.4 for D10
3. **Hero protein affinity** — over-index on Clear + Lean (D1 index 265–275 in category analysis)
4. **Repeat behaviour** — 88% repeat rate vs 4% for D10
5. **Moderate frequency** — 4.4 orders avg (profit-only D1 often have fewer orders but higher AOV)

**The 69× GP gap** (D1 S$357 vs D10 S$6) comes from **basket quality × breadth**, not order count alone.

---

## 2. Identification factors (ranked by lift vs non-D1)

*100 = same as non-D1. Above 100 = D1 over-indexes.*

| Rank | Factor | D1 rate/avg | Non-D1 | Index |
|------|--------|-------------|--------|-------|
| 1 | Loyal repeater flag | 64% | 6% | **1052** |
| 2 | 3+ categories | 44% | 10% | **434** |
| 3 | Is repeat buyer | 88% | 21% | **427** |
| 4 | Ever bought Collagen Glow | 24% | 8% | **286** |
| 5 | Ever subscribed | 38% | 15% | **258** |
| 6 | 2+ categories | 73% | 38% | **189** |
| 7 | Dominant pack = 1kg | 51% | 32% | **160** |
| 8 | First channel = Subscription | 54% | 35% | **157** |

### Continuous metrics (D1 vs non-D1)

| Metric | D1 | Non-D1 | D1 index |
|--------|-----|--------|----------|
| avg_gp | 356.55 | 53.71 | 664 |
| avg_orders | 4.37 | 1.32 | 331 |
| avg_aov | 210.83 | 65.98 | 320 |
| avg_categories | 2.46 | 1.51 | 164 |
| dollars_per_unit | 61.32 | 38.32 | 160 |
| avg_disc_pct | 0.1 | 0.09 | 118 |

**Key insight:** The strongest *predictive* signals are **loyal repeater flag**, **3+ categories**, and **repeat purchase**. Product signals: **Collagen**, **Clear**, **Lean**, and **1kg packs**. Frequency alone does not separate profit D1 from frequency D1.

---

## 3. Three D1 archetypes (not one monolith)

| Archetype | Count | Avg GP | Orders | AOV | Categories | Playbook |
|-----------|-------|--------|--------|-----|------------|----------|
| VIP (profit+freq D1) | 238 | S$388 | 5.9 | S$125 | 2.7 | See below |
| Profit D1 only | 130 | S$300 | 1.7 | S$368 | 2.0 | See below |
| Freq D1 only | 264 | S$105 | 3.7 | S$54 | 2.0 | See below |

### VIP (profit D1 + frequency D1) — 238 customers
- **Who:** Highest GP (S$388), 5.9 orders, 2.7 categories. 54% subscribed.
- **Identification:** `profit_decile_true = D1` AND `freq_decile_true = D1` (or `is_top_both` in decile table)
- **Action:** Protect — no blanket discounts. Early access, flavour drops, subscription perks.

### Profit D1 only — 130 customers
- **Who:** High spend per order (AOV S$368), only 1.7 orders avg. Whales and big-basket buyers.
- **Identification:** `profit_decile_true = D1` AND `freq_decile_true != D1`
- **Action:** Premium upsell (1kg packs, bundles). Do not push frequency — push basket value.

### Frequency D1 only — 264 customers
- **Who:** 3.7 orders but lower GP (S$105) and AOV (S$54). Replenishment without premium basket.
- **Identification:** `freq_decile_true = D1` AND `profit_decile_true != D1`
- **Action:** Subscribe-and-save, pack-size upgrade (500g→1kg), cross-sell to raise $/unit.

---

## 4. Product-side identification (what D1 buys)

From category x decile analysis (T4) and line-level data:

| Signal | D1 behaviour | vs All customers |
|--------|--------------|------------------|
| **Lean Protein** | D1 index **275**; 30% penetration | Higher $/unit (S$54 vs S$40) |
| **Clear Protein** | D1 index **265**; 35% penetration | Higher ACOV (S$105 vs S$78) |
| **Collagen Glow** | D1 index **202**; 22% penetration | VIP onboarding candidate |
| **Accessories** | D1 index **127** | Cart add-on only — not a D1 driver |
| **Pack size** | 51% dominant 1kg | 500g = acquisition; 1kg = loyalty |
| **Sole category** | Only ~28% stay in 1 category | Cross-shop is the norm for D1 |

**Hero SKUs among D1 loyal buyers:** Clear Peach 500g, Lean TMT 1kg, Clear White Grape 500g (from `12_loyal_repeater_reorder_skus.csv`).

---

## 5. Customer-side identification (how D1 arrives)

### First product that predicts D1 probability

| First product | D1 rate | Avg GP | Repeat rate |
|---------------|---------|--------|-------------|
| Collagen Glow | 12% | S$88 | 37% |
| Unknown | 11% | S$83 | 33% |
| Other | 9% | S$81 | 29% |
| Clear Protein | 8% | S$89 | 20% |
| Lean Protein | 6% | S$75 | 21% |
| Accessories | 5% | S$52 | 20% |
| Soy Protein | 5% | S$62 | 25% |

### Channel patterns
- **Direct / Organic** and **Subscription** channels over-index among D1
- **Accessories-first** acquisition under-indexes (VTD index ~68)
- **Collagen-first** over-indexes on lifetime quality despite smaller volume

### Discount behaviour
- D1 avg discount depth: **10.4%** — D1 can be discount-trained too; guardrail needed (Rec A)
- Do not use heavy discounting to *create* D1 — it attracts low-$/unit buyers

---

## 6. D1 scoring checklist (practical identification)

Use this to score any customer 0–100 for "D1 potential":

| Criterion | Points | How to check |
|-----------|--------|--------------|
| 2+ categories ever | +25 | `n_categories_ever >= 2` in customers.parquet |
| 3+ categories ever | +15 | `n_categories_ever >= 3` |
| Ever bought Lean | +15 | line history |
| Ever bought Clear | +15 | line history |
| $/unit above S$45 | +10 | line revenue / units |
| 1kg pack dominant | +10 | variant titles |
| Subscribed | +10 | `ever_subscribed` |
| 3+ orders | +10 | `total_orders` |
| **Accessories-only** | **-20** | only Accessories in history |
| **Single order, low AOV** | **-15** | 1 order, AOV < S$50 |

**Score ≥ 60:** High D1 potential — route to VIP nurture  
**Score 35–59:** Moveable middle (D5–D7) — cross-sell + pack upgrade  
**Score < 35:** Standard acquisition — do not spend VIP-level retention $

---

## 7. How to convert non-D1 → D1 behaviour

### Target segments (where the gap is)

| Segment | N | GP gap vs D1 | Main gap | Priority action |
|---------|---|--------------|----------|-------------------|
| D5-D7 (moveable middle) | 1309 | S$312 | 1.1 categories | See playbook |
| D2-D4 (near-D1) | 1310 | S$255 | 0.6 categories | See playbook |
| Single-category only | 2514 | S$297 | 1.5 categories | See playbook |
| Repeat non-subscriber | 689 | S$197 | 0.5 categories | See playbook |
| One-time buyers | 3160 | S$309 | 1.0 categories | See playbook |

### Conversion playbook by gap type

#### Gap 1: Single category (2,514 customers) — biggest pool
- **Problem:** Stuck at 1 category, S$59 GP, 17% repeat
- **D1 target:** 2.3+ categories, S$144+ GP at 3 categories
- **Actions:**
  1. Day 14 after order 1: Clear↔Lean cross-sell email (Rec B)
  2. Clear+Lean bundle at checkout
  3. Day 7 after order 2: push 3rd category (Collagen or 2nd flavour)
- **Prize:** 5% reach 3 categories = S$10,693 GP/yr

#### Gap 2: Low $/unit (middle deciles D5–D7)
- **Problem:** Buying 500g trial packs, not 1kg loyalty packs
- **D1 target:** S$53+/unit vs S$30–40 for middle deciles
- **Actions:**
  1. Order 2 email: "Upgrade to 1kg — better $/serve"
  2. PDP: default to 1kg for logged-in repeaters
  3. Bundle: 2× 1kg flavours at modest discount (not site-wide %)
- **Prize:** Pack upgrade on 10% of middle decile = ~S$13K GP/yr

#### Gap 3: Repeat but not subscribed (689 customers)
- **Problem:** Proved product fit, no replenishment lock-in
- **D1 target:** 62% repeat rate (subscriber benchmark)
- **Actions:**
  1. 48 days post-order 2: Subscribe & Save on exact SKU
  2. Target Freq D1 non-subs first (228 customers)
- **Prize:** 5% convert = S$2,262 GP/yr + compounding repeat

#### Gap 4: Accessories-first acquirers (371 customers)
- **Problem:** 20% repeat, S$71 avg revenue — shaker without protein habit
- **D1 target:** Protein trial within 30 days
- **Actions:**
  1. Mandatory protein upsell: sachet trial pack S$9.90
  2. Do not use shakers as paid acquisition lead

#### Gap 5: Near-D1 (D2–D4, 1,287 customers)
- **Problem:** Close to D1 economically — small nudge needed
- **Actions:**
  1. One more category or one 1kg upgrade may push them to D1
  2. Personalised email: "You're S$X away from VIP status" (gamification)

---

## 8. What does NOT convert someone to D1

| Action | Why it fails |
|--------|--------------|
| Blanket 10%-off promos | Attracts low-$/unit buyers; erodes existing D1 margin |
| Shaker-led acquisition | Accessories index 127 — not a profit driver |
| Pushing frequency alone on low-AOV buyers | Creates Freq D1, not Profit D1 |
| Win-back on D10 one-and-dones | S$5 avg GP — negative ROI |
| Generic "shop now" emails | Flavour-specific bundles outperform 3:1 |

---

## 9. Charts

| Figure | File |
|--------|------|
| GP by decile | `outputs/d1_profile/fig_gp_by_decile.png` |
| Identification factor lifts | `outputs/d1_profile/fig_d1_identification_factors.png` |
| GP vs categories scatter | `outputs/d1_profile/fig_gp_vs_categories.png` |
| D1 vs D5 vs D10 fingerprint | `outputs/d1_profile/fig_d1_fingerprint.png` |

---

## 10. Data files

| File | Contents |
|------|----------|
| `outputs/d1_profile/decile_comparison.csv` | All metrics by decile |
| `outputs/d1_profile/identification_factors.csv` | Lift indices |
| `outputs/d1_profile/d1_archetypes.csv` | VIP / profit-only / freq-only |
| `outputs/d1_profile/conversion_gaps.csv` | Target segments vs D1 |
| `outputs/d1_profile/first_product_d1_rate.csv` | First product → D1 probability |

---

## 11. Regenerate

```bash
python EDA/aditya_findings/enrich_finals_with_margin.py
python EDA/decile_analysis/run_d1_profile_analysis.py
```
