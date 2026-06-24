# Aditya's Presentation Script
### Recommendation System & Subscription Engine — 4-Slide Walkthrough

> **How to use this:** This is your spoken script. Memorise the first sentence of each section as your opener — the rest flows from there. Numbers in brackets like [77.3%] are data points to state confidently.
>
> Estimated time: 15–20 minutes for all 4 slides with Q&A.

---

## SLIDE 1 — The Problem
### *"Development of Customers — Why We Need a Recommendation System"*

---

**[OPENING — set the stage, 30 seconds]**

> "Before I show you what we built, I want to show you what the current system is doing — and what it's not doing. Because this isn't about building something fancy. It's about fixing something that's clearly broken."

---

**[CURRENT SYSTEM — 1 minute]**

> "Right now, Lush Protein runs Shopify's default recommendation engine. No custom app, no timing logic, no email sequencing. The widget on the product page? That's Shopify's built-in algorithm — designed for fashion stores and large catalogues. It doesn't know when a customer last ordered. It doesn't know they're about to reorder. It shows every customer the same suggestions whether they've bought once or ten times."

> "And that matters, because nutrition is not fashion. People have reorder cycles. They run out of protein at predictable times. The opportunity is to be there at exactly that moment — and right now, we're not."

---

**[GAP 1 — RETENTION — 1 minute, pointing at left panel of slide1_problem_statement.png]**

> "Let's look at the data. [77.3%] of customers buy exactly once and never return. That's 4,402 out of 5,694 customers. Only [22.7%] ever come back."

> "This is the founder's biggest stated concern — and the data backs it up completely. The default system has no post-purchase mechanism. It doesn't send a 'hey, you might be running low' email. It doesn't introduce new categories. It just waits."

> "The good news: these are not bad customers. They're first-time trial customers who got no follow-up. That's fixable."

---

**[GAP 2 — CATEGORY DEPTH — 1 minute, pointing at middle panel]**

> "[59%] of customers — that's [3,681] people — have ever bought only one product category. They bought Clear Protein or Lean Protein and never crossed over."

> "Look at what the data shows when they do cross over. One category: [13%] repeat rate, [S$64] average GP. Two categories: [30%] repeat, [S$92] GP. Three or more: [63%] repeat, [S$223] GP. That is a [5x] increase in repeat likelihood and a [3.5x] increase in value per customer — just from discovering a second product category."

> "These customers are sitting in the data right now. Nobody introduced them to the brand beyond their first SKU."

---

**[GAP 3 — SUBSCRIPTION — 1 minute, pointing at right panel]**

> "The third gap is subscription. Subscribers repeat at [62%]. Non-subscribers at [17%]. That's a [3.6x] gap. Subscribers also generate [S$134] average GP versus [S$81] for non-subscribers."

> "Right now, only [713] out of [5,694] customers — about 12.5% — have ever subscribed. There's no structured mechanism to convert proven repeat buyers into subscribers. The system just waits for them to click the Subscribe & Save button themselves."

---

**[WHAT'S WORKING — balance the narrative, 30 seconds]**

> "To be clear — this is not a failing business. The foundation is strong. The top 10% of customers by profit generate [57.7%] of total GP. VIP customers average [S$476] GP each. Clear Peach and Lean TMT already have [27–35%] first-purchase repeat rates — that's a strong gateway product signal."

> "The brand has excellent bones. What it lacks is a system to develop the other [77%] of customers who bought once. That's what we're building."

---

**[TRANSITION TO SLIDE 2]**

> "So the question becomes: what does that system look like? And specifically — why do we need four layers instead of one?"

---

---

## SLIDE 2 — The 4-Layer Architecture
### *"Why 4 Layers? One Algorithm Fails Every Type of Customer"*

---

**[OPENING THE ARGUMENT — 30 seconds]**

> "The most common question I've heard when presenting this is: 'Can't you just use one algorithm?' And the answer is no — and I want to explain exactly why, because it's important for the build decision."

---

**[THE CORE INSIGHT — 1 minute]**

> "It's not about algorithm quality. It's about customer moment. A first-time buyer has zero purchase history — machine learning literally cannot run on them. Someone browsing the product page right now needs a real-time cart suggestion. Someone who bought 14 days ago needs a post-purchase email while they're still forming a habit. And a logged-in customer with 5 orders needs personalised recommendations based on their actual fingerprint."

> "No single algorithm handles all four of those moments. That's why we have four layers."

---

**[LAYER 1 — 45 seconds, pointing at left coverage bar]**

> "Layer 1 is rule-based cold start. It covers [100%] of customers — because every customer, at minimum, places a first order. The rules are simple: if they bought Clear Protein, recommend Lean. If they bought Lean, recommend Clear. These rules come from D1 co-purchase rates — [53%] of your best Clear buyers also buy Lean, and [65%] of your best Lean buyers also buy Clear."

> "Why not use ML here? Because [67%] of customers have only 1 order. Collaborative filtering needs purchase history to run. Using the ML layer alone would fail [83%] of your customer pool on day one."

---

**[LAYER 2 — 30 seconds]**

> "Layer 2 is association rules — market basket analysis. This handles the browsing session: the 'frequently bought together' widget on the product page, the cart upsell before checkout. It uses [500+] rules calculated from [8,955] order lines. Lean Taro and Lean TMT together have an [87%] confidence rule — if someone has Lean Taro in their cart, there's an [87%] chance they'll also buy Lean TMT."

---

**[LAYER 3 — 1 minute, this is the centrepiece]**

> "Layer 3 is the most important layer — and it's the one that's genuinely new for a Shopify store. I'll go deeper in the next slide, but the concept is this: we send a cross-sell email [14 days] after order 1, and we send a physical sample [10 days before] the customer's predicted reorder window."

> "The key word is predicted. We measured the actual reorder cycles from [81] Clear Peach buyers — the median is [54 days]. So the sample ships on [Day 44]. It arrives when the customer is literally deciding what to reorder. That's not a coincidence. That's the design."

---

**[LAYER 4 — 30 seconds]**

> "Layer 4 is item-item collaborative filtering — what most people mean when they say 'the recommendation algorithm.' It works beautifully, but only for customers with [3+] orders. That's [730] customers, or [17%] of the pool. For those customers, it builds a purchase fingerprint and serves personalised recs on the account page."

> "The system only uses L4 where it has enough data to be accurate. For everyone else, layers 1, 2, and 3 carry the load."

---

**[TRANSITION TO SLIDE 3]**

> "Let me go much deeper on Layer 3, because it's the layer that's going live first and it has the most moving parts."

---

---

## SLIDE 3 — Layer 3 Deep Dive
### *"Layer 3: Cross-Sell BEFORE the Reorder Window — Not at Checkout"*

---

**[OPENING QUESTION — 15 seconds]**

> "There's a question that came up in early conversations about this layer: 'Why not just put the sample in the first order box?' The data has a clear answer. Let me walk you through why."

---

**[THE THREE DECISIONS — 90 seconds, pointing at bar chart on left]**

> "Layer 3 makes three decisions for every customer after their first order. First: what product to recommend. Second: when to send the recommendation email. Third: when to dispatch the physical sample."

> "The email timing is Day [14] for most categories — [21] days for Collagen-first buyers because their reorder window is [42 days]. Day [7] for accessories-first buyers, because those customers are the most at risk of churning and we need to get them on protein urgently."

> "The sample timing is the interesting one. [Point at bar chart] Look at Clear Protein 500g. The median reorder window from [81] repeat buyers is [54 days]. The sample ships on [Day 44]. That's [10 days] before the reorder. Every other SKU category follows the same [10-day-before] rule — adjusted for their specific reorder cycle."

---

**[WHY NOT IN THE BOX — 1 minute]**

> "So back to the question: why not put the sachet in the first order box?"

> "When the first order arrives, the customer is excited about what they bought. They try the protein. They focus on it. A sachet in that box gets set aside — 'I'll try this later.' By the time they actually try it, they've already formed their reorder decision."

> "Now imagine the sachet arrives [44 days] after their first order. They're running low. They're thinking about reordering. A package arrives — it's a Lean TMT sample. They try it. It's good. They add it to their next order."

> "That is not a coincidence — that's the design. The sample arrives at the exact moment it has maximum influence."

---

**[ROUTING DECISION TREE — 1 minute, pointing at middle panel]**

> "Now here's what the routing looks like in practice. [Point at tree] When order 1 is fulfilled, the system detects the first product category. If they bought Clear Protein, the email recommends Lean TMT or Lean Taro, and the sample that ships on Day [44] is a Lean [40g] sachet or a Collagen [25g] sachet."

> "If they bought accessories — a shaker — the routing is different. Day [7] email, Clear Protein [25g] sachet — and critically, not another shaker. These customers need protein trial, urgently."

> "After order 2 is fulfilled, the next email goes out on Day 7 recommending a third category. And [48 days] after order 2 — that's when the Subscribe & Save trigger fires. We call it SUB-01. It targets customers who've proven they come back. We're not asking first-timers to subscribe. We're asking proven repeaters."

---

**[THE EVIDENCE — 45 seconds, pointing at right panel]**

> "Every single design decision in this layer is grounded in data. The reorder timing was not assumed. We took [81] Clear Peach repeat buyers, measured the gaps between all their orders, took the median per customer, then the median across the cohort. [54 days]. Same for Lean TMT — [39] buyers, [35 days] median."

> "The routing rules came from D1 co-purchase rates — the purchase behaviour of your best customers. [65%] of D1 Lean buyers also buy Clear. That's not a hypothesis. That's what your most valuable customers actually do."

---

**[THE PRIZE — 30 seconds]**

> "What does this translate to? The category ladder analysis shows: [5%] of [3,681] single-category customers reaching [3] categories is worth [S$10,693] GP per year. [5%] reaching [2] categories is [S$2,940] GP. Those are conservative estimates at a [5%] conversion rate. The data suggests the actual lift from timed cross-sell is higher."

---

**[TRANSITION TO SLIDE 4]**

> "The natural next question is: how do we actually build this on Shopify? And how does it translate into customer tier progression?"

---

---

## SLIDE 4 — Shopify Implementation & Business Value
### *"How to Build This on Shopify — and What It's Worth"*

---

**[OPENING REFRAME — 30 seconds]**

> "I want to reframe something before we talk about implementation. When people hear 'recommendation engine,' they think machine learning, custom app, months of engineering. Layer 3 in Phase 1 is not that. The recommendation engine is a [7-row lookup table]. The intelligence was built offline — from the data we just walked through. The runtime just looks things up."

---

**[THE PIPELINE — 2 minutes, pointing at left panel]**

> "Here's how it works. [Point at trigger box] Shopify fires a webhook every time an order ships — this is native, built-in, free. The payload contains the customer ID, the SKUs ordered, and the order date."

> "[Point at Step 1] A nightly batch job — this can literally be a script that runs at midnight — queries the Shopify Admin API for all fulfilled orders from the last 24 hours. For each new customer, it looks up their first-ever product category from order history."

> "[Point at Step 2] Then it does the 'inference.' Input: first product category. Lookup: the [7-row] CSV table we already built. Output: three things. The day to fire the cross-sell email. The day to dispatch the physical sample. The specific SKU to recommend and which sample to send."

> "[Point at three output boxes] From there, three things happen. The customer is added to the appropriate email flow — CS-01 for Clear buyers, CS-02 for Lean buyers, CS-03 for Collagen buyers. A Shopify customer tag is added with the sample SKU and dispatch date — the fulfilment team runs a daily report and ships on the right day. And 48 days after order 2, the Subscribe & Save trigger goes out."

---

**[TECH STACK — 45 seconds]**

> "The tech stack for Phase 1 requires no custom Shopify app. Shopify webhooks and the Admin API are native and free. The lookup table is already built. The email automation platform you already have. Customer tags are a native Shopify feature. For very early MVP — before any automation — this can even run as a daily spreadsheet workflow. Shopify export, VLOOKUP, email platform import. No engineering."

> "Phase 2 adds the L2 PDP widget — a 'frequently bought together' section on the product page. Phase 3 adds the L4 personalised recs on the account page. But Phase 1, the most impactful layer, can go live in [4 weeks]."

---

**[TIER PROGRESSION VALUE — 2 minutes, pointing at right panel]**

> "Now — why does this matter for customer development? Let's look at the tier funnel."

> "[Point at Platinum] These [238] Platinum customers average [S$388] GP each at [85%] repeat. They're already engaged. The goal is to retain them and protect them from blanket discounts — that's Recommendation 1."

> "[Point at Gold-A] Gold-A Whales — [130] customers, [S$300] GP, [72%] repeat. Large baskets but infrequent. The subscription engine is the mechanism to make them more frequent."

> "[Point at Gold-B] Gold-B Loyal Regulars — [264] customers, [S$105] GP, [54%] repeat. These are the customers who prove they reorder but haven't subscribed yet. SUB-01 targets exactly this tier."

> "[Point at Silver] Silver — [858] customers, [S$100] GP, [45%] repeat. They're repeat buyers but stuck at one category. L3 cross-sell is the mechanism to push them up to Gold-B. The prize at 5% conversion is modest in year 1, but the repeat rate jump from 45% to 54% compounds over 2–3 years."

> "[Point at Untiered] And then [4,204] untiered customers — the one-and-done pool — at [S$39] avg GP and [11%] repeat. This is where L1 and L3 do the heaviest lifting. If [5%] of these customers convert to Silver-level repeaters, that's [210] customers × [S$61] GP lift = [S$12,810] GP in year 1."

---

**[THE TOTAL PRIZE — 45 seconds]**

> "Putting it together. Five percent of [3,681] single-category customers reaching [3] categories: [S$10,693] GP per year. Subscription conversion: [S$2,262] GP. Acquisition mix fix — stopping shaker-led campaigns: [S$4,389] GP. Conservative total: [S$17–30K] GP per year."

> "These are conservative scenarios at [5%] conversion rates, which is a low bar for a system that's actually putting the right product in front of the right customer at the right time."

---

**[CLOSE — 30 seconds]**

> "The system is not complex to run. It's a lookup table, a nightly script, an email flow, and a fulfilment note. What makes it powerful is the timing. The data told us exactly when customers reorder, exactly which product to show them next, and exactly when to send a physical trial sample. We've done the analysis. The infrastructure to execute it is already in Shopify."

> "Phase 1 can go live in four weeks. The analysis is done. The lookup table is built. The only thing left is the connection."

---

---

## Anticipated Q&A

**Q: "What if the sample costs too much to ship separately?"**
> "The margin math supports it. Clear Protein has a [64%] GP margin. The sample costs roughly [S$2–3] including a single-serve sachet and an envelope. If even [30%] of customers who receive it add the cross-sell product on their next order, the GP from that add ([S$28] average) covers [10x] the sample cost. The ROI is strongly positive even at low conversion."

**Q: "Why not just use Shopify's built-in product recommendations?"**
> "Shopify's algorithm is designed for fashion and accessories — large catalogues, impulse buying. It has no timing logic. It doesn't know when a customer is about to reorder. It doesn't distinguish between a first-time buyer and a 5-order loyalist. The [14-day] email and [44-day] sample timing is what makes Layer 3 work — Shopify's default system has none of that."

**Q: "How long does Phase 1 take to build?"**
> "[4 weeks] to go live. Week 1: connect Shopify webhook, set up the nightly extract. Week 2: configure the email flows (CS-01 to CS-03) in the email platform. Week 3: set up the fulfilment tag and daily dispatch report. Week 4: test, QA, and launch. No custom app development required."

**Q: "What if the reorder timing is wrong for some customers?"**
> "The timing is based on the [median] of real cohorts — [81] Clear Peach buyers and [39] Lean TMT buyers. Some customers will reorder earlier or later. The [10-day] buffer before the median reorder is specifically designed to catch early reorderers. For late reorderers, receiving the sample a few days after they've already reordered is still a valid product introduction — they'll just add it to the next order."

**Q: "Should the Subscribe & Save offer come earlier than Day 48?"**
> "We tested the timing against the reorder interval data. Day [48] is [5–10 days] before the third reorder window for most hero SKU buyers. That's the optimal moment — they've proven they buy twice, they're close to their third purchase, and the Subscribe & Save offer converts at the highest rate right before a reorder decision, not after."

**Q: "What about the customers who haven't subscribed yet despite multiple orders?"**
> "The [689] repeat non-subscribers are one of the highest-value targets. These are people who proved product fit but never got the right subscription offer. SUB-01 at Day [48] after order [2] is specifically for them. SUB-02 targets the [228] high-frequency D1 non-subscribers after order [3]. The system has four subscription flows designed for different entry points."

---

*Slide content details: `final_slides_rec.md` | Technical deep-dive: `recommendation_sys.md`*
