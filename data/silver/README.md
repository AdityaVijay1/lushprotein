# Silver Layer

Silver contains cleaned, source-aligned tables. These tables have parsed dates, cleaned IDs, consistent object columns, and SGD-normalized money fields where relevant. They are still close to the original source grains and are intended for auditability and reusable downstream modeling.

| Dataset | Grain | What it contains | Notes |
|---|---:|---|---|
| `orders.parquet` | 1 row per Shopify order | Cleaned order headers, customer ID, order date, store, channel, payment/fulfilment status, shipping geography, shipping fee, non-shipping order revenue, discount totals, subscription flag, and a array-based `line_items` and `line_item_skus` summary columns | Use for customer value, cohorts, retention, geography, channel, and shipping-fee analysis. Use `order_revenue_sgd` for revenue because it excludes shipping. |
| `lines.parquet` | 1 row per Shopify product line item | Product line items from `Line: Type == Line Item`, including SKU, handle, quantity, line value excluding shipping, and product category | Use for product/category/basket analysis. |
| `order_non_product_lines.parquet` | 1 row per non-product Shopify row | Shipping lines, discount rows, transaction rows, refund rows, and fulfilment lines | Preserved for audit. Do not mix fulfilment lines into product demand metrics because they mirror product lines with negative quantities. |
| `products.parquet` | 1 row per product variant SKU | Cleaned product master variant lookup | Used to enrich line items by SKU when a reliable SKU match exists. |
| `discounts.parquet` | 1 row per discount code | Discount metadata, value/type/status/usage | Kept separate unless an order-level discount-code key exists. |
| `campaigns.parquet` | 1 row per aggregate referrer/session combination | Pre-aggregated traffic by referrer, UTM, landing page, city, visitors, sessions | No date/customer/order key, so it is not joined to orders. |
| `recharge_orders.parquet` | 1 row per Recharge order | Subscription order totals and Shopify order IDs | Kept at Recharge order grain. |
| `recharge_checkout_items.parquet` | 1 row per Recharge checkout item | First subscription checkout item lines | Kept separate from recurring items. |
| `recharge_recurring_items.parquet` | 1 row per Recharge recurring item | Subscription renewal item lines | Kept separate from checkout items. |
| `recharge_reactivated.parquet` | 1 row per reactivation event | Subscriber reactivation dates | Recharge customer IDs are not assumed to equal Shopify customer IDs. |
| `recharge_churned.parquet` | 1 row per churned subscription record | Subscription churn dates, SKU/title, churn type, cancellation reason | Subscription grain; not merged to other Recharge files by default. |

## Customer Transaction Grain Decision

For customer analytics, order headers and product line items are necessary. Shipping geography, shipping fee, and fulfilment status are retained on `orders.parquet`; revenue analysis should use `order_revenue_sgd`, which excludes shipping. Detailed `Shipping Line`, `Discount`, `Refund Line`, and `Refund Shipping` rows can support operational diagnostics, so they are preserved in `order_non_product_lines.parquet`. `Fulfillment Line` rows are not promoted to Gold because they do not contain delivery timing/carrier detail in this export and would double-count or reverse product quantities if mixed with product line items.
