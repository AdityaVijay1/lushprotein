# LushProtein Final Presentation — Slide Deck Guide

**Audience:** LP founder · **Format:** Cover + **10 slides max** (instructor rule)  
**Narrative:** Retention is the prize. Two recommendations, one system: **segment by value** → **move customers up the ladder** → **lock in subscribers**.  
**Full EDA / breadth:** PDF report · **This deck:** only numbers that drive action.

**Figures folder:** `outputs/charts/` · **Regenerate:** `python EDA/aditya_findings/build_presentation_charts.py`

---

## Cover (not counted toward 10)

| Element | Content |
|---------|---------|
| **Title** | Keep More of Your Best Customers |
| **Subtitle** | Profit-margin segmentation + lifecycle recommendation engine |
| **Team** | Group 1 · ISSS603 · SMU |
| **Data** | 4,290 customers · 8,955 orders · hybrid COGS on 74.7% revenue |
| **Date** | June 2026 |

**Speaker note (10 sec):** *"We're not here with ten ideas. Two recommendations, backed by your data, that protect VIP margin and grow repeat revenue without blanket discounts."*

---

## Slide 1 — The problem is retention, not traffic

**Headline:** 68% of customers buy once and never come back.

| On slide | Number |
|----------|--------|
| One-and-done rate | **67.6%** |
| Top 20% (CM D1) share of profit | **57.7%** |
| 1-category customers | **59%** of pool (2,514) |
| Repeat at 3 categories | **55%** vs **17%** at 1 category |

**Figure:** `r2_category_ladder.png` (repeat rate + profit margin by category count)

**Speaker note:** *"Revenue isn't the bottleneck — repeat is. Most customers stop at one category. Every step up the ladder doubles repeat rate. That's the prize we sized."*

**Why this slide:** Sets founder frame (retention > acquisition) before any methodology.

---

## Slide 2 — Two recommendations, one story

**Headline:** Segment first. Recommend second. Subscribe last.

```
PROBLEM          REC 1 (WHO)              REC 2 (WHEN + WHAT)         OUTCOME
────────         ───────────              ───────────────────         ───────
Same treatment   T1–T5 CRM tiers          4-layer engine              Higher repeat
for everyone  →  + incentive budgets   →  + timed cross-sell       →  + subscribers
                 (no % discounts)         + samples before reorder
```

| Rec | One line | Prize (annual) | Execution |
|-----|----------|----------------|-----------|
| **1** | Treat customers by profit margin — VIPs get experiences, not promos | **S$14K protected** + ladder uplift | **Easy** — import 1 CSV to Klaviyo |
| **2** | Custom engine: right product, right time, right segment | **S$11–17K** ladder + **S$4–5K** sub | **Medium** — Klaviyo flows + PDP widgets |

**Figure:** None (simple diagram on slide)

**Speaker note:** *"Rec 1 is the guardrail and budget. Rec 2 is the engine that moves T4 first buyers to T2 repeaters. Subscription is the end-state after order 2 — not a cold-start pitch."*

**Why this slide:** Instructor ask — lead with 2 recs, one narrative, prioritised by prize.

---

## Slide 3 — Recommendation 1: Your top 500 customers are not "everyone"

**Headline:** Stop treating a S$9 one-time buyer like a S$265 VIP.

| Segment | N | Avg profit margin | Treatment |
|---------|---|-------------------|-----------|
| **T1 VIP** (`is_top_both`) | **500** | **S$265** | HYROX/events, early access — **no % off** |
| **T4 First purchasers** | **2,120** | S$51 | Onboarding + 2nd-order journey |
| **T5 One-and-done** | **831** | S$9 | Email only — no product gifts |

**Figure:** `r1_profit_margin_concentration.png` (D1 = 57.7% of pool profit margin)

**Speaker note:** *"Only 500 customers rank top on both profit margin and frequency — that's your VIP core. Blanket 10% promos on them cost S$14K a year with no retention gain. Founder said no random discounts — we built a tier system instead."*

**Depth (don't put on slide):** v2 decile from `decile_customer_table.csv` · automated in `crm_treatment_tiers.csv`

**Why this slide:** Founder pain — "help us decide what incentives to give."

---

## Slide 4 — Recommendation 1: How much can you afford to give?

**Headline:** Incentives = merch, shakers, samples — capped by profit margin.

| Tier | Avg 10% budget | What to give | What NOT to give |
|------|----------------|--------------|------------------|
| **T1** | **S$25.82** | Partner merch, event invite | Site-wide % codes |
| **T4** | S$5.08 | Single-serve sachet (≤S$2.54) | VIP treatment |
| **T5** | S$0.88 | Win-back email | Product gifts |

**Figure:** `r1_incentive_budget_by_decile.png` + `r1_incentive_mix_no_discounts.png`

**Speaker note:** *"Formula: max gift = X% × customer profit margin. D1 averages S$23 at 10%. That's a shaker or sample pack — not a 15% code. Merch works for you; we sized it."*

**Ask founder:** Sign off **5% vs 10%** cap per tier.

**Why this slide:** Answers "how much can we give?" with one number per tier — execution-ready.

---

## Slide 5 — Recommendation 1: Easy to execute this week

**Headline:** Import one file. Block VIPs from blanket promos. Done.

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Import `outputs_finals/crm_treatment_tiers.csv` → Klaviyo | CRM | Week 1 |
| 2 | Exclude T1/T2 from site-wide % promos | Marketing | Week 1 |
| 3 | Launch VIP experience track for `is_top_both` (500) | Brand | Week 2–4 |

**Prize recap**

| Impact | S$/yr |
|--------|-------|
| VIP discount guardrail | **S$14,000 protected** |
| Category ladder (feeds Rec 2) | **S$10,693** (5% → 3 cats) |

**Figure:** `r1_crm_tier_overview.png`

**Speaker note:** *"Highest execution-ease, immediate impact. No new product. No engineering. Klaviyo tags + promo rules. Rec 1 unlocks Rec 2 because every email knows the tier."*

**Why this slide:** Instructor ask — execution-ease vs revenue. Rec 1 wins on ease.

---

## Slide 6 — Recommendation 2: Shopify can't do what you need

**Headline:** Use Shopify for the cart. Use your data for the journey.

| You asked for | Shopify default | Our engine |
|---------------|-----------------|------------|
| Cross-**category** (Clear→Lean) | ✗ | ✓ 53–65% co-purchase on your D1 buyers |
| **When** to send samples | ✗ | ✓ Day 44 sachet, 10d before 54d reorder |
| **Who** gets gifts | Same for all | ✓ T1 merch · T4 sachet · T5 email only |
| Sub after proven fit | ✗ | ✓ SUB-01 at order 2 + 48 days |

**Figure:** `r2_shopify_vs_custom_engine.png`

**Speaker note:** *"Founder meeting: stick with the custom engine. Shopify 'Recommended products' is fine for Layer 2 — Peach + White Grape in cart. It cannot time cross-category samples before reorder or tie treatment to CRM tier."*

**Why this slide:** Justifies build vs buy in founder terms, not ML jargon.

---

## Slide 7 — Recommendation 2: Four layers, four algorithms (your `recommendation_systems/`)

**Headline:** One algorithm per lifecycle moment — not one model for everything.

| Layer | When | Algorithm | Built by | Output file |
|-------|------|-----------|----------|-------------|
| **L1** | 1st purchase (cold start) | Rule-based co-purchase | `build_recommenders.py` | `recommender_01_rule_based.csv` |
| **L2** | Same cart / PDP | Association rules (MBA) | `sku_market_basket.py` | `sku_association_rules.csv` |
| **L3** | Between orders | Sequential + timed Klaviyo | `build_recommenders.py` | `first_to_second_sku_matrix.csv` · `next_best_sku_per_first.csv` |
| **L4** | 3+ orders, logged in | Item-item CF | `build_recommenders.py` | `recommender_04_item_similarity_matrix.csv` |

**Same SKU, different valid answers** (`recommender_comparison_demo.csv`):

| Moment | Clear Peach 500g → recommend |
|--------|------------------------------|
| L1 (welcome email) | Lean Protein |
| L2 (in cart now) | White Grape (36% same-order) |
| L3 (day 14 email) | Lean for **order 2** |
| L4 (account page) | W.Grape, Shaker, TMT (similarity) |

**Figure:** `r2_four_layer_architecture.png` · optional `recommendation_systems/outputs/fig_top_association_rules.png`

**Speaker note:** *"This is what was missing from a high-level rec doc — the actual scripts and CSVs. L1–L4 are in recommendation_systems/outputs/. CRM tier from Rec 1 picks which layer fires."*

**Why this slide:** Depth on Rec 2 logic — maps architecture to real files.

---

## Slide 8 — Recommendation 2: When to nudge (founder's question)

**Headline:** Ship cross-category samples **before** reorder — not in the first order box.

**Clear Protein buyer timeline:**

| Day | Action |
|-----|--------|
| 0 | Order 1 delivered |
| **14** | Email: try Lean on order 2 (CS-01) |
| **44** | Ship Collagen/Lean sachet (**10d before** 54d median reorder) |
| 54 | Median reorder decision |
| **48** (after order 2) | Subscribe & Save (SUB-01) |

**Who gets single-serves:** T4 (1st buy) + T3 (2nd buy) · T1 gets merch · T5 email only

**Figure:** `r2_cross_sell_timeline_clear.png` · `r2_sample_by_purchase_stage.png`

**Operational files:** `outputs/cross_sell_timing_and_samples.csv` · `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv`

**Speaker note:** *"You asked: at order or before reorder? Data says before reorder — customer tries new category before deciding. Checkout = same-category bundle only (L2). Cross-category = day 14 email + day 44 physical sample."*

**Why this slide:** Direct answer to founder meeting — highest "depth" moment for Rec 2.

---

## Slide 9 — Recommendation 2: Subscription follows repeat, not cold traffic

**Headline:** Subscribers repeat 3× more — offer S&S only after order 2.

| Metric | Subscribers | Non-subscribers |
|--------|-------------|-----------------|
| Repeat rate | **62%** | 19% |
| Avg profit margin | **S$134** | S$69 |
| PM D1 sub rate | **33.4%** | PM D5: 2.6% |

**Trigger:** SUB-01 → 689 customers (2+ orders, never subscribed) · order 2 + **48 days**

**Prize:** 5% convert = **S$2,262/yr** · Freq D1 tier = **S$1,497/yr**

**Figure:** `r2_subscription_by_profit_decile.png`

**Speaker note:** *"51% of your 500 VIPs already subscribe — sub is a D1 signal. Engine path: L3 day-14 email → order 2 → SUB-01. No discount-led sub pitch on first purchase."*

**Why this slide:** Subscription as outcome of engine, sized by decile study.

---

## Slide 10 — Combined impact + 90-day rollout

**Headline:** ~S$30–35K GP/yr — start with what’s easiest, scale what’s biggest.

| Priority | Action | Prize | Ease |
|----------|--------|-------|------|
| **1** | Klaviyo T1–T5 + VIP promo guardrail | S$14K protected | ★★★★★ |
| **2** | L1 + L3 Klaviyo (day 14 / CS-01–03) | S$10.7K ladder | ★★★★☆ |
| **3** | L2 PDP bundles (top 5 SKUs) | +AOV | ★★★★☆ |
| **4** | SUB-01 after order 2 | S$4.5K sub | ★★★☆☆ |
| **5** | L4 account CF | Retention polish | ★★☆☆☆ (week 6+) |

**Total modeled uplift:** **~S$30–35K GP/yr** (conservative conversion assumptions)

**Ask of LP (close):**
1. Sign off incentive cap (5% or 10% of profit margin per tier)
2. Approve Klaviyo import of `crm_treatment_tiers.csv`
3. Confirm sample COGS budget for T4 sachets (~S$2.54/customer)
4. Share HYROX/event calendar for VIP experience track

**Figure:** None — table only (sharp)

**Speaker note:** *"We're not asking you to rebuild Shopify. Week 1: tiers. Week 2: day-14 emails. Week 4: subscriptions. Full EDA, clusters, and sensitivity live in the report — this deck is the execution path."*

---

## Slide checklist (grading)

| # | Slide | Rec | Shows prize? | Shows execution? | Figure |
|---|-------|-----|--------------|------------------|--------|
| 1 | Retention problem | Setup | ✓ (ladder) | — | r2_category_ladder |
| 2 | Two-pillar story | Both | ✓ | ✓ | — |
| 3 | Segmentation insight | 1 | ✓ (concentration) | — | r1_profit_margin_concentration |
| 4 | Incentive budgets | 1 | — | ✓ | r1_incentive_budget + mix |
| 5 | Rec 1 execution | 1 | ✓ S$14K | ✓★★★★★ | r1_crm_tier_overview |
| 6 | vs Shopify | 2 | — | ✓ | r2_shopify_vs_custom |
| 7 | 4 layers + files | 2 | — | ✓ | r2_four_layer_architecture |
| 8 | Sample timing | 2 | ✓ ladder | ✓ | r2_cross_sell_timeline + sample_stage |
| 9 | Subscription | 2 | ✓ S$4.5K | ✓ | r2_subscription_by_profit_decile |
| 10 | Rollout + ask | Both | ✓ S$30–35K | ✓ | — |

**Total content slides: 10** ✓

---

## What stays in the PDF report (not deck)

- Full decile overlap heatmaps · hierarchical clustering (`customer_cluster_assignments.csv`)
- Margin leakage scenarios · COGS coverage audit
- POS vs web · discount taxonomy · `new_potential_analysis.md` ideas
- H3–H5 hypotheses · acquisition mix · creatine bundles · free shipping threshold
- `FOUNDER_FEEDBACK_VERIFICATION.md` requirement audit

---

## File map for presenters

| Need | Open |
|------|------|
| Slide content | **This file** (`PRESENTATION.md`) |
| Rec 1 depth | `RECOMMENDATION_1_CUSTOMER_SEGREGATION_AND_INCENTIVES.md` |
| Rec 2 depth | `RECOMMENDATION_2_ENGINE_AND_SUBSCRIPTION.md` |
| Engine evidence | `recommendation_systems/RECOMMENDER_SYSTEMS.md` |
| Email/PDP copy | `pitch_analysis/INTEGRATION_DEMO.md` |
| Klaviyo flows | `Recommendation_B/outputs/klaviyo_cross_sell_flows.csv` |
| Charts | `outputs/charts/r1_*.png` · `r2_*.png` |

---

## Anticipated Q&A (one line each)

| Question | Answer |
|----------|--------|
| Why not one recommender? | 67% one-and-done = cold start; CF fails without history (see `recommender_system_comparison.csv`) |
| Why profit margin not revenue? | Founder formula Revenue−COGS; D1 gap is orders + categories, not discount depth |
| Why not samples in first box? | Margin cost; pre-reorder timing lifts 2nd-category attach |
| What about new flavours? | L1 rules update from `co_purchase_matrix_d1.csv`; Peach Oolong pre-order worked (see `new_potential_analysis.md`) |
| How do we measure success? | 2nd-category attach +5pp · sub conversion 5% of 689 · T1 promo exclusion enforced |
