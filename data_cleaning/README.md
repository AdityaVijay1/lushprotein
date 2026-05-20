# Data Cleaning Report

This folder contains the data cleaning and preparation workflow for the LushProtein customer analytics project. The work is organised using a medallion architecture:

- `01_silver_layer.ipynb` builds the **Silver layer**: cleaned, source-aligned datasets from the raw numbered folders.
- `02_gold_layer.ipynb` builds the **Gold layer**: analysis-ready customer, line-item, and subscription marts derived only from Silver.

The cleaned outputs are stored in:

- `data/silver/`
- `data/gold/`

The cleaning process was designed to support customer analytics, cohort analysis, retention analysis, discount analysis, product analysis, and subscription analysis while preserving enough source-level detail for auditability.

---

## 1. Scope Of Datasets

The workflow uses the raw numbered source folders:

| Source folder | Source type | Primary analytical use |
|---|---|---|
| `1.customer_transaction` | Shopify / Matrixify order exports | Orders, customers, line items, discounts, shipping, fulfilment, refunds |
| `2.product_master` | Shopify product master | Product variant / SKU lookup |
| `3.Discounts` | Discount code export | Discount metadata and usage |
| `4.Campaigns` | Aggregated sessions by referrer | Top-of-funnel channel context |
| `5.Recharge_data` | Recharge subscription exports | Subscription orders, checkout items, recurring items, churn, reactivation |

The current cleaned dataset covers Shopify order activity from **2020-01-01 to 2026-03-31**.

---

## 2. Medallion Outputs

### Silver Layer

Silver tables are cleaned but remain close to source grain.

| Dataset | Rows | Columns | Grain |
|---|---:|---:|---|
| `orders.parquet` | 27,350 | 49 | One row per cleaned Shopify order |
| `lines.parquet` | 50,963 | 42 | One row per Shopify product line item |
| `order_non_product_lines.parquet` | 102,608 | 41 | One row per non-product Shopify row |
| `products.parquet` | 56 | 25 | One row per product variant SKU |
| `discounts.parquet` | 367 | 17 | One row per discount code |
| `campaigns.parquet` | 137,033 | 10 | One aggregate row per referrer / UTM / landing-page / city combination |
| `recharge_orders.parquet` | 1,215 | 10 | One row per Recharge order |
| `recharge_checkout_items.parquet` | 1,094 | 14 | One row per Recharge checkout item |
| `recharge_recurring_items.parquet` | 650 | 14 | One row per Recharge recurring item |
| `recharge_reactivated.parquet` | 50 | 4 | One row per reactivation event |
| `recharge_churned.parquet` | 526 | 12 | One row per churned subscription record |

### Gold Layer

Gold tables are analysis-ready marts.

| Dataset | Rows | Columns | Grain |
|---|---:|---:|---|
| `customers.parquet` | 13,780 | 17 | One row per Shopify customer |
| `order_lines_enriched.parquet` | 50,963 | 51 | One row per product line item enriched with product master fields |
| `recharge_orders_enriched.parquet` | 1,215 | 22 | One row per Recharge order enriched with Shopify order context |

---

## 3. Exploratory Data Analysis Summary

### 3.1 Shopify Order Coverage

The cleaned Shopify order table contains:

- **27,350** unique orders.
- **13,780** unique customers.
- **0 duplicate `order_id` rows** in `orders.parquet`.
- Date range: **2020-01-01 to 2026-03-31**.
- All order revenue is converted to SGD.

Store distribution:

| Store | Orders |
|---|---:|
| SG | 16,039 |
| MY | 11,309 |
| HK | 2 |

Channel distribution:

| Channel | Orders |
|---|---:|
| Direct / Organic | 13,208 |
| Subscription | 10,230 |
| Marketplace | 3,268 |
| Paid Social | 473 |
| Email | 128 |
| Affiliate | 40 |
| Paid Search | 3 |

### 3.2 Revenue, Discounts, And Shipping

Revenue was separated into product/order revenue and shipping revenue because customer analytics should not treat shipping fees as customer product value.

| Metric | Value |
|---|---:|
| Order revenue excluding shipping | SGD 3,075,739 |
| Shipping revenue | SGD 37,212 |
| Discounts given | SGD 464,184 |
| Total including shipping | SGD 3,112,952 |

The Silver notebook validates:

```text
order_revenue_sgd = order_total_incl_shipping_sgd - shipping_revenue_sgd
```

This validation passes for all cleaned orders.

### 3.3 Customer Summary

The Gold customer table contains:

- **13,780** unique customers.
- **32.4%** repeat rate.
- Median days to second purchase: **49 days**.
- **7.9%** of customers ever subscribed.
- **45.2%** of customers ever had a discount.
- Customer revenue reconciles exactly to Silver order revenue, with only floating point rounding difference.

### 3.4 Product Line Items

The Silver line-item table contains:

- **50,963** product line rows.
- **0 duplicate (`order_id`, `line_id`) rows**.
- **98.4%** of line items map to cleaned orders.
- **51.6%** of line items have a non-null SKU.

The Gold enriched line-item table preserves the same line-item row count:

- `lines.parquet`: 50,963 rows.
- `order_lines_enriched.parquet`: 50,963 rows.

Product master matching is intentionally conservative:

- Only **11.1%** of line items match the current product master by SKU.
- Unmatched SKUs are retained and reported rather than force-joined.

Top unmatched SKU examples include:

| SKU | Unmatched line count |
|---|---:|
| Missing / null SKU | 24,680 |
| `0724999808361` | 1,860 |
| `0724999807814` | 1,494 |
| `0724999807821` | 1,206 |
| `0724999808507` | 1,168 |

### 3.5 Non-Product Shopify Rows

The raw Shopify export contains many non-product rows. These are preserved separately in Silver.

| Row type | Rows |
|---|---:|
| Fulfillment Line | 50,089 |
| Shipping Line | 24,980 |
| Transaction | 17,262 |
| Discount | 8,774 |
| Refund Line | 1,329 |
| Refund Shipping | 174 |

These rows are useful for audit and operational diagnostics, but not for direct product demand analysis.

### 3.6 Campaign Coverage

The campaigns table contains **137,033** rows of pre-aggregated traffic data.

Important limitation:

- There is no order ID.
- There is no customer ID.
- There is no date column.
- About **50.1%** of rows have at least one missing dimension among the referrer / UTM / landing-page / city key fields.
- There are **0 duplicate rows** across the full campaign dimension key.

This table is therefore useful for top-of-funnel context, not exact attribution or conversion analysis.

### 3.7 Recharge Subscription Coverage

Recharge tables are cleaned separately because they have different grains.

| Recharge table | Rows | Key finding |
|---|---:|---|
| `recharge_orders` | 1,215 | `recharge_order_id` is unique; `shopify_order_id` coverage is 100% |
| `recharge_checkout_items` | 1,094 | 16.6% missing `product_sku`; 41 duplicate (`recharge_order_id`, `product_sku`) rows |
| `recharge_recurring_items` | 650 | 11.2% missing `product_sku`; 3 duplicate (`recharge_order_id`, `product_sku`) rows |
| `recharge_reactivated` | 50 | 0 duplicate (`customer_id`, `reactivated_date`) rows |
| `recharge_churned` | 526 | 3 duplicate (`subscription_id`, `subscription_churn_date`) rows |

Recharge order enrichment is validated:

- **95.7%** of Recharge orders match Shopify orders by `shopify_order_id`.
- **52 Recharge orders** do not match Shopify orders.
- Row count is preserved after enrichment: 1,215 in, 1,215 out.

---

## 4. Critical Data Issues, Impact, And Mitigation

### Issue 1: Shopify Export Has Mixed Grain

**Problem**

The Shopify customer transaction export is not one row per order. It mixes order headers, product line items, fulfilment lines, shipping lines, discount rows, transaction rows, and refund rows.

**Why it matters**

If all rows are treated as orders or product lines, revenue, quantity, order counts, and product demand can be severely double-counted. Fulfilment lines are especially dangerous because they can mirror product lines with negative quantities.

**Mitigation**

The Silver notebook separates the export into:

- `orders.parquet`: order header grain.
- `lines.parquet`: product line-item grain.
- `order_non_product_lines.parquet`: non-product operational / audit rows.

Order-level context is forward-filled within each order block before splitting the data, which makes the pipeline robust to Matrixify-style exports where child rows visually belong to the previous filled order.

**Evidence**

- `orders.parquet` has **27,350 rows** and **27,350 unique `order_id`s**.
- `lines.parquet` has **50,963 rows** and **0 duplicate (`order_id`, `line_id`) rows**.
- Non-product rows are preserved separately instead of being discarded.

---

### Issue 2: Shipping Was Included In Revenue

**Problem**

Shopify total revenue includes shipping. For customer analytics, shipping fees should not generally be interpreted as product revenue or customer value.

**Why it matters**

Including shipping inflates revenue per customer and can distort cohort quality, AOV, CLV, repeat purchase value, and discount effectiveness analysis.

**Mitigation**

The Silver layer creates explicit revenue fields:

- `order_total_incl_shipping_sgd`
- `shipping_revenue_sgd`
- `order_revenue_sgd`

Gold customer revenue uses `order_revenue_sgd`, not shipping-inclusive Shopify totals.

**Evidence**

The notebook validates the formula:

```text
order_revenue_sgd = order_total_incl_shipping_sgd - shipping_revenue_sgd
```

This check passes for all orders. Gold customer revenue also reconciles back to Silver order revenue.

---

### Issue 3: Multi-Currency Data Across Asian Markets

**Problem**

The data spans Singapore, Malaysia, and Hong Kong store prefixes. Revenue fields may be in different store currencies.

**Why it matters**

Combining currencies without conversion would make revenue, discount, AOV, and CLV comparisons invalid.

**Mitigation**

The pipeline derives store from order prefixes:

- `LP` / `LPSG` = Singapore.
- `LPMY` = Malaysia.
- `LPHK` = Hong Kong.

Revenue fields are converted to SGD using fixed project assumptions:

- `1 SGD = 3.30 MYR`
- `1 SGD = 6.10 HKD`

**Evidence**

The cleaned order table records all order money fields in SGD, and preserves the original currency context separately where applicable. Store distribution is explicitly checked after cleaning.

**Limitation**

Fixed exchange rates do not capture historical FX movement. This is acceptable for directional customer analytics, but absolute historical revenue comparisons should mention this limitation.

---

### Issue 4: Product Master Coverage Is Low

**Problem**

Only **11.1%** of line items match the product master by SKU. Many line items have missing SKUs or old barcode-style SKUs that are not represented in the current product master.

**Why it matters**

If product enrichment is forced, product-level insights may be wrong. Older products or legacy SKUs could be misclassified, undercounted, or incorrectly mapped to current products.

**Mitigation**

The Gold layer performs a conservative SKU-based enrichment only. It does not force fuzzy joins or handle-level joins where SKU confidence is low.

Unmatched records are retained and reported.

**Evidence**

- Line-item row count before enrichment: **50,963**.
- Line-item row count after enrichment: **50,963**.
- Product master has **56 unique variant SKUs**.
- Top unmatched SKU values are reported in validation output.

This proves enrichment does not change the line-item grain or silently drop unmatched products.

---

### Issue 5: Recharge Tables Are Not All Mergeable

**Problem**

Recharge exports represent different business grains:

- Recharge orders.
- Checkout items.
- Recurring items.
- Reactivated subscribers.
- Churned subscriptions.

Recharge customer IDs are not assumed to be the same as Shopify customer IDs.

**Why it matters**

Blindly merging Recharge tables together can create many-to-many joins, duplicate subscription revenue, or attach churn/reactivation events to the wrong customer/order.

**Mitigation**

Recharge tables are kept separate in Silver. The only Gold enrichment is:

```text
recharge_orders.shopify_order_id -> orders.order_id
```

This join is validated as many-to-one and row-preserving.

**Evidence**

- Recharge orders before join: **1,215**.
- Recharge orders after enrichment: **1,215**.
- Shopify match rate: **95.7%**.
- Unmatched Recharge orders: **52**.

The unmatched orders are preserved instead of dropped.

---

### Issue 6: Campaign Data Has No Conversion Join Key

**Problem**

Campaign/session data is aggregated and has no date, order ID, or customer ID.

**Why it matters**

It cannot support precise customer-level attribution or conversion rate analysis.

**Mitigation**

Campaigns are kept as a standalone Silver table for directional channel context only. They are not joined into Gold customer or order tables.

**Evidence**

- Campaign rows: **137,033**.
- Duplicate campaign dimension rows: **0**.
- Rows with at least one missing dimension field: **50.1%**.
- No customer/order/date join key exists.

This supports the decision to avoid direct attribution joins.

---

### Issue 7: Missing Values And Duplicate Keys

**Problem**

Several datasets contain missing values or duplicate business keys:

- Shopify shipping country missing in **3.9%** of cleaned orders.
- Shopify fulfilment status missing in **0.8%** of cleaned orders.
- Discounts contain **1 duplicate `Name`**.
- Recharge checkout items have **16.6% missing `product_sku`**.
- Recharge recurring items have **11.2% missing `product_sku`**.
- Recharge churned has **3 duplicate (`subscription_id`, `subscription_churn_date`) rows**.

**Why it matters**

Missing and duplicate keys can bias geography analysis, SKU-level subscription analysis, churn counts, discount-code analysis, and joins.

**Mitigation**

The notebooks report these issues instead of hiding them. Mitigation depends on analysis use case:

- For customer/order analysis, missing shipping country is flagged but not imputed.
- For product-level Recharge analysis, missing SKU rows should be grouped as `Unknown` or excluded in sensitivity checks.
- For discount-code analysis, duplicate discount names should be inspected before treating code name as a strict primary key.
- For churn analysis, duplicate subscription/date rows should be deduplicated only if confirmed to represent duplicate exports rather than separate churn records.

**Evidence**

Validation summaries print null-key counts, duplicate-key counts, and required-column checks for every Silver and Gold dataset.

---

### Issue 8: Outliers And Skewed Customer Value

**Problem**

Customer revenue is highly skewed. Averages can be distorted by high-spending customers or bulk-like orders.

**Why it matters**

Annual revenue per customer can overstate or understate true cohort quality if the distribution changes.

**Mitigation**

The deeper cohort-quality notebook adds distribution checks such as median, p75, p90, p95, top 10% revenue share, and top 1% revenue share.

**Evidence**

The deep-dive outputs are stored in:

```text
data/gold/cohort_quality_deepdive/
```

These outputs compare average and distributional customer value, not only annual totals.

---

## 5. Evidence That Mitigation Is Reasonable

The mitigation approach is supported by several validation checks.

### 5.1 Grain Preservation

| Check | Result |
|---|---|
| `orders.parquet` has one row per `order_id` | Pass |
| `lines.parquet` has no duplicate (`order_id`, `line_id`) rows | Pass |
| `customers.parquet` has one row per `customer_id` | Pass |
| `order_lines_enriched.parquet` preserves line-item row count | Pass |
| `recharge_orders_enriched.parquet` preserves Recharge order row count | Pass |

### 5.2 Revenue Reconciliation

| Check | Result |
|---|---|
| Order revenue excludes shipping | Pass |
| Gold customer revenue reconciles to Silver order revenue | Pass |
| Money columns are numeric | Pass |

### 5.3 Join Robustness

| Join | Validation |
|---|---|
| Product line item -> product master | Conservative many-to-one SKU join; unmatched retained |
| Recharge order -> Shopify order | Many-to-one join; row count preserved |
| Campaign -> order/customer | Not attempted because no valid join key exists |
| Recharge item/churn/reactivation joins | Not attempted by default because grains differ |

### 5.4 Before / After Logic

| Before cleaning risk | After cleaning mitigation |
|---|---|
| Mixed Shopify rows could double-count orders and demand | Split into order, line-item, and non-product tables |
| Shipping-inclusive revenue could inflate customer value | Created `order_revenue_sgd` excluding shipping |
| Child rows may rely on prior order header context | Forward-filled order-level fields within order blocks |
| Product master gaps could cause bad joins | Retained unmatched rows and reported match coverage |
| Recharge files could create many-to-many joins | Kept separate unless validated keys exist |
| Aggregated campaign data could imply false attribution | Kept standalone for context only |

---

## 6. Recommended Use Of Cleaned Layers

Use `data/silver` when the analysis needs source-level auditability or a custom aggregation.

Use `data/gold` for most project analysis:

| Analysis question | Recommended dataset |
|---|---|
| Customer repeat rate / retention / CLV | `data/gold/customers.parquet` |
| Product mix / basket analysis | `data/gold/order_lines_enriched.parquet` |
| Subscription order analysis | `data/gold/recharge_orders_enriched.parquet` |
| Discount and cohort quality deep dive | `data/gold/cohort_quality_deepdive/` |
| Raw shipping / refund / fulfilment diagnostics | `data/silver/order_non_product_lines.parquet` |
| Top-of-funnel campaign context | `data/silver/campaigns.parquet` |

---

## 7. Key Takeaway

The most important cleaning decision was to avoid forcing all data into one wide table. The source data contains multiple platforms and multiple grains. The cleaning pipeline therefore separates grain first, validates keys and joins second, and only then creates Gold tables for analysis.

This approach reduces the risk of double-counting, false attribution, shipping-inflated revenue, and invalid Recharge joins. It also gives the project a defensible audit trail: every major mitigation has a validation check or coverage statistic attached to it.

