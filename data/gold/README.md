# Gold Layer

Gold contains analysis-ready marts built from validated Silver tables. These are the recommended starting point for customer analytics, dashboards, and modeling.

| Dataset | Grain | What it contains | Notes |
|---|---:|---|---|
| `customers.parquet` | 1 row per Shopify customer | First/last order date, total orders, non-shipping revenue, discounts, repeat flag, subscription/discount flags, first channel/product/store, recency, cohort month | Recommended for retention, RFM, repeat behavior, and CLV-style analysis. Revenue uses `order_revenue_sgd`, excluding shipping. |
| `order_lines_enriched.parquet` | 1 row per Shopify product line item | Silver line items enriched with product master fields where SKU matching is valid; line-level values exclude shipping | Product-master coverage is reported in the notebook; unmatched older SKUs are kept rather than forced into bad joins. |
| `recharge_orders_enriched.parquet` | 1 row per Recharge order | Recharge orders enriched with Shopify order context using validated `shopify_order_id -> order_id` many-to-one merge | Created only when merge validation passes. Checkout, recurring, churn, and reactivation files remain separate because they have different grains. |

## Recommended Usage

Use `customers.parquet` for customer-level questions, `order_lines_enriched.parquet` for product/category/basket questions, and `recharge_orders_enriched.parquet` for subscription order questions. Use Silver only when you need source-level auditability or a different custom aggregation.
