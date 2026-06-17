# LushProtein — Findings & Recommendations (Product × Customer)

**Author:** Aditya · Group 1 · ISSS603  
**Pool:** 4,290 customers · true COGS on 74.7% of revenue · **70.5% measured margin**  
**Date:** June 2026

> **Deck:** Lead with **Rec C + Rec D**. Rec B executes C. Rec A is guardrail only.

---

## 1. The one narrative

**59% of customers have only ever bought one product category.** They average S$59 GP and 17% repeat. Customers with 3 categories average **S$144 GP and 55% repeat** — 2.4× the profit, 3× the repeat.

The fix is not more discounting (that saves S$14K on VIPs at best). The fix is **product structure**: cross-sell Clear↔Lean on order 2, add a 3rd category by order 3, and put repeat buyers on Subscribe & Save for hero SKUs.

---

## 2. Lead recommendations (pitch order)

### Recommendation C — Climb the category ladder (LEAD)

| | |
|---|---|
| **What** | 2,514 single-category buyers → target 2nd category on order 2, 3rd by order 3 |
| **Why** | GP S$59 → S$144 (+S$85); repeat 17% → 55% |
| **Prize** | 5% reach 3 categories = **S$10,693 GP/yr**; 8% add 2nd = **S$3,969** |
| **How** | Rec B flows (day 14 after order 1) + Clear+Lean bundle |
| **Figure** | `pitch_analysis/outputs/fig_category_ladder.png` |

**Full doc:** `pitch_analysis/NEW_RECOMMENDATIONS.md` · **Hypothesis:** H1 in `pitch_analysis/HYPOTHESES.md`

---

### Recommendation D — Subscribe the repeaters

| | |
|---|---|
| **What** | Klaviyo flow: 48 days after 2nd order → Subscribe & Save on exact SKU (Peach Clear / TMT Lean) |
| **Why** | Subscribers repeat **62%** vs **19%**; GP gap **S$66/customer** |
| **Prize** | 5% of 689 repeat non-subs = **S$2,262 GP/yr** (+ compounding repeat) |
| **Product** | Target top replenishment SKUs: Clear Peach 500g, Lean TMT 1kg |
| **Figure** | `pitch_analysis/outputs/fig_prize_by_hypothesis.png` |

**Hypothesis:** H2

---

### Recommendation B — Cross-sell execution engine (supports C)

**Phase 1 timing (critical):**

| When | Action |
|------|--------|
| **Day 14 after order 1 ships** | Email: recommend other protein for **order 2** |
| **Day 7 after order 2 ships** | Email: recommend 3rd category for **order 3** |
| **At order 1 checkout** | Clear+Lean bundle offer |

**Not** "after order 2" — the email fires after order 1 so it influences order 2.

**Prize explained:** See `Recommendation_B/RECOMMENDATION_B.md` — pool = eligible customers, conversion = % converted, uplift = GP gain per customer.

**Full doc:** `Recommendation_B/RECOMMENDATION_B.md`

---

### Recommendation A — VIP guardrail (keep, don't lead)

Exclude 429 profit D1 + 245 VIP from site-wide % promos. Saves **S$14K GP/yr**. Operational — implement alongside C/D.

**Full doc:** `Recommendation_A/RECOMMENDATION_A.md`

---

### Recommendation E — Fix acquisition product mix

Accessories-first: 20% repeat. Collagen-first: 37%. Stop shaker-led acquisition; 30-day protein upsell for shaker buyers. **S$4,389 GP** if 15% convert.

**Hypothesis:** H4

---

## 3. COGS integration

**Script:** `enrich_finals_with_margin.py` — updates `outputs_finals/*.parquet`

| Table | New columns |
|-------|-------------|
| `lines.parquet` | `unit_cost`, `cogs`, `gross_profit`, `margin_pct`, `pack_size` |
| `orders.parquet` | `order_gp`, `order_margin_pct`, `n_categories` |
| `customers.parquet` | `true_gross_profit`, `n_categories_ever`, `crm_tier`, `profit_decile_true` |

---

## 4. Hypothesis framework (all 5)

| ID | Hypothesis | Prize | Rec |
|----|------------|-------|-----|
| H1 | Category ladder drives GP + repeat | S$11–17K | C + B |
| H2 | Subscription captures replenishment | S$2–4K + repeat | D |
| H3 | Pack-size upgrade (500g→1kg) | S$13K | Product |
| H4 | First-product steers ceiling | S$4K | E |
| H5 | VIP discount guardrail | S$14K protected | A |

**Full write-up:** `pitch_analysis/HYPOTHESES.md`  
**Scenarios with pool explained:** `pitch_analysis/outputs/prize_scenarios_explained.csv`

---

## 5. Recommendation systems + integration demo

| System | Deploy | Evidence |
|--------|--------|----------|
| Rule-based | Klaviyo day-14 email | 65% Clear↔Lean co-purchase |
| Association rules | PDP bundle widget | Peach↔White Grape 36% conf, 333 orders |
| Sequential | Order 2 email | 739 SKU transitions measured |
| Item-CF | Logged-in page | 83 SKUs, cosine similarity |

**Integration mockups:** `pitch_analysis/INTEGRATION_DEMO.md` (email copy + PDP wireframes with real rules)

---

## 6. Combined prize

| Source | GP/yr |
|--------|-------|
| Rec C (category ladder) | S$11–17K |
| Rec D (subscription) | S$2–4K |
| Rec E (acquisition) | S$4K |
| Rec A (guardrail) | S$14K protected |
| **Total** | **S$30–35K** |

---

## 7. Regenerate

```bash
python EDA/aditya_findings/run_all.py
```

---

## 8. Folder index

| Folder | Purpose |
|--------|---------|
| `pitch_analysis/` | Hypotheses, new recs, integration demo, prize charts |
| `margin_analysis/` | COGS proof |
| `Recommendation_A/` | VIP guardrail |
| `Recommendation_B/` | Cross-sell flows + bundle |
| `recommendation_systems/` | SKU MBA + 4 recommenders |
| `outputs_finals/` | Enriched parquets with true margin |
