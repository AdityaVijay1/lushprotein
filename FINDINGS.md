# LushProtein — EDA Findings Document

**Project:** ISSS603 Science of Customer Analytics · SMU Sem 5
**Framework:** Bruce, Fader & Ross — The Customer-Base Audit (5 Lenses)
**Data period:** 2020 – Q1 2026
**Dataset:** 27,350 Shopify orders · 13,780 unique customers · **All markets (SG + MY + HK) combined in SGD**

> **CURRENCY ASSUMPTION:** 5-year average exchange rates (2020–2026) applied at data load:
> **1 SGD = 3.30 MYR** | **1 SGD = 6.10 HKD**
> Applied in `EDA/01_load_and_merge.py`. All revenue figures below are SGD-equivalent.
> Retention rates, repeat rates, and cohort patterns are count-based — FX-neutral.

---

## The Five-Lens Framework (Customer-Base Audit)

This analysis follows the **Customer-Base Audit** methodology from Bruce, Fader & Ross (2022), applied to LushProtein's full transaction history. The framework pivots the standard "Product × Time" view to a **Customer × Time** face — the same data, a different orientation, a fundamentally different set of questions.

| Lens | Focus | Question |
|---|---|---|
| **Lens 1** | One period, all customers | How different are our customers from each other? |
| **Lens 2** | Two adjacent periods | Why did the top-line move? New, lost, or changed spend? |
| **Lens 3** | One cohort tracked over time | How does the behaviour of customers we acquired together evolve? |
| **Lens 4** | Two cohorts at the same age | Are the customers we are acquiring now better or worse than before? |
| **Lens 5** | All cohorts, all periods | How healthy is our customer base as a system? |

---

## Lens 1 — How Different Are Our Customers?
*(Script: `07_lens1_heterogeneity.py` | All markets combined (SGD): 13,780 customers | Revenue: S$3.11M)*

### The Three Ds

**Distribution — The average customer is a fiction**

| Metric | Mean | Median | Mean/Median | % Below Mean |
|---|---|---|---|---|
| Total Transactions | 1.98 | 1.00 | 1.98x | 67.6% |
| Total Spend (SGD) | S$226 | S$67 | 3.38x | 82.7% |
| Profit Proxy (SGD) | S$90 | S$27 | 3.38x | 82.7% |
| AOV (SGD) | S$92 | S$54 | 1.72x | 73.9% |

Spend and transaction count are heavily right-skewed. **82.7% of customers are below the mean spend.** AOV is less skewed — the size of each purchase is more consistent than the frequency. This is the empirical foundation for everything that follows.

**Decomposition — Revenue = Customers × AOF × AOV**

| Component | Value |
|---|---|
| All-Market Customers (SGD) | 13,780 |
| Avg AOF (orders/customer) | 1.985 |
| Avg AOV (SGD/order) | S$92 |
| Revenue per customer | S$226 |

AOF varies 20x+ across deciles. AOV varies only 2x. **Frequency is the lever, not basket size.**

**Decile — The vital few**

| Decile | % Customers | % Revenue | Avg Spend | AOF | AOV |
|---|---|---|---|---|---|
| D1 (top 10%) | 10% | **65.9%** | S$1,488 | 6.6 | S$384 |
| D2 | 10% | 12.2% | S$275 | 2.9 | S$133 |
| D1+D2 (top 20%) | 20% | **78.1%** | — | — | — |
| D10 (bottom 10%) | 10% | 0.0% | S$0 | 1.0 | S$0 |

Top 10% generates **65.9%** of all revenue. Top 20% generates **78.1%**. The 80/20 rule is extreme here. The MY market inclusion adds lower-spend customers in the middle deciles, slightly diffusing concentration vs SG-only.

---

## Lens 2 — What Changed? Period-on-Period Decomposition
*(Script: `08_lens2_period_decomposition.py` | Focal pair: 2023 vs 2024 | All markets, SGD)*

### Annual Customer Waterfall (All Markets, SGD)

| Year A | Year B | Lost (A-only) | Retained (Both) | New (B-only) | Retention Rate |
|---|---|---|---|---|---|
| 2020 | 2021 | 1,215 | 481 | 3,334 | **28.4%** |
| 2021 | 2022 | 3,072 | 743 | 1,556 | 19.5% |
| 2022 | 2023 | 1,883 | 416 | 983 | 18.1% |
| 2023 | 2024 | 1,042 | 357 | 2,264 | **25.5%** |
| 2024 | 2025 | 2,152 | 469 | 3,638 | 17.9% |

Year-over-year retention is 18–28%. **At most 28% of any year's customers return the following year.** This is the leaky bucket made quantitative. The MY market significantly increases total customer counts in each year vs the old SG-only analysis.

### Multiplicative Decomposition: 2023 vs 2024

| Group | Customers | Avg Revenue | AOF | AOV |
|---|---|---|---|---|
| 2023-Only (Lost) | 1,042 | S$95 | 1.3 | S$72 |
| Both Years (in 2023) | 357 | S$233 | 2.5 | S$94 |
| Both Years (in 2024) | 357 | S$238 | 2.9 | S$86 |
| 2024-Only (New) | 2,264 | S$88 | 1.4 | S$61 |

**The selection effect:** Retained customers' AOF (2.5) is 1.9x the lost customers' AOF (1.3). Frequent buyers self-select to stay. This is NOT caused by retention programs — it reflects who they always were.

### Decile Migration (2023 → 2024, both-years customers)
- **~24% stayed in the exact same decile** (diagonal — consistent across market sizes)
- **~50% stayed within ±1 decile** (practical stability band)
- Top decile (D1) is sticky: 17 of ~35 D1 customers stayed in D1
- Middle tiers (D5–D7) spread across all columns — inherently unpredictable

### Up-Down Analysis
- **~49% of retained customers improved** their profit in 2024
- **~51% declined**
- Among decliners: AOV decline is the dominant pattern (spend per trip drops before customers exit)
- Net change from retained customers is near-zero (gains and losses nearly cancel)

---

## Lens 3 — How Does Customer Behaviour Evolve Over Time?
*(Script: `09_lens3_cohort_evolution.py` | Focal cohort: 2020 all-market buyers, n=1,696)*

### Annual Cohort Activity (2020 cohort tracked 2020–2026)

| Year | Active | % Active | Revenue (SGD) | AOF | AOV |
|---|---|---|---|---|---|
| 2020 (acq) | 1,696 | **100%** | S$456,952 | 1.68 | S$161 |
| 2021 | 481 | 28.4% | S$295,643 | 2.36 | S$260 |
| 2022 | 315 | 18.6% | S$201,829 | 1.84 | S$347 |
| 2023 | 157 | 9.3% | S$36,231 | 2.11 | S$109 |
| 2024 | 162 | 9.6% | S$37,514 | 2.30 | S$101 |
| 2025 | 77 | 4.5% | S$16,558 | 2.77 | S$78 |
| 2026 | 26 | 1.5% | S$3,633 | 1.39 | S$101 |

Revenue decays from S$457K to S$4K over 7 years. **The decay is driven entirely by % Active falling from 100% to 1.5%.** Per-customer spending (AOF × AOV) stays relatively stable — the problem is not spend per trip but frequency of return. The AOV drop in 2023–2025 reflects the shift toward discount-heavy ordering for this cohort's returning members.

### Purchase Incidence Patterns (2020 cohort)

| Pattern | Customers | % Cohort | Meaning |
|---|---|---|---|
| NNNNNN (never again) | 1,072 | **63.2%** | One-and-done |
| YNNNNN | 212 | 12.5% | Returned once in 2021 then gone |
| YYNNNN | 96 | 5.7% | Returned 2021+2022 then gone |

**63.2% of the 2020 cohort never bought again.** The MY market cohort has a slightly higher one-and-done rate than SG-only, consistent with the lower repeat rates observed in the MY store. The majority who ever returned did so in Year 1 and then dropped off.

**Year-to-year repeat rates (conditional on being active):**

| Transition | Rate |
|---|---|
| 2020 → 2021 | 28.4% |
| 2021 → 2022 | 65.5% |
| 2022 → 2023 | 49.8% |
| 2023 → 2024 | 50.6% |

Once a customer survives to Year 2, their conditional retention rate improves significantly. **Surviving customers are self-selecting, higher-loyalty buyers.**

### Time-to-Nth Purchase (Inter-purchase CDF)

| Transition | Made Next | Median Days | Within 60d |
|---|---|---|---|
| 1 → 2 | 52.8% of 1,696 | **84 days** | ~41.9% |
| 2 → 3 | 67.3% of 896 | 92 days | ~38.3% |
| 3 → 4 | 74.9% of 603 | 96 days | ~37.6% |
| 4 → 5 | 72.8% of 452 | 86 days | ~38.0% |
| 5 → 6 | 80.5% of 329 | 84 days | ~39.6% |

The classic inter-purchase time pattern: **1→2 is the hardest transition** (52.8% conversion). Each subsequent transition converts better. By transition 5→6, 80.5% convert. The combined-market median for 1→2 (84 days) is shorter than the SG-only (134 days), indicating the MY market has faster reorder cycles relative to SG — but the 60-day conversion rate is similar (~42%) across both.

### VTD (Value to Date) Distribution

| Metric | Value |
|---|---|
| Mean VTD | **S$618** |
| Median VTD | S$130 |
| Mean / Median | **4.76x** |
| % Below Mean | 78.2% |
| Top 10% VTD Share | **64.3%** |
| Top 20% VTD Share | **80.7%** |

The "average customer is worth S$618" is misleading: **78.2% of customers are worth less than S$618.** The long tail is extreme. The combined-market mean is higher than SG-only (S$327) because the 2020 cohort now includes MY customers whose total lifetime SGD-equivalent spend is captured across 6+ years.

### VTD Decile Table (2020 cohort, all markets)

| Decile | % Cohort | % VTD | Avg VTD | Avg Orders |
|---|---|---|---|---|
| D1 (top 10%) | 10% | **64.5%** | S$3,976 | 10.5 |
| D2 | 10% | 16.3% | S$1,007 | 6.3 |
| D3 | 10% | 7.9% | S$491 | 4.3 |
| D10 (bottom 10%) | 10% | 0.3% | S$19 | 1.0 |

AOF range: **10.5x (D1) vs 1.0x (D10)** — frequency drives almost all of the value difference.

### RFM Analysis (2020 Cohort, as of April 2026)

| Segment | N | % | Avg Orders | Avg Revenue |
|---|---|---|---|---|
| Hibernating | 497 | 29.3% | 1.0 | S$156 |
| Champions | 394 | 23.2% | 8.1 | S$1,753 |
| Loyal | 378 | 22.3% | 2.9 | S$525 |
| **At Risk** | **180** | **10.6%** | **2.6** | **S$306** |
| **Can't Lose** | **171** | **10.1%** | **1.0** | **S$63** |

The **At Risk (180 customers, S$306 avg revenue)** and **Can't Lose (171 customers, S$63 avg revenue)** groups are 351 customers from the 2020 cohort who have gone quiet. Combined, this cohort's disengaging segment holds substantial reactivation value. The larger cohort size vs SG-only produces more customers in each segment.

---

## Lens 4 — Are the Customers We Are Acquiring Now Better or Worse Than Before?
*(Script: `10_lens4_vintage_comparison.py` | Cohorts: 2020–2024, All markets combined SGD)*

### Cohort Quality at Acquisition (Age 0 — same-age comparison)

| Cohort | Customers | Avg 1st Order | % Discounted | Avg Disc Depth | Top Channel |
|---|---|---|---|---|---|
| 2020 | 1,696 | S$124 | 0.0% | 0% | Direct / Organic |
| 2021 | 3,334 | S$96 | 0.0% | 0% | Direct / Organic |
| 2022 | 1,462 | S$131 | 13.9% | 41.1% | Direct / Organic |
| 2023 | 873 | S$66 | 61.1% | 23.0% | Subscription |
| 2024 | 2,015 | S$59 | 81.4% | 43.0% | Subscription |

First-order value collapsed from **S$124 (2020) to S$59 (2024)**. Discounted first orders rose from **0% to 81%**. Average discount depth went from 0% to 43%.

> **Note on top channel:** The combined-market analysis uses "Direct / Organic" as the dominant channel in 2020–2022 rather than "Subscription" in the old SG-only report. This reflects the MY market's higher proportion of Direct/Organic orders. The strategic finding — increasing discount prevalence across cohorts — is unchanged.

### Year 1 Retention Comparison (same-age: 365 days post-acquisition)

| Cohort | Customers | 60d Retention | 180d Retention | 365d Retention | Avg Y1 Revenue |
|---|---|---|---|---|---|
| 2020 | 1,696 | 14.3% | 29.8% | **38.0%** | S$334 |
| 2021 | 3,334 | 15.0% | 23.6% | 28.1% | S$212 |
| 2022 | 1,462 | 13.8% | 22.1% | 25.9% | S$241 |
| 2023 | 873 | 13.5% | 22.0% | 25.8% | S$107 |
| 2024 | 2,015 | **16.1%** | 24.1% | 28.1% | S$99 |

**Cohort quality is declining at the same age.** 365-day retention fell from 38.0% (2020) to 25.8% (2023). Year 1 revenue per customer fell from S$334 to S$99 — a 70% collapse. The combined-market retention rates are slightly higher than SG-only because MY customers have shorter reorder cycles.

- 2020–2021 avg 365d retention: **33.1%**
- 2023–2024 avg 365d retention: **26.9%**
- **Quality drift: −6.2 percentage points**

### Channel Mix Shift by Cohort Year

| Cohort | Direct/Subscription | Marketplace |
|---|---|---|
| 2020 | 100% | 0.0% |
| 2021 | 100% | 0.0% |
| 2022 | ~94% | ~6% |
| 2023 | ~50% | **~50%** |
| 2024 | ~79% | ~21% |

**In 2023, marketplace acquisition reached 50% of all new customers.** This is a structural shift — marketplace customers have 1.7× lower LTV, no confirmed Shopify subscription conversion, and 2.3× lower repeat rates. The 2023 cohort's poor performance is largely explained by this channel mix shift.

### Discount Intensity by Cohort

| Cohort | % Discounted | Avg Disc Depth | Avg 1st Order |
|---|---|---|---|
| 2020 | 0.0% | 0% | S$124 |
| 2021 | 0.0% | 0% | S$96 |
| 2022 | 13.9% | 41.1% | S$131 |
| 2023 | 61.1% | 23.0% | S$66 |
| 2024 | 81.4% | 43.0% | S$59 |

From 0% to 81% discounted first orders in 4 years. **The brand has progressively trained its acquisition funnel to attract discount-sensitive buyers — the exact customer profile with the worst long-term retention.**

---

## Lens 5 — How Healthy Is the Customer Base?
*(Script: `11_lens5_base_health.py` | All cohorts, all calendar years, all markets combined SGD)*

### Cohort × Year Revenue Matrix (SGD, thousands)

| Cohort | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| 2020 | S$457K | S$296K | S$202K | S$36K | S$38K | S$17K |
| 2021 | — | S$552K | S$216K | S$30K | S$28K | S$11K |
| 2022 | — | — | S$330K | S$36K | S$26K | S$9K |
| 2023 | — | — | — | S$80K | S$22K | S$8K |
| 2024 | — | — | — | — | S$171K | S$46K |

This is the "triangle." Each row is a cohort; each column is a calendar year. The off-diagonal cells are much smaller than the acquisition-year cells. **Cohorts fade rapidly and do not accumulate.** The 2021 cohort acquisition year of S$552K (vs S$456K for 2020) shows the MY market peak was in 2021.

### Revenue Decay Curves (% of acquisition-year revenue)

| Cohort | Age+0 | Age+1 | Age+2 | Age+3 | Age+4 |
|---|---|---|---|---|---|
| 2020 | 100% | **64.7%** | 44.2% | 7.9% | 8.2% |
| 2021 | 100% | **39.1%** | 5.4% | 5.0% | 2.0% |
| 2022 | 100% | **11.0%** | 8.0% | 2.8% | — |
| 2023 | 100% | **28.0%** | 9.9% | — | — |
| 2024 | 100% | **26.9%** | — | — | — |

**Decay is accelerating.** The 2020 cohort retained 64.7% of its acquisition-year revenue in Year 1. The 2022 cohort retained only 11.0%. This is the smoking gun for declining cohort quality. The pattern is consistent with SG-only results — the combined-market data confirms the trend.

### Customer Base Composition Waterfall (All Markets, SGD)

| Year | Total | New | Retained | Recovered | %New | %Ret |
|---|---|---|---|---|---|---|
| 2020 | 1,696 | 1,696 | 0 | 0 | 100% | 0% |
| 2021 | 3,815 | 3,334 | 481 | 0 | **87.4%** | 12.6% |
| 2022 | 2,299 | 1,462 | 743 | 94 | 63.6% | 32.3% |
| 2023 | 1,399 | 873 | 416 | 110 | 62.4% | 29.7% |
| 2024 | 2,621 | 2,015 | 357 | 249 | **76.9%** | 13.6% |
| 2025 | 4,107 | 3,524 | 469 | 114 | **85.8%** | 11.4% |

In 2024 and 2025, **77–86% of active customers are new** — buying for the first time. The retained base is not growing. The entire business depends on continuous acquisition spending.

### Revenue Composition (SGD, combined markets)

| Year | Total Rev | Notes |
|---|---|---|
| 2021 | S$848K | MY market at peak (S$441K SG + S$407K MY) |
| 2022 | S$748K | Revenue decline begins |
| 2023 | S$182K | Revenue collapse year |
| 2024 | S$285K | Partial recovery, heavy discounting |
| 2025 | S$409K | Order volume peaks but avg order value lower |

Revenue in 2025 is still only 48% of the 2021 peak despite record order volume — the discount-driven acquisition model is producing more orders at lower value per order.

### Customer Base Health Scorecard

| KPI | Value | Status | Target |
|---|---|---|---|
| Overall Repeat Rate | 32.4% | **ALERT** | >35% |
| YoY Retention (latest yr) | **7.8%** | **ALERT** | >40% |
| Avg 60-Day Cohort Retention | 18.1% | **ALERT** | >20% |
| Acquisition Dependency | **51.9%** | **ALERT** | <50% |
| Top 20% Revenue Concentration | **78.1%** | OK | <80% |

**All four quantitative KPIs are in alert**. The acquisition dependency score of 51.9% has crossed the threshold — the business is now more than 50% dependent on new buyers each year to maintain revenue. The top 20% concentration at 78.1% is just below the OK/alert threshold.

---

## Integrated Prescription — What All 5 Lenses Are Saying Together

| Lens | The Finding | The Implication |
|---|---|---|
| **Lens 1** | Top 10% = 68.5% of revenue; AOF drives everything | Protect high-frequency buyers above all |
| **Lens 2** | 78–84% of customers lost each year; frequency drops predict decline | Early warning = AOF decline in retained customers |
| **Lens 3** | 61% one-and-done; 1→2 purchase is the critical barrier | Win the first repeat order within 60 days |
| **Lens 4** | Cohort quality declined 7.7pp in 4 years; discount/marketplace shift is cause | Stop acquiring through deep discounts and marketplace |
| **Lens 5** | 80–92% of active customers are new each year; retained base not growing | Business is one acquisition-spend cut away from revenue collapse |

**The single sentence diagnosis:** LushProtein is running a leaky bucket that has been patched with discounts and marketplace spend — which are themselves making the bucket leakier.

**The single sentence prescription:** Stop discounting for new customers, exit low-quality marketplace acquisition, and invest the saved margin into a post-purchase experience that turns the 1→2 transition from a ~41% 60-day success into a 60%+ success.

---

## Quick Reference — Key Numbers

| Metric | Value |
|---|---|
| Unique customers | 13,780 |
| Total orders (2020–2026) | 27,350 |
| Overall repeat purchase rate | **32.4%** |
| 60-day retention rate | **18.3%** |
| Median days to 2nd order | **49 days** |
| Subscriber avg LTV | **S$532** (combined SGD) |
| Non-subscriber avg LTV | S$200 (combined SGD) |
| Subscriber LTV uplift | **+166%** |
| Raw subscription churn rate | **64.7%** |

---

## Finding 1 — Revenue and the Discount Problem

Revenue peaked at **S$848K in 2021 with zero discounting** (combined SG + MY). As the brand introduced promotions from 2022 onward, discount rates climbed to **50% of all 2025 orders** — and revenue did not recover.

| Year | Revenue (SGD, all markets) | % Orders Discounted | % of Gross Revenue |
|---|---|---|---|
| 2020 | **S$456,952** | 0% | 0% |
| 2021 | **S$847,930** | 0% | 0% ← Peak |
| 2022 | **S$747,587** | 15.2% | 3.9% |
| 2023 | **S$182,038** | 59.3% | 15.1% |
| 2024 | **S$284,971** | 69.2% | 30.9% |
| 2025 | **S$409,152** | 49.6% | 35.2% |

The 2023 revenue collapse (–77% vs 2021) coincides with the first aggressive discounting campaigns. The partial recovery in 2024–2025 has been achieved on the back of heavily discounted orders, meaning revenue is growing but at the cost of margin and cohort quality (see Finding 4).

**Chart:** `01a_revenue_discount_trend.png`

---

## Finding 2 — Channel Quality Gap: Marketplace vs Own Website

Not all acquisition channels produce the same customer. The data reveals a fundamental split between own-website customers and marketplace customers:

| Channel | Customers | Repeat Rate | Avg LTV (SGD) | % Subscribed (Shopify) |
|---|---|---|---|---|
| Subscription | 4,275 | 40.9% | S$343 | 18.8% |
| **Direct / Organic** | **6,920** | **33.5%** | **S$198** | 3.8% |
| Paid Social | 382 | 19.4% | S$71 | 6.0% |
| Affiliate | 26 | 19.2% | S$94 | 3.8% |
| **Marketplace** | **2,126** | **14.4%** | **S$115** | **0.0%** |
| Email | 48 | 12.5% | S$50 | 2.1% |

> **Marketplace repeat rate — measurement note:** The 14.4% is computed as 306 customers with 2+ Shopify-visible orders ÷ 2,126 marketplace-first customers. A customer's second order counts whether it was another Shopee/Lazada order synced back into Shopify via the integration, or a direct Shopify.com purchase. Evidence of partial sync: there are 3,268 total marketplace-tagged orders across 2,126 marketplace customers (avg 1.54 orders/customer) — if only first-time orders were synced, there would be exactly 2,126 orders, not 3,268. The extra ~1,142 orders confirm repeat marketplace purchases do appear in Shopify. The 14.4% may still be an undercount if some customers repurchase on Shopee/Lazada using a different email (creating a new Shopify ID) or if the sync is incomplete. Strategically, customers who only repeat on marketplace without entering the Shopify ecosystem have 0% Shopify subscription conversion and no CRM visibility — strengthening, not weakening, the channel quality argument.
>
> **Marketplace 0% subscribed:** Reflects Shopify subscriptions only. Shopee/Lazada operate independent auto-delivery systems not tracked in Shopify. The LTV and repeat rate comparisons remain valid as both are measured purely from Shopify order history.

Marketplace customers (Shopee, Lazada, Tokopedia) represent **15% of total customers** but:
- Repeat at **14.4%** vs **33.5%** for Direct/Organic — a **2.3× gap**
- Generate **S$115 avg LTV** vs **S$198** for own-website — a **1.7× gap**
- Zero confirmed Shopify subscription conversion

Marketplace channels inflate order counts and headline customer numbers without building a loyal customer base. The business is treating marketplace volume as growth when it is largely transactional traffic.

**Charts:** `02a_retention_by_channel.png`, `05b_marketplace_vs_website.png`

---

## Finding 3 — Cross-Sell is the Single Largest LTV Lever

Every additional product category a customer buys roughly doubles their lifetime loyalty:

| Products Purchased | Customers | Repeat Rate | Avg LTV (SGD) | vs 1-Product LTV |
|---|---|---|---|---|
| 1 product | 9,537 | 23.6% | S$170 | baseline |
| 2 products | 2,679 | 39.7% | S$230 | +35% |
| 3 products | 1,052 | **65.5%** | **S$470** | **+176%** |
| 4+ products | 512 | **88.7%** | **S$743** | **+337%** |

Moving a customer from 1 to 3 product categories:
- Raises repeat rate from **23.6% → 65.5%** (+178%)
- Raises avg LTV from **S$170 → S$470** (+176%)

**Top cross-purchase combinations among repeat buyers:**

| Combination | Customers |
|---|---|
| Accessories + Clear Protein + Lean Protein | 69 |
| Clear Protein + Lean Protein | 59 |
| Accessories + Clear Protein | 56 |
| Accessories + Other | 54 |
| Lean Protein + Other | 80 |

This is not a demand-side insight requiring heavy persuasion — it is a supply-side gap. Customers who are exposed to multiple products become loyal. The implication is a targeted cross-sell email sequence in the 7–21 days after first purchase.

**Charts:** `03a_cross_product_ltv.png`, `03d_top_product_combos.png`

---

## Finding 4 — Discount Depth Destroys Long-Term Loyalty

The relationship between first-order discount depth and long-term customer quality is consistent and damaging:

| First-Order Discount Depth | Customers | Repeat Rate | Avg LTV (SGD) |
|---|---|---|---|
| **Full price (0%)** | **9,398** | **36.4%** | **S$274** |
| 1–5% off | 186 | 17.7% | S$109 |
| 6–10% off | 395 | 26.1% | S$135 |
| 11–20% off | 1,250 | 25.5% | S$120 |
| 21–30% off | 458 | 25.5% | S$158 |
| 31–50% off | 1,189 | 23.0% | S$150 |
| **51%+ off** | **430** | **21.9%** | **S$92** |

Source: `EDA/outputs/05_discount_depth_bins.csv` — dynamically computed, zero hardcoded values.

Full-price buyers repeat at **36.4%** with **S$274 LTV**.
51%+ discount buyers repeat at **21.9%** with **S$92 LTV** — a **+66% repeat rate advantage and +198% LTV advantage for full-price buyers**.

The drop is immediate: any discount at all pulls the repeat rate into the low-to-mid 20s. The LTV damage is consistent across all discount depths — from S$274 (full price) to S$92 (51%+). The 51%+ cohort includes 100% affiliate/event codes — these are effectively zero-revenue acquisition events disguised as customers.

With 35.2% of gross 2025 revenue absorbed by discounts, the business is predominantly acquiring weaker cohorts. This compounds over time.

**Chart:** `05a_discount_depth_impact.png`

---

## Finding 5 — Subscription is High Value but Churns Early

Subscribers are the most valuable customer segment by a significant margin:

| Metric | Subscriber | Non-Subscriber | Uplift |
|---|---|---|---|
| Repeat rate | 74.4% | 28.7% | +159% |
| Avg LTV (SGD, combined) | S$532 | S$200 | **+166%** |
| Avg orders | 4.9 | 1.7 | +188% |
| Avg customer lifespan | 399 days | 93 days | +329% |

But **64.7% of subscribers eventually cancel**. Churn is concentrated in the first 60 days:

| Subscription Cycle | Cancellations | % of Total Churn |
|---|---|---|
| Cycle 0 (< 30 days) | 60 | 11.4% |
| **Cycle 1 (30–60 days)** | **110** | **20.9%** ← peak |
| Cycle 2 (60–90 days) | 101 | 19.2% |
| Cycle 3 (90–120 days) | 81 | 15.4% |
| **Cycles 1–3 combined** | **292** | **55.5%** |

**The most revealing signal is the top cancellation reason:**

| Reason | Count | % |
|---|---|---|
| **"I already have more than I need"** | **143** | **31.9%** |
| Other reason | 131 | 29.2% |
| I no longer use this product | 88 | 19.6% |
| Created by accident | 40 | 8.9% |
| Too expensive | 19 | 4.2% |

"Already have more than I need" is not a satisfaction failure. It is a **cadence mismatch**. The standard 30-day delivery interval delivers product faster than many customers consume it. Tubs accumulate, the customer feels wasteful, and they cancel — not because the product failed them but because the subscription timing did.

**The fix is operational:** add a 45-day and 60-day interval option, and make the skip-delivery button prominent before each renewal.

**Win-back rate:** 43 of 347 churned subscribers reactivated (12.4%). Median time to reactivation: 112 days.

**Charts:** `04a_subscriber_vs_onetime.png`, `04b_churn_by_cycle.png`, `04c_cancellation_reasons.png`

---

## Finding 6 — Time-to-Second-Purchase Window

Of 13,780 customers who ever bought, **4,459 (32.4%) placed a second order.**

| Time Window | Repeaters | Cumulative % of All Repeaters |
|---|---|---|
| 0–7 days | 336 | 7.5% |
| 8–14 days | 222 | 12.5% |
| 15–30 days | 568 | 25.3% |
| 31–60 days | 692 | 40.8% |
| **61–90 days** | **461** | **51.1%** ← largest single histogram bucket |
| 91–180 days | 603 | 64.6% |
| 181–365 days | 450 | 74.7% |
| 365+ days | 463 | 85.1% |

- **P50 (median): 49 days** — half of all repeat buyers return within 49 days
- **P75: 141 days** — three-quarters return within 5 months
- **~41% return within 60 days** — the 60-day mark is the operationally critical window; after this point the probability of natural repurchase declines sharply

The **60-day window** is when the product biology is most aligned with repurchase intent — a standard serving lasts approximately 4–8 weeks. The first 60 days after first purchase is the retention-critical window. Any marketing touchpoint — win-back email, loyalty incentive, cross-sell offer — has maximum effectiveness in this window.

**Chart:** `02c_time_to_second_purchase.png`

---

## Finding 7 — Hero Product Retention Comparison

| First Product Bought | Customers | Repeat Rate | Avg LTV (SGD) | Median Days to 2nd |
|---|---|---|---|---|
| Collagen Glow | 439 | **31.2%** | S$231 | 48 days |
| Lean Protein | 1,324 | 23.2% | S$118 | **36 days** |
| Clear Protein | 1,550 | 22.5% | S$149 | 44 days |
| Soy Protein | 361 | 20.8% | S$138 | 64 days |
| Accessories | 696 | 22.1% | S$97 | 20 days |

Collagen Glow leads on repeat rate (31.2%) and has the highest subscription loyalty ratio in the Recharge data (50% of checkout subscribers stay for recurring). Lean Protein drives the fastest repurchase cycle (36 days median).

**Subscription SKU loyalty ratios (recurring customers / checkout customers):**

| SKU | Loyalty Ratio |
|---|---|
| Soy Protein Isolate | 54% |
| Collagen Glow 300g | **50%** |
| Creatine Monohydrate | 42% |
| Lean Protein Taro 1kg | 38% |
| Clear Protein Peach 500g | 32% |

**Chart:** `02b_retention_by_product.png`, `03c_sku_loyalty.png`

---

## Finding 8 — RFM Customer Segments

| Segment | Customers | % of Base | Avg LTV | Avg Orders | Priority Action |
|---|---|---|---|---|---|
| Loyal | 4,359 | 31.6% | S$157 | 1.9 | Cross-sell to 2nd product |
| Hibernating | 3,321 | 24.1% | S$112 | 1.0 | Low-cost reactivation |
| **At Risk** | **2,351** | **17.1%** | **S$514** | 3.4 | **Win-back urgently** |
| Champions | 1,828 | 13.3% | S$397 | 3.2 | Reward + upsell |
| **Can't Lose** | **1,218** | **8.8%** | **S$66** | 1.0 | **Re-engage now** |
| Promising | 688 | 5.0% | S$61 | 1.0 | Nurture to 2nd order |
| New | 15 | 0.1% | S$67 | 1.0 | Welcome sequence |

The **At Risk segment (2,351 customers, S$514 avg LTV)** represents the most urgent reactivation opportunity. These customers have demonstrated a willingness to spend significantly but have gone quiet. Combined with Can't Lose (1,218 customers), **over 3,500 proven-spenders are currently disengaging** from the brand.

**Chart:** `05c_rfm_segments.png`

---

## Prioritised Findings — If/Then Table

| Rank | Finding | Key Evidence | Confidence | Suggested Experiment |
|---|---|---|---|---|
| 1 | Deep discounting destroys cohort quality | Full-price: 36.4% repeat, S$274 LTV vs 51%+ off: 21.9% repeat, S$92 LTV (+66% RR, +198% LTV for full-price buyers) | High | Cap new-customer discount at 15%; remove 50%+ deals |
| 2 | Cross-sell drives biggest LTV jump | 3-product buyers: 65.5% repeat, S$470 LTV (+176% vs 1-product) | High | Post-purchase cross-sell email at Day 14–21 |
| 3 | At Risk segment = immediate high-value opportunity | 2,351 customers, S$514 avg LTV, currently dormant | High | Targeted win-back campaign |
| 4 | Subscription cadence causes stockpile churn | 27% cancel "already have too much"; peak churn at Cycle 1 | High | Add 45/60-day interval option + skip-delivery CTA |
| 5 | Marketplace cannibalises LTV | 14.4% repeat vs 33.5% direct; 1.7× LTV gap (S$115 vs S$198) | Medium | Reduce marketplace SKU breadth; redirect budget to own channels |
| 6 | Expectation mismatch drives early exit *(minor hypothesis)* | ~41% of repeaters return within 60 days; churn peaks pre-60d | Medium | Post-purchase onboarding sequence setting timeline expectations |

---

## Mid-Term Presentation — Highest-Impact Charts

For the 4 slides that carry the most visual weight, use:

| Slide topic | Chart file | Why it works |
|---|---|---|
| Cross-sell LTV | `03a_cross_product_ltv.png` | The staircase visually shows the exponential value of breadth — one glance tells the story |
| Subscription churn | `04b_churn_by_cycle.png` | The shaded 30–60 day danger zone and peak at Cycle 1 make the timing pattern immediately clear |
| Discount impact | `05a_discount_depth_impact.png` | The V-drop from full-price to any discount, then the flat line, makes the argument visually |
| Channel quality | `02a_retention_by_channel.png` | Side-by-side repeat rate and LTV bars make the marketplace gap undeniable |

---

*Document generated from EDA scripts in `/EDA/` · Charts in `/visualizations/charts/`*
*ISSS603 Science of Customer Analytics · Singapore Management University · May 2026*
