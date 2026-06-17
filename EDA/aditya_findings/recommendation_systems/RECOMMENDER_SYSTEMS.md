# Four Recommendation Systems — Comparison, Evidence & Integration

**Scripts:** `sku_market_basket.py`, `build_recommenders.py`  
**Integration demo:** `../pitch_analysis/INTEGRATION_DEMO.md` (email + PDP mockups with real data)

---

## Which to use — decision guide

| If you need… | Use this | Evidence it works |
|--------------|----------|-------------------|
| Recommend on **1st purchase** (cold start) | **Rule-based** | 65% D1 Lean buyers also buy Clear; 53% Clear also buy Lean |
| **Same-cart** bundle on PDP | **Association rules** | Peach↔White Grape: 36% confidence, 333 co-orders, lift 2.5× |
| **Next order** SKU after replenishment | **Sequential** | 739 measured 1st→2nd SKU transitions in finals data |
| **Logged-in** personalised suggestions | **Item-based CF** | 83 SKUs with 10+ buyers; TMT→Taro similarity 0.40 |

**Deploy order:** Rule-based (week 1) → Sequential (week 3) → Association PDP (week 4) → Item-CF (week 6+)

---

## Evidence backing each system

### 1. Rule-based — measured co-purchase rates

From `Recommendation_B/outputs/co_purchase_matrix_d1.csv` (profit D1 buyers):

| If bought | Recommend | Co-purchase % |
|-----------|-----------|---------------|
| Clear Protein | Lean Protein | 53% |
| Lean Protein | Clear Protein | 65% |
| Lean Protein | Accessories | 35% |
| Collagen Glow | Clear/Lean | 30.5% first-tx repeat |

**Why it works:** These are observed behaviour rates among your best customers — not industry benchmarks.

### 2. Association rules — same-order basket data

From `outputs/sku_association_rules.csv` (8,955 orders analysed):

| Antecedent | Consequent | Confidence | Orders |
|------------|------------|------------|--------|
| Lean TMT 1kg | Clear shaker | 93% | 144 |
| Lean Taro 1kg | Lean TMT | 92% | 123 |
| Clear Peach 500g | Clear White Grape | 36% | 333 |
| Clear sachet Peach | Clear sachet W.Grape | 71% | 152 |

**Why it works:** High-confidence pairs are same-cart behaviour — ideal for PDP "Add both" widgets.

### 3. Sequential — order sequence transitions

From `outputs/first_to_second_sku_matrix.csv`:

- Clear Peach 1st order → White Grape 2nd order: among top transitions for repeaters
- Lean TMT 1st → Lean Taro 2nd: flavour rotation within category

**Why it works:** Captures **when** customers buy, not just what they buy together.

### 4. Item-based CF — customer similarity

From `outputs/recommender_04_item_similarity_matrix.csv`:

- 4,290 customers × 83 SKUs (binary purchase matrix)
- Cosine similarity: customers who bought TMT also bought Taro (0.40), Shaker (0.30), Clear Peach (0.16)

**Why item-based not user-based:** 67% one-and-done = too sparse for user vectors. Item similarity works from first purchase.

---

## Integration demo (website + email)

See **`pitch_analysis/INTEGRATION_DEMO.md`** for:

1. **Klaviyo post-purchase email** — full copy with merge tags, triggered day 14 after order 1
2. **Shopify PDP bundle widget** — Peach + White Grape with confidence % from data
3. **Cart drawer CF** — "You may also like" for logged-in repeaters
4. **Subscribe & Save** — 48-day trigger with reorder gap evidence

All product pairs in the demo come from `sku_association_rules.csv` — not invented.

---

## Demo comparison file

`outputs/recommender_comparison_demo.csv` — same input SKU, 4 systems side-by-side:

| Input | Rule-based | Association | Sequential | Item-CF |
|-------|------------|-------------|------------|---------|
| Clear Peach | Lean; Accessories | White Grape | Peach (replenish) | W.Grape, Shaker, TMT |

---

## Charts

- `fig_top_association_rules.png` — top 10 rules for deck
- `fig_recommender_effort_impact.png` — effort vs expected lift

---

## Regenerate

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
python EDA/aditya_findings/recommendation_systems/build_recommenders.py
```

---

## Deployment roadmap

| Week | System | Where |
|------|--------|-------|
| 1–2 | Rule-based | 3 Klaviyo flows (Rec B) |
| 3–4 | Association rules | PDP widgets on top 5 SKUs |
| 5–6 | Sequential | Post-purchase flow order 2 |
| 7+ | Item-CF | Logged-in recommendations |
