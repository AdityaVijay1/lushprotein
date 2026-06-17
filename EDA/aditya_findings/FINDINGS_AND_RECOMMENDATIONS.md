# LushProtein — Findings & Recommendations (Product × Customer)

**Author:** Aditya · Group 1 · ISSS603  
**Pool:** 4,290 customers · true COGS on 74.7% of revenue · **70.5% measured margin**  
**Date:** June 2026

> **Deck:** Lead with **Rec C + Rec D**. Rec B executes C. Rec A is guardrail only.

---

## 1. The one narrative

**59% of customers have only ever bought one product category.** They average S$59 GP and 17% repeat. Customers with 3 categories average **S$144 GP and 55% repeat** — 2.4× the profit, 3× the repeat.

The fix is not more discounting (that saves S$14K on VIPs at best). The fix is **product structure + customer journey design**: cross-sell Clear↔Lean on order 2, add a 3rd category by order 3, put repeat buyers on Subscribe & Save, and systematically route customers toward **D1 behaviour** (2.5 categories, S$357 GP, 88% repeat).

**Execution playbooks:** `FOUNDER_MEETING_PREP.md` Sections 2A (cross-sell), 2B (subscription), 3 (D1 path).

---

## 2. Lead recommendations (pitch order)

### Recommendation C — Climb the category ladder (LEAD)

| | |
|---|---|
| **What** | 2,514 single-category buyers → target 2nd category on order 2, 3rd by order 3 |
| **Why** | GP S$59 → S$144 (+S$85); repeat 17% → 55% |
| **Prize** | 5% reach 3 categories = **S$10,693 GP/yr**; 8% add 2nd = **S$3,969** |
| **How** | 5 Klaviyo flows (CS-01–05) + checkout bundle + PDP widgets — **Section 2A in `FOUNDER_MEETING_PREP.md`** |
| **Figure** | `pitch_analysis/outputs/fig_category_ladder.png` |

**Full doc:** `pitch_analysis/NEW_RECOMMENDATIONS.md` · **Hypothesis:** H1 in `pitch_analysis/HYPOTHESES.md`

---

### Recommendation D — Build a subscription growth engine

| | |
|---|---|
| **What** | 4-tier S&S: repeat non-subs (689) · freq D1 non-subs (228) · first-time hero buyers · checkout subscribe |
| **Why** | Subscribers repeat **62%** vs **19%**; 38% of D1 ever subscribed |
| **Prize** | Tiers D1+D2 = **S$3,759 GP/yr** direct; all tiers **~S$4.5K** + compounding |
| **Product** | Hero SKUs: Peach 500g (54-day), TMT 1kg (35-day) |
| **Figure** | `pitch_analysis/outputs/fig_prize_by_hypothesis.png` |

**Execution:** SUB-01–04 Klaviyo flows + checkout pre-check — **`FOUNDER_MEETING_PREP.md` Section 2B**

**Hypothesis:** H2

---

### The D1 path — how C + D create your best customers

| D1 signal | Index vs non-D1 | Driven by |
|-----------|-----------------|-----------|
| 3+ categories | 434 | Rec C (CS-04 Collagen push) |
| Ever subscribed | 258 | Rec D (4-tier S&S) |
| Repeat buyer | 427 | Both — ladder lifts 17%→55%; subs at 62% |
| Lean + Clear affinity | 265–275 | Rec C cross-sell at day 14 |

**368 profit D1** = S$357 avg GP, 41% of all GP. **D1 scoring (0–100)** routes customers in Klaviyo: score ≥60 → VIP nurture; 35–59 → full C+D stack; <35 → Gateway Hero acquisition.

**Full playbook:** `FOUNDER_MEETING_PREP.md` Section 3 · `decile_analysis/D1_CUSTOMER_PROFILE.md`

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
| Rec D (subscription engine) | S$4–5K |
| Rec E (acquisition) | S$4K |
| Rec A (guardrail) | S$14K protected |
| **Total** | **S$30–35K** |

---

## 7. Regenerate

```bash
# Full medallion pipeline
python data/pipeline/run_full_pipeline.py

# Or layer by layer
python data/pipeline/run_bronze_to_silver.py
python data/pipeline/run_silver_to_gold.py
python data/pipeline/run_gold_analytics.py

# Legacy entry point (Silver scripts only)
python EDA/aditya_findings/run_all.py
```

---

## 8. Folder index

| Folder | Purpose |
|--------|---------|
| `data/` | **Medallion data lake** — bronze/silver/gold + pipeline |
| `pitch_analysis/` | Hypotheses, new recs, integration demo, prize charts |
| `margin_analysis/` | COGS proof |
| `Recommendation_A/` | VIP guardrail |
| `Recommendation_B/` | Cross-sell flows + bundle |
| `recommendation_systems/` | SKU MBA + 4 recommenders |
| `decile_analysis/` | D1 customer profile |
| `FOUNDER_MEETING_PREP.md` | Meeting prep + execution playbooks + D1 path |
| `outputs_finals/` | Enriched parquets with true margin |
