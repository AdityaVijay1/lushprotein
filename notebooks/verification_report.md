# Gold/Silver Notebook Verification Report

Primary source of truth: `data/gold` and `data/silver`. Primary revenue excludes shipping (`order_revenue_sgd`, `total_revenue_sgd`). Legacy EDA/chart revenue used `Price: Total` including shipping; notebooks report that delta where revenue totals are compared.

## Coverage Matrix

| File | Status | Notebook Coverage | Notes |
|---|---|---|---|
| `EDA/00_config.py` | Partial | `00_data_mart_quality_and_source_map.ipynb` | Product/channel semantics are reflected through mart columns; raw path constants are obsolete for Gold/Silver notebooks. |
| `EDA/01_load_and_merge.py` | Cannot verify from Gold/Silver | `00_data_mart_quality_and_source_map.ipynb` | Raw Excel/CSV ingestion creates the downstream marts; Gold/Silver cannot verify raw import behavior by themselves. |
| `EDA/02_data_quality.py` | Verified with revenue-basis delta | `00_data_mart_quality_and_source_map.ipynb` | Recreated with Gold revenue excluding shipping; legacy including-shipping delta is reported. Product master row count is partially comparable because Silver is cleaned/deduplicated. |
| `EDA/03_customer_retention.py` | Verified | `01_customer_retention_rfm.ipynb` | Repeat slices, time-to-second purchase, cohort retention, and RFM recreated. |
| `EDA/04_product_analysis.py` | Verified | `02_product_crosssell_subscription.ipynb` | Product repeat, cross-sell, product revenue, SKU popularity recreated from Gold/Silver. |
| `EDA/05_channel_discount.py` | Verified with revenue-basis delta | `03_channel_discount_cohort_quality.ipynb` | Channel, discount sensitivity, depth bins, and taxonomy recreated using Gold revenue. |
| `EDA/06_subscription_churn.py` | Verified | `02_product_crosssell_subscription.ipynb` | Subscription LTV and Recharge churn/reactivation outputs recreated from Gold/Silver and Silver Recharge detail tables. |
| `EDA/07_lens1_heterogeneity.py` | Verified with revenue-basis delta | `04_customer_base_audit_lenses.ipynb` | Lens 1 recreated with Gold revenue excluding shipping. |
| `EDA/08_lens2_period_decomposition.py` | Verified with revenue-basis delta | `04_customer_base_audit_lenses.ipynb` | Period decomposition, migration, and up/down recreated. |
| `EDA/09_lens3_cohort_evolution.py` | Verified with revenue-basis delta | `04_customer_base_audit_lenses.ipynb` | Cohort evolution, purchase incidence, inter-purchase timing, and VTD recreated. |
| `EDA/10_lens4_vintage_comparison.py` | Verified with revenue-basis delta | `04_customer_base_audit_lenses.ipynb` | Vintage quality, year-1 comparison, channel mix, and discount intensity recreated. |
| `EDA/11_lens5_base_health.py` | Verified with revenue-basis delta | `04_customer_base_audit_lenses.ipynb` | Cohort revenue matrix, decay, composition, and scorecard recreated. |
| `EDA/disc_depth_check.py` | Verified | `03_channel_discount_cohort_quality.ipynb` | Discount-depth bins and chart inputs recreated. |
| `EDA/disc_pct_compare.py` | Verified with revenue-basis delta | `00_data_mart_quality_and_source_map.ipynb`, `03_channel_discount_cohort_quality.ipynb` | Annual discount percent uses Gold revenue basis. |
| `EDA/fix_encoding.py` | Cannot verify from Gold/Silver | None | Raw encoding repair utility, not an insight file. |
| `EDA/fix_encoding2.py` | Cannot verify from Gold/Silver | None | Raw encoding repair utility, not an insight file. |
| `EDA/fix_encoding3.py` | Cannot verify from Gold/Silver | None | Raw encoding repair utility, not an insight file. |
| `EDA/overlap_check.py` | Verified | `04_customer_base_audit_lenses.ipynb` | Annual overlap/new/retained/lost analysis recreated. |
| `EDA/run_eda.py` | Not an insight file | All notebooks | Orchestrator only; downstream analytical outputs are covered. |
| `EDA/slide1_verify.py` | Verified with revenue-basis delta | `03_channel_discount_cohort_quality.ipynb` | Scope, repeat, and LTV checks recreated using Gold revenue. |
| `EDA/slide5_claims_check.py` | Verified | `01_customer_retention_rfm.ipynb` | Time-to-second and related slide claims recreated. |
| `EDA/slide_numbers_check.py` | Verified with revenue-basis delta | `01_customer_retention_rfm.ipynb`, `02_product_crosssell_subscription.ipynb`, `03_channel_discount_cohort_quality.ipynb` | Slide metrics recreated; revenue claims use Gold excluding-shipping basis. |
| `EDA/t2_breakdown.py` | Verified | `01_customer_retention_rfm.ipynb` | Time-to-second purchase bucket details recreated. |
| `EDA/t2_check.py` | Verified | `01_customer_retention_rfm.ipynb` | Time-to-second purchase checks recreated. |
| `EDA/trace_datasets.py` | Partial | `00_data_mart_quality_and_source_map.ipynb` | Mart lineage is recreated; raw file row-level trace requires raw source reads and is outside Gold/Silver-only verification. |
| `EDA/verify_all.py` | Verified with revenue-basis delta | All notebooks | Core row counts and metric checks recreated across grouped notebooks. |
| `visualizations/01_revenue_and_volume.py` | Verified with revenue-basis delta | `05_presentation_charts_recreated.ipynb` | Charts recreated inline from Gold revenue basis. |
| `visualizations/02_retention_overview.py` | Verified | `01_customer_retention_rfm.ipynb`, `05_presentation_charts_recreated.ipynb` | Retention charts recreated inline. |
| `visualizations/03_product_and_crosssell.py` | Verified | `02_product_crosssell_subscription.ipynb`, `05_presentation_charts_recreated.ipynb` | Product/cross-sell charts recreated inline. |
| `visualizations/04_subscription_churn.py` | Verified | `02_product_crosssell_subscription.ipynb`, `05_presentation_charts_recreated.ipynb` | Subscription/churn charts recreated inline. |
| `visualizations/05_discount_channel.py` | Verified with revenue-basis delta | `03_channel_discount_cohort_quality.ipynb`, `05_presentation_charts_recreated.ipynb` | Discount/channel charts recreated inline. |
| `visualizations/06_channel_quality_chart.py` | Verified | `03_channel_discount_cohort_quality.ipynb`, `05_presentation_charts_recreated.ipynb` | Channel quality dual-axis chart recreated inline. |
| `visualizations/07_slide3_charts.py` | Verified with revenue-basis delta | `05_presentation_charts_recreated.ipynb` | Slide 3 charts recreated inline from Gold revenue basis. |
| `visualizations/run_visualizations.py` | Not an insight file | `05_presentation_charts_recreated.ipynb` | Orchestrator only. |
| `visualizations/style.py` | Not an insight file | `05_presentation_charts_recreated.ipynb` | Styling helper only; chart output coverage verifies downstream use. |

## Expected Non-Exact Matches

- Revenue totals in the new notebooks are lower than old EDA/chart totals by shipping revenue because Gold/Silver revenue excludes shipping.
- Silver product master has fewer rows than the legacy raw-loaded product workbook because it is cleaned and variant-aligned.
- Raw encoding and raw import utilities cannot be verified solely from downstream Gold/Silver marts.
