# LushProtein — EDA Findings Document

**Project:** ISSS603 Science of Customer Analytics · SMU Sem 5
**Framework:** Bruce, Fader & Ross — The Customer-Base Audit (5 Lenses)
**Data period:** 2020 – Q1 2026
**Dataset:** 27,350 Shopify orders · 13,780 unique customers · **All markets (SG + MY + HK) combined in SGD**

> **CURRENCY ASSUMPTION:** Fixed exchange rates applied at data load:
> **1 SGD = 3.30 MYR** | **1 SGD = 6.10 HKD** (rates as of April 2026)
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
*(Script: `07_lens1_heterogeneity.py` | SGD customers: 8,182 | SGD revenue: S$1.79M)*

### The Three Ds

**Distribution — The average customer is a fiction**

| Metric | Mean | Median | Mean/Median | % Below Mean |
|---|---|---|---|---|
| Total Transactions | 1.84 | 1.00 | 1.84x | 72% |
| Total Spend (SGD) | S$218 | S$64 | 3.42x | 84% |
| Profit Proxy (SGD) | S$87 | S$26 | 3.42x | 84% |
| AOV (SGD) | S$91 | S$54 | 1.68x | 73% |

Spend and transaction count are heavily right-skewed. **84% of SGD customers are below the mean spend.** AOV is less skewed — the size of each purchase is more consistent than the frequency. This is the empirical foundation for everything that follows.

**Decomposition — Revenue = Customers × AOF × AOV**

| Component | Value |
|---|---|
| SGD Customers | 8,182 |
| Avg AOF (orders/customer) | 1.84 |
| Avg AOV (SGD/order) | S$91 |
| Revenue per customer | S$167 |

AOF varies 20x+ across deciles. AOV varies only 2x. **Frequency is the lever, not basket size.**

**Decile — The vital few**

| Decile | % Customers | % Revenue | Avg Spend | AOF | AOV |
|---|---|---|---|---|---|
| D1 (top 10%) | 10% | **68.5%** | S$1,494 | 6.2 | S$392 |
| D2 | 10% | 11.0% | S$241 | 2.5 | S$126 |
| D1+D2 (top 20%) | 20% | **79.5%** | — | — | — |
| D10 (bottom 10%) | 10% | 0.0% | S$0 | 1.2 | S$0 |

Top 10% generates **68.5%** of all SGD revenue. Top 20% generates **79.5%**. The 80/20 rule is not just real here — it is extreme. To generate 10% of revenue, you need just **6 customers** (0.1% of the base).

**Equal-Revenue Slicing:** Making the first 50% of revenue requires only **3.3%** of the customer base. Making the last 10% requires the remaining 61%.

---

## Lens 2 — What Changed? Period-on-Period Decomposition
*(Script: `08_lens2_period_decomposition.py` | Focal pair: 2023 vs 2024)*

### Annual Customer Waterfall (SGD)

| Year A | Year B | Lost (A-only) | Retained (Both) | New (B-only) | Retention Rate |
|---|---|---|---|---|---|
| 2020 | 2021 | 569 | 234 | 1,283 | **29.1%** |
| 2021 | 2022 | 1,200 | 317 | 666 | 20.9% |
| 2022 | 2023 | 801 | 182 | 554 | 18.5% |
| 2023 | 2024 | 575 | 161 | 1,171 | 21.9% |
| 2024 | 2025 | 1,111 | 221 | 3,400 | 16.6% |

Year-over-year retention is 17–22%. **At most 30% of any year's customers return the following year.** This is the leaky bucket made quantitative.

### Multiplicative Decomposition: 2023 vs 2024

| Group | Customers | Avg Revenue | AOF | AOV |
|---|---|---|---|---|
| 2023-Only (Lost) | 575 | S$105 | 1.3 | S$80 |
| Both Years (in 2023) | 161 | S$254 | 2.2 | S$115 |
| Both Years (in 2024) | 161 | S$251 | 2.5 | S$101 |
| 2024-Only (New) | 1,171 | S$94 | 1.4 | S$66 |

**The selection effect:** Retained customers' AOF (2.2) is 1.7x the lost customers' AOF (1.3). Frequent buyers self-select to stay. This is NOT caused by retention programs — it reflects who they always were.

### Decile Migration (2023 → 2024, both-years customers)
- **24% stayed in the exact same decile** (diagonal)
- **50% stayed within ±1 decile** (practical stability band)
- Top decile (D1) is sticky: 10 of the ~16 D1 customers stayed in D1
- Middle tiers (D5–D7) spread across all columns — inherently unpredictable

### Up-Down Analysis
- **45% of retained customers improved** their profit in 2024
- **55% declined**
- Among decliners: **74% had declining AOV (spend erosion is the dominant thread)**
- Net change from retained customers: −S$214 (gains and losses nearly cancel)

---

## Lens 3 — How Does Customer Behaviour Evolve Over Time?
*(Script: `09_lens3_cohort_evolution.py` | Focal cohort: 2020 SGD buyers, n=803)*

### Annual Cohort Activity (2020 cohort tracked 2020–2026)

| Year | Active | % Active | Revenue (SGD) | AOF | AOV |
|---|---|---|---|---|---|
| 2020 (acq) | 803 | **100%** | S$286,181 | 1.59 | S$224 |
| 2021 | 234 | 29.1% | S$180,586 | 2.23 | S$346 |
| 2022 | 159 | 19.8% | S$127,432 | 1.76 | S$455 |
| 2023 | 87 | 10.8% | S$23,658 | 2.20 | S$124 |
| 2024 | 88 | 11.0% | S$25,302 | 2.55 | S$113 |
| 2025 | 44 | 5.5% | S$11,061 | 3.25 | S$77 |
| 2026 | 17 | 2.1% | S$2,126 | 1.35 | S$92 |

Revenue decays from S$286K to S$2K over 7 years. **The decay is driven entirely by % Active falling from 100% to 2%.** Per-customer spending (AOF × AOV) stays relatively stable — the problem is not spend per trip but frequency of return.

### Purchase Incidence Patterns (2020 cohort)

| Pattern | Customers | % Cohort | Meaning |
|---|---|---|---|
| NNNNNN (never again) | 493 | **61.4%** | One-and-done |
| YNNNNN | 97 | 12.1% | Returned once in 2021 then gone |
| YYNNNN | 50 | 6.2% | Returned 2021+2022 then gone |
| YYYYYY (every year) | 6 | 0.7% | Loyal core |

**61.4% of the 2020 cohort never bought again.** Only 0.7% bought every subsequent year. The majority who ever returned did so in Year 1 and then dropped off.

**Year-to-year repeat rates (conditional on being active):**

| Transition | Rate |
|---|---|
| 2020 → 2021 | 29.1% |
| 2021 → 2022 | 47.4% |
| 2022 → 2023 | 42.1% |
| 2023 → 2024 | 55.2% |

Once a customer survives to Year 2, their conditional retention rate improves significantly. **Surviving customers are self-selecting, higher-loyalty buyers.**

### Time-to-Nth Purchase (Inter-purchase CDF)

| Transition | Made Next | Median Days | Within 60d |
|---|---|---|---|
| 1 → 2 | 51.2% of 803 | **134 days** | ~40.8% |
| 2 → 3 | 67.9% of 411 | 113 days | ~42.1% |
| 3 → 4 | 76.0% of 279 | 103 days | ~43.5% |
| 4 → 5 | 74.5% of 212 | 86 days | ~49.7% |
| 5 → 6 | 82.9% of 158 | 76 days | ~51.4% |

The classic inter-purchase time pattern: **1→2 is the hardest transition** (51.2% conversion, 134-day median). Each subsequent transition converts better and faster. By transition 5→6, 83% convert with a 76-day median. This is the selection effect: committed repeat buyers accelerate.

### VTD (Value to Date) Distribution

| Metric | Value |
|---|---|
| Mean VTD | S$327 |
| Median VTD | S$68 |
| Mean / Median | **4.8x** |
| % Below Mean | 78% |
| Top 10% VTD Share | **63%** |
| Top 20% VTD Share | **80%** |

The "average customer is worth S$327" is a profound misleading statement: **78% of customers are worth less than S$327.** The long tail is extremely long.

### VTD Decile Table (2020 cohort)

| Decile | % Cohort | % VTD | Avg VTD | AOF | AOV |
|---|---|---|---|---|---|
| D1 (top 10%) | 10% | **63%** | S$2,044 | 10.9 | S$979 |
| D2 | 10% | 17% | S$553 | 6.1 | S$334 |
| D3 | 10% | 9% | S$287 | 4.8 | S$231 |
| D10 (bottom 10%) | 10% | 0.3% | S$8 | 1.0 | S$21 |

AOF range: **10.9x (D1) vs 1.0x (D10)** — 10.9x difference driven entirely by frequency.
AOV range: **S$979 vs S$21** — but this is partially explained by the fact that high-frequency buyers buy more types of products.

### % Active by VTD Decile per Year

| Decile | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| D1 (top) | 100% | 85% | 64% | 42% | 36% | 24% |
| D2 | 100% | 64% | 48% | 30% | 29% | 11% |
| D5 | 100% | 20% | 5% | 5% | 7% | 4% |
| D8 | 100% | 3% | 0% | 0% | 0% | 0% |
| D10 (bottom) | 100% | 0% | 0% | 0% | 0% | 0% |

The **retention gradient** is the key diagnostic: D8–D10 customers are gone after Year 1. D1 retains at 85% in Year 1 and still at 24% in Year 5. A retention campaign that retains a D1 customer (VTD=S$2,044) is worth **255x** a campaign that retains a D10 customer (VTD=S$8).

### RFM Analysis (2020 Cohort, as of April 2026)

| Segment | N | % | Avg Orders | Avg Revenue | Avg Recency |
|---|---|---|---|---|---|
| Hibernating | 269 | 33.5% | 1.0 | S$118 | 2,110d |
| Champions | 187 | 23.3% | 8.3 | S$2,102 | 822d |
| Loyal | 175 | 21.8% | 3.1 | S$866 | 1,757d |
| At Risk | 70 | 8.7% | 2.6 | S$573 | 2,121d |
| Can't Lose | 63 | 7.8% | 1.0 | S$448 | 2,194d |

The **At Risk (70 customers, S$573 avg revenue)** and **Can't Lose (63 customers, S$448 avg revenue)** groups are 133 high-value customers from the 2020 cohort who have gone quiet. They are the highest-urgency reactivation targets within this cohort.

---

## Lens 4 — Are the Customers We Are Acquiring Now Better or Worse Than Before?
*(Script: `10_lens4_vintage_comparison.py` | Cohorts: 2020–2024, SGD)*

### Cohort Quality at Acquisition (Age 0 — same-age comparison)

| Cohort | Customers | Avg 1st Order | % Discounted | Avg Disc Depth | Top Channel |
|---|---|---|---|---|---|
| 2020 | 803 | S$176 | 0.0% | 0% | Subscription |
| 2021 | 1,283 | S$102 | 0.0% | 0% | Subscription |
| 2022 | 618 | S$169 | 11.0% | 51.6% | Subscription |
| 2023 | 510 | S$73 | 59.4% | 22.6% | Marketplace |
| 2024 | 1,065 | S$63 | 82.7% | 41.0% | Subscription |

First-order value has collapsed from **S$176 (2020) to S$63 (2024)**. Discounted first orders rose from **0% to 83%**. Average discount depth went from 0% to 41%.

### Year 1 Retention Comparison (same-age: 365 days post-acquisition)

| Cohort | Customers | 60d Retention | 180d Retention | 365d Retention | Avg Y1 Revenue |
|---|---|---|---|---|---|
| 2020 | 803 | 12.0% | 27.4% | **37.1%** | S$441 |
| 2021 | 1,283 | 13.4% | 21.9% | 26.0% | S$235 |
| 2022 | 618 | 12.1% | 20.6% | 24.3% | S$282 |
| 2023 | 510 | **10.0%** | 18.4% | 22.2% | S$108 |
| 2024 | 1,065 | 14.0% | 22.4% | 25.6% | S$105 |

**Cohort quality is declining at the same age.** 365-day retention fell from 37.1% (2020) to 22.2% (2023). Year 1 revenue per customer fell from S$441 to S$105 — a 76% collapse.

- 2020–2021 avg 365d retention: **31.6%**
- 2023–2024 avg 365d retention: **23.9%**
- **Quality drift: −7.7 percentage points**

### Channel Mix Shift by Cohort Year

| Cohort | Direct/Subscription | Marketplace |
|---|---|---|
| 2020 | 100% | 0.0% |
| 2021 | 100% | 0.0% |
| 2022 | 94.5% | 5.5% |
| 2023 | 49.6% | **50.4%** |
| 2024 | 79.4% | 20.6% |

**In 2023, marketplace acquisition reached 50% of all new customers.** This is a structural shift — marketplace customers have 1.7× lower LTV, no confirmed Shopify subscription conversion, and 2.3× lower repeat rates. The 2023 cohort's poor performance is largely explained by this channel mix shift.

### Discount Intensity by Cohort

| Cohort | % Discounted | Avg Disc Depth | Avg 1st Order |
|---|---|---|---|
| 2020 | 0.0% | 0% | S$176 |
| 2021 | 0.0% | 0% | S$102 |
| 2022 | 11.0% | 51.6% | S$169 |
| 2023 | 59.4% | 22.6% | S$73 |
| 2024 | 82.7% | 41.0% | S$63 |

From 0% to 83% discounted first orders in 4 years. **The brand has progressively trained its acquisition funnel to attract discount-sensitive buyers — the exact customer profile with the worst long-term retention.**

---

## Lens 5 — How Healthy Is the Customer Base?
*(Script: `11_lens5_base_health.py` | All cohorts, all SGD calendar years)*

### Cohort × Year Revenue Matrix (SGD, thousands)

| Cohort | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| 2020 | S$286K | S$181K | S$127K | S$24K | S$25K | S$11K |
| 2021 | — | S$226K | S$95K | S$11K | S$9K | S$6K |
| 2022 | — | — | S$163K | S$17K | S$10K | S$4K |
| 2023 | — | — | — | S$49K | S$10K | S$5K |
| 2024 | — | — | — | — | S$95K | S$30K |

This is the "triangle." Each row is a cohort; each column is a calendar year. The off-diagonal cells are much smaller than the acquisition-year cells. **Cohorts fade rapidly and do not accumulate.**

### Revenue Decay Curves (% of acquisition-year revenue)

| Cohort | Age+0 | Age+1 | Age+2 | Age+3 | Age+4 |
|---|---|---|---|---|---|
| 2020 | 100% | **63.1%** | 44.5% | 8.3% | 8.8% |
| 2021 | 100% | **41.9%** | 5.1% | 4.1% | — |
| 2022 | 100% | **10.3%** | 6.4% | 2.5% | — |
| 2023 | 100% | **20.1%** | 10.5% | — | — |

**Decay is accelerating.** The 2020 cohort retained 63% of its acquisition-year revenue in Year 1. The 2022 cohort retained only 10.3%. This is the smoking gun for declining cohort quality.

### Customer Base Composition Waterfall (SGD)

| Year | Total | New | Retained | Recovered | %New | %Ret |
|---|---|---|---|---|---|---|
| 2020 | 803 | 803 | 0 | 0 | 100% | 0% |
| 2021 | 1,517 | 1,283 | 234 | 0 | **85%** | 15% |
| 2022 | 983 | 618 | 317 | 48 | 63% | 32% |
| 2023 | 736 | 510 | 182 | 44 | 69% | 25% |
| 2024 | 1,332 | 1,065 | 161 | 106 | **80%** | 12% |
| 2025 | 3,621 | 3,340 | 221 | 60 | **92%** | 6% |

In 2024 and 2025, **80–92% of active customers are new** — buying for the first time. The retained base is not growing. The entire business depends on continuous acquisition spending.

### Revenue Composition (SGD)

| Year | Total Rev | % from New | % from Retained | % from Recovered |
|---|---|---|---|---|
| 2021 | S$407K | 56% | 44% | 0% |
| 2022 | S$385K | 42% | 53% | 5% |
| 2023 | S$101K | 49% | 45% | 6% |
| 2024 | S$150K | 63% | 27% | 10% |
| 2025 | S$335K | **83%** | 13% | 3% |

In 2025, **83% of SGD revenue came from first-time buyers**. Only 13% from customers who had bought before. This is the definition of an acquisition-dependent revenue model.

### Customer Base Health Scorecard

| KPI | Value | Status | Target |
|---|---|---|---|
| Overall Repeat Rate | 32.4% | **ALERT** | >35% |
| YoY Retention (latest yr) | 6.8% | **ALERT** | >40% |
| Avg 60-Day Cohort Retention | 18.1% | **ALERT** | >20% |
| Acquisition Dependency | 41.0% | OK | <50% |
| Top 20% Revenue Concentration | 79.5% | OK | <80% |

Three of five KPIs are in alert. The acquisition dependency score at 41% is only borderline OK — and trending toward alert if the 2025 pattern (83% new) continues.

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

> Marketplace 0% subscribed reflects Shopify subscriptions only. Shopee/Lazada auto-delivery systems are not tracked in Shopify.

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
| **Full price (0%)** | **8,635** | **38.0%** | **S$293** |
| 1–5% off | 395 | 25.1% | S$132 |
| 5–10% off | 536 | 23.3% | S$129 |
| 10–20% off | 1,133 | 24.8% | S$119 |
| 20–30% off | 1,286 | 24.2% | S$155 |
| 30–50% off | 555 | 22.3% | S$105 |
| **50%+ off** | **1,240** | **19.1%** | **S$54** |

Full-price buyers repeat at **38.0%** with **S$293 LTV**.
50%+ discount buyers repeat at **19.1%** with **S$54 LTV** — a **2.0× repeat gap and 5.4× LTV gap**.

The drop is immediate and steep: any discount at all pulls the repeat rate from 38% to the low 20s. The LTV damage is consistent across all discount depths. The 50%+ cohort (S$54 LTV) is acquiring customers at near-zero lifetime value — many of these are the 100% affiliate orders or event give-away codes.

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
| 1 | Deep discounting destroys cohort quality | Full-price: 38.0% repeat, S$293 LTV vs 50%+ off: 19.1% repeat, S$54 LTV | High | Cap new-customer discount at 15%; remove 50%+ deals |
| 2 | Cross-sell drives biggest LTV jump | 3-product buyers: 65.5% repeat, S$470 LTV (+176% vs 1-product) | High | Post-purchase cross-sell email at Day 14–21 |
| 3 | At Risk segment = immediate high-value opportunity | 2,351 customers, S$514 avg LTV, currently dormant | High | Targeted win-back campaign |
| 4 | Subscription cadence causes stockpile churn | 27% cancel "already have too much"; peak churn at Cycle 1 | High | Add 45/60-day interval option + skip-delivery CTA |
| 5 | Marketplace cannibalises LTV | 14.4% repeat vs 33.5% direct; 1.7× LTV gap (S$115 vs S$198) | Medium | Reduce marketplace SKU breadth; redirect budget to own channels |
| 3 | At Risk segment = urgent win-back opportunity | 2,351 customers, S$514 avg LTV, currently dormant | High | Targeted win-back campaign with strongest available offer |
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
