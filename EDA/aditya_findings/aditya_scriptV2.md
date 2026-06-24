# aditya_scriptV2 — 5-Minute Presentation Script
### Recommendation System & Subscription Engine (4 Slides)

> **Format:** ~75 seconds per slide. Speak at a confident, measured pace — not rushed.
> Numbers in **bold** are your key data points. Say them clearly and pause briefly after each.

---

## SLIDE 1 — The Problem (75 seconds)

> "Let me show you what the data actually looks like."

> "**77%** of your customers buy once and disappear. That is **4,400 out of 5,700** people — gone after one order. Right now, Shopify's default algorithm has no post-purchase engine. It shows every customer the same generic widget whether it's their first order or their tenth."

> "When customers do add a second product category, something dramatic happens. One category: **13% repeat rate**, **S$64** gross profit. Three or more categories: **63% repeat rate**, **S$223** gross profit. That's a five times improvement in return likelihood — from the same customers, just introduced to more of your product range."

> "And subscribers? They repeat at **62%** versus **17%** for non-subscribers. A **3.6 times** gap. Only **713** out of **5,700** customers have ever subscribed. The system to convert proven repeaters into subscribers simply doesn't exist yet."

> "The good news: the brand's top 10% of customers already generate **57% of total profit**. The foundation is strong. We just need the engine to develop the rest."

---

## SLIDE 2 — 4 Layers (75 seconds)

> "The question I always get is: why not just use one algorithm?"

> "Because the right recommendation depends entirely on *where the customer is*. A first-time buyer has zero history — machine learning fails. Someone on the product page right now needs a real-time cart suggestion. Someone who bought 14 days ago needs a post-purchase email. A 5-order loyalist needs personalised recs."

> "So we built four layers — one for each customer moment."

> "**Layer 1** is rule-based. Fires for every customer on first purchase. If they bought Clear Protein, recommend Lean — because **53%** of your best customers also buy Lean. Simple, always-on."

> "**Layer 2** is market basket analysis — the 'frequently bought together' widget on the product page. **500+** rules from your actual order data."

> "**Layer 3** is the most important — post-purchase timing. Email on Day 14, physical sample dispatched 10 days before the reorder window. I'll come back to this."

> "**Layer 4** is collaborative filtering — personalised recs for logged-in customers with 3+ orders. That's **730** people, your most valuable 17%."

---

## SLIDE 3 — Layer 3 Deep Dive (75 seconds)

> "Layer 3 is where the real leverage is."

> "After order 1 ships, two things happen on a precise schedule. First, an email fires at **Day 14** — for Clear Protein buyers, it recommends Lean TMT. For Lean buyers, it recommends Clear Peach. The routing is based on D1 co-purchase rates — **65%** of your best Lean buyers also buy Clear."

> "Second, a physical sample is dispatched — but not in the first order box. It ships **10 days before the customer's median reorder window**. For Clear Protein buyers, that's **Day 44** — because the measured reorder median from **81** actual repeat buyers is **54 days**."

> "Why not in the first box? Because in the first box, the sachet gets ignored. On Day 44, the customer is running low and thinking about their next order. The sample arrives at exactly that moment. They try it. They add it to their reorder."

> "After Order 2, the sequence continues — Day 7 email recommends a third category, and at **Day 48** the Subscribe & Save offer fires. Only for customers who've proven they come back."

> "The category prize: **5%** of the **3,681** single-category customers reaching three categories is worth **S$10,693** GP per year."

---

## SLIDE 4 — Shopify Implementation & Business Value (75 seconds)

> "The implementation is simpler than it sounds."

> "Shopify fires a webhook every time an order ships — free, native. A nightly batch job reads those orders, maps each customer to their first product category, and looks up a **7-row CSV table** we already built. Output: which email to send, which day to send it, which sample to dispatch, and which day."

> "Three outputs. Email schedule goes to the email platform as a timed flow. A Shopify customer tag marks the sample SKU and dispatch date for the fulfilment team. And 48 days after Order 2, the Subscribe & Save trigger fires. Phase 1 goes live in **4 weeks**. No custom app. No machine learning. Just a lookup table and email flows."

> "On the business side — look at the tier table. **Silver** buyers repeat at **45%** and average **S$100** GP. **Gold-B Loyal Regulars** are at **54%** repeat and **S$105** GP. That looks like a small jump — but the compounding over two to three years is real."

> "The conservative prize model: **5%** of single-category customers reaching three categories is **S$10,693** GP. Add subscription conversion and acquisition mix fix, and the total is **S$17 to S$30K** GP per year — at a **5%** conversion assumption."

> "The analysis is done. The lookup table is built. Phase 1 can start this week."

---

> **Total time: ~5 minutes**
>
> *Full detailed script with Q&A: `aditya_script.md`*
> *Slide content reference: `final_slides_rec.md`*
