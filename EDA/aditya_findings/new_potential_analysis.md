# New Potential Analysis — LP Team Ideas Worth Exploring

**Author:** Aditya · June 2026  
**Method:** Quick validation against finals pool (4,290 customers · 8,955 orders) + discount taxonomy + POS channel split  
**Verdict key:** ✅ Worth pursuing · ⚠️ Worth a pilot · ❌ Deprioritise / data gap

---

## Executive summary

| Idea | Verdict | Why |
|------|---------|-----|
| Retention over acquisition | ✅ **Core strategy** | 67.6% one-and-done; PM D1 = 57.7% of profit margin |
| HYROX / big events (not gym promos) | ✅ **Focus big events** | Event codes tiny in web data; POS is 99.5% discounted — shift to experience-led T1 rewards |
| Merch / shaker incentives | ✅ **Strong fit** | Aligns with T1/T2 budget framework (S$12–26/customer) |
| Peach Oolong Kickstarter model | ⚠️ **Pilot for new flavours** | 85 pre-order lines; proven excitement + cashflow |
| Checkout demographic survey | ⚠️ **Pilot with care** | Useful for segmentation; use merch/sample reward not % discount |
| Creatine bundles | ✅ **Quick win** | 360 orders with creatine + protein overlap |
| Free shipping threshold | ✅ **Data-supported** | Median basket S$60; S$80 captures 33% of orders |
| Starter pack for retargeting | ✅ **T4 priority** | 2,120 first purchasers need structured 2nd-order journey |
| Single-serve by customer type | ✅ **Already scoped** | T4/T3 get sachets; T1 gets merch; T5 email only |
| Random % discount promos | ❌ **Reject** | S$14K VIP leakage; founder explicitly said NO discounts |
| Region segregation | ❌ **Skip** | Founder: no region split needed |

---

## 1. Retention over acquisition

**Founder focus:** Keep current customers happy rather than broad acquisition discounts.

**Data evidence:**

| Metric | Value |
|--------|-------|
| One-and-done rate | **67.6%** |
| PM D1 share of profit margin | **57.7%** |
| 1-category customers | **59%** of pool (2,514) |
| Repeat at 3 categories | **55%** vs 17% at 1 category |

**Recommendation:** Allocate incentive budget to T1–T4 retention (merch, samples, sub offers) per `RECOMMENDATION_1_CUSTOMER_SEGREGATION_AND_INCENTIVES.md`. Deprioritise mass acquisition discount codes.

---

## 2. POS data & event attribution (HYROX vs gym promos)

**Founder ask:** Use discount codes to see which events LP attended. Small spikes = local gym promos; big spikes = HYROX (June/Nov Singapore, July Hong Kong). Focus on bigger events.

**What we found:**

### POS vs Web channel (`EDA/outputs/12_pos_vs_web_orders.csv`)

| Channel | Orders | Avg basket | % discounted |
|---------|--------|------------|--------------|
| POS (on-site) | 415 | S$59 | **99.5%** |
| Web | 4,912 | S$85 | 52.6% |

POS is almost entirely discount-driven with lower baskets — gym/event sampling channel, not loyalty channel.

### Event discount codes (`EDA/outputs/discounts.parquet`)

| Code | Type | Redemptions |
|------|------|-------------|
| SGHYROX100 | HYROX | 1 |
| HyroxFH2025 | HYROX | 1 |
| GYMCON100 | Gym | 1 |
| EVENT100 | Event | 1 |
| EVO FITNESS CHALLENGE | Gym/fitness | 1 |

Event/Partnership taxonomy: **6 codes, 17 total redemptions** — small in absolute terms but aligned with founder's "big event" narrative.

### Monthly order volume (web finals)

Top months: 2025-05 (464), 2026-02 (462), 2025-09 (453). Aug 2024 spike (369) may reflect early growth/POS activity — **cannot confirm HYROX attribution without event-date overlay from LP**.

**Verdict:** ✅ **Worth pursuing** — but LP should provide event calendar dates to join against `order_date`. Use HYROX/partner rewards for **T1 VIP** (experiences, not codes) rather than mass event discount codes.

**Gap:** Discount codes are not joined to individual orders in finals export — only discount *amount* is available per order.

---

## 3. Marketing — merch over mailings, no random discounts

**Founder:** Merch (shaker, sweaters) works well for branding. Random discount promotions don't.

**Data:**

| Signal | Finding |
|--------|---------|
| Discounted orders | 42.5% of pool |
| Avg basket (discounted) | S$88 |
| Avg basket (no discount) | S$76 |
| VIP guardrail | 10% site-wide on PM D1 = **S$14K/yr** erosion |

Discounted orders have higher baskets (bundle behaviour) but blanket promos hit high-PM customers without retention lift.

**Verdict:** ✅ Align T1/T2 incentives with **merch + experiences** within profit margin budget (5–10%). See `r1_incentive_mix_no_discounts.png`.

---

## 4. Peach Oolong Kickstarter / pre-order model

**Founder:** Peach Oolong tea flavour Kickstarter worked — cashflow + customer excitement. Explore for future expansion.

**Data:** **85** order lines for `LEAN PROTEIN PEACH OOLONG (PRE-ORDER)` in finals.

**Verdict:** ⚠️ **Worth a pilot** for limited-edition flavours:

- Pre-order format validates demand before production run
- Creates shareable moment (founder liked the excitement factor)
- Best targeted at **T2/T1** (proven repeaters) + email list, not cold acquisition
- Pair with early-access merch for T1 VIPs, not % off

**Risk:** Pre-orders add fulfilment complexity — cap batch size and set clear delivery dates.

---

## 5. Checkout demographic survey (5–10% discount alternative)

**Founder idea:** Small survey at checkout for target demographic data, incentive for completion.

**Verdict:** ⚠️ **Worth a pilot** — with modifications:

| Do | Don't |
|----|-------|
| Offer **merch insert or sachet** for survey completion | Offer 5–10% **discount** (founder said NO discounts) |
| Ask 2–3 fields: training goal, product use case, referral source | Long forms that hurt conversion |
| Feed answers into Klaviyo + future segmentation | Region-based splits |

**Value:** Improves cold-start recommendations (L1) for the 67% one-and-done cohort. Especially useful for T4 first purchasers where behaviour data is sparse.

**Estimated cost:** ≤ S$2.54 per T4 customer (5% profit margin cap) — one sachet or sticker pack.

---

## 6. Creatine push + bundles

**Founder:** Push creatine more; use in bundles.

**Data:**

| Metric | Value |
|--------|-------|
| Orders containing creatine | **702** |
| Orders with creatine + protein/collagen | **360** (51% of creatine buyers) |
| Creatine median reorder | **66 days** (longer than protein) |

**Verdict:** ✅ **Quick win** — deploy in:

- **L2 checkout:** "Add creatine" on Lean/Clear 1kg orders
- **L3 email:** Day 21 creatine education for protein-only buyers (between day-14 cross-sell and pre-reorder sample)
- **T2 bundle:** Protein + creatine shaker kit (merch + product, not % off)

---

## 7. Free shipping threshold

**Founder:** What threshold makes sense? Look at basket size.

**Data (order `Price: Total`):**

| Stat | Value |
|------|-------|
| Median basket | **S$60** |
| Mean basket | S$81 |
| Orders ≥ S$80 | **33.1%** |
| Orders ≥ S$100 | **24.5%** |
| Orders ≥ S$120 | 15.9% |

**Verdict:** ✅ **Data-supported options:**

| Threshold | Trade-off |
|-----------|-----------|
| **S$80** | ~33% already qualify — moderate bar, encourages one extra sachet or upsize |
| **S$100** | ~25% qualify — stronger margin protection |
| **S$60** | At median — easy to hit but little upsell incentive |

**Recommendation:** Test **S$80 free shipping** for web channel; POS stays separate (already event-driven). Message as "add a sachet pack to unlock free shipping" — ties to category ladder, not discount.

---

## 8. Starter pack for initial customer retargeting

**Founder:** Starter pack idea to convert first-time buyers into loyal customers.

**Data:**

| Segment | N | Avg PM | Repeat |
|---------|---|--------|--------|
| T4 First Purchasers | **2,120** | S$51 | ~11% subscribed |
| 1-category pool | 2,514 | S$59 | 17% repeat |

**Verdict:** ✅ **High priority** — structure as:

- **Starter Pack A:** Clear 500g + 2 flavour sachets (same category, L2)
- **Starter Pack B:** Lean 1kg + cross-category collagen sachet (post-purchase insert, not checkout default)
- **Retargeting:** T4 email series day 3, 14, 44 (per `cross_sell_timing_and_samples.csv`)

Cost cap: ≤ S$5.08 (10% of T4 avg profit margin) or use sachet-only insert at S$2.54 (5%).

---

## 9. Single-serve — which customer types?

**Founder:** On what type of customers would single serves work?

**Data — sachet buyer rate by CRM tier:**

| Tier | Sachet buyer rate | Recommendation |
|------|-------------------|----------------|
| T4 First-tx | 7.6% | **Primary target** — category discovery |
| T3 Growth | 1.6% | 3rd-category sample at order 2 |
| T2 High-value | 10.3% | Bundle trials with replenishment |
| T1 VIP | 13.3% | Premium samples / new flavour first access |
| T5 Low | 27.0% | High rate but **low ROI** — sachet wasted on one-and-done |

**Verdict:** ✅ **Already scoped** in recommendation engine:

- **1st & 2nd purchase (T4/T3):** Cross-category sachet before reorder
- **VIP (T1):** New flavour samples + merch, not mass sachet drops
- **T5:** No product gifts — email only

T5's high sachet rate likely reflects low-cost trial purchases (sachet-only orders) — not a retention success signal.

---

## 10. Ideas explicitly deprioritised

| Idea | Reason |
|------|--------|
| Random % discount promotions | S$14K VIP leakage; contradicts founder NO-discount rule |
| Region segregation | Founder: not needed |
| Points-based mass loyalty programme | Previous programme failed (low traffic); T1 partner-led model preferred |
| Samples in every first order box | Margin cost unjustified; pre-reorder timing wins |

---

## Recommended next steps for LP

1. **Share event calendar** (HYROX SG/HK dates, gym pop-ups) so we can overlay on `order_date` and quantify big-event spikes.
2. **Pick free shipping threshold** — recommend S$80 pilot for 90 days.
3. **Approve T4 starter pack** SKU bundle with sachet COGS ≤ S$2.54.
4. **Pilot Peach Oolong-style pre-order** for next limited flavour — email T1/T2 first.
5. **Checkout survey** — 2 questions, reward = sachet not discount.

---

## Data sources

| File | Use |
|------|-----|
| `outputs_finals/orders.parquet` | Basket size, monthly volume |
| `outputs_finals/crm_treatment_tiers.csv` | Tier-level sachet rates |
| `outputs/discounts.parquet` | Event code taxonomy |
| `outputs/12_pos_vs_web_orders.csv` | POS vs web economics |
| `outputs/05_discount_code_taxonomy.csv` | Promo type breakdown |
| `pitch_analysis/outputs/category_ladder_gp.csv` | Retention ladder |

**Exploration script:** `_explore_potential.py` (regenerate numbers)
