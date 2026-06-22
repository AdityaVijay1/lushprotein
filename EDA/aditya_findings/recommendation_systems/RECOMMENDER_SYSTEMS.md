# Four Recommendation Systems — Comparison, Evidence & Integration

**Scripts:** `sku_market_basket.py`, `build_recommenders.py`  
**Architecture (founder-facing):** `RECOMMENDATION_ARCHITECTURE.md` — 4-layer lifecycle map  
**Parent recommendation:** `../FINDINGS_AND_RECOMMENDATIONS.md` (Recommendation 2)  
**Integration demo:** `../pitch_analysis/INTEGRATION_DEMO.md` (email + PDP mockups with real data)

---

## 4-layer architecture summary

| Layer | Stage | System | Deploy |
|-------|-------|--------|--------|
| **L1** | First purchase (cold start) | Rule-based | Klaviyo welcome / day 3 |
| **L2** | Same cart | Association rules (MBA) | PDP + cart widgets |
| **L3** | Post-purchase (future orders) | Sequential + timed Klaviyo | Day 14 / day 7 flows |
| **L4** | Logged-in repeat (3+ orders) | Item-item CF | Account page |

**Full business justification:** `RECOMMENDATION_ARCHITECTURE.md`

---

## Which to use — decision guide

| If you need… | Layer | Use this | Evidence it works |
|--------------|-------|----------|-------------------|
| Recommend on **1st purchase** (cold start) | L1 | **Rule-based** | 65% D1 Lean buyers also buy Clear; 53% Clear also buy Lean |
| **Same-cart** bundle on PDP | L2 | **Association rules** | Peach↔White Grape: 36% confidence, 333 co-orders, lift 2.5× |
| **Next order** after replenishment cycle | L3 | **Sequential + Klaviyo** | 739 measured 1st→2nd SKU transitions; day 14 timing |
| **Logged-in** personalised suggestions | L4 | **Item-based CF** | 83 SKUs with 10+ buyers; TMT→Taro similarity 0.40 |

**Deploy order:** L1 (week 1) → L3 (week 2) → L2 (week 3) → Subscription (week 4) → L4 (week 6+)

---

## Lifecycle stage → recommender map

| Customer stage | CRM tier (Rec 1) | Layer | Klaviyo / Shopify |
|----------------|------------------|-------|-------------------|
| First order placed | T4 First Purchasers | L1 + L3 (day 14 queued) | CS-01/02/03 |
| Browsing PDP | Any active session | L2 | Bundle widget |
| Order 1 delivered + 14 days | T4 → moving to T3 | L3 | CS-01/02/03 email |
| Order 2 delivered + 7 days | T3 Growth | L3 | CS-04 |
| Order 2 + 48 days, not subscribed | T2 High-Value | Subscription | SUB-01 |
| 3+ orders, logged in | T1/T2 | L4 | Account recommendations |

---

## Evidence backing each system

### L1. Rule-based — measured co-purchase rates

From `Recommendation_B/outputs/co_purchase_matrix_d1.csv` (CM D1 buyers):

| If bought | Recommend | Co-purchase % |
|-----------|-----------|---------------|
| Clear Protein | Lean Protein | 53% |
| Lean Protein | Clear Protein | 65% |
| Lean Protein | Accessories | 35% |
| Collagen Glow | Clear/Lean | 30.5% first-tx repeat |

**Why it works:** Observed behaviour among best customers — not industry benchmarks.

### L2. Association rules — same-order basket data

From `outputs/sku_association_rules.csv` (8,955 orders):

| Antecedent | Consequent | Confidence | Orders |
|------------|------------|------------|--------|
| Lean TMT 1kg | Clear shaker | 93% | 144 |
| Lean Taro 1kg | Lean TMT | 92% | 123 |
| Clear Peach 500g | Clear White Grape | 36% | 333 |
| Clear sachet Peach | Clear sachet W.Grape | 71% | 152 |

**Why it works:** Same-cart behaviour — ideal for PDP "Add both" widgets.

### L3. Sequential — order sequence transitions

From `outputs/first_to_second_sku_matrix.csv`:

- Clear Peach 1st → White Grape 2nd: top transition for repeaters
- Clear Peach 1st → Lean TMT 2nd: category expansion
- Lean TMT 1st → Lean Taro 2nd: flavour rotation

**Why it works:** Captures **when** customers buy. Combined with **day 14 / day 7** timing from Rec B.

### L4. Item-based CF — customer similarity

From `outputs/recommender_04_item_similarity_matrix.csv`:

- 4,290 customers × 83 SKUs (binary purchase matrix)
- Cosine similarity: TMT→Taro (0.40), Shaker (0.30), Clear Peach (0.16)

**Why item-based not user-based:** 67% one-and-done = too sparse for user vectors.

---

## Sample + subscription connection

| Trigger | System | Detail |
|---------|--------|--------|
| Pre-reorder sample | L3 + sample strategy | 7–10 days before median reorder (Clear 54d, Lean 35d, Collagen 42d) |
| Subscribe & Save | Subscription engine | After 2nd purchase + 48 days (SUB-01) |
| VIP sub (no discount) | T1 `is_top_both` | 51% already subscribed — grow remainder |

See `RECOMMENDATION_ARCHITECTURE.md` for full sample framework.

---

## Integration demo (website + email)

See **`../pitch_analysis/INTEGRATION_DEMO.md`** for:

1. **Klaviyo post-purchase email** — full copy, day 14 after order 1
2. **Shopify PDP bundle widget** — Peach + White Grape with confidence %
3. **Cart drawer CF** — logged-in repeaters
4. **Subscribe & Save** — 48-day trigger with reorder gap evidence

All pairs from `sku_association_rules.csv` — not invented.

---

## Demo comparison file

`outputs/recommender_comparison_demo.csv` — same input SKU, 4 systems side-by-side:

| Input | Rule-based (L1) | Association (L2) | Sequential (L3) | Item-CF (L4) |
|-------|-----------------|---------------|------------|---------|
| Clear Peach | Lean; Accessories | White Grape | Peach (replenish) | W.Grape, Shaker, TMT |

---

## Charts

- `fig_top_association_rules.png` — top 10 rules for deck
- `fig_recommender_effort_impact.png` — effort vs expected lift
- `fig_cluster_heatmap.png` — hierarchical clusters (supplementary)

---

## Regenerate

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
```

---

## Deployment roadmap

| Week | Layer | System | Where |
|------|-------|--------|-------|
| 1–2 | L1 + L3 | Rule-based + Klaviyo CS-01–03 | Email flows |
| 2–3 | L2 | Association rules | PDP widgets on top 5 SKUs |
| 3–4 | L3 | CS-04 sequential | Post-purchase order 2 |
| 4–5 | Sub | SUB-01–02 | Subscribe & Save |
| 6+ | L4 | Item-CF | Logged-in recommendations |
